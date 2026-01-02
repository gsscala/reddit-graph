import json
from pathlib import Path
from typing import Dict, Any
import networkx as nx
from tqdm import tqdm
from classifier import classifier

"""
Graph Labeling Module

This module processes user interaction data from a JSON file, performs sentiment
analysis on comments, and creates a labeled graph representation of user interactions.
"""

# Configuration constants
MESSAGES_FILE = "messages.json"
PROMPT_FILE = "prompt.txt"
OUTPUT_FILE = "./labeled_graph.gexf"
MODEL_NAME = "gemma3:12b"


def load_json(filepath: str) -> Dict[str, Any]:
    """
    Load and parse a JSON file.
    
    Args:
        filepath: Path to the JSON file
        
    Returns:
        Parsed JSON data as a dictionary
    """
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def load_text(filepath: str) -> str:
    """
    Load text content from a file.
    
    Args:
        filepath: Path to the text file
        
    Returns:
        File content as a string
    """
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def create_labeled_graph(messages: Dict[str, Any], model: classifier, prompt: str) -> nx.MultiDiGraph:
    """
    Create a labeled graph from user messages with sentiment analysis.
    
    Args:
        messages: Dictionary containing user interaction data
        model: Classifier instance for sentiment analysis
        prompt: Additional context prompt for the classifier
        
    Returns:
        NetworkX MultiDiGraph with labeled edges
    """
    graph = nx.MultiDiGraph()
    
    # Calculate total edges for progress bar
    total_edges = sum(
        len(edges)
        for user_interactions in messages.values()
        for edges in user_interactions.values()
    )
    
    with tqdm(total=total_edges, desc="Processing edges") as pbar:
        for user1, interactions in messages.items():
            for user2, edges in interactions.items():
                for edge in edges:
                    # Extract comment and classify sentiment
                    comment = edge["comments"]
                    sentiment = model.classify(f"{comment}\n{prompt}")
                    
                    # Add edge with all metadata
                    graph.add_edge(
                        user1,
                        user2,
                        weight=sentiment,
                        subreddit=edge["subreddit"],
                        score=edge["score"],
                        submissionDate=edge["submissionDate"],
                        collectionDate=edge["collectionDate"]
                    )
                    
                    pbar.update(1)
    
    return graph


def main():
    """Main execution function."""
    # Load input data
    messages = load_json(MESSAGES_FILE)
    prompt = load_text(PROMPT_FILE)
    
    # Initialize classifier
    model = classifier(MODEL_NAME)
    
    # Create labeled graph
    labeled_graph = create_labeled_graph(messages, model, prompt)
    
    # Save to file
    nx.write_gexf(labeled_graph, OUTPUT_FILE)
    print(f"Graph saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()