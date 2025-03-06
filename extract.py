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

def dfs(parent, comment, graph):
    try:
        currentAuthor = comment.author
        parentAuthor = parent.author
        if not currentAuthor or not parentAuthor:
            return
        
        currentAuthor = currentAuthor.name
        parentAuthor = parentAuthor.name
        
        if currentAuthor == "AutoModerator" or parentAuthor == "AutoModerator":
            return

        graph.add_edge(currentAuthor, parentAuthor, subreddit=subreddit_name, currentComment=comment.body, parentComment=parent.body, score=comment.score)

        for child in comment.replies:
            dfs(comment, child, graph)
    except Exception as e:
        print(e)
        time.sleep(60)

def extract_interactions(subreddit_name, post_limit, graph, minComments, maxComments, maxPosts):

    trackedPosts = 0

    subreddit = reddit.subreddit(subreddit_name)
    
    for submission in subreddit.new(limit = post_limit):
        if trackedPosts == maxPosts:
            break
        try:
            numComments = submission.num_comments
            if not submission.author or not (maxComments >= numComments >= minComments):
                print(f"Skipped submission from {submission.author} with {numComments} comments")
                continue
            
            trackedPosts += 1

            print(f"Attempting to add {numComments} comments from post {trackedPosts} / {maxPosts} of {subreddit_name}")
            
            submission.comments.replace_more(limit = None)

            for comment in submission.comments:
                dfs(submission, comment, graph)
            
        except Exception as e:
            print(e)
            time.sleep(60)
    
    return graph

G = nx.MultiDiGraph()
with open('subreddits.txt', 'r') as subreddits:
    for subreddit_name in subreddits:
        G = extract_interactions(subreddit_name, post_limit = 2e3, graph = G, minComments = 300, maxComments = 500, maxPosts = 10)

with open("reddit_graph.json", "w") as f:
    json.dump(nx.node_link_data(G), f, indent=4)

print(f"The graph was successfully generated, with {len(G.nodes())} nodes and {len(G.edges())} edges.")
