import networkx as nx
from collections import defaultdict

old_graph = nx.read_gexf("labeled_graph.gexf")

graph = defaultdict(lambda: defaultdict(list))

for u, v, data in old_graph.edges(data=True):
    if u == v:
        continue
    graph[u][v].append(data["weight"])
    
new_graph = nx.DiGraph()

for u, neighbors in graph.items():
    for v, weights in neighbors.items():
        new_graph.add_edge(u, v, **{f"weight{i}":weights[i] for i in range(len(weights))})

nx.write_gexf(new_graph, "merged_labeled_edges.gexf")
