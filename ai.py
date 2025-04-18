import ollama
import networkx as nx

class OllamaSentimentAnalysisGraph:
    def __init__(self, model, graph, prompt, host):
        self.model = model
        self.original_graph = graph
        self.prompt = prompt
        self.weighted_graph = nx.MultiDiGraph()
        self.client = ollama.Client(host)

    def process_graph(self):
        for u, v, data in self.original_graph.edges(data=True):
            response = self.client.generate(self.model, self.prompt + "\n" + data["comments"])
            
            self.weighted_graph.add_edge(u, v,
                **{key: value for key, value in data.items() if key not in {"id", "comments"}},
                sentiment=response
            )
    
    def save_graph(self):
        nx.write_gexf(self.weighted_graph)


if __name__ == "__main__":
    import argparse
    ArgumentParser = argparse.ArgumentParser()
    ArgumentParser.add_argument("--model", type=str)
    ArgumentParser.add_argument("--graph_path", type=str)
    ArgumentParser.add_argument("--prompt_path", type=str)
    ArgumentParser.add_argument("--host", type=str)
    args = ArgumentParser.parse_args()
    graph = nx.read_gexf(args.graph_path)
    with open(args.prompt_path, "r") as file:
        prompt = file.read()
    ollama_graph = OllamaSentimentAnalysisGraph(args.model, graph, prompt, args.host)
    ollama_graph.process_graph()
    ollama_graph.save_graph()