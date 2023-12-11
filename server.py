from concurrent import futures
import logging
import grpc
import proto.reddit_pb2 as reddit_pb2
import proto.reddit_pb2_grpc as reddit_pb2_grpc

post_database = {}
comment_database = {}


def check_post_id(post_id):
    if post_id not in post_database:
        print(f"Post ID {post_id} cannot be found")
        return False
    return True


def check_comment_id(comment_id):
    if comment_id not in comment_database:
        print(f"Comment ID {comment_id} cannot be found")
        return False
    return True


class RedditServer(reddit_pb2_grpc.RedditService):
    def CreatePost(self, request, context):
        post = request.post
        id = post.id = len(post_database) + 1
        post.score = 0
        post.post_state = reddit_pb2.POST_STATE_NORMAL
        post_database[id] = {"post": post, "child_comment_ids": set()}
        print(f"Created Post with ID {id}")
        return reddit_pb2.CreatePostResponse(post_id=id, status=reddit_pb2.STATUS_OK)

    def VotePost(self, request, context):
        print("Vote Post")
        id = request.post_id
        if not check_post_id(id):
            return reddit_pb2.VotePostResponse(status=reddit_pb2.STATUS_ID_NOT_FOUND)
        vote = 1 if (request.vote_type == reddit_pb2.VOTE_TYPE_UPVOTE) else -1
        post_database[id]["post"].score += vote
        return reddit_pb2.VoteCommentResponse(
            score=post_database[id]["post"].score, status=reddit_pb2.STATUS_OK
        )

    def GetPost(self, request, context):
        if not check_post_id(request.post_id):
            return reddit_pb2.GetPostResponse(status=reddit_pb2.STATUS_ID_NOT_FOUND)
        print(f"Get Post with ID {request.post_id}")
        return reddit_pb2.GetPostResponse(
            post=post_database[request.post_id], status=reddit_pb2.STATUS_OK
        )

    def CreateComment(self, request, context):
        comment = request.comment
        selected_post = comment.attached_post_id is not None

        if selected_post:
            if not check_post_id(comment.attached_post_id):
                print(f"Post ID {comment.attached_post_id} cannot be found")
                return reddit_pb2.CreateCommentResponse(
                    status=reddit_pb2.STATUS_ID_NOT_FOUND
                )
        else:
            if not check_comment_id(comment.attached_comment_id):
                print(f"Comment ID {comment.attached_comment_id} cannot be found")
                return reddit_pb2.CreateCommentResponse(
                    status=reddit_pb2.STATUS_ID_NOT_FOUND
                )

        # setup comment
        id = comment.id = len(comment_database) + 1
        comment.score = 0
        comment.comment_state = reddit_pb2.COMMENT_STATE_NORMAL
        comment_database[id] = {"comment": comment, "child_comment_ids": set()}

        # add attached comment to parent's attached comment list
        if not selected_post:
            comment_database[comment.attached_comment_id]["child_comment_ids"].add(id)
        else:
            post_database[comment.attached_post_id]["child_comment_ids"].add(id)

        print(f"Created Comment with ID {id}")
        return reddit_pb2.CreateCommentResponse(
            comment_id=id, status=reddit_pb2.STATUS_OK
        )

    def VoteComment(self, request, context):
        print("Vote Comment")
        id = request.comment_id
        if not check_comment_id(id):
            print(f"Comment ID {id} cannot be found")
            return reddit_pb2.VoteCommentResponse(status=reddit_pb2.STATUS_ID_NOT_FOUND)
        if request.vote_type == reddit_pb2.VOTE_TYPE_UPVOTE:
            comment_database[id]["comment"].score += 1
        elif request.vote_type == reddit_pb2.VOTE_TYPE_DOWNVOTE:
            comment_database[id]["comment"].score -= 1
        return reddit_pb2.VoteCommentResponse(
            score=comment_database[id]["comment"].score,
            status=reddit_pb2.STATUS_OK,
        )

    def GetTopComments(self, request, context):
        print("GetTopComments")
        # return reddit_pb2.GetTopCommentsResponse()
        # message GetTopCommentsResponse {
        #     repeated Comment comments = 1;
        # }

    def ExpandCommentBranch(self, request, context):
        print("ExpandCommentBranch")
        return reddit_pb2.ExpandCommentBranchResponse()
        # message ExpandCommentBranchResponse {
        #     repeated Comment comments = 1;
        # }

    def MonitorCommentUpdates(self, request, context):
        pass
        # message MonitorCommentUpdatesResponse {
        #     DataType data_type = 1;
        #     int32 score = 2;
        # }


def serve():
    port = "50051"
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    reddit_pb2_grpc.add_RedditServiceServicer_to_server(RedditServer(), server)
    server.add_insecure_port("[::]:" + port)
    print("Server started, listening on " + port)
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig()
    serve()
