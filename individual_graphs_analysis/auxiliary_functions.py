import numpy as np
import networkx as nx
import random

def generate_null_model(graph: nx.Graph):
    weights = [graph[a][b]["weight"] for a, b in graph.edges()]
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

def calculate_bw(graph: nx.Graph):
    # BW(α) = 1/2 Tr[N(αλPI - P)-1]
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