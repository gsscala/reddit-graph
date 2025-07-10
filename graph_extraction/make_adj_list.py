import networkx as nx
from collections import defaultdict
import json
import os
from tqdm import tqdm

class Separator:
    def __init__(self, graph: nx.MultiDiGraph):
        self.messages = defaultdict(lambda: defaultdict(list))
        self.graph = graph

    def separate(self):
        for u, v, data in tqdm(self.graph.edges(data=True), desc="Processing edges"):
            self.messages[u][v].append({key: value for key, value in data.items() if key != 'id'})
        return self.messages

    def dump(self, sourceFolder):
        if sourceFolder[-1] != "/":
            sourceFolder += "/"
        path = sourceFolder + 'messages.json'

        counter = 1
        while os.path.exists(path):
            path = sourceFolder + f"messages({counter}).json"
            counter += 1

        assert(not os.path.exists(path))

        with open(path, 'w') as json_file:
            json.dump(self.messages, json_file, indent=4)
        
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=str, help="Input path to .gexf file")
    parser = parser.parse_args()
    messages = Separator(nx.read_gexf(parser.path))
    messages.separate()
    messages.dump(parser.path[:parser.path.rfind("/") + 1])
