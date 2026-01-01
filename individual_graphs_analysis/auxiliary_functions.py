import numpy as np
import pandas as pd
import networkx as nx
import random
import math
import matplotlib.pyplot as plt
from collections import defaultdict

def generate_null_model(graph: nx.Graph):
    weights = [graph[a][b]["weight"] for a, b in graph.edges()]
    # random.seed(42)
    random.shuffle(weights)
    null_model = nx.Graph()
    for i, (a, b) in enumerate(graph.edges()):
        null_model.add_edge(a, b, weight=weights[i])
    return null_model

def absolute_graph(graph: nx.Graph):
    new_graph = nx.Graph()
    for a, b, data in graph.edges(data=True):
        new_graph.add_edge(a, b, weight=np.sign(data["weight"]))
    return new_graph

def calculate_bw(graph: nx.Graph, z = 3):
    nodes = list(graph.nodes())
    n = len(nodes)
    N = np.zeros((n, n))
    P = np.zeros((n, n))
    node_index = {node: idx for idx, node in enumerate(nodes)}

    for a, b, data in graph.edges(data=True):
        i, j = node_index[a], node_index[b]
        if data["weight"] == -1:
            N[i, j] = 1
            N[j, i] = 1
        else:
            P[i, j] = 1
            P[j, i] = 1
    
    max_eigenvalue = max(np.linalg.eigvalsh(P))
    
    # alfa = z / max_eigenvalue
    alfa = 2
    
    #BW(α) = 1/2 Tr[N((αλI - P)^(-1))]
    I = np.eye(n)
    matrix_to_invert = alfa * max_eigenvalue * I - P
    inv_matrix = np.linalg.inv(matrix_to_invert)
    bw_matrix = np.dot(N, inv_matrix)
    bw_value = np.trace(bw_matrix) / 2
    return bw_value

def geo_abs(triangle: list):
    product = (abs(triangle[0]) * abs(triangle[1]) * abs(triangle[2])) ** (1 / 3)
    signs = [np.sign(triangle[0]), np.sign(triangle[1]), np.sign(triangle[2])]
    if signs.count(-1) % 2:
        product *= -1
    return product

def in_balance(triangle: list):
    triangle = list(np.sign(np.array(triangle)))
    for el in triangle:
        assert(el)
    
    return 1 - (triangle.count(-1) % 2)

def kolmogorov(vals_a, cum_a, vals_b, cum_b, normalize=False):
    """
    Compute the Kolmogorov-like maximum absolute difference between two cumulative distributions.

    Parameters
    - vals_a, cum_a: arrays for the real distribution (sorted x values and cumulative counts)
    - vals_b, cum_b: arrays for the null/average distribution (sorted x values and cumulative counts)
    - normalize: if True, normalize both cumulative series to [0,1] by dividing by their final value

    Returns
    - int: maximum absolute difference across the union of x values (rounded to nearest integer)
    """
    vals_a = np.asarray(vals_a)
    cum_a = np.asarray(cum_a, dtype=float)
    vals_b = np.asarray(vals_b)
    cum_b = np.asarray(cum_b, dtype=float)

    # Combined x-grid (union of both sets of x positions)
    all_vals = np.array(sorted(set(vals_a.tolist()) | set(vals_b.tolist())))
    if all_vals.size == 0:
        return 0

    def forward_fill(vals, cum, x_grid):
        """For each x in x_grid, return the cumulative value at the largest vals <= x (or 0)."""
        if vals.size == 0:
            return np.zeros_like(x_grid, dtype=float)
        idx = np.searchsorted(vals, x_grid, side='right') - 1
        return np.where(idx >= 0, cum[idx], 0.0)

    y_a = forward_fill(vals_a, cum_a, all_vals)
    y_b = forward_fill(vals_b, cum_b, all_vals)

    if normalize:
        denom_a = y_a[-1] if y_a.size > 0 else 0.0
        denom_b = y_b[-1] if y_b.size > 0 else 0.0
        if denom_a > 0:
            y_a = y_a / denom_a
        if denom_b > 0:
            y_b = y_b / denom_b

    diffs = np.abs(y_a - y_b)
    max_diff = diffs.max() if diffs.size > 0 else 0

    return max_diff

def find_alfa(vals_a, cum_a, vals_b, cum_b):
    D = kolmogorov(vals_a, cum_a, vals_b, cum_b, normalize=True)
    
    return 2 * np.exp(-2 * D * D * len(vals_a) * len(vals_b) / (len(vals_b) + len(vals_a)))

def plot_weight_distribution(graphs):
    # Configuration for weight distribution histograms
    WEIGHT_BIN_CENTERS = np.arange(-1, 1.1, 0.2)
    WEIGHT_BIN_EDGES = np.append(WEIGHT_BIN_CENTERS - 0.1, WEIGHT_BIN_CENTERS[-1] + 0.1)

    # Configuration for sign distribution histograms
    SIGN_BIN_EDGES = [-1.5, -0.5, 0.5, 1.5]
    SIGN_LABELS = ["negative", "neutral", "positive"]
    SIGN_TICK_POSITIONS = [-1, 0, 1]

    # Create subplots: one row per subreddit, two columns (weight and sign distributions)
    n_subreddits = len(graphs)
    fig, axes = plt.subplots(n_subreddits, 2, figsize=(16, 8 * n_subreddits))


    def add_percentage_labels(ax, counts, bins, fontsize=14):
        """
        Add percentage labels on top of histogram bars.
        
        Parameters:
        -----------
        ax : matplotlib.axes.Axes
            The axes to add labels to
        counts : array-like
            Histogram bin counts
        bins : array-like
            Histogram bin edges
        fontsize : int, optional
            Font size for the labels (default: 14)
        """
        total = counts.sum()
        
        for count, bin_left, bin_right in zip(counts, bins[:-1], bins[1:]):
            # Calculate percentage for this bin
            percent = 100 * count / total if total > 0 else 0
            
            # Position label at the center of the bin
            x_position = (bin_left + bin_right) / 2
            
            # Add text label above the bar
            ax.text(x_position, count, f"{percent:.1f}%", 
                    ha='center', va='bottom', fontsize=fontsize)


    # Generate histograms for each subreddit
    for idx, subreddit in enumerate(graphs):
        # Extract edge weights for this subreddit
        weights = np.array([data["weight"] for _, _, data in graphs[subreddit].edges(data=True)])
        
        # --- Left panel: Weight distribution histogram ---
        ax_weight = axes[idx][0]
        
        # Plot histogram of edge weights
        counts, _, _ = ax_weight.hist(weights, bins=WEIGHT_BIN_EDGES, edgecolor="black")
        
        # Configure x-axis
        ax_weight.set_xticks(WEIGHT_BIN_CENTERS)
        ax_weight.set_xticklabels([f"{x:.1f}" for x in WEIGHT_BIN_CENTERS], rotation=60)
        
        # Add percentage labels to bars
        add_percentage_labels(ax_weight, counts, WEIGHT_BIN_EDGES)
        
        # Configure labels and title
        ax_weight.set_title(subreddit, fontsize=20)
        ax_weight.set_xlabel("Weight", fontsize=18)
        ax_weight.set_ylabel("Count", fontsize=18)
        ax_weight.tick_params(axis='both', labelsize=16)
        
        # --- Right panel: Sign distribution histogram ---
        ax_sign = axes[idx][1]
        
        # Plot histogram of edge signs (-1, 0, +1)
        sign_counts, _, _ = ax_sign.hist(np.sign(weights), bins=SIGN_BIN_EDGES, 
                                        edgecolor="black", rwidth=0.8)
        
        # Configure x-axis with categorical labels
        ax_sign.set_xticks(SIGN_TICK_POSITIONS)
        ax_sign.set_xticklabels(SIGN_LABELS, fontsize=16)
        
        # Add percentage labels to bars
        add_percentage_labels(ax_sign, sign_counts, SIGN_BIN_EDGES)
        
        # Configure labels and title
        ax_sign.set_title(subreddit, fontsize=20)
        ax_sign.set_xlabel("Sign", fontsize=18)
        ax_sign.tick_params(axis='both', labelsize=16)

    # Adjust layout to prevent overlapping elements
    plt.tight_layout()
    plt.show()
    
def simplify_graph(graph, std_threshold):
    # Step 1: Create individual subgraphs for each subreddit from the main graph
    graphs = defaultdict(nx.MultiDiGraph)

    # Extract edges by subreddit, preserving all individual interactions
    for node_a, node_b, edge_data in graph.edges(data=True):
        subreddit = edge_data["subreddit"]
        weight = edge_data["weight"]
        graphs[subreddit].add_edge(node_a, node_b, weight=weight)

    # Step 2: Consolidate multiple edges between same nodes and filter by standard deviation
    for subreddit, subreddit_graph in graphs.items():
        # Group all edge weights by node pairs
        edge_weights = defaultdict(lambda: defaultdict(list))
        
        for node_a, node_b, edge_data in subreddit_graph.edges(data=True):
            edge_weights[node_a][node_b].append(edge_data["weight"])
        
        # Create simplified undirected graph with averaged weights
        simplified_graph = nx.Graph()
        
        for node in edge_weights.keys():
            for neighbor in edge_weights[node].keys():
                # Skip self-loops
                if node == neighbor:
                    continue
                
                # Collect weights in both directions (treating as undirected)
                forward_weights = edge_weights[node][neighbor]
                backward_weights = (edge_weights[neighbor][node] 
                                if neighbor in edge_weights and node in edge_weights[neighbor] 
                                else [])
                all_weights = np.array(forward_weights + backward_weights)
                
                # Filter out edges with high variance (std >= threshold)
                if all_weights.std() >= std_threshold:
                    continue
                
                # Calculate mean weight and skip zero-weight edges
                mean_weight = np.mean(all_weights)
                if mean_weight == 0:
                    continue
                
                # Add consolidated edge to simplified graph
                simplified_graph.add_edge(node, neighbor, weight=mean_weight)
        
        # Replace multidigraph with simplified undirected graph
        graphs[subreddit] = simplified_graph
    
    return graphs

def calculate_triangles_graph(graphs):
    triangles = {}

    for subreddit in graphs.keys():
        triangles[subreddit] = set()
        graph = graphs[subreddit]
        for node1 in graph.nodes:
            for node2 in graph.neighbors(node1):
                for node3 in graph.neighbors(node2):
                    if (graph.has_edge(node1, node3)):
                        triangles[subreddit].add(tuple(sorted([node1, node2, node3])))

    for subreddit, triangles_set in triangles.items():
        numerical_triangles = []
        for triangle in triangles_set:
            node1 = triangle[0]
            node2 = triangle[1]
            node3 = triangle[2]
            weight1 = graphs[subreddit][node1][node2]["weight"]
            weight2 = graphs[subreddit][node1][node3]["weight"]
            weight3 = graphs[subreddit][node2][node3]["weight"]
            numerical_triangles.append((weight1, weight2, weight3))
        triangles[subreddit] = numerical_triangles
        
    return triangles

def plot_triangle_distribution(graphs, triangles_graph):
    # Configuration for weight distribution histograms
    WEIGHT_BIN_CENTERS = np.arange(-1, 1.1, 0.2)
    WEIGHT_BIN_EDGES = np.append(WEIGHT_BIN_CENTERS - 0.1, WEIGHT_BIN_CENTERS[-1] + 0.1)

    
    fig, axes = plt.subplots(len(graphs), 2, figsize=(16, 8 * len(graphs)))

    for i, (subreddit, triangles_list) in enumerate(triangles_graph.items()):
        means = []
        stds = []
        for triangle in triangles_list:
            means.append(np.mean(triangle))
            stds.append(np.std(triangle))
        
        # Plot histogram of means
        axes[i][0].hist(means, bins=WEIGHT_BIN_EDGES, edgecolor="black")
        axes[i][0].set_xticks(WEIGHT_BIN_CENTERS)
        axes[i][0].set_title(f"{subreddit} - Triangle Means", fontsize=18)
        axes[i][0].set_xlabel("Mean Weight", fontsize=16)
        axes[i][0].set_ylabel("Count", fontsize=16)
        axes[i][0].tick_params(axis='both', labelsize=16)

        # Plot histogram of stds
        std_bins = np.arange(-0.05, 1.11, 0.1)
        std_centers = np.arange(0, 1.1, 0.1)

        axes[i][1].hist(stds, bins=std_bins, edgecolor="black")
        axes[i][1].set_xticks(std_centers)
        axes[i][1].set_title(f"{subreddit} - Triangle Stds", fontsize=18)
        axes[i][1].set_xlabel("Std of Weights", fontsize=16)
        axes[i][1].tick_params(axis='both', labelsize=16)

        
    plt.tight_layout()
    plt.show()
    
def number_of_triangles_per_type(graphs, triangles_graph):
    series_dict = {}

    for subreddit in graphs.keys():
        qnt_pos = [0, 0, 0, 0]

        for triangle in triangles_graph[subreddit]:
            qnt_pos[list(np.sign(triangle)).count(1)] += 1

        qnt_pos_series = pd.Series(qnt_pos, name=subreddit)
        series_dict[subreddit] = qnt_pos_series

    # Create DataFrame from the series
    df = pd.DataFrame(series_dict).T
    df.columns = ['0 pos edges', '1 pos edge', '2 pos edges', '3 pos edges']
    return df
    
def calculate_balance_metrics(graphs, null_models, NumberOfRandoms):
    results = {}
    for subreddit, graph in graphs.items():
        simplified_original_graph = absolute_graph(graph)
        simplified_null_model = [absolute_graph(null_models[subreddit][i]) for i in range(NumberOfRandoms)]
        nu_w = calculate_bw(simplified_original_graph)
        standard = [calculate_bw(simplified_null_model[i]) for i in range(NumberOfRandoms)]
        standard = sum(standard) / NumberOfRandoms
        results[subreddit] = {'B_w': nu_w, "Standard_B_w": standard, "nu_w" : nu_w / standard}

    df_nu = pd.DataFrame.from_dict(results, orient='index')
    return df_nu

def calculate_triangles_null_graph(graphs, null_models):
    # Calculate triangles for null models
    null_triangles = {}

    for subreddit in graphs.keys():
        null_triangles[subreddit] = []
        
        for null_graph in null_models[subreddit]:
            triangles_set = set()
            for node1 in null_graph.nodes:
                for node2 in null_graph.neighbors(node1):
                    for node3 in null_graph.neighbors(node2):
                        if null_graph.has_edge(node1, node3):
                            triangles_set.add(tuple(sorted([node1, node2, node3])))
            
            numerical_triangles = []
            for triangle in triangles_set:
                node1, node2, node3 = triangle[0], triangle[1], triangle[2]
                weight1 = null_graph[node1][node2]["weight"]
                weight2 = null_graph[node1][node3]["weight"]
                weight3 = null_graph[node2][node3]["weight"]
                numerical_triangles.append((weight1, weight2, weight3))
            
            null_triangles[subreddit].append(numerical_triangles)
    
    return null_triangles

def non_binary_metric(triangles_graph, null_triangles):
    results = []

    for subreddit, triangle_list in triangles_graph.items():
        prod = 0
        for triangle in triangle_list:
            temp = triangle[0] * triangle[1] * triangle[2]
            temp *= abs(temp) ** (1/3)
            prod += temp
        prod /= len(triangle_list)
        to_average = []
        for null_triangle_list in null_triangles[subreddit]:
            null_prod = 0
            for triangle in null_triangle_list:
                temp = triangle[0] * triangle[1] * triangle[2]
                temp *= abs(temp) ** (1/3)
                null_prod += temp
            null_prod /= len(null_triangle_list)
            to_average.append(null_prod)
        avg = np.abs(np.mean(np.array(to_average)))
        ratio = prod/avg if avg != 0 else np.inf
        
        results.append({
            'subreddit': subreddit,
            'prod': prod,
            'avg_null': avg,
            'ratio': ratio
        })

    results_df = pd.DataFrame(results)
    return results_df

def kolmogorov_smirnov(triangles_graph, null_triangles):
    # Calculate number of subreddits
    n_subreddits = len(triangles_graph)

    # Create figure with subplots arranged vertically
    fig, axes = plt.subplots(n_subreddits, 1, figsize=(10, 5 * n_subreddits))

    # Ensure axes is iterable even for single subplot
    if n_subreddits == 1:
        axes = [axes]

    # Dictionary to store Kolmogorov statistics
    kolmogorov_results = {}

    for idx, (subreddit, triangle_list) in enumerate(triangles_graph.items()):
        # Process real data
        all_triangles_dict = defaultdict(int)

        for triangle in triangle_list:
            val = geo_abs(triangle)
            all_triangles_dict[val] += 1
        
        # Process null models
        null_all_dicts = []
        
        for null_model in null_triangles[subreddit]:
            null_all = defaultdict(int)
            
            for triangle in null_model:
                val = geo_abs(triangle)
                null_all[val] += 1
            
            null_all_dicts.append(null_all)
        
        # Helper function to prepare cumulative data
        def prepare_cumulative(d):
            if len(d) == 0:
                return np.array([]), np.array([])
            vals = np.array(sorted(d.keys()))
            counts = np.array([d[v] for v in vals], dtype=int)
            return vals, np.cumsum(counts)
        
        # Calculate average null model cumulative curves using forward-fill
        def average_null_models(dict_list):
            if not dict_list:
                return np.array([]), np.array([])
            
            # Collect all unique values
            all_vals = set()
            for d in dict_list:
                all_vals.update(d.keys())
            
            if not all_vals:
                return np.array([]), np.array([])
            
            all_vals = np.array(sorted(all_vals))
            
            # Build cumulative curves with forward-fill interpolation
            cumulative_curves = []
            for d in dict_list:
                vals, cum = prepare_cumulative(d)
                if len(vals) == 0:
                    cumulative_curves.append(np.zeros_like(all_vals))
                else:
                    # Forward-fill: take the value immediately before
                    cum_interp = np.searchsorted(vals, all_vals, side='right') - 1
                    cum_interp = np.where(cum_interp >= 0, cum[cum_interp], 0)
                    cumulative_curves.append(cum_interp)
            
            avg_cumulative = np.mean(cumulative_curves, axis=0)
            return all_vals, avg_cumulative
        
        # Get cumulative curves
        vals_all, cum_all = prepare_cumulative(all_triangles_dict)
        vals_all_null, cum_all_null = average_null_models(null_all_dicts)

        # Calculate Kolmogorov statistics
        if vals_all.size > 0 and vals_all_null.size > 0:
            D = int(round(kolmogorov(vals_all, cum_all, vals_all_null, cum_all_null)))
            alfa = find_alfa(vals_all, cum_all, vals_all_null, cum_all_null)
            kolmogorov_results[subreddit] = {'D': D, 'p-value': alfa}
        else:
            kolmogorov_results[subreddit] = {'D': None, 'p-value': None}

        # Determine common x-limits
        x_min, x_max = -1, 1

        # Get axis for this subreddit
        ax = axes[idx]

        # Plot all triangles using step function (post: horizontal line extends to the right)
        if vals_all.size > 0:
            ax.step(vals_all, cum_all, where='post', color='C0', linewidth=2, label='Real data')
            ax.plot(vals_all, cum_all, 'o', color='C0', markersize=6)
        if vals_all_null.size > 0:
            ax.step(vals_all_null, cum_all_null, where='post', color='C2', linewidth=2, label='Null model avg')
            ax.plot(vals_all_null, cum_all_null, 's', color='C2', markersize=5, alpha=0.7)
        
        if vals_all.size == 0 and vals_all_null.size == 0:
            ax.text(0.5, 0.5, 'No triangles', ha='center', va='center', fontsize=12, transform=ax.transAxes)
        
        # Add Kolmogorov statistics to plot title
        if kolmogorov_results[subreddit]['D'] is not None:
            title_text = f"{subreddit} (D={kolmogorov_results[subreddit]['D']}, p={kolmogorov_results[subreddit]['p-value']:.4f})"
        else:
            title_text = f"{subreddit}"
        
        ax.set_xlabel('Geometric mean weight', fontsize=12)
        ax.set_ylabel('Accumulated number of triangles', fontsize=12)
        ax.set_title(title_text, fontsize=14)
        ax.grid(alpha=0.3)
        ax.set_xlim(x_min, x_max)
        ax.legend(fontsize=10)

    plt.suptitle("Accumulated triangles: Real vs Null Model", fontsize=16, y=0.998)
    plt.tight_layout()
    plt.show()

    # Print Kolmogorov statistics summary
    print("\nKolmogorov-Smirnov Test Results:")
    print("=" * 60)
    for subreddit, stats in kolmogorov_results.items():
        if stats['D'] is not None:
            print(f"{subreddit:30s} | D = {stats['D']:8.4f} | p-value = {stats['p-value']:8.4f}")
        else:
            print(f"{subreddit:30s} | No data available")
