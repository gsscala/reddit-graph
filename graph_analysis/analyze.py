import networkx as nx
from json import dump as dp
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=str)
    parser.parse_args()
    graph = nx.read_gexf(parser.path)
    centrality = nx.degree_centrality(graph)
    betweeness = nx.betweenness_centrality(graph)
    with open("centrality.json" , "w") as f:
        dp(centrality, f)
    with open("betweeness.json", "w") as f:
        dp(betweeness, f)