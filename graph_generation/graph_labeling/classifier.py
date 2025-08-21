import ollama
import re

class classifier:
    # A classifier that uses an Ollama model to score sentiment from a message
    def __init__(self, model):
        # Initialize the Ollama client and set the model name
        self.client = ollama.Client("localhost:11434")
        self.model = model
    def classify(self, message):
        # Generate a response from the model for the given message
        response = self.client.generate(self.model, message).response
        # Extract all numbers (including negative and decimals) from the response
        score = re.findall(r"-?\d+\.?\d*", response)
        # Use the last number found as the sentiment score
        sentiment = float(score[-1])
        # Ensure the sentiment score is between -1 and 1, otherwise set to 0.0
        if (not(1 >= sentiment >= -1)):
            sentiment = 0.0
        return sentiment
