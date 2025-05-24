import ollama
import networkx as nx
import re
from multiprocessing import Process, Manager
from tqdm import tqdm

class OllamaSentimentAnalysisGraph:
    def __init__(self, model, graph, prompt, hosts, name):
        self.model = model
        self.original_graph = graph
        self.prompt = prompt
        self.weighted_graph = nx.MultiDiGraph()
        self.hosts = hosts
        self.name = name
        self.pool = Manager().list()

    def worker(self, edges, host, position):
        client = ollama.Client(host)
        for u, v, data in tqdm(edges, desc=f"[{host} || {self.name}]", position=position):
            try:
                response = client.generate(self.model, self.prompt + "\n" + data["comments"]).response
                score = re.findall(r"-?\d+\.?\d*", response)
                sentiment = float(score[-1])
                assert(-1 <= sentiment <= 1)
            except Exception as e:
                sentiment = 0.0
            data["sentiment"] = sentiment
            self.pool.append((u, v, data))

    def process_graph(self):
        edges = list(self.original_graph.edges(data=True))
        n = len(self.hosts)

        processes = [
            Process(target=self.worker, args=(edges[i::n], self.hosts[i], i))
            for i in range(n)
        ]
        
        for p in processes:
            p.start()
        for p in processes:
            p.join()

        for u, v, data in self.pool:
            self.weighted_graph.add_edge(u, v, **{k: v for k, v in data.items() if k != "id"})

    def save_graph(self):
        nx.write_gexf(self.weighted_graph, f"./{self.name}_weighted.gexf")

if __name__ == "__main__":
    import argparse
    import os

    ArgumentParser = argparse.ArgumentParser()
    ArgumentParser.add_argument("--model", type=str)
    ArgumentParser.add_argument("--graph_path", type=str)
    ArgumentParser.add_argument("--prompt_path", type=str)
    ArgumentParser.add_argument("--host", type=str, nargs="+")
    args = ArgumentParser.parse_args()

    with open(args.prompt_path, "r") as file:
        prompt = file.read()

    if not os.path.exists(args.graph_path):
        raise ValueError(f"Path does not exist: {args.graph_path}")

    import gc

    def numEdges(filepath):
        with open(filepath, "rb") as graph:
            g = nx.read_gexf(graph)
            num_edges = g.number_of_edges()
            rtrn = (num_edges, filepath)
            del g
            del num_edges
            gc.collect()
            return rtrn

    filepaths = []
    if os.path.isdir(args.graph_path):
        for filename in os.listdir(args.graph_path):
            filepath = os.path.join(args.graph_path, filename)
            if os.path.isfile(filepath) and filename.endswith('.gexf'):
                filepaths.append((numEdges(filepath), filepath))
    else:
        filepaths.append((numEdges(args.graph_path), args.graph_path))

    for edge_count, filepath in sorted(filepaths):
        filename = os.path.basename(filepath)
        graph = nx.read_gexf(filepath)
        ollama_graph = OllamaSentimentAnalysisGraph(
            model=args.model,
            graph=graph,
            prompt=prompt,
            hosts=args.host,
            name=filename[:-5]
        )
        ollama_graph.process_graph()
        ollama_graph.save_graph()
