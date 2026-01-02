# Graph Analysis Tools

This directory contains tools for analyzing network graphs, with a focus on centrality metrics and power law distributions. The analysis is designed to work with GEXF format graph files and provides comprehensive visualization and statistical analysis capabilities.

## 📁 Files Overview

### 1. `auxiliary_functions.py`
A Python module containing reusable functions for graph analysis, data transformation, and visualization.

### 2. `graph_analysis.ipynb`
An interactive Jupyter notebook that demonstrates the complete workflow for analyzing graph centrality metrics using the auxiliary functions.

## 🚀 Quick Start

### Prerequisites

Ensure you have the following Python packages installed:

```bash
pip install networkx matplotlib numpy
```

Required packages:
- `networkx` - For graph operations and centrality calculations
- `matplotlib` - For plotting and visualization
- `numpy` - For numerical computations
- `json` - For data persistence (built-in)

### Basic Usage

1. **Prepare your graph file**: Ensure you have a GEXF format graph file (e.g., `labeled_graph.gexf`)

2. **Open the Jupyter notebook**:
   ```bash
   jupyter notebook graph_analysis.ipynb
   ```

3. **Update the graph path** in cell 2:
   ```python
   GRAPH_PATH = "labeled_graph.gexf"  # Update with your file path
   ```

4. **Run all cells** to perform the complete analysis

## 📊 Analysis Workflow

The notebook guides you through a complete centrality analysis workflow:

### Step 1: Calculate Centrality Metrics
- **Degree Centrality**: Measures the fraction of nodes a given node is connected to
- **Betweenness Centrality**: Measures how often a node appears on shortest paths between other nodes

### Step 2: Generate Frequency Distributions
Creates dictionaries mapping centrality values to their frequencies across the graph.

### Step 3: Visualize Raw Distributions
Generates histograms showing the distribution of centrality values.

### Step 4: Compute Cumulative Distributions
Calculates complementary cumulative distributions (CCDF) for both metrics.

### Step 5: Power Law Analysis
Fits a power law distribution ($y = a \cdot x^{-\gamma}$) to the cumulative data using log-log regression.

### Step 6: Summary Statistics
Displays min, max, mean, and total node counts for both centrality metrics.

## 📄 Output Files

The analysis generates the following JSON files:

- `centrality.json` - Raw degree centrality frequency distribution
- `betweeness.json` - Raw betweenness centrality frequency distribution
- `accumulated_centrality.json` - Cumulative degree centrality distribution
- `accumulated_betweenness.json` - Cumulative betweenness centrality distribution

### Data Format
All JSON files follow the format:
```json
{
  "0.0": 150,
  "0.001": 75,
  "0.002": 50,
  ...
}
```
Keys represent centrality values (as strings), values represent frequencies.

## 🔧 Auxiliary Functions Reference

### Classes

#### `DictInverter`
Inverts a dictionary by counting frequency of each unique value.

```python
inverter = DictInverter(my_dict)
frequency_dict = inverter.invert()
```

### Functions

#### `calculate_centrality_metrics(graph_path: str)`
Calculates degree and betweenness centrality for a graph.

**Parameters:**
- `graph_path`: Path to GEXF graph file

**Returns:**
- Tuple: `(centrality_dict, betweenness_dict)`

**Example:**
```python
centrality, betweenness = calculate_centrality_metrics("my_graph.gexf")
```

#### `accumulate_distribution(dictionary: Dict)`
Computes complementary cumulative distribution (CCDF) from right to left.

**Parameters:**
- `dictionary`: Dictionary with numeric string keys and numeric values

**Returns:**
- Dictionary with cumulative sums

**Example:**
```python
ccdf = accumulate_distribution(centrality_dict)
```

#### `plot_histogram(data_dict, xlabel, ylabel, title, bins)`
Plots a histogram from dictionary data.

**Parameters:**
- `data_dict`: Dictionary with numeric string keys and values
- `xlabel`: X-axis label (default: 'Centrality')
- `ylabel`: Y-axis label (default: 'Frequency')
- `title`: Plot title (optional)
- `bins`: Number of bins (default: number of unique keys)

**Example:**
```python
plot_histogram(
    centrality_dict,
    xlabel='Degree Centrality',
    ylabel='Frequency',
    title='Distribution'
)
```

#### `plot_line_graph(data_dict, xlabel, ylabel, title)`
Plots a line graph from dictionary data.

**Parameters:**
- `data_dict`: Dictionary with numeric string keys and values
- `xlabel`: X-axis label (default: 'Centrality')
- `ylabel`: Y-axis label (default: 'Cumulative Frequency')
- `title`: Plot title (optional)

**Example:**
```python
plot_line_graph(
    accumulated_centrality,
    xlabel='Degree Centrality',
    ylabel='Cumulative Frequency'
)
```

#### `fit_power_law(data_dict, xlabel, ylabel)`
Fits a power law distribution to log-log data and visualizes it.

**Parameters:**
- `data_dict`: Dictionary with numeric string keys and values
- `xlabel`: X-axis label
- `ylabel`: Y-axis label

**Returns:**
- Tuple: `(gamma, a, r_squared)` where:
  - `gamma`: Power law exponent
  - `a`: Coefficient
  - `r_squared`: Goodness of fit (R²)

**Example:**
```python
gamma, a, r_squared = fit_power_law(
    accumulated_centrality,
    xlabel='Degree Centrality',
    ylabel='Frequency'
)
print(f"Power law: y = {a:.4f} * x^(-{gamma:.3f})")
print(f"R² = {r_squared:.4f}")
```

#### `save_json(data, filepath, indent=2)`
Saves dictionary to JSON file.

**Example:**
```python
save_json(centrality_dict, "centrality.json")
```

#### `load_json(filepath)`
Loads dictionary from JSON file.

**Example:**
```python
data = load_json("centrality.json")
```