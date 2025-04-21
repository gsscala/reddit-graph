import praw
import networkx as nx
from time import sleep
from datetime import datetime
import pytz
from merger import GraphMerger
from separate import Separator
from tqdm import tqdm

class RedditGraphExtractor:
    def __init__(self, client_id, client_secret, user_agent):
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        self.graph = nx.MultiDiGraph()
    
    def _dfs(self, parent, comment, subreddit_name, history):
        try:
            current_author = comment.author
            parent_author = parent.author
            
            history += " |~:~| " + comment.body

            if current_author and parent_author:
                current_author = current_author.name
                parent_author = parent_author.name

                if current_author != "AutoModerator" and parent_author != "AutoModerator":
                    self.graph.add_edge(
                        current_author, parent_author,
                        subreddit=subreddit_name,
                        comments=history,
                        score=comment.score,
                        submissionDate = str(datetime.fromtimestamp(comment.created_utc, tz=pytz.utc).strftime('%Y-%m-%d %H:%M:%S %Z%z')),
                        collectionDate = str(datetime.now(pytz.utc).strftime('%Y-%m-%d %H:%M:%S %Z%z'))
                    )
            
            for child in comment.replies:
                try:
                    self._dfs(comment, child, subreddit_name, history)
                except Exception as e:
                    sleep(60)
                    self._dfs(comment, child, subreddit_name, history)
            
        except Exception as e:
            sleep(60)
            self._dfs(parent, comment, subreddit_name, history)
    
    def extract_interactions(self, subreddit_name, post_limit, min_comments, max_comments, max_posts):
        subreddit = self.reddit.subreddit(subreddit_name)
        tracked_posts = 0
        pbar = tqdm(total=max_posts, desc=f"r/{subreddit_name}")

        for submission in subreddit.new(limit=post_limit):
            if tracked_posts >= max_posts:
                break
            try:
                num_comments = submission.num_comments
                
                if not (max_comments >= num_comments >= min_comments):
                    continue
                
                submission.comments.replace_more(limit=None)
                title = submission.title
                for top_level_comment in submission.comments:
                    try:
                        post = top_level_comment.body
                        for second_level_comment in top_level_comment.replies:
                            try:
                                self._dfs(top_level_comment, second_level_comment, subreddit_name, title + " |~:~| " + post)
                            except Exception as e:
                                sleep(60)
                                self._dfs(top_level_comment, second_level_comment, subreddit_name, title + " |~:~| " + post)
                    except Exception as e:
                        sleep(60)
                
                tracked_posts += 1
                pbar.update(1)
                    
            except Exception as e:
                sleep(60)
        
    def save_graph(self, path):
        nx.write_gexf(self.graph, path)

if __name__ == "__main__":
    import argparse
    from dotenv import load_dotenv
    import os
    parser = argparse.ArgumentParser(description="Extract Reddit interactions and build a graph.")
    parser.add_argument("--post_limit", type=int, default=100000, help="Maximum number of posts to process per subreddit.")
    parser.add_argument("--min_comments", type=int, default=200, help="Minimum number of comments required for a post to be considered.")
    parser.add_argument("--max_comments", type=int, default=1000, help="Maximum number of comments allowed for a post to be considered.")
    parser.add_argument("--max_posts", type=int, default=30, help="Maximum number of posts to track per subreddit.")
    parser.add_argument('--merge_graphs', action='store_true', help='Create a separate file with all graphs merged.')
    parser.add_argument('--dump_messages', action='store_true', help='Create a JSON file of a python dictionary storing all edges between any two nodes')

    args = parser.parse_args()

    load_dotenv()

    folder_name = "reddit-graph"
    folder_path = f"./{folder_name}/"

    counter = 1
    while os.path.exists(folder_path):
        folder_path = f"./{folder_name}({counter})/"
        counter += 1

    os.makedirs(folder_path, exist_ok=False)

    with open('subreddits.txt', 'r') as file:
        for subreddit in file:
            extractor = RedditGraphExtractor(
                client_id=os.getenv('REDDIT_CLIENT_ID'), client_secret=os.getenv('REDDIT_CLIENT_SECRET'), user_agent=os.getenv('USER_AGENT')
            )
            extractor.extract_interactions(
                subreddit.strip(), post_limit=args.post_limit, min_comments=args.min_comments, max_comments=args.max_comments, max_posts=args.max_posts
            )
            extractor.save_graph(os.path.join(folder_path, f"{subreddit.strip()}.gexf"))
    
    if args.merge_graphs or args.dump_messages:
        MergedGraph = GraphMerger(folder_path)
        MergedGraph.merge()
        if args.merge_graphs:
            MergedGraph.save()
        if args.dump_messages:
            messages = Separator(MergedGraph.merged_graph)
            messages.separate()
            messages.dump(folder_path)
