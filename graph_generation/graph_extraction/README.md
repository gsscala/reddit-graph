# Graph Extraction

Reddit user interaction graph extraction tool. This module uses the Reddit API (PRAW) to extract comment interactions from specified subreddits and build NetworkX graphs representing user-to-user communication patterns.

## Overview

This toolset extracts and processes Reddit comment data to create interaction graphs where:
- **Nodes** represent Reddit users
- **Edges** represent comment interactions (replies)
- **Edge attributes** include comment text, subreddit, score, and timestamps
- **Graph structure** preserves conversation threads through depth-first traversal

The module provides three main components:
1. **extract_comments.py**: Extracts comments from Reddit and builds individual subreddit graphs
2. **merge_graphs.py**: Combines multiple subreddit graphs into a single unified graph
3. **make_adj_list.py**: Converts graphs into JSON adjacency list format for easier processing

## Features

- 🔍 **Configurable extraction** with limits on posts and comments
- 🌳 **Thread-aware traversal** using DFS to preserve conversation context
- 🔄 **Automatic retry logic** for handling API rate limits
- 📊 **Progress tracking** with real-time progress bars
- 🔗 **Graph merging** to combine multiple subreddit datasets
- 💾 **Multiple export formats** (GEXF and JSON)
- ⏱️ **Timestamp tracking** for both submission and collection dates

## Requirements

### Python Dependencies

```bash
pip install praw networkx python-dotenv pytz tqdm
```

### Reddit API Credentials

You need Reddit API credentials to access the Reddit API:
1. Go to https://www.reddit.com/prefs/apps
2. Click "Create App" or "Create Another App"
3. Select "script" as the app type
4. Note your `client_id`, `client_secret`, and create a `user_agent`

### Required Files

- **`.env`**: Environment variables file containing Reddit API credentials
- **`subreddits.txt`**: Text file with subreddit names (one per line)

## Installation

1. **Install Python dependencies:**
   ```bash
   pip install praw networkx python-dotenv pytz tqdm
   ```

2. **Set up Reddit API credentials:**

   Create a `.env` file in the project directory:
   ```env
   REDDIT_CLIENT_ID=your_client_id_here
   REDDIT_CLIENT_SECRET=your_client_secret_here
   USER_AGENT=your_user_agent_here
   ```

3. **Create subreddit list:**

   Create `subreddits.txt` with one subreddit name per line:
   ```
   science
   technology
   programming
   datascience
   ```

## Usage

### Basic Usage

Extract comments from subreddits listed in `subreddits.txt`:

```bash
python extract_comments.py
```

This creates a new folder (e.g., `reddit-graph/`) containing:
- Individual `.gexf` files for each subreddit
- One file per subreddit (e.g., `science.gexf`, `technology.gexf`)

### Advanced Usage

#### Extract with Custom Parameters

```bash
python extract_comments.py \
    --post_limit 100000 \
    --min_comments 200 \
    --max_comments 2000 \
    --max_posts 30 \
    --merge_graphs \
    --dump_messages
```

**Parameters:**
- `--post_limit`: Maximum number of posts to scan per subreddit (default: 100000)
- `--min_comments`: Minimum comments required for a post to be processed (default: 200)
- `--max_comments`: Maximum comments allowed for a post to be processed (default: 2000)
- `--max_posts`: Number of posts to extract per subreddit (default: 30)
- `--merge_graphs`: Create a merged graph file combining all subreddits
- `--dump_messages`: Create a JSON file with adjacency list format

#### Merge Existing Graphs

Combine multiple `.gexf` files from a directory:

```bash
python merge_graphs.py --src ./reddit-graph/
```

This creates `reddit_graph_merged.gexf` in the specified directory.

#### Convert Graph to JSON Format

Convert a `.gexf` graph file to JSON adjacency list:

```bash
python make_adj_list.py --path ./reddit-graph/science.gexf
```

This creates `messages.json` in the same directory as the input file.

## Configuration

### Extraction Parameters

The extraction process can be fine-tuned:

- **Post Limit**: Controls how many recent posts to scan
  - Higher values = more comprehensive but slower
  - Recommended: 10000-100000

- **Comment Range**: Filters posts by comment count
  - `min_comments`: Ensures sufficient data per post
  - `max_comments`: Avoids extremely large threads that are slow to process
  - Recommended: 200-2000 for balanced datasets

- **Max Posts**: Number of valid posts to extract per subreddit
  - Directly impacts dataset size
  - Recommended: 20-50 for exploratory analysis, 100+ for research

## Output Formats

### GEXF Format (`.gexf`)

NetworkX-compatible graph format with complete edge attributes.

**Structure:**
- Graph type: MultiDiGraph (multiple directed edges allowed)
- Nodes: Reddit usernames
- Edges: Comment interactions

**Edge Attributes:**
- `subreddit` (str): Subreddit where interaction occurred
- `comments` (str): Full conversation thread context
- `score` (int): Comment score (upvotes - downvotes)
- `submissionDate` (str): When the comment was posted (UTC)
- `collectionDate` (str): When the data was collected (UTC)

**Loading:**
```python
import networkx as nx
graph = nx.read_gexf("science.gexf")
```

### JSON Format (`messages.json`)

Nested dictionary structure for easier text processing.

**Structure:**
```json
{
  "user1": {
    "user2": [
      {
        "subreddit": "science",
        "comments": "Post title |~:~| Parent comment |~:~| Reply comment",
        "score": 42,
        "submissionDate": "2024-01-15 10:30:00 UTC+0000",
        "collectionDate": "2024-01-20 14:20:00 UTC+0000"
      }
    ]
  }
}
```

**Key Points:**
- Top level: Source user (commenter)
- Second level: Target user (parent comment author)
- Third level: Array of all interactions between those users
- Comments separated by `|~:~|` delimiter

**Loading:**
```python
import json
with open("messages.json", "r") as f:
    messages = json.load(f)
```

## Workflow Integration

This module is the first step in the analysis pipeline:

1. **Graph Extraction** (this module) → Individual subreddit graphs
2. **Graph Labeling** (`graph_labeling/`) → Add sentiment scores
3. **Graph Analysis** (`graph_analysis/` or `individual_graphs_analysis/`) → Analyze structure

**Pipeline Example:**
```bash
# Step 1: Extract comments
python extract_comments.py --max_posts 30 --dump_messages

# Step 2: Label with sentiment (in graph_labeling directory)
cd ../graph_labeling
python label.py

# Step 3: Analyze (in individual_graphs_analysis directory)
cd ../../individual_graphs_analysis
jupyter notebook ind_graphs.ipynb
```

## Data Considerations

### Comment Context

The `comments` field contains concatenated text using `|~:~|` as separator:
```
Post Title |~:~| Top-level comment |~:~| Reply comment
```

This preserves conversation context for sentiment analysis and NLP tasks.

### Timestamps

Two timestamps are captured:
- `submissionDate`: When the comment was originally posted
- `collectionDate`: When the data was extracted

Useful for temporal analysis and data freshness tracking.

### Edge Direction

Edges point from commenter to parent comment author:
```
commenter → parent_author
```

This represents "User A replied to User B."

### Multi-edges

The graph uses `MultiDiGraph` to preserve all interactions:
- Multiple edges between same users are kept
- Each edge represents a distinct comment
- Edge attributes differentiate interactions