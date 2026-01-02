# Graph Labeling

Sentiment analysis and graph labeling tool for Reddit user interaction data. This module processes comment data and creates labeled interaction graphs using Large Language Models (LLMs) for sentiment classification.

## Overview

This tool takes user interaction data (comments between Reddit users) and produces a labeled graph where:
- **Nodes** represent Reddit users
- **Edges** represent interactions (comments/replies)
- **Edge weights** represent sentiment scores from -1 (negative) to 1 (positive)
- **Edge attributes** include subreddit, score, and timestamps

The sentiment analysis is performed using Ollama-hosted language models, providing flexible and customizable sentiment scoring.

## Features

- 🤖 **LLM-powered sentiment analysis** using Ollama models
- 📊 **Multi-attribute graph generation** with metadata preservation
- 🔄 **Progress tracking** with real-time progress bars
- 📈 **Flexible scoring** with customizable prompts
- 💾 **GEXF export** for compatibility with graph analysis tools

## Requirements

### Python Dependencies

```bash
pip install ollama networkx tqdm
```

### External Services

- **Ollama**: Must be installed and running locally
  - Download from: https://ollama.ai/
  - Default host: `localhost:11434`

### Required Files

- `messages.json`: Input file with user interaction data
- `prompt.txt`: Context prompt for sentiment analysis
- Language model downloaded via Ollama (e.g., `gemma3:12b`)

## Installation

1. **Install Python dependencies:**
   ```bash
   pip install ollama networkx tqdm
   ```

2. **Install and start Ollama:**
   ```bash
   # Install from https://ollama.ai/
   # Then start the service
   ollama serve
   ```

3. **Download your preferred model:**
   ```bash
   ollama pull gemma3:12b
   # Or choose another model: llama2, mistral, etc.
   ```

4. **Prepare input files:**
   - Place `messages.json` in the working directory
   - Create `prompt.txt` with your sentiment analysis instructions

## Configuration

### Model Selection

Edit the `MODEL_NAME` constant in `label.py`:

```python
MODEL_NAME = "gemma3:12b"  # Change to your preferred Ollama model
```


### File Paths

Modify these constants in `label.py` if needed:

```python
MESSAGES_FILE = "messages.json"    # Input data file
PROMPT_FILE = "prompt.txt"         # Sentiment prompt file
OUTPUT_FILE = "./labeled_graph.gexf"  # Output graph file
```

### Ollama Host

If Ollama is running on a different host or port, modify the classifier initialization:

```python
model = SentimentClassifier(MODEL_NAME, host="your-host:port")
```

## Usage

### Basic Usage

Run the labeling script:

```bash
python label.py
```

This will:
1. Load user interactions from `messages.json`
2. Process each comment through the sentiment classifier
3. Create a labeled graph with sentiment scores
4. Save the result to `labeled_graph.gexf`

## Input Format

### `messages.json`

Nested dictionary structure containing user interactions:

```json
{
  "user1": {
    "user2": [
      {
        "comments": "Text of the comment",
        "subreddit": "SubredditName",
        "score": 42,
        "submissionDate": "2024-01-15",
        "collectionDate": "2024-01-20"
      }
    ]
  }
}
```

**Structure:**
- Top level: Source user (commenter)
- Second level: Target user (comment recipient)
- Third level: Array of individual interactions

**Fields:**
- `comments` (str): The comment text to analyze
- `subreddit` (str): Subreddit where the interaction occurred
- `score` (int): Reddit score/upvotes for the comment
- `submissionDate` (str): When the comment was posted
- `collectionDate` (str): When the data was collected

### `prompt.txt`

Additional context for the sentiment classifier. Example:

```
Analyze the sentiment of the above comment on a scale from -1 to 1, where:
- -1 represents highly negative/hostile sentiment
- 0 represents neutral sentiment
- 1 represents highly positive/friendly sentiment

Consider the tone, language, and intent. Return only a numeric score.
```

## Output Format

### `labeled_graph.gexf`

GEXF (Graph Exchange XML Format) file containing:

**Graph Properties:**
- Type: MultiDiGraph (multiple directed edges between nodes)
- Format: GEXF 1.2 XML

**Edge Attributes:**
- `weight` (float): Sentiment score from -1 to 1
- `subreddit` (str): Subreddit name
- `score` (int): Comment score
- `submissionDate` (str): Submission timestamp
- `collectionDate` (str): Collection timestamp

**Usage:** Can be loaded with NetworkX, Gephi, Cytoscape, or other graph tools:

```python
import networkx as nx
graph = nx.read_gexf("labeled_graph.gexf")
```

## Module Documentation

### `classifier.py`

#### `SentimentClassifier`

Main class for sentiment analysis using Ollama models.

**Constructor:**
```python
SentimentClassifier(model: str, host: str = "localhost:11434")
```

**Parameters:**
- `model` (str): Name of the Ollama model to use
- `host` (str, optional): Ollama server address

**Methods:**

##### `classify(message: str) -> float`

Classifies the sentiment of a text message.

**Parameters:**
- `message` (str): Text to analyze

**Returns:**
- `float`: Sentiment score between -1 and 1

**Raises:**
- `ValueError`: If no numeric score can be extracted from model response

**Behavior:**
- Extracts the last numeric value from the model's response
- Constrains output to [-1, 1] range
- Returns 0.0 if score is outside valid range

### `label.py`

#### Functions

##### `load_json(filepath: str) -> Dict[str, Any]`

Loads and parses a JSON file.

**Parameters:**
- `filepath` (str): Path to JSON file

**Returns:**
- `dict`: Parsed JSON data

##### `load_text(filepath: str) -> str`

Loads text content from a file.

**Parameters:**
- `filepath` (str): Path to text file

**Returns:**
- `str`: File content

##### `create_labeled_graph(messages, model, prompt) -> nx.MultiDiGraph`

Creates a labeled graph with sentiment-scored edges.

**Parameters:**
- `messages` (dict): User interaction data
- `model` (SentimentClassifier): Classifier instance
- `prompt` (str): Additional context for classification

**Returns:**
- `nx.MultiDiGraph`: Labeled graph with sentiment scores

**Processing:**
1. Iterates through all user interactions
2. Classifies sentiment for each comment
3. Creates directed edges with metadata
4. Shows progress bar during processing

##### `main()`

Main execution function that orchestrates the entire pipeline.

**Workflow:**
1. Loads `messages.json` and `prompt.txt`
2. Initializes sentiment classifier
3. Creates labeled graph
4. Saves to `labeled_graph.gexf`