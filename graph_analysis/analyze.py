import networkx as nx
from json import dump as dp
import argparse
from invert_dict import DictInverter

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=str)
    parser = parser.parse_args()
    graph = nx.DiGraph(nx.read_gexf(parser.path))
    centrality = DictInverter(nx.degree_centrality(graph))
    betweeness = DictInverter(nx.betweenness_centrality(graph))

    centrality.invert()
    betweeness.invert()

    with open("centrality.json" , "w") as f:
        dp(centrality.new_dict, f)
    with open("betweeness.json", "w") as f:
        dp(betweeness.new_dict, f)