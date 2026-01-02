"""Module for sentiment classification using Ollama language models."""

import re
from typing import Optional

import ollama


class SentimentClassifier:
    """A classifier that uses an Ollama model to score sentiment from text.
    
    Attributes:
        client: An Ollama client instance for model communication.
        model: The name of the Ollama model to use for classification.
    """
    
    def __init__(self, model: str, host: str = "localhost:11434") -> None:
        """Initialize the sentiment classifier.
        
        Args:
            model: Name of the Ollama model to use for sentiment analysis.
            host: Ollama server host address. Defaults to "localhost:11434".
        """
        self.client = ollama.Client(host)
        self.model = model
    
    def classify(self, message: str) -> float:
        """Classify the sentiment of a given message.
        
        Extracts a sentiment score from the model's response by finding numeric
        values and using the last one as the sentiment score. The score is
        constrained to the range [-1, 1], where -1 is negative, 0 is neutral,
        and 1 is positive sentiment.
        
        Args:
            message: The text message to analyze for sentiment.
            
        Returns:
            A float between -1 and 1 representing the sentiment score.
            Returns 0.0 if the extracted score is outside the valid range.
            
        Raises:
            ValueError: If no numeric score can be extracted from the response.
        """
        # Get sentiment analysis from the model
        response = self.client.generate(self.model, message).response
        
        # Extract numeric values from the response
        scores = re.findall(r"-?\d+\.?\d*", response)
        
        if not scores:
            raise ValueError(
                f"No numeric sentiment score found in model response: {response}"
            )
        
        # Use the last numeric value as the sentiment score
        sentiment = float(scores[-1])
        
        # Validate sentiment is within expected range [-1, 1]
        if not -1 <= sentiment <= 1:
            return 0.0
        
        return sentiment
