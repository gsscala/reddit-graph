import praw
import networkx as nx
from time import sleep
import argparse
from dotenv import load_dotenv
from os import getenv

class RedditGraphExtractor:
    def __init__(self, client_id, client_secret, user_agent):
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        self.graph = nx.MultiDiGraph()
    
    def _dfs(self, parent, comment, subreddit_name, parent_body):
        try:
            current_author = comment.author
            parent_author = parent.author
            
            if not current_author or not parent_author:
                return
            
            current_author = current_author.name
            parent_author = parent_author.name
            
            if current_author == "AutoModerator" or parent_author == "AutoModerator":
                return

            post = comment.body
            
            self.graph.add_edge(
                current_author, parent_author,
                subreddit=subreddit_name,
                currentComment=post,
                parentComment=parent_body,
                score=comment.score
            )
            
            for child in comment.replies:
                self._dfs(comment, child, subreddit_name, post)
        except Exception as e:
            print(f"Error in DFS: {e}")
            sleep(60)
    
    def extract_interactions(self, subreddit_name, post_limit, min_comments, max_comments, max_posts):
        subreddit = self.reddit.subreddit(subreddit_name)
        tracked_posts = 0
        
        for submission in subreddit.new(limit=post_limit):
            if tracked_posts >= max_posts:
                break
            try:
                num_comments = submission.num_comments
                
                if not submission.author or not (max_comments >= num_comments >= min_comments):
                    print(f"Skipped submission from {submission.author} with {num_comments} comments")
                    continue
                
                tracked_posts += 1
                print(f"Processing post {tracked_posts}/{max_posts} from r/{subreddit_name} with {num_comments} comments")
                
                submission.comments.replace_more(limit=None)

                post = submission.title
                
                for comment in submission.comments:
                    self._dfs(submission, comment, subreddit_name, post)
            except Exception as e:
                print(f"Error processing submission: {e}")
                sleep(60)
        
    def save_graph(self, filename):
        nx.write_gexf(self.graph, filename)
        print(f"Graph saved with {len(self.graph.nodes())} nodes and {len(self.graph.edges())} edges.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract Reddit interactions and build a graph.")
    parser.add_argument("--post_limit", type=int, default=2000, help="Maximum number of posts to process per subreddit.")
    parser.add_argument("--min_comments", type=int, default=300, help="Minimum number of comments required for a post to be considered.")
    parser.add_argument("--max_comments", type=int, default=500, help="Maximum number of comments allowed for a post to be considered.")
    parser.add_argument("--max_posts", type=int, default=10, help="Maximum number of posts to track per subreddit.")
    args = parser.parse_args()

    load_dotenv()

    extractor = RedditGraphExtractor(
        client_id=getenv('REDDIT_CLIENT_ID'), client_secret=getenv('REDDIT_CLIENT_SECRET'), user_agent=getenv('USER_AGENT')
    )
    
    with open('subreddits.txt', 'r') as file:
        for subreddit in file:
            extractor.extract_interactions(
                subreddit.strip(), post_limit=args.post_limit, min_comments=args.min_comments, max_comments=args.max_comments, max_posts=args.max_posts
            )
    
    extractor.save_graph("reddit_graph.gexf")
