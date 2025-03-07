import networkx as nx
import os
import argparse

class GraphMerger:
    def __init__(self, sourceFolder):
        if not sourceFolder.endswith("/"):
            sourceFolder += "/"
        self.sourceFolder = sourceFolder
        self.merged_graph = nx.MultiDiGraph()
    def merge(self):
        for filename in os.listdir(self.sourceFolder):
            file_path = os.path.join(self.sourceFolder, filename)
            if os.path.isfile(file_path) and file_path.endswith(".gexf"):
                print(f"Adding graph {filename}")
                for u, v, data in nx.read_gexf(file_path).edges(data=True):
                    self.merged_graph.add_edge(u, v,
                    **{key: value for key, value in data.items() if key != 'id'}
                    )
    def save(self):
        folder_path = self.sourceFolder + "reddit_graph_merged.gexf"
        counter = 1
        while os.path.exists(folder_path):
            folder_path = self.sourceFolder + f"reddit_graph_merged({counter}).gexf"
            counter += 1

        nx.write_gexf(self.merged_graph, folder_path)
        print(f"Written file successfully to {folder_path}")


parser = argparse.ArgumentParser(description="Merge multiple graphs into a single .gexf")
parser.add_argument("--src", type=str, default="./", help="Path of the folder where the graphs are located.\nUse ./ to indicate relative paths instead of global ones")
args = parser.parse_args()

MergedGraph = GraphMerger(args.src)
MergedGraph.merge()
MergedGraph.save()