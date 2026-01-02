"""
Auxiliary functions for graph analysis.
Contains reusable functions for centrality analysis, data transformation, and visualization.
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from collections import defaultdict
from typing import Dict, List, Tuple


class DictInverter:
    """
    Inverts a dictionary by counting the frequency of each unique value.
    """
    def __init__(self, dictionary: dict):
        self.new_dict = defaultdict(int)
        self.dictionary = dictionary
    
    def invert(self):
        """Count frequency of each unique value in the dictionary."""
        for val in self.dictionary.values():
            self.new_dict[val] += 1
        return dict(self.new_dict)


def calculate_centrality_metrics(graph_path: str) -> Tuple[Dict, Dict]:
    """
    Calculate degree centrality and betweenness centrality for a graph.
    
    Args:
        graph_path: Path to the GEXF graph file
        
    Returns:
        Tuple of (centrality_dict, betweenness_dict) with frequency distributions
    """
    graph = nx.DiGraph(nx.read_gexf(graph_path))
    
    # Calculate centrality metrics
    degree_centrality = nx.degree_centrality(graph)
    betweenness = nx.betweenness_centrality(graph)
    
    # Invert dictionaries to get frequency distributions
    centrality_inverter = DictInverter(degree_centrality)
    betweenness_inverter = DictInverter(betweenness)
    
    centrality_dict = centrality_inverter.invert()
    betweenness_dict = betweenness_inverter.invert()
    
    return centrality_dict, betweenness_dict


def accumulate_distribution(dictionary: Dict) -> Dict:
    """
    Compute cumulative distribution (from right to left).
    
    Args:
        dictionary: Dictionary with numeric string keys and numeric values
        
    Returns:
        Dictionary with cumulative sums
    """
    # Convert keys to floats for numerical sorting
    to_sort = [[float(key), val] for key, val in dictionary.items()]
    to_sort.sort(key=lambda x: x[0])
    
    # Compute cumulative sum from right to left
    for i in range(len(to_sort) - 2, -1, -1):
        to_sort[i][1] += to_sort[i+1][1]
    
    # Convert back to dictionary with string keys
    result = {str(key): val for key, val in to_sort}
    return result


def plot_histogram(data_dict: Dict, xlabel: str = 'Centrality', ylabel: str = 'Frequency', 
                   title: str = None, bins: int = None):
    """
    Plot histogram from dictionary data.
    
    Args:
        data_dict: Dictionary with numeric string keys and values
        xlabel: Label for x-axis
        ylabel: Label for y-axis
        title: Plot title (optional)
        bins: Number of bins (default: number of unique keys)
    """
    keys = list(map(float, data_dict.keys()))
    values = list(data_dict.values())
    
    if bins is None:
        bins = len(data_dict)
    
    plt.figure(figsize=(10, 6))
    plt.hist(keys, weights=values, bins=bins)
    plt.xlabel(xlabel, fontsize=14)
    plt.ylabel(ylabel, fontsize=14)
    if title:
        plt.title(title, fontsize=16)
    plt.tick_params(axis='both', which='major', labelsize=12)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


def plot_line_graph(data_dict: Dict, xlabel: str = 'Centrality', 
                    ylabel: str = 'Cumulative Frequency', title: str = None):
    """
    Plot line graph from dictionary data.
    
    Args:
        data_dict: Dictionary with numeric string keys and values
        xlabel: Label for x-axis
        ylabel: Label for y-axis
        title: Plot title (optional)
    """
    # Sort by key (converted to float)
    sorted_items = sorted(data_dict.items(), key=lambda item: float(item[0]))
    keys = [float(item[0]) for item in sorted_items]
    values = [item[1] for item in sorted_items]
    
    plt.figure(figsize=(10, 6))
    plt.plot(keys, values, marker='.', linestyle='-')
    plt.xlabel(xlabel, fontsize=14)
    plt.ylabel(ylabel, fontsize=14)
    if title:
        plt.title(title, fontsize=16)
    plt.tick_params(axis='both', which='major', labelsize=12)
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def fit_power_law(data_dict: Dict, xlabel: str = 'Complementary Cumulative Degree Centrality', 
                  ylabel: str = 'Frequency') -> Tuple[float, float, float]:
    """
    Fit a power law distribution to log-log data and visualize it.
    
    Args:
        data_dict: Dictionary with numeric string keys and values
        xlabel: Label for x-axis
        ylabel: Label for y-axis
        
    Returns:
        Tuple of (gamma, a, r_squared) where y = a * x^(-gamma)
    """
    # Extract and convert data
    x_raw = list(map(float, data_dict.keys()))
    y_raw = list(map(float, data_dict.values()))
    
    # Filter out zero values (log(0) undefined)
    x_clean = []
    y_clean = []
    for x_val, y_val in zip(x_raw, y_raw):
        if x_val > 0 and y_val > 0:
            x_clean.append(x_val)
            y_clean.append(y_val)
    
    # Transform to log-space
    log_x = np.log(x_clean)
    log_y = np.log(y_clean)
    
    # Linear regression in log-space
    A = np.vstack([log_x, np.ones(len(log_x))]).T
    slope, log_intercept = np.linalg.lstsq(A, log_y, rcond=None)[0]
    
    # Power law parameters: y = a * x^(-gamma)
    gamma = -slope
    a = np.exp(log_intercept)
    
    # Calculate R²
    predicted_log_y = slope * log_x + log_intercept
    ss_res = np.sum((log_y - predicted_log_y) ** 2)
    ss_tot = np.sum((log_y - np.mean(log_y)) ** 2)
    r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
    
    # Generate fitted curve
    x_fit = np.logspace(np.log10(min(x_clean)), np.log10(max(x_clean)), 500)
    y_fit = a * (x_fit ** (-gamma))
    
    # Plot
    plt.figure(figsize=(10, 6))
    plt.scatter(x_clean, y_clean, alpha=0.6, label='Data', color='blue')
    plt.plot(x_fit, y_fit, 'r-', linewidth=2, 
             label=f'Fit: $y = {a:.8f} \\cdot x^{{-{gamma:.3f}}}$')
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel(f'{xlabel} (log scale)', fontsize=25)
    plt.ylabel(f'{ylabel} (log scale)', fontsize=25)
    plt.legend(fontsize=20)
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    plt.grid(True, which="both", ls="-", alpha=0.3)
    plt.tight_layout()
    plt.show()
    
    return gamma, a, r_squared


def save_json(data: Dict, filepath: str, indent: int = 2):
    """Save dictionary to JSON file."""
    with open(filepath, "w") as f:
        json.dump(data, f, indent=indent)


def load_json(filepath: str) -> Dict:
    """Load dictionary from JSON file."""
    with open(filepath, "r") as f:
        return json.load(f)
