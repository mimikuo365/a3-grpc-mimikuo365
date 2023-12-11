import logging
import sys
import grpc
import proto.reddit_pb2 as reddit_pb2
import proto.reddit_pb2_grpc as reddit_pb2_grpc


class RedditClient:
    def __init__(self):
        self.channel = grpc.insecure_channel("localhost:50051")
        self.stub = reddit_pb2_grpc.RedditServiceStub(self.channel)

    def close_channel(self):
        self.channel.close()

    def create_post(self, title="default", text="default", subreddit_id=0):
        post = reddit_pb2.Post(
            title=title,
            text=text,
            subreddit_id=subreddit_id,
        )
        response = self.stub.CreatePost(reddit_pb2.CreatePostRequest(post=post))
        if response.status != reddit_pb2.STATUS_OK:
            print(f"[CreatePost] Failed to create Post")
            return
        post_id = response.post_id
        print(f"[CreatePost] Created Post with ID {post_id}")
        return post_id

    def run_create_post(self, args):
        if len(args) != 5:
            print("Usage: python3 client.py create_post <title> <text> <subreddit_id>")
            sys.exit(1)
        title, text, subreddit_id = args[2:]
        self.create_post(title, text, int(subreddit_id))

    def vote_post(self, post_id, vote_type):
        response = self.stub.VotePost(
            reddit_pb2.VotePostRequest(post_id=post_id, vote_type=vote_type)
        )
        if response.status != reddit_pb2.STATUS_OK:
            print(f"[VotePost] Failed to vote for Post {post_id}")
        elif vote_type == reddit_pb2.VOTE_TYPE_UPVOTE:
            print(f"[VotePost] Upvoted for Post {post_id}; score is now {response.score}")
        elif vote_type == reddit_pb2.VOTE_TYPE_DOWNVOTE:
            print(f"[VotePost] Downvoted for Post {post_id}; score is now {response.score}")
        else:
            print(
                f"[VotePost] Invalid vote_type {vote_type}. Only 1 (upvote) or 2 (downvote) is allowed."
            )

    def run_vote_post(self, args):
        if len(args) != 4:
            print("Usage: python3 client.py vote_post <post_id> <vote_type>")
            sys.exit(1)
        post_id, vote_type = args[2:]
        self.vote_post(int(post_id), int(vote_type))

    def get_post(self, post_id):
        response = self.stub.GetPost(reddit_pb2.GetPostRequest(post_id=post_id))
        if response.status != reddit_pb2.STATUS_OK:
            print(f"[GetPost] Reddit client received: Post ID {post_id} cannot be found")
        else:
            print(f"[GetPost] Reddit client received: {response.post.title}")

    def run_get_post(self, args):
        if len(args) != 3:
            print("Usage: python3 client.py get_post <post_id>")
            sys.exit(1)
        post_id = args[2]
        self.get_post(int(post_id))

    def create_comment(self, author_id, text, parent_type, parent_id):
        parent_fields = {"post": "attached_post_id", "comment": "attached_comment_id"}
        field_name = parent_fields.get(parent_type)
        if field_name is None:
            print(f"[CreateComment] Invalid parent_type: {parent_type}")
            return

        comment = reddit_pb2.Comment(
            author_id=author_id,
            text=text,
        )
        setattr(comment, field_name, parent_id)

        response = self.stub.CreateComment(reddit_pb2.CreateCommentRequest(comment=comment))
        if response.status == reddit_pb2.STATUS_OK:
            print(f"[CreateComment] Created Comment with ID {response.comment_id}")
        else:
            print(f"[CreateComment] Failed to create Comment")

    def run_create_comment(self, args):
        if len(args) != 6:
            print(
                "Usage: python3 client.py create_comment <author_id> <text> <parent_type> <parent_id>"
            )
            sys.exit(1)
        author_id, text, parent_type, parent_id = args[2:]
        self.create_comment(int(author_id), text, parent_type, int(parent_id))

    def vote_comment(self, comment_id, vote_type):
        if (
            vote_type != reddit_pb2.VOTE_TYPE_UPVOTE
            and vote_type != reddit_pb2.VOTE_TYPE_DOWNVOTE
        ):
            print(
                f"[VoteComment] Invalid vote_type {vote_type}. Only 1 (upvote) or 2 (downvote) is allowed."
            )

        response = self.stub.VoteComment(
            reddit_pb2.VoteCommentRequest(comment_id=comment_id, vote_type=vote_type)
        )
        if response.status == reddit_pb2.STATUS_OK:
            up_or_down = (
                "Upvoted" if vote_type == reddit_pb2.VOTE_TYPE_UPVOTE else "Downvoted"
            )
            print(
                f"[VoteComment] {up_or_down} for Comment {comment_id}. Score is now {response.score}"
            )
        else:
            print(f"[VoteComment] Failed to vote for Comment {comment_id}")

    def run_vote_comment(self, args):
        if len(args) != 4:
            print("Usage: python3 client.py vote_comment <comment_id> <vote_type>")
            sys.exit(1)
        comment_id, vote_type = args[2:]
        self.vote_comment(int(comment_id), int(vote_type))

    def get_top_comments(self, post_id, n):
        response = self.stub.GetTopComments(
            reddit_pb2.GetTopCommentsRequest(post_id=post_id, n=n)
        )
        if response.status == reddit_pb2.STATUS_OK:
            print(f"[GetTopComments] Reddit client received: {response.comments}")
        else:
            print(f"[GetTopComments] Failed to get top {n} comments for Post {post_id}")

    def run_get_top_comments(self, args):
        if len(args) != 4:
            print("Usage: python3 client.py get_top_comments <post_id> <n>")
            sys.exit(1)
        post_id, n = args[2:]
        self.get_top_comments(int(post_id), int(n))

    def expand_comment_branch(self, comment_id, n):
        response = self.stub.ExpandCommentBranch(
            reddit_pb2.ExpandCommentBranchRequest(comment_id=comment_id, n=n)
        )
        if response.status == reddit_pb2.STATUS_OK:
            print(f"[ExpandCommentBranch] Reddit client received: {response.comments}")
        else:
            print(
                f"[ExpandCommentBranch] Failed to expand comment branch for Comment {comment_id}"
            )

    def run_expand_comment_branch(self, args):
        if len(args) != 4:
            print("Usage: python3 client.py expand_comment_branch <comment_id> <n>")
            sys.exit(1)
        comment_id, n = args[2:]
        self.expand_comment_branch(int(comment_id), int(n))

    def generate_requests(self, post_id, comment_id_ls):
        print("Generating requests")
        # Send the initial request
        yield reddit_pb2.MonitorCommentUpdatesRequest(post_id=int(post_id))

        # Add comment IDs to the stream
        for comment_id in comment_id_ls:
            yield reddit_pb2.MonitorCommentUpdatesRequest(comment_id=int(comment_id))

    def run_monitor_comment_updates(self, args):
        if len(args) < 3:
            print(
                "Usage: python3 client.py monitor_comment_updates <post_id> <comment_id>..."
            )
            sys.exit(1)
        post_id, comment_id_ls = args[2], args[3:]
        responses = self.stub.MonitorCommentUpdates(self.generate_requests(post_id, comment_id_ls))

        # Monitor server responses
        for response in responses:
            print(response)

    def run_api(self, args):
        if len(args) < 2:
            print("Usage: python3 client.py <api_name> <args>")
            sys.exit(1)
        api_name = args[1]
        if api_name == "create_post":
            self.run_create_post(args)
        elif api_name == "vote_post":
            self.run_vote_post(args)
        elif api_name == "get_post":
            self.run_get_post(args)
        elif api_name == "create_comment":
            self.run_create_comment(args)
        elif api_name == "vote_comment":
            self.run_vote_comment(args)
        elif api_name == "get_top_comments":
            self.run_get_top_comments(args)
        elif api_name == "expand_comment_branch":
            self.run_expand_comment_branch(args)
        elif api_name == "monitor_comment_updates":
            self.run_monitor_comment_updates(args)
        else:
            print(f"Invalid API name {api_name}")
            sys.exit(1)


if __name__ == "__main__":
    args = sys.argv
    logging.basicConfig()
    reddit_client = RedditClient()
    reddit_client.run_api(args)
    reddit_client.close_channel()
