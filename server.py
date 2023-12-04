from concurrent import futures
import logging
import reddit.v1.reddit_pb2 as reddit_pb2
import reddit.v1.reddit_pb2_grpc as reddit_pb2_grpc
import grpc

database = {}


class RedditServer(reddit_pb2_grpc.RedditService):
    def CreatePost(self, request, context):
        post = request.post
        post.id = len(database) + 1
        post.score = 0
        post.post_state = reddit_pb2.POST_STATE_NORMAL
        database[post.id] = post
        print(f"Created Post with ID {post.id}")
        return reddit_pb2.CreatePostResponse(post_id=post.id)

    # def VotePost(self, request, context):
    #     print("VotePost")
    #     print(request)
    #     id = request.post.id
    #     if id not in database:
    #         return
    #     print(database[id])
    #     if request.vote_type == 1:
    #         database[id].score += 1
    #     elif request.vote_type == 2:
    #         database[id].score -= 1
    #     return database[id]

    # def GetPost(self, request, context):
    #     print("GetPost")
    #     return reddit_pb2.Post()

    # def CreateComment(self, request, context):
    #     print("CreateComment")
    #     return reddit_pb2.Comment()

    # def VoteComment(self, request, context):
    #     print("VoteComment")
    #     return reddit_pb2.Comment()

    # def GetTopComments(self, request, context):
    #     print("GetTopComments")
    #     return reddit_pb2.GetTopCommentsResponse()

    # def ExpandCommentBranch(self, request, context):
    #     print("ExpandCommentBranch")
    #     return reddit_pb2.ExpandCommentBranchResponse()


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
