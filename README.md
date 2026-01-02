# Reddit Graph Analysis Project

A comprehensive toolkit for extracting, labeling, and analyzing Reddit user interaction networks. This project enables researchers to study social network dynamics, sentiment patterns, and structural balance in online communities through graph-based analysis.

## 📋 Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Complete Workflow](#complete-workflow)
- [Installation](#installation)
- [Quick Start Guide](#quick-start-guide)
- [Detailed Usage](#detailed-usage)
- [Output Files](#output-files)
- [Analysis Capabilities](#analysis-capabilities)
- [Requirements](#requirements)
- [Troubleshooting](#troubleshooting)

## 🔍 Overview

This project provides a complete pipeline for Reddit network analysis:

1. **Graph Generation**: Extract user interaction data from Reddit
2. **Sentiment Labeling**: Apply sentiment analysis to interactions using LLMs
3. **Graph Analysis**: Analyze network properties, centrality metrics, and structural balance

### Key Features

- 🌐 **Reddit Data Extraction**: Automated collection of user interactions from multiple subreddits
- 🤖 **LLM-Powered Sentiment Analysis**: Flexible sentiment labeling using Ollama models
- 📊 **Centrality Analysis**: Degree and betweenness centrality with power law fitting
- ⚖️ **Structural Balance Analysis**: Triangle patterns and balance metrics per subreddit
- 📈 **Null Model Comparison**: Statistical significance testing with randomized graphs
- 💾 **Multiple Export Formats**: GEXF, JSON, and CSV outputs

## 📁 Project Structure

```
reddit-graph/
├── README.md                          # This file
├── graph_generation/                  # Step 1 & 2: Data extraction and labeling
│   ├── .env.template                  # Template for Reddit API credentials
│   ├── graph_extraction/              # Extract Reddit interactions
│   │   ├── extract_comments.py        # Main extraction script
│   │   ├── merge_graphs.py            # Merge multiple subreddit graphs
│   │   ├── make_adj_list.py           # Convert to adjacency list format
│   │   ├── subreddits.txt             # List of subreddits to extract
│   │   ├── prompt.txt                 # Extraction configuration
│   │   └── README.md                  # Detailed extraction documentation
│   └── graph_labeling/                # Label edges with sentiment
│       ├── label.py                   # Main labeling script
│       ├── classifier.py              # Sentiment classifier using Ollama
│       ├── prompt.txt                 # Sentiment analysis prompt
│       └── README.md                  # Detailed labeling documentation
├── entire_graph_analysis/             # Step 3a: Analyze complete network
│   ├── graph_analysis.ipynb           # Centrality and power law analysis
│   ├── auxiliary_functions.py         # Analysis utilities
│   └── README.md                      # Detailed analysis documentation
└── individual_graphs_analysis/        # Step 3b: Analyze per-subreddit graphs
    ├── ind_graphs.ipynb               # Structural balance analysis
    ├── auxiliary_functions.py         # Balance analysis utilities
    ├── labeled_graph.gexf             # Input: labeled graph file
    ├── file.csv                       # Output: triangle statistics
    └── README.md                      # Detailed balance documentation
```

## 🔄 Complete Workflow

### Phase 1: Data Extraction
Extract user interactions from Reddit subreddits → Generate `.gexf` graph files

### Phase 2: Sentiment Labeling
Apply sentiment analysis to edge comments → Create labeled graph with weights

### Phase 3a: Network-Wide Analysis
Analyze centrality metrics and power law distributions across the entire network

### Phase 3b: Subreddit-Level Analysis
Analyze structural balance and triangle patterns within individual subreddits

## 🚀 Installation

### Prerequisites

- **Python 3.8+**
- **Reddit API Account** (for data extraction)
- **Ollama** (for sentiment labeling)

### 1. Install Python Dependencies

```bash
pip install networkx matplotlib numpy pandas praw python-dotenv pytz tqdm ollama jupyter ipykernel
```

### 2. Set Up Reddit API Access

1. Go to https://www.reddit.com/prefs/apps
2. Click "Create App" or "Create Another App"
3. Select **"script"** as the app type
4. Fill in the required information
5. Note your `client_id`, `client_secret`, and create a descriptive `user_agent`

6. Create `.env` file in `graph_generation/`:

```bash
cd graph_generation
cp .env.template .env
```

Edit `.env` with your credentials:
```env
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
USER_AGENT=reddit-graph-extractor/1.0
```

### 3. Set Up Ollama for Sentiment Analysis

```bash
# Install Ollama from https://ollama.ai/

# Start Ollama service
ollama serve

# Pull a language model (in a new terminal)
ollama pull gemma3:12b

# Alternative models: llama2, mistral, phi, etc.
# ollama pull llama2
```

## 🎯 Quick Start Guide

### End-to-End Example

```bash
# 1. Extract Reddit data
cd graph_generation/graph_extraction
python extract_comments.py --max_posts 10

# 2. Label with sentiment (ensure Ollama is running)
cd ../graph_labeling
python label.py

# 3a. Analyze centrality metrics
cd ../../entire_graph_analysis
jupyter notebook graph_analysis.ipynb

# 3b. Analyze structural balance
cd ../individual_graphs_analysis
jupyter notebook ind_graphs.ipynb
```

## 📖 Detailed Usage

### Step 1: Extract Reddit Interactions

Navigate to the extraction directory:

```bash
cd graph_generation/graph_extraction
```

#### Configure Subreddits

Edit `subreddits.txt` to specify which subreddits to extract:

```txt
science
technology
datascience
MachineLearning
```

#### Run Extraction

**Basic extraction** (10 posts per subreddit):
```bash
python extract_comments.py --max_posts 10
```

**Advanced extraction** with custom parameters:
```bash
python extract_comments.py \
    --post_limit 100000 \
    --min_comments 50 \
    --max_comments 500 \
    --max_posts 50 \
    --merge_graphs \
    --dump_messages
```

#### Parameters Explained

- `--post_limit`: Maximum posts to scan per subreddit (default: 100,000)
- `--min_comments`: Minimum comments required to process a post (default: 0)
- `--max_comments`: Maximum comments to process per post (default: 1,000,000)
- `--max_posts`: Number of posts to extract per subreddit (default: 10)
- `--merge_graphs`: Combine all subreddit graphs into one file
- `--dump_messages`: Export adjacency list as JSON

#### Output

- Individual `.gexf` files per subreddit (e.g., `science.gexf`)
- `merged_graph.gexf` (if `--merge_graphs` used)
- `messages.json` (if `--dump_messages` used)

**For detailed extraction documentation, see:** [graph_generation/graph_extraction/README.md](graph_generation/graph_extraction/README.md)

---

### Step 2: Label with Sentiment Analysis

Navigate to the labeling directory:

```bash
cd graph_generation/graph_labeling
```

#### Prepare Input Files

1. **Copy `messages.json`** from the extraction output to this directory
2. **Review/edit `prompt.txt`** to customize sentiment analysis instructions

Example `prompt.txt`:
```txt
You are an expert sentiment analyzer. Given a conversation thread from Reddit,
analyze the sentiment of the interaction and provide a score from -1 (negative)
to 1 (positive), with 0 being neutral.
```

#### Configure Model

Edit `label.py` to set your preferred Ollama model:

```python
MODEL_NAME = "gemma3:12b"  # or "llama2", "mistral", etc.
```

#### Run Labeling

Ensure Ollama is running (`ollama serve`), then:

```bash
python label.py
```

This processes all interactions and creates `labeled_graph.gexf` with sentiment-weighted edges.

#### Output

- `labeled_graph.gexf`: Graph file with edges weighted by sentiment scores (-1 to 1)

**For detailed labeling documentation, see:** [graph_generation/graph_labeling/README.md](graph_generation/graph_labeling/README.md)

---

### Step 3a: Analyze Centrality Metrics

Navigate to the entire graph analysis directory:

```bash
cd entire_graph_analysis
```

#### Setup

1. Copy or move `labeled_graph.gexf` to this directory
2. Open the Jupyter notebook:

```bash
jupyter notebook graph_analysis.ipynb
```

#### Workflow

The notebook guides you through:

1. **Load graph** and calculate degree/betweenness centrality
2. **Visualize distributions** with histograms
3. **Compute cumulative distributions** (CCDF)
4. **Fit power law** distributions with log-log regression
5. **Generate summary statistics**

#### Outputs

- `centrality.json` - Degree centrality frequency distribution
- `betweeness.json` - Betweenness centrality frequency distribution
- `accumulated_centrality.json` - Cumulative degree distribution
- `accumulated_betweenness.json` - Cumulative betweenness distribution
- Multiple visualization plots

#### Key Metrics

- **Degree Centrality**: Measures node connectivity (0 to 1)
- **Betweenness Centrality**: Measures bridge node importance (0 to 1)
- **Power Law Exponent (γ)**: Characterizes scale-free properties
- **R² Value**: Goodness of power law fit

**For detailed analysis documentation, see:** [entire_graph_analysis/README.md](entire_graph_analysis/README.md)

---

### Step 3b: Analyze Structural Balance

Navigate to the individual graphs analysis directory:

```bash
cd individual_graphs_analysis
```

#### Setup

1. Copy or move `labeled_graph.gexf` to this directory
2. Open the Jupyter notebook:

```bash
jupyter notebook ind_graphs.ipynb
```

#### Configuration

Set analysis parameters in the notebook:

```python
std_threshold = 0.5      # Edge filtering threshold
NumberOfRandoms = 100    # Null model iterations
```

#### Workflow

The notebook performs:

1. **Split graph** into individual subreddit graphs
2. **Generate null models** for statistical comparison
3. **Analyze weight distributions** (positive/negative/neutral edges)
4. **Identify triangles** and categorize by edge signs
5. **Calculate balance metrics** (B_w) vs null models
6. **Test significance** of structural balance patterns

#### Outputs

- `file.csv` - Triangle type counts per subreddit
- Weight distribution plots
- Triangle distribution visualizations
- Balance metric comparisons

#### Key Concepts

- **Structural Balance**: Theory that "friend of friend is friend" and "enemy of enemy is friend"
- **Triangle Types**: Classified by number of positive edges (0, 1, 2, or 3)
- **Null Models**: Randomized graphs preserving structure but shuffling weights
- **Balance Metric (B_w)**: Quantifies deviation from balance theory

**For detailed balance analysis documentation, see:** [individual_graphs_analysis/README.md](individual_graphs_analysis/README.md)

---

## 🔬 Analysis Capabilities

### Network-Wide Metrics

- **Degree Distribution**: Understand connectivity patterns
- **Centrality Analysis**: Identify influential users
- **Power Law Testing**: Determine scale-free properties

### Subreddit-Level Metrics

- **Sentiment Distribution**: Positive vs negative interaction ratios
- **Triangle Patterns**: Measure three-way interaction dynamics
- **Balance Theory Testing**: Evaluate "enemy of enemy" patterns
- **Null Model Comparison**: Statistical significance testing

### Visualization Capabilities

- Histograms and line plots
- Log-log scale power law fits
- Weight distribution plots
- Triangle distribution charts
- Statistical comparison plots