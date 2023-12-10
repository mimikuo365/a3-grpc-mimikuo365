from concurrent import futures
import logging
import grpc
import proto.reddit_pb2 as reddit_pb2
import proto.reddit_pb2_grpc as reddit_pb2_grpc

post_database = {}


class RedditServer(reddit_pb2_grpc.RedditService):
    def CreatePost(self, request, context):
        post = request.post
        id = post.id = len(post_database) + 1
        post.score = 0
        post.post_state = reddit_pb2.POST_STATE_NORMAL
        post_database[id] = post
        print(f"Created Post with ID {id}")
        return reddit_pb2.CreatePostResponse(post_id=id)

    def VotePost(self, request, context):
        id = request.post_id
        if id not in post_database:
            print(f"Post ID {post.id} cannot be found")
            return -1
        if request.vote_type == reddit_pb2.VOTE_TYPE_UPVOTE:
            post_database[id].score += 1
        elif request.vote_type == reddit_pb2.VOTE_TYPE_DOWNVOTE:
            post_database[id].score -= 1
        return reddit_pb2.VoteCommentResponse(score=post_database[id].score)

    def GetPost(self, request, context):
        print(f"Get Post with ID {request.post_id}")
        return reddit_pb2.GetPostResponse(post=database[request.post_id])

    def CreateComment(self, request, context):
        print("CreateComment")
        return reddit_pb2.CreateCommentResponse(comment_id=1)

    def VoteComment(self, request, context):
        print("VoteComment")
        return reddit_pb2.Comment()
        #     message VoteCommentResponse {
        #   int32 score = 1;
        # }

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
