from __future__ import print_function

import logging

import reddit.v1.reddit_pb2 as reddit_pb2
import reddit.v1.reddit_pb2_grpc as reddit_pb2_grpc
import grpc


def run_create_post(stub, title, text, subreddit):
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


# def run_vote_post(stub, post_id, vote_type):
#     response = stub.VotePost(reddit_pb2.VoteRequest(, vote_type=1))
#     print("Reddit client received: " + response.title)


def run():
    # NOTE(gRPC Python Team): .close() is possible on a channel and should be
    # used in circumstances in which the with statement does not fit the needs
    # of the code.
    print("Will try to run APIs...")
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = reddit_pb2_grpc.RedditServiceStub(channel)
        subreddit = reddit_pb2.Subreddit(name="test subreddit")
        post_id: int = run_create_post(stub, "Test title", "Test content", subreddit)
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


if __name__ == "__main__":
    logging.basicConfig()
    run()
