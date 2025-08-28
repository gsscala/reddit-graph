import numpy as np
import networkx as nx
import random
import math

def generate_null_model(graph: nx.Graph):
    weights = [graph[a][b]["weight"] for a, b in graph.edges()]
    random.seed(42)
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

def calculate_bs(graph: nx.Graph, z = 3):
    nodes = list(graph.nodes())
    n = len(nodes)
    if n == 0:
        return 0 # Or handle as an error for an empty graph

    N = np.zeros((n, n))
    P = np.zeros((n, n))
    node_index = {node: idx for idx, node in enumerate(nodes)}

    for a, b, data in graph.edges(data=True):
        i, j = node_index[a], node_index[b]
        if data.get("weight") == -1: # Use .get() for safety
            N[i, j] = 1
            N[j, i] = 1
        else:
            P[i, j] = 1
            P[j, i] = 1

    # Combining P and N for eigenvalue calculation
    A_plus = P + N
    A_minus = P - N
    
    max_eigenvalue = max(np.linalg.eigvalsh(A_plus).max(), np.linalg.eigvalsh(A_minus).max())

    # Note: If max_eigenvalue is zero or very small, the original alfa calculation
    # (z / max_eigenvalue) could be problematic. Using a fixed value is safer.
    alfa = 2.0
    
    I = np.eye(n)

    # Define the two matrices for the determinant calculation
    M_num = alfa * max_eigenvalue * I - A_minus
    M_den = alfa * max_eigenvalue * I - A_plus

    # === FIX: Use slogdet to prevent overflow ===

    # Calculate sign and log-determinant for numerator and denominator matrices
    sign_num, logdet_num = np.linalg.slogdet(M_num)
    sign_den, logdet_den = np.linalg.slogdet(M_den)

    # It's crucial to handle edge cases where the math would be invalid
    # Case 1: Denominator's determinant is zero (singular matrix)
    if sign_den == 0:
        print("Warning: Denominator matrix is singular (determinant is zero).")
        return float('-inf') # Represents log(x / 0)

    # Case 2: Numerator is zero, but denominator is not.
    if sign_num == 0:
        print("Warning: Numerator matrix is singular (determinant is zero).")
        return float('-inf') # Represents log(0 / y)

    # Case 3: The ratio of determinants is negative. The log of a negative
    # number is undefined in real numbers.
    if sign_num != sign_den:
        print("Warning: Ratio of determinants is negative. Log is undefined for real numbers.")
        return float('nan') # 'Not a Number' is appropriate here

    # Now, use the logarithm property: log(x / y) = log(x) - log(y)
    # This calculation is performed on the small log-determinant values,
    # completely avoiding the large numbers that caused the overflow.
    stable_log_ratio = logdet_num - logdet_den
    
    bs = stable_log_ratio / 4
    
    return bs