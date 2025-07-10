import json
from classifier import classifier
import networkx as nx
from tqdm import tqdm

with open("messages.json", "r") as f:
    messages = json.load(f)

with open("prompt.txt", "r") as f:
    prompt = f.read()
#
model = classifier("gemma3:12b")
updated_graph = nx.MultiDiGraph()

for user1 in tqdm(messages.keys()):
    for user2 in messages[user1].keys():
        for edge in messages[user1][user2]:
            comment = edge["comments"]
            sentiment = model.classify(comment + "\n" + prompt)
            updated_graph.add_edge(user1, user2, weight = sentiment, subreddit = edge["subreddit"], score = edge["score"], submissionDate = edge["submissionDate"], collectionDate = edge["collectionDate"])

nx.write_gexf(updated_graph, "./labeled_graph.gexf")
