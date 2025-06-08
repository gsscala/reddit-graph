import collections

class betweeness:
    def __init__(self, graph):
        self.graph = graph
        self.betweeness = {v: 0.0 for v in graph.nodes()}

    def calculate(self):
        # Brandes' algorithm

        n = self.graph.number_of_nodes()
        for s in self.graph.nodes():
            dist = {v: -1 for v in self.graph.nodes()}
            sigma = {v: 0 for v in self.graph.nodes()}
            pred = {v: [] for v in self.graph.nodes()}
            queue = collections.deque()
            dist[s] = 0
            sigma[s] = 1
            queue.append(s)
            order = []
            
            while queue:
                u = queue.popleft()
                order.append(u)
                if u in self.graph:
                    for v, mult in self.graph[u].items():
                        if dist[v] == -1:
                            dist[v] = dist[u] + 1
                            queue.append(v)
                        if dist[v] == dist[u] + 1:
                            sigma[v] += sigma[u] * mult
                            pred[v].append(u)
            
            delta = {v: 0.0 for v in self.graph.nodes()}
            for u in reversed(order):
                for p in pred[u]:
                    mult = self.graph[p].get(u, 0) if p in self.graph else 0
                    if sigma[u] > 0:
                        factor = (sigma[p] * mult) / sigma[u]
                    else:
                        factor = 0
                    delta[p] += factor * (1 + delta[u])
                if u != s:
                    self.betweeness[u] += delta[u]
        
        if n > 2:
            norm_factor = (n-1) * (n-2)
            for v in self.graph.nodes():
                self.betweeness[v] /= norm_factor