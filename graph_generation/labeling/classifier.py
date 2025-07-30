import ollama
import re

class classifier:
    def __init__(self, model):
        self.client = ollama.Client("localhost:11434")
        self.model = model
    def classify(self, message):
        response = self.client.generate(self.model, message).response
        score = re.findall(r"-?\d+\.?\d*", response)
        sentiment = float(score[-1])
        if (not(1 >= sentiment >= -1)):
            sentiment = 0.0
        return sentiment
