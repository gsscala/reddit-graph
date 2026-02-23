"""
Auxiliary functions for graph analysis and visualization.

This module provides utilities for analyzing social network graphs, including:
- Null model generation
- Balance metrics calculation
- Triangle analysis
- Weight distribution visualization
- Kolmogorov-Smirnov statistical tests
"""

import numpy as np
import pandas as pd
import networkx as nx
import random
import scipy.sparse.linalg as spla
import scipy.linalg as la
import matplotlib.pyplot as plt
from collections import defaultdict


def generate_null_model(graph: nx.Graph) -> nx.Graph:
    """
    Generate a null model by randomly shuffling edge weights.
    
    Creates a new graph with the same structure as the input but with
    edge weights randomly reassigned to different edges.
    
    Args:
        graph: Input NetworkX graph with weighted edges.
        
    Returns:
        A new graph with shuffled edge weights.
    """
    weights = [graph[a][b]["weight"] for a, b in graph.edges()]
    random.shuffle(weights)
    
    null_model = nx.Graph()
    for i, (a, b) in enumerate(graph.edges()):
        null_model.add_edge(a, b, weight=weights[i])
    
    return null_model


def absolute_graph(graph: nx.Graph) -> nx.Graph:
    """
    Convert edge weights to their signs (-1, 0, or +1).
    
    Args:
        graph: Input NetworkX graph with weighted edges.
        
    Returns:
        A new graph where each edge weight is replaced by its sign.
    """
    new_graph = nx.Graph()
    for a, b, data in graph.edges(data=True):
        new_graph.add_edge(a, b, weight=np.sign(data["weight"]))
    
    return new_graph


def calculate_bw(graph: nx.Graph, z: int = 3) -> float:
    """
    Calculate the balance metric BW(α) for a signed graph.
    
    The balance metric is computed as:
    BW(α) = 1/2 Tr[N((αλI - P)^(-1))]
    where N is the negative adjacency matrix, P is the positive adjacency matrix,
    and λ is the maximum eigenvalue of P.
    
    Args:
        graph: Input NetworkX graph with edge weights of -1 or +1.
        z: Scaling parameter (currently unused; α is hardcoded to 2).
        
    Returns:
        The balance metric value.
    """
    # nodes = list(graph.nodes())
    # n = len(nodes)
    # N = np.zeros((n, n))  # Negative adjacency matrix
    # P = np.zeros((n, n))  # Positive adjacency matrix
    # node_index = {node: idx for idx, node in enumerate(nodes)}

    # # Populate adjacency matrices based on edge signs
    # for a, b, data in graph.edges(data=True):
    #     i, j = node_index[a], node_index[b]
    #     if data["weight"] == -1:
    #         N[i, j] = 1
    #         N[j, i] = 1
    #     else:
    #         P[i, j] = 1
    #         P[j, i] = 1
    
    # max_eigenvalue = max(np.linalg.eigvalsh(P))
    # alfa = 2  # Scaling parameter
    
    # # Calculate BW(α) = 1/2 Tr[N((αλI - P)^(-1))]
    # I = np.eye(n)
    # matrix_to_invert = alfa * max_eigenvalue * I - P
    # inv_matrix = np.linalg.inv(matrix_to_invert)
    # bw_matrix = np.dot(N, inv_matrix)
    # bw_value = np.trace(bw_matrix) / 2
    
    # return bw_value

    n = graph.number_of_nodes()
    if n == 0:
        return 0.0
        
    # 1. Fast sparse matrix construction
    nodes = list(graph.nodes())
    A = nx.to_scipy_sparse_array(graph, nodelist=nodes, weight="weight", format="csr")
    
    # Extract Positive (P) and Negative (N) adjacency matrices
    P = A.copy()
    P.data = np.where(P.data > 0, P.data, 0)
    P.eliminate_zeros()
    
    N = A.copy()
    N.data = np.where(N.data < 0, -N.data, 0) # Convert -1 to 1 to match original logic
    N.eliminate_zeros()
    
    # 2. Fast Maximum Eigenvalue computation
    if P.nnz == 0:
        max_eigenvalue = 0.0
    else:
        if n < 10:
            # Fallback for very small graphs
            max_eigenvalue = max(la.eigvalsh(P.toarray())) 
        else:
            # eigsh finds only the top k eigenvalues, dramatically faster than all of them
            max_eigenvalue = spla.eigsh(P.astype(float), k=1, which='LA', return_eigenvectors=False)[0]
            
    alfa = 2.0
    
    # 3. Dense inversion using Cholesky
    matrix_to_invert = np.eye(n) * (alfa * max_eigenvalue) - P.toarray()
    
    try:
        # Since (αλI - P) is Symmetric Positive Definite, Cholesky factorization 
        # is roughly 2x faster than a standard inverse.
        c, lower = la.cho_factor(matrix_to_invert, check_finite=False)
        inv_matrix = la.cho_solve((c, lower), np.eye(n), check_finite=False)
    except la.LinAlgError:
        # Fallback to standard inverse if matrix acts singular
        inv_matrix = la.inv(matrix_to_invert, check_finite=False)
        
    # 4. Eliminate O(n^3) matrix multiplication for the trace
    N_coo = N.tocoo()
    
    # We only sum the specific elements of inv_matrix where N has non-zero entries
    trace_val = np.sum(N_coo.data * inv_matrix[N_coo.row, N_coo.col])
    
    return trace_val / 2.0



def geo_abs(triangle: list) -> float:
    """
    Calculate the signed geometric mean of triangle edge weights.
    
    Computes the geometric mean of absolute values and applies the sign
    based on the product of signs (negative if odd number of negative edges).
    
    Args:
        triangle: List of three edge weights.
        
    Returns:
        Signed geometric mean of the triangle weights.
    """
    product = (abs(triangle[0]) * abs(triangle[1]) * abs(triangle[2])) ** (1 / 3)
    signs = [np.sign(triangle[0]), np.sign(triangle[1]), np.sign(triangle[2])]
    
    # Apply negative sign if odd number of negative edges
    if signs.count(-1) % 2:
        product *= -1
    
    return product


def in_balance(triangle: list) -> int:
    """
    Determine if a triangle is balanced according to structural balance theory.
    
    A triangle is balanced if it has an even number of negative edges.
    
    Args:
        triangle: List of three edge weights.
        
    Returns:
        1 if balanced (even number of negative edges), 0 otherwise.
    """
    triangle = list(np.sign(np.array(triangle)))
    for el in triangle:
        assert(el)
    
    return 1 - (triangle.count(-1) % 2)


def kolmogorov(vals_a: np.ndarray, cum_a: np.ndarray, 
               vals_b: np.ndarray, cum_b: np.ndarray, 
               normalize: bool = False) -> float:
    """
    Compute the Kolmogorov-Smirnov statistic between two cumulative distributions.
    
    Calculates the maximum absolute difference between two cumulative distribution
    functions across the union of their support points.
    
    Args:
        vals_a: Sorted x-values for distribution A.
        cum_a: Cumulative counts for distribution A.
        vals_b: Sorted x-values for distribution B.
        cum_b: Cumulative counts for distribution B.
        normalize: If True, normalize both distributions to [0,1].
        
    Returns:
        Maximum absolute difference between the two distributions.
    """
    vals_a = np.asarray(vals_a)
    cum_a = np.asarray(cum_a, dtype=float)
    vals_b = np.asarray(vals_b)
    cum_b = np.asarray(cum_b, dtype=float)

    # Create combined x-grid from union of both distributions
    all_vals = np.array(sorted(set(vals_a.tolist()) | set(vals_b.tolist())))
    if all_vals.size == 0:
        return 0

    def forward_fill(vals, cum, x_grid):
        """
        Forward-fill cumulative values onto a new grid.
        
        For each x in x_grid, return the cumulative value at the largest
        vals <= x (or 0 if no such value exists).
        """
        if vals.size == 0:
            return np.zeros_like(x_grid, dtype=float)
        idx = np.searchsorted(vals, x_grid, side='right') - 1
        return np.where(idx >= 0, cum[idx], 0.0)

    # Interpolate both distributions onto common grid
    y_a = forward_fill(vals_a, cum_a, all_vals)
    y_b = forward_fill(vals_b, cum_b, all_vals)

    # Normalize if requested
    if normalize:
        denom_a = y_a[-1] if y_a.size > 0 else 0.0
        denom_b = y_b[-1] if y_b.size > 0 else 0.0
        if denom_a > 0:
            y_a = y_a / denom_a
        if denom_b > 0:
            y_b = y_b / denom_b

    # Calculate maximum difference
    diffs = np.abs(y_a - y_b)
    max_diff = diffs.max() if diffs.size > 0 else 0

    return max_diff


def find_alfa(vals_a: np.ndarray, cum_a: np.ndarray,
              vals_b: np.ndarray, cum_b: np.ndarray) -> float:
    """
    Calculate the p-value for the Kolmogorov-Smirnov test.
    
    Uses the asymptotic distribution of the KS statistic to compute
    a p-value indicating the probability that two distributions are identical.
    
    Args:
        vals_a: Sorted x-values for distribution A.
        cum_a: Cumulative counts for distribution A.
        vals_b: Sorted x-values for distribution B.
        cum_b: Cumulative counts for distribution B.
        
    Returns:
        P-value for the two-sample KS test.
    """
    D = kolmogorov(vals_a, cum_a, vals_b, cum_b, normalize=True)
    n_a = len(vals_a)
    n_b = len(vals_b)
    
    return 2 * np.exp(-2 * D * D * n_a * n_b / (n_b + n_a))


def plot_weight_distribution(graphs: dict) -> None:
    """
    Visualize edge weight and sign distributions for multiple graphs.
    
    Creates a two-column plot for each subreddit:
    - Left: Histogram of edge weights
    - Right: Histogram of edge signs (negative/neutral/positive)
    
    Args:
        graphs: Dictionary mapping subreddit names to NetworkX graphs.
    """
    # Configuration for weight distribution histograms
    WEIGHT_BIN_CENTERS = np.arange(-1, 1.1, 0.2)
    WEIGHT_BIN_EDGES = np.append(WEIGHT_BIN_CENTERS - 0.1, WEIGHT_BIN_CENTERS[-1] + 0.1)

    # Configuration for sign distribution histograms
    SIGN_BIN_EDGES = [-1.5, -0.5, 0.5, 1.5]
    SIGN_LABELS = ["negative", "neutral", "positive"]
    SIGN_TICK_POSITIONS = [-1, 0, 1]

    # Create subplots: one row per subreddit, two columns
    n_subreddits = len(graphs)
    fig, axes = plt.subplots(n_subreddits, 2, figsize=(16, 8 * n_subreddits))

    def add_percentage_labels(ax, counts, bins, fontsize=14):
        """
        Add percentage labels on top of histogram bars.
        
        Args:
            ax: Matplotlib axes object.
            counts: Histogram bin counts.
            bins: Histogram bin edges.
            fontsize: Font size for labels.
        """
        total = counts.sum()
        
        for count, bin_left, bin_right in zip(counts, bins[:-1], bins[1:]):
            percent = 100 * count / total if total > 0 else 0
            x_position = (bin_left + bin_right) / 2
            ax.text(x_position, count, f"{percent:.1f}%", 
                    ha='center', va='bottom', fontsize=fontsize)

    # Generate histograms for each subreddit
    for idx, subreddit in enumerate(graphs):
        weights = np.array([data["weight"] for _, _, data in graphs[subreddit].edges(data=True)])
        
        # Left panel: Weight distribution
        ax_weight = axes[idx][0]
        counts, _, _ = ax_weight.hist(weights, bins=WEIGHT_BIN_EDGES, edgecolor="black")
        ax_weight.set_xticks(WEIGHT_BIN_CENTERS)
        ax_weight.set_xticklabels([f"{x:.1f}" for x in WEIGHT_BIN_CENTERS], rotation=60)
        add_percentage_labels(ax_weight, counts, WEIGHT_BIN_EDGES)
        ax_weight.set_title(subreddit, fontsize=20)
        ax_weight.set_xlabel("Weight", fontsize=18)
        ax_weight.set_ylabel("Count", fontsize=18)
        ax_weight.tick_params(axis='both', labelsize=16)
        
        # Right panel: Sign distribution
        ax_sign = axes[idx][1]
        sign_counts, _, _ = ax_sign.hist(np.sign(weights), bins=SIGN_BIN_EDGES, 
                                        edgecolor="black", rwidth=0.8)
        ax_sign.set_xticks(SIGN_TICK_POSITIONS)
        ax_sign.set_xticklabels(SIGN_LABELS, fontsize=16)
        add_percentage_labels(ax_sign, sign_counts, SIGN_BIN_EDGES)
        ax_sign.set_title(subreddit, fontsize=20)
        ax_sign.set_xlabel("Sign", fontsize=18)
        ax_sign.tick_params(axis='both', labelsize=16)

    plt.tight_layout()
    plt.show()


def simplify_graph(graph: nx.Graph, std_threshold: float) -> dict:
    """
    Simplify a multi-edge graph by consolidating parallel edges.
    
    For each pair of nodes:
    1. Collects all edge weights (treating graph as undirected)
    2. Filters out edges with high variance (std >= threshold)
    3. Replaces multiple edges with a single edge having mean weight
    4. Removes zero-weight edges and self-loops
    
    Args:
        graph: MultiDiGraph with 'subreddit' and 'weight' edge attributes.
        std_threshold: Maximum allowed standard deviation for edge weights.
        
    Returns:
        Dictionary mapping subreddit names to simplified undirected graphs.
    """
    # Step 1: Create individual subgraphs for each subreddit
    graphs = defaultdict(nx.MultiDiGraph)

    for node_a, node_b, edge_data in graph.edges(data=True):
        subreddit = edge_data["subreddit"]
        weight = edge_data["weight"]
        graphs[subreddit].add_edge(node_a, node_b, weight=weight)

    # Step 2: Consolidate edges and filter by standard deviation
    for subreddit, subreddit_graph in graphs.items():
        # Group all edge weights by node pairs
        edge_weights = defaultdict(lambda: defaultdict(list))
        
        for node_a, node_b, edge_data in subreddit_graph.edges(data=True):
            edge_weights[node_a][node_b].append(edge_data["weight"])
        
        # Create simplified undirected graph
        simplified_graph = nx.Graph()
        
        for node in edge_weights.keys():
            for neighbor in edge_weights[node].keys():
                if node == neighbor:  # Skip self-loops
                    continue
                
                # Collect weights in both directions
                forward_weights = edge_weights[node][neighbor]
                backward_weights = (edge_weights[neighbor][node] 
                                if neighbor in edge_weights and node in edge_weights[neighbor] 
                                else [])
                all_weights = np.array(forward_weights + backward_weights)
                
                # Filter by variance threshold
                if all_weights.std() >= std_threshold:
                    continue
                
                # Add edge with mean weight (skip zero weights)
                mean_weight = np.mean(all_weights)
                if mean_weight == 0:
                    continue
                
                simplified_graph.add_edge(node, neighbor, weight=mean_weight)
        
        graphs[subreddit] = simplified_graph
    
    return graphs


def calculate_triangles_graph(graphs: dict) -> dict:
    """
    Find all triangles in each graph and extract their edge weights.
    
    A triangle is a set of three nodes where each pair is connected by an edge.
    
    Args:
        graphs: Dictionary mapping subreddit names to NetworkX graphs.
        
    Returns:
        Dictionary mapping subreddit names to lists of triangles,
        where each triangle is a tuple of three edge weights.
    """
    triangles = {}

    for subreddit in graphs.keys():
        triangles[subreddit] = set()
        graph = graphs[subreddit]
        
        # Find all triangles using three nested loops
        for node1 in graph.nodes:
            for node2 in graph.neighbors(node1):
                for node3 in graph.neighbors(node2):
                    if graph.has_edge(node1, node3):
                        triangles[subreddit].add(tuple(sorted([node1, node2, node3])))

    # Convert node triangles to weight triangles
    for subreddit, triangles_set in triangles.items():
        numerical_triangles = []
        for triangle in triangles_set:
            node1, node2, node3 = triangle[0], triangle[1], triangle[2]
            weight1 = graphs[subreddit][node1][node2]["weight"]
            weight2 = graphs[subreddit][node1][node3]["weight"]
            weight3 = graphs[subreddit][node2][node3]["weight"]
            numerical_triangles.append((weight1, weight2, weight3))
        triangles[subreddit] = numerical_triangles
        
    return triangles


def plot_triangle_distribution(graphs: dict, triangles_graph: dict) -> None:
    """
    Visualize distributions of triangle statistics.
    
    For each subreddit, creates two histograms:
    - Left: Mean of edge weights within each triangle
    - Right: Standard deviation of edge weights within each triangle
    
    Args:
        graphs: Dictionary mapping subreddit names to NetworkX graphs.
        triangles_graph: Dictionary mapping subreddit names to triangle weight tuples.
    """
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

        # Plot histogram of standard deviations
        std_bins = np.arange(-0.05, 1.11, 0.1)
        std_centers = np.arange(0, 1.1, 0.1)

        axes[i][1].hist(stds, bins=std_bins, edgecolor="black")
        axes[i][1].set_xticks(std_centers)
        axes[i][1].set_title(f"{subreddit} - Triangle Stds", fontsize=18)
        axes[i][1].set_xlabel("Std of Weights", fontsize=16)
        axes[i][1].tick_params(axis='both', labelsize=16)
        
    plt.tight_layout()
    plt.show()


def number_of_triangles_per_type(graphs: dict, triangles_graph: dict) -> pd.DataFrame:
    """
    Count triangles by the number of positive edges they contain.
    
    Categorizes each triangle into four types based on how many of its
    three edges have positive weight.
    
    Args:
        graphs: Dictionary mapping subreddit names to NetworkX graphs.
        triangles_graph: Dictionary mapping subreddit names to triangle weight tuples.
        
    Returns:
        DataFrame with columns for 0, 1, 2, and 3 positive edges,
        and rows for each subreddit.
    """
    series_dict = {}

    for subreddit in graphs.keys():
        qnt_pos = [0, 0, 0, 0]  # Count for 0, 1, 2, 3 positive edges

        for triangle in triangles_graph[subreddit]:
            qnt_pos[list(np.sign(triangle)).count(1)] += 1

        qnt_pos_series = pd.Series(qnt_pos, name=subreddit)
        series_dict[subreddit] = qnt_pos_series

    df = pd.DataFrame(series_dict).T
    df.columns = ['0 pos edges', '1 pos edge', '2 pos edges', '3 pos edges']
    return df


def calculate_balance_metrics(graphs: dict, null_models: dict, 
                              NumberOfRandoms: int) -> pd.DataFrame:
    """
    Calculate balance metrics comparing real graphs to null models.
    
    Computes the BW balance metric for each graph and compares it to
    the average BW of randomly shuffled null models.
    
    Args:
        graphs: Dictionary mapping subreddit names to NetworkX graphs.
        null_models: Dictionary mapping subreddit names to lists of null model graphs.
        NumberOfRandoms: Number of null model realizations to average.
        
    Returns:
        DataFrame with columns 'B_w' (real), 'Standard_B_w' (null average),
        and 'nu_w' (ratio of real to null).
    """
    results = {}
    distributions = []
    
    for subreddit, graph in graphs.items():
        # Convert to absolute (signed) graphs
        simplified_original_graph = absolute_graph(graph)
        simplified_null_model = [absolute_graph(null_models[subreddit][i]) 
                                for i in range(NumberOfRandoms)]
        
        print(f"Starting {subreddit}")
        
        # Calculate balance metrics
        b_w = calculate_bw(simplified_original_graph)
        null_model_distribution = np.array([calculate_bw(simplified_null_model[i]) 
                   for i in range(NumberOfRandoms)])
        
        distributions.append(null_model_distribution)
        
        mean = np.mean(null_model_distribution)
        
        std = np.std(null_model_distribution)
        
        results[subreddit] = {
            'B_w': b_w, 
            "mean": mean, 
            "std": std,
            "z-score": (b_w - mean) / std
        }

    df_nu = pd.DataFrame.from_dict(results, orient='index')
    return df_nu, distributions


def calculate_triangles_null_graph(graphs: dict, null_models: dict) -> dict:
    """
    Calculate triangles for all null model realizations.
    
    Finds triangles in each null model graph and extracts their edge weights.
    
    Args:
        graphs: Dictionary mapping subreddit names to NetworkX graphs.
        null_models: Dictionary mapping subreddit names to lists of null model graphs.
        
    Returns:
        Dictionary mapping subreddit names to lists of triangle weight lists,
        where each inner list corresponds to one null model realization.
    """
    null_triangles = {}

    for subreddit in graphs.keys():
        null_triangles[subreddit] = []
        
        for null_graph in null_models[subreddit]:
            triangles_set = set()
            
            # Find all triangles in this null model
            for node1 in null_graph.nodes:
                for node2 in null_graph.neighbors(node1):
                    for node3 in null_graph.neighbors(node2):
                        if null_graph.has_edge(node1, node3):
                            triangles_set.add(tuple(sorted([node1, node2, node3])))
            
            # Convert to weight triangles
            numerical_triangles = []
            for triangle in triangles_set:
                node1, node2, node3 = triangle[0], triangle[1], triangle[2]
                weight1 = null_graph[node1][node2]["weight"]
                weight2 = null_graph[node1][node3]["weight"]
                weight3 = null_graph[node2][node3]["weight"]
                numerical_triangles.append((weight1, weight2, weight3))
            
            null_triangles[subreddit].append(numerical_triangles)
    
    return null_triangles


def non_binary_metric(triangles_graph: dict, null_triangles: dict) -> pd.DataFrame:
    """
    Calculate a non-binary balance metric for triangles.
    
    Computes the average signed geometric mean of triangle weights for real data
    and compares it to the average across null models.
    
    Args:
        triangles_graph: Dictionary mapping subreddit names to triangle weight tuples.
        null_triangles: Dictionary mapping subreddit names to lists of null triangle weights.
        
    Returns:
        DataFrame with columns 'subreddit', 'prod' (real metric),
        'avg_null' (null average), and 'ratio' (real/null).
    """
    results = []
    distributions = {}

    for subreddit, triangle_list in triangles_graph.items():
        # Calculate metric for real data
        prod = 0
        for triangle in triangle_list:
            temp = triangle[0] * triangle[1] * triangle[2]
            temp *= abs(temp) ** (1/3)
            prod += temp
        prod /= len(triangle_list)
        
        # Calculate metric for null models
        null_model_distribution = []
        for null_triangle_list in null_triangles[subreddit]:
            null_prod = 0
            for triangle in null_triangle_list:
                temp = triangle[0] * triangle[1] * triangle[2]
                temp *= abs(temp) ** (1/3)
                null_prod += temp
            null_prod /= len(null_triangle_list)
            null_model_distribution.append(null_prod)
        
        null_model_distribution = np.array(null_model_distribution)

        mean = np.mean(null_model_distribution)
        
        std = np.std(null_model_distribution)
        
        results.append({
            'subreddit': subreddit,
            'prod': prod,
            "mean": mean, 
            "std": std,
            "z-score": (prod - mean) / std
        })

        distributions[subreddit] = null_model_distribution

    results_df = pd.DataFrame(results).set_index("subreddit")

    return results_df, distributions


def kolmogorov_smirnov(triangles_graph: dict, null_triangles: dict) -> None:
    """
    Perform Kolmogorov-Smirnov test comparing real and null triangle distributions.
    
    For each subreddit:
    1. Computes cumulative distribution of signed geometric means
    2. Compares real data to average of null models
    3. Calculates KS statistic and p-value
    4. Visualizes distributions with step plots
    
    Args:
        triangles_graph: Dictionary mapping subreddit names to triangle weight tuples.
        null_triangles: Dictionary mapping subreddit names to lists of null triangle weights.
    """
    n_subreddits = len(triangles_graph)
    fig, axes = plt.subplots(n_subreddits, 1, figsize=(10, 5 * n_subreddits))

    # Ensure axes is iterable for single subplot
    if n_subreddits == 1:
        axes = [axes]

    kolmogorov_results = {}

    for idx, (subreddit, triangle_list) in enumerate(triangles_graph.items()):
        # Process real data: compute signed geometric means
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
        
        def prepare_cumulative(d):
            """Convert dictionary to sorted values and cumulative counts."""
            if len(d) == 0:
                return np.array([]), np.array([])
            vals = np.array(sorted(d.keys()))
            counts = np.array([d[v] for v in vals], dtype=int)
            return vals, np.cumsum(counts)
        
        def average_null_models(dict_list):
            """Average cumulative distributions across null models using forward-fill."""
            if not dict_list:
                return np.array([]), np.array([])
            
            # Collect all unique values
            all_vals = set()
            for d in dict_list:
                all_vals.update(d.keys())
            
            if not all_vals:
                return np.array([]), np.array([])
            
            all_vals = np.array(sorted(all_vals))
            
            # Build cumulative curves with forward-fill
            cumulative_curves = []
            for d in dict_list:
                vals, cum = prepare_cumulative(d)
                if len(vals) == 0:
                    cumulative_curves.append(np.zeros_like(all_vals))
                else:
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

        # Plot cumulative distributions
        x_min, x_max = -1, 1
        ax = axes[idx]

        # Plot real data
        if vals_all.size > 0:
            ax.step(vals_all, cum_all, where='post', color='C0', 
                   linewidth=2, label='Real data')
            ax.plot(vals_all, cum_all, 'o', color='C0', markersize=6)
        
        # Plot null model average
        if vals_all_null.size > 0:
            ax.step(vals_all_null, cum_all_null, where='post', color='C2', 
                   linewidth=2, label='Null model avg')
            ax.plot(vals_all_null, cum_all_null, 's', color='C2', 
                   markersize=5, alpha=0.7)
        
        # Handle empty data
        if vals_all.size == 0 and vals_all_null.size == 0:
            ax.text(0.5, 0.5, 'No triangles', ha='center', va='center', 
                   fontsize=12, transform=ax.transAxes)
        
        # Add title with statistics
        if kolmogorov_results[subreddit]['D'] is not None:
            title_text = (f"{subreddit} (D={kolmogorov_results[subreddit]['D']}, "
                         f"p={kolmogorov_results[subreddit]['p-value']:.4f})")
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

    # Print summary statistics
    print("\nKolmogorov-Smirnov Test Results:")
    print("=" * 60)
    for subreddit, stats in kolmogorov_results.items():
        if stats['D'] is not None:
            print(f"{subreddit:30s} | D = {stats['D']:8.4f} | "
                  f"p-value = {stats['p-value']:8.4f}")
        else:
            print(f"{subreddit:30s} | No data available")
