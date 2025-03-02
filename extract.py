import praw
import networkx as nx
import json
import time

REDDIT_CLIENT_ID = ""
REDDIT_CLIENT_SECRET = ""
REDDIT_USER_AGENT = ""

reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT
)

def extract_interactions(subreddit_name, post_limit=100, G=None, minComments=100, maxPosts=5, maxComments=5000):
    if G is None:
        G = nx.MultiDiGraph()
    
    trackedPosts = 0

    subreddit = reddit.subreddit(subreddit_name)
    
    for submission in subreddit.new(limit=post_limit):
        if trackedPosts == maxPosts:
            break
        try:
            numComments = submission.num_comments
            if not submission.author or numComments < minComments or numComments > maxComments:
                print(f"Skipped submission from {submission.author} with {numComments} comments")
                continue
            
            trackedPosts += 1
            print(f"Attempting to add {numComments} comments from post {trackedPosts} / {maxPosts} of {subreddit_name}")
            OP = submission.author.name
            submission.comments.replace_more(limit=None)
            comments = submission.comments.list()
            
            for comment in comments:
                if isinstance(comment, praw.models.MoreComments):
                    continue

                parent = comment.parent()
                author = comment.author

                if not author or not parent.author:
                    continue
                
                author = author.name
                parent = parent.author.name
                
                if author == "AutoModerator" or parent == "AutoModerator":
                    continue

                if isinstance(comment.parent, praw.models.Comment):
                    parent_author = parent
                else:
                    parent_author = OP
                
                G.add_edge(parent_author, author, subreddit=subreddit_name, comment=comment.body)
        except Exception as e:
            print(e)
            time.sleep(60)
    
    return G

G = nx.MultiDiGraph()
with open('subreddits.txt', 'r') as subreddits:
    for subreddit_name in subreddits:
        subreddit_name = subreddit_name.strip()
        G = extract_interactions(subreddit_name, post_limit=1000, G=G, minComments=500, maxPosts=3, maxComments=1200)

with open("reddit_graph.json", "w") as f:
    json.dump(nx.node_link_data(G), f, indent=4)

print(f"The graph was successfully generated, with {len(G.nodes())} nodes and {len(G.edges())} edges.")
