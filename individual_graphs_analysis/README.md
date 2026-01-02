# Individual Graphs Analysis

This directory contains tools for analyzing individual subreddit graphs extracted from Reddit data, with a focus on structural balance theory and triangle statistics. It's expected that the graph's edges are weighted, possible assigned through sentiment polarity of the text involved in the interaction.

## Overview

The analysis pipeline processes a labeled graph file (`labeled_graph.gexf`) and splits it into individual subreddit-specific graphs. It then performs various statistical analyses including weight distributions, triangle patterns, balance metrics, and comparisons with randomized null models.

## Files

- **`ind_graphs.ipynb`**: Main Jupyter notebook containing the complete analysis workflow
- **`auxiliary_functions.py`**: Python module with all helper functions for graph processing and analysis
- **`labeled_graph.gexf`**: Input graph file (GEXF format) containing Reddit interaction data with subreddit labels
- **`file.csv`**: Output CSV file containing triangle type counts per subreddit

## Workflow (`ind_graphs.ipynb`)

### 1. Setup and Configuration

```python
import networkx as nx
import pandas as pd
import numpy as np
from auxiliary_functions import *

# Load the labeled graph
graph = nx.read_gexf("labeled_graph.gexf")

# Configuration parameters
std_threshold = 0.5      # Standard deviation threshold for edge filtering
NumberOfRandoms = 100    # Number of null models to generate per subreddit
```

### 2. Graph Simplification

```python
graphs = simplify_graph(graph, std_threshold)
```

Splits the main graph into individual subreddit graphs, consolidates multiple edges between nodes, and filters edges with high variance.

### 3. Null Model Generation

```python
null_models = {}
for subreddit, subreddit_graph in graphs.items():
    null_models[subreddit] = [
        generate_null_model(subreddit_graph) 
        for _ in range(NumberOfRandoms)
    ]
```

Creates randomized versions of each graph (null model) by shuffling edge weights while preserving graph structure. Used for statistical significance testing.

### 4. Weight Distribution Analysis

```python
plot_weight_distribution(graphs)
```

Visualizes the distribution of edge weights and their signs (positive/negative/neutral) for each subreddit.

### 5. Triangle Analysis

```python
# Calculate triangles in real graphs
triangles_graph = calculate_triangles_graph(graphs)

# Visualize triangle distributions
plot_triangle_distribution(graphs, triangles_graph)

# Count triangles by type
df = number_of_triangles_per_type(graphs, triangles_graph)
df.to_csv('file.csv', index=True)
```

Identifies all triangles in the graphs and categorizes them by the number of positive edges (0, 1, 2, or 3).

### 6. Balance Metrics

```python
calculate_balance_metrics(graphs, null_models, NumberOfRandoms)
```

Computes balance metrics (B_w) comparing real graphs to null models using structural balance theory.

### 7. Null Triangle Analysis

```python
null_triangles = calculate_triangles_null_graph(graphs, null_models)
```

Calculates triangle statistics for all null models to establish baseline comparisons.

### 8. Non-Binary Balance Metric (Experimental)

```python
results_df = non_binary_metric(triangles_graph, null_triangles)
```

Computes a continuous balance metric based on the geometric mean of triangle edge weights. This is still in development.

### 9. Statistical Testing

```python
kolmogorov_smirnov(triangles_graph, null_triangles)
```

Performs Kolmogorov-Smirnov-like tests to compare the distribution of triangle types between real and null models, with visualization.

## Functions Reference (`auxiliary_functions.py`)

### Graph Manipulation

#### `simplify_graph(graph, std_threshold)`
Processes the main graph into individual subreddit graphs with consolidated edges.

**Parameters:**
- `graph` (nx.Graph): Input multi-graph with subreddit labels
- `std_threshold` (float): Standard deviation threshold for filtering edges

**Returns:**
- `dict`: Dictionary mapping subreddit names to simplified NetworkX graphs

**Process:**
1. Splits edges by subreddit
2. Consolidates multiple edges between same nodes
3. Filters edges with std ≥ threshold
4. Averages remaining weights
5. Removes zero-weight edges

#### `generate_null_model(graph)`
Creates a randomized version of a graph by shuffling edge weights.

**Parameters:**
- `graph` (nx.Graph): Input graph

**Returns:**
- `nx.Graph`: Graph with same structure but shuffled weights

#### `absolute_graph(graph)`
Converts edge weights to their signs (-1, 0, +1).

**Parameters:**
- `graph` (nx.Graph): Input graph

**Returns:**
- `nx.Graph`: Graph with binary edge weights

### Triangle Analysis

#### `calculate_triangles_graph(graphs)`
Finds all triangles in each subreddit graph.

**Parameters:**
- `graphs` (dict): Dictionary of subreddit graphs

**Returns:**
- `dict`: Dictionary mapping subreddits to lists of triangle weight tuples

**Output format:** Each triangle is represented as `(weight1, weight2, weight3)`

#### `calculate_triangles_null_graph(graphs, null_models)`
Calculates triangles for all null models.

**Parameters:**
- `graphs` (dict): Dictionary of real subreddit graphs
- `null_models` (dict): Dictionary of null model lists per subreddit

**Returns:**
- `dict`: Nested dictionary with triangle data for each null model

#### `number_of_triangles_per_type(graphs, triangles_graph)`
Counts triangles categorized by number of positive edges.

**Parameters:**
- `graphs` (dict): Dictionary of subreddit graphs
- `triangles_graph` (dict): Triangle data from `calculate_triangles_graph`

**Returns:**
- `pd.DataFrame`: DataFrame with columns ['0 pos edges', '1 pos edge', '2 pos edges', '3 pos edges']

### Balance Metrics

#### `calculate_balance_metrics(graphs, null_models, NumberOfRandoms)`
Computes structural balance metrics using the B_w measure.

**Parameters:**
- `graphs` (dict): Dictionary of real subreddit graphs
- `null_models` (dict): Dictionary of null model lists
- `NumberOfRandoms` (int): Number of null models per subreddit

**Returns:**
- `pd.DataFrame`: DataFrame with columns ['B_w', 'Standard_B_w', 'nu_w']
  - `B_w`: Balance metric for real graph
  - `Standard_B_w`: Average balance metric for null models
  - `nu_w`: Normalized ratio (B_w / Standard_B_w)

#### `calculate_bw(graph, z=3)`
Calculates the B_w balance metric for a single graph.

**Parameters:**
- `graph` (nx.Graph): Input graph with signed weights
- `z` (float): Parameter for eigenvalue scaling (default: 3)

**Returns:**
- `float`: B_w balance value

**Formula:** `BW(α) = 1/2 Tr[N((αλI - P)^(-1))]`
- N: negative adjacency matrix
- P: positive adjacency matrix
- λ: maximum eigenvalue of P

#### `non_binary_metric(triangles_graph, null_triangles)`
Experimental metric using geometric mean of triangle edge weights.

**Parameters:**
- `triangles_graph` (dict): Real triangle data
- `null_triangles` (dict): Null model triangle data

**Returns:**
- `pd.DataFrame`: DataFrame with columns ['subreddit', 'prod', 'avg_null', 'ratio']

**Metric:** For each triangle, computes signed geometric mean: `sign(product) × |w₁ × w₂ × w₃|^(1/3)`

### Statistical Analysis

#### `kolmogorov_smirnov(triangles_graph, null_triangles)`
Performs modified Kolmogorov-Smirnov test and visualizes cumulative distributions.

**Parameters:**
- `triangles_graph` (dict): Real triangle data
- `null_triangles` (dict): Null model triangle data

**Output:**
- Plots cumulative distributions comparing real vs null models
- Prints test statistics (D-statistic and p-value) for each subreddit

#### `kolmogorov(vals_a, cum_a, vals_b, cum_b, normalize=False)`
Computes maximum absolute difference between two cumulative distributions.

**Parameters:**
- `vals_a`, `cum_a`: Arrays for first distribution (x values and cumulative counts)
- `vals_b`, `cum_b`: Arrays for second distribution
- `normalize` (bool): If True, normalize to [0,1] range

**Returns:**
- `float`: Maximum absolute difference (Kolmogorov-Smirnov statistic)

#### `find_alfa(vals_a, cum_a, vals_b, cum_b)`
Calculates p-value approximation for Kolmogorov-Smirnov test.

**Parameters:**
- Same as `kolmogorov` function

**Returns:**
- `float`: P-value estimate using Kolmogorov-Smirnov formula

### Visualization

#### `plot_weight_distribution(graphs)`
Creates histograms showing edge weight distributions per subreddit.

**Parameters:**
- `graphs` (dict): Dictionary of subreddit graphs

**Output:**
- Two-column plot for each subreddit:
  - Left: Distribution of continuous edge weights (-1 to 1)
  - Right: Distribution of edge signs (negative/neutral/positive)
- Includes percentage labels on bars

#### `plot_triangle_distribution(graphs, triangles_graph)`
Visualizes distributions of triangle statistics.

**Parameters:**
- `graphs` (dict): Dictionary of subreddit graphs
- `triangles_graph` (dict): Triangle data

**Output:**
- Two-column plot for each subreddit:
  - Left: Distribution of triangle mean weights
  - Right: Distribution of triangle standard deviations

### Utility Functions

#### `geo_abs(triangle)`
Computes signed geometric mean of triangle edge weights.

**Parameters:**
- `triangle` (list): List of 3 edge weights

**Returns:**
- `float`: Signed geometric mean preserving sign structure

**Formula:** `sign(product) × (|w₁| × |w₂| × |w₃|)^(1/3)` where sign is negative if odd number of negative weights

#### `in_balance(triangle)`
Determines if a triangle is balanced according to structural balance theory.

**Parameters:**
- `triangle` (list): List of 3 edge weights

**Returns:**
- `int`: 1 if balanced, 0 if unbalanced

**Balance rule:** A triangle is balanced if it has an even number of negative edges (0 or 2)

## Output Files

### `file.csv`
CSV file containing triangle counts categorized by number of positive edges:

| Subreddit | 0 pos edges | 1 pos edge | 2 pos edges | 3 pos edges |
|-----------|-------------|------------|-------------|-------------|
| subreddit1 | count | count | count | count |
| subreddit2 | count | count | count | count |

- **0 pos edges**: All negative (unbalanced)
- **1 pos edge**: Two negative, one positive (unbalanced)
- **2 pos edges**: Two positive, one negative (balanced)
- **3 pos edges**: All positive (balanced)

## Requirements

```python
networkx
pandas
numpy
matplotlib
```

## Usage Example

```python
# Complete analysis workflow
graph = nx.read_gexf("labeled_graph.gexf")
graphs = simplify_graph(graph, std_threshold=0.5)

# Generate null models
null_models = {
    subreddit: [generate_null_model(g) for _ in range(100)]
    for subreddit, g in graphs.items()
}

# Run analyses
plot_weight_distribution(graphs)
triangles = calculate_triangles_graph(graphs)
balance_df = calculate_balance_metrics(graphs, null_models, 100)
kolmogorov_smirnov(triangles, calculate_triangles_null_graph(graphs, null_models))
```

## Notes

- The `std_threshold` parameter controls edge quality filtering; higher values retain more edges but with potentially noisier data
- Null model generation uses random shuffling without a fixed seed for statistical robustness
- The `non_binary_metric` function is experimental and under development
- Kolmogorov-Smirnov tests are adapted for discrete distributions with step-function interpolation
