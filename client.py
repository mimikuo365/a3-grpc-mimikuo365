import logging
import sys
import grpc
import proto.reddit_pb2 as reddit_pb2
import proto.reddit_pb2_grpc as reddit_pb2_grpc


def create_post(stub, title="default", text="default", subreddit_id=0):
    response: int = stub.CreatePost(
        reddit_pb2.CreatePostRequest(
            post=reddit_pb2.Post(
                title=title,
                text=text,
                subreddit_id=subreddit_id,
            )
        )
    )
    id: int = response.post_id
    print("[CreatePost] Created Post with ID " + str(id))
    return id


def run_create_post(args, stub):
    if len(args) != 5:
        print("Usage: python3 client.py create_post <title> <text> <subreddit_id>")
        sys.exit(1)
    title, text, subreddit_id = args[2:]
    create_post(stub, title, text, int(subreddit_id))


def vote_post(stub, post_id, vote_type):
    response = stub.VotePost(
        reddit_pb2.VotePostRequest(post_id=post_id, vote_type=vote_type)
    )
    if vote_type == reddit_pb2.VOTE_TYPE_UPVOTE:
        print(f"[VotePost] Upvoted for Post {post_id}; score is now {response.score}")
    elif vote_type == reddit_pb2.VOTE_TYPE_DOWNVOTE:
        print(f"[VotePost] Downvoted for Post {post_id}; score is now {response.score}")
    else:
        print(f"[VotePost] Invalid vote_type {vote_type}")


def run_vote_post(args, stub):
    if len(args) != 4:
        print("Usage: python3 client.py vote_post <post_id> <vote_type>")
        sys.exit(1)
    post_id, vote_type = args[2:]
    vote_post(stub, int(post_id), int(vote_type))


def get_post(stub, post_id):
    response = stub.GetPost(reddit_pb2.GetPostRequest(post_id=post_id))
    if response == reddit_pb2.GetPostResponse():
        print(f"[GetPost] Reddit client received: Post ID {post_id} cannot be found")
    else:
        print(f"[GetPost] Reddit client received: {response.post.title}")


def run_get_post(args, stub):
    if len(args) != 3:
        print("Usage: python3 client.py get_post <post_id>")
        sys.exit(1)
    post_id = args[2]
    get_post(stub, int(post_id))


def create_comment(stub, author_id, text, parent_type, parent_id):
    if parent_type == "post":
        response = stub.CreateComment(
            reddit_pb2.CreateCommentRequest(
                comment=reddit_pb2.Comment(
                    author_id=author_id,
                    text=text,
                    attached_post_id=parent_id,
                )
            )
        )
    else:
        response = stub.CreateComment(
            reddit_pb2.CreateCommentRequest(
                comment=reddit_pb2.Comment(
                    author_id=author_id,
                    text=text,
                    attached_comment_id=parent_id,
                )
            )
        )
    if response != reddit_pb2.CreateCommentResponse():
        print(f"[CreateComment] Created Comment with ID {response.comment_id}")
    else:
        print(f"[CreateComment] Failed to create Comment")


def run_create_comment(args, stub):
    if len(args) != 6:
        print(
            "Usage: python3 client.py create_comment <author> <text> <parent_type> <parent_id>"
        )
        sys.exit(1)
    author_id, text, parent_type, parent_id = args[2:]
    create_comment(stub, int(author_id), text, parent_type, int(parent_id))


def vote_comment(stub, comment_id, vote_type):
    if vote_type == reddit_pb2.VOTE_TYPE_UPVOTE:
        print(f"[VoteComment] Upvoted for Comment {comment_id}")
        stub.VoteComment(
            reddit_pb2.VoteCommentRequest(
                comment_id=comment_id, vote_type=reddit_pb2.VOTE_TYPE_UPVOTE
            )
        )
    elif vote_type == reddit_pb2.VOTE_TYPE_DOWNVOTE:
        print(f"[VoteComment] Downvoted for Comment {comment_id}")
        stub.VoteComment(    
            reddit_pb2.VoteCommentRequest(
                comment_id=comment_id, vote_type=reddit_pb2.VOTE_TYPE_DOWNVOTE
            )
        )
    else:
        print(f"[VoteComment] Invalid vote_type {vote_type}")

def run_vote_comment(args, stub):
    if len(args) != 4:
        print("Usage: python3 client.py vote_comment <comment_id> <vote_type>")
        sys.exit(1)
    comment_id, vote_type = args[2:]
    vote_comment(stub, int(comment_id), int(vote_type))


def run_get_top_comments(args, stub):
    pass
    # message GetTopCommentsRequest {
    #   int32 post_id = 1;
    #   int32 n = 2;
    # }


def run_expand_comment_branch(args, stub):
    pass
    # message ExpandCommentBranchRequest {
    #   int32 comment_id = 1;
    #   int32 n = 2;
    # }


def run_monitor_comment_updates(args, stub):
    pass


# message MonitorCommentUpdatesRequest {
#   oneof id {
#     int32 post_id = 1;
#     int32 comment_id = 2;
#   }
# }


def run_api(args, stub):
    if len(args) == 1:
        run_all_tests(stub)
    api_name = args[1]
    if api_name == "create_post":
        run_create_post(args, stub)
    elif api_name == "vote_post":
        run_vote_post(args, stub)
    elif api_name == "get_post":
        run_get_post(args, stub)
    elif api_name == "create_comment":
        run_create_comment(args, stub)
    elif api_name == "vote_comment":
        run_vote_comment(args, stub)
    # elif api_name == "get_top_comments":
    #     run_get_top_comments(args, stub)
    # elif api_name == "expand_comment_branch":
    #     run_expand_comment_branch(args, stub)
    # else:
    #     print(f"Invalid API name {api_name}")
    #     sys.exit(1)


if __name__ == "__main__":
    args = sys.argv
    logging.basicConfig()
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = reddit_pb2_grpc.RedditServiceStub(channel)
        run_api(args, stub)
