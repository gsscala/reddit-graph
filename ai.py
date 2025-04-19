import ollama
import networkx as nx
import re

class OllamaSentimentAnalysisGraph:
    def __init__(self, model, graph, prompt, host, name):
        self.model = model
        self.original_graph = graph
        self.prompt = prompt
        self.weighted_graph = nx.MultiDiGraph()
        self.client = ollama.Client(host)
        self.name = name

    def process_graph(self):
        for u, v, data in self.original_graph.edges(data=True):
            response = self.client.generate(self.model, self.prompt + "\n" + data["comments"]).response
            score = re.findall(r"-?\d+\.?\d*", response)
            score = 0 if not len(score) else float(score[-1])
            self.weighted_graph.add_edge(u, v,
                **{key: value for key, value in data.items() if key not in {"id", "comments"}},
                sentiment=score
            )
            print(f"Added edge from {u} to {v} with weight {score}")
    
    def save_graph(self):
        nx.write_gexf(self.weighted_graph, f"./{self.name + "_weighted"}.gexf")


if __name__ == "__main__":
    import argparse
    ArgumentParser = argparse.ArgumentParser()
    ArgumentParser.add_argument("--model", type=str)
    ArgumentParser.add_argument("--graph_path", type=str)
    ArgumentParser.add_argument("--prompt_path", type=str)
    ArgumentParser.add_argument("--host", type=str)
    args = ArgumentParser.parse_args()
    with open(args.prompt_path, "r") as file:
        prompt = file.read()

    import os

    if not os.path.exists(args.graph_path):
        raise ValueError(f"Path does not exist: {args.graph_path}")

    if os.path.isdir(args.graph_path):
        for filename in os.listdir(args.graph_path):
            filepath = os.path.join(args.graph_path, filename)
            
            if not os.path.isfile(filepath) or not filename.endswith('.gexf'):
                continue
            
            try:
                graph = nx.read_gexf(filepath)
                ollama_graph = OllamaSentimentAnalysisGraph(args.model, graph, prompt, args.host, filename[:-5])
                ollama_graph.process_graph()
                ollama_graph.save_graph()
            except Exception as e:
                print(f"Failed to load {filename}: {str(e)}")

    elif os.path.isfile(args.graph_path):
        try:
            filename = args.graph_path[args.graph_path.rfind("/") + 1:]
            graph = nx.read_gexf(args.graph_path)
            ollama_graph = OllamaSentimentAnalysisGraph(args.model, graph, prompt, args.host, filename[:-5])
            ollama_graph.process_graph()
            ollama_graph.save_graph()
        except Exception as e:
            print(f"Failed to load file: {str(e)}")

