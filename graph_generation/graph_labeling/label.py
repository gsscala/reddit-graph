import json  # For reading and parsing JSON files
from classifier import classifier  # Custom classifier for sentiment analysis
import networkx as nx  # NetworkX for graph operations
from tqdm import tqdm  # Progress bar for loops

with open("messages.json", "r") as f:
    messages = json.load(f)  # Load user messages from JSON file

with open("prompt.txt", "r") as f:
    prompt = f.read()  # Read prompt text for classifier
model = classifier("gemma3:12b")  # Initialize classifier model
updated_graph = nx.MultiDiGraph()  # Create a new directed multigraph

for user1 in tqdm(messages.keys()):  # Iterate over all users with progress bar
    for user2 in messages[user1].keys():  # Iterate over users they interacted with
        for edge in messages[user1][user2]:  # Iterate over each message edge
            comment = edge["comments"]  # Get the comment text
            sentiment = model.classify(comment + "\n" + prompt)  # Classify sentiment using model and prompt
            # Add edge to graph with sentiment as weight and other metadata
            updated_graph.add_edge(
                user1,
                user2,
                weight=sentiment,
                subreddit=edge["subreddit"],
                score=edge["score"],
                submissionDate=edge["submissionDate"],
                collectionDate=edge["collectionDate"]
            )

nx.write_gexf(updated_graph, "./labeled_graph.gexf")  # Save the labeled graph to a GEXF file