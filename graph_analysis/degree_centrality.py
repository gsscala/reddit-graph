import NetworkX as nx

class degree:
    def __init__(self, graph):
        self.graph = graph
        self.indegree = {v : 0 for v in graph.nodes()}
        self.outdegree = {v : 0 for v in graph.nodes()}
        
    def calc(self):
        for node in self.graph.nodes():
            for neighbor in self.graph.neighbors(node):
                numEdges = self.graph.number_of_edges(node, neighbor)
                self.indegree[neighbor] += numEdges
                self.outdegree[node] += numEdges
        for node in self.graph.nodes():
            assert(self.indegree[node] % 2 == self.outdegree[node] % 2 == 0)
            self.indegree[node] //= 2
            self.outdegree[node] //= 2