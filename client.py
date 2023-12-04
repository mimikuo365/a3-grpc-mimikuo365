from __future__ import print_function

import logging
import sys
import reddit.v1.reddit_pb2 as reddit_pb2
import reddit.v1.reddit_pb2_grpc as reddit_pb2_grpc
import grpc


def run_create_post(stub, title="default titile", text="default text", subreddit_name="default subreddit"):
    subreddit = reddit_pb2.Subreddit(name=subreddit_name)
    response: int = stub.CreatePost(
        reddit_pb2.CreatePostRequest(
            post=reddit_pb2.Post(
                title=title,
                text=text,
                subreddit=subreddit,
            )
        )
    )
    id: int = response.post_id
    print("[CreatePost] Created Post with ID " + str(id))
    return id


def run_vote_post(stub, post_id=1, vote_type=1):
    response = stub.VotePost(reddit_pb2.VotePostRequest(post_id=post_id, vote_type=1))
    print(f"[VotePost] Voted for Post {post_id}; score is now {response.score}")


def run_all_tests(stub):
    # NOTE(gRPC Python Team): .close() is possible on a channel and should be
    # used in circumstances in which the with statement does not fit the needs
    # of the code.
    print("Will try to run APIs...")
    post_id: int = run_create_post(stub, "Test title", "Test content", "Alice")
    run_vote_post(stub, post_id, reddit_pb2.VOTE_TYPE_UPVOTE)
    # response = stub.GetPost(reddit_pb2.GetPostRequest(post_id=1))
    # print("Reddit client received: " + response.title)
    # response = stub.CreateComment(
    #     reddit_pb2.Comment(post_id=1, content="test comment")
    # )
    # print("Reddit client received: " + response.content)
    # response = stub.VoteComment(
    #     reddit_pb2.VoteCommentRequest(comment_id=1, vote_type=1)
    # )
    # print("Reddit client received: " + response.content)
    # response = stub.GetTopComments(reddit_pb2.GetTopCommentsRequest(post_id=1))
    # print("Reddit client received: " + str(response.comments))
    # response = stub.ExpandCommentBranch(
    #     reddit_pb2.ExpandCommentBranchRequest(comment_id=1)
    # )
    # print("Reddit client received: " + str(response.comments))

def run_api(args, stub):
    if len(args) == 1:
        run_all_tests(stub)
    elif args[1] == "create_post":
        if len(args) != 5:
            print(
                "Usage: python3 client.py create_post <title> <text> <subreddit_name>"
            )
            sys.exit(1)
        title, text, subreddit_name = args[2:]
        run_create_post(stub, title, text, subreddit_name)
    elif args[1] == "vote_post":
        if len(args) != 4:
            print("Usage: python3 client.py vote_post <post_id> <vote_type>")
            sys.exit(1)
        post_id, vote_type = args[2:]
        run_vote_post(stub, int(post_id), int(vote_type))


if __name__ == "__main__":
    args = sys.argv
    logging.basicConfig()
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = reddit_pb2_grpc.RedditServiceStub(channel)
        run_api(args, stub)
        