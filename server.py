from concurrent import futures
import logging
import grpc
import proto.reddit_pb2 as reddit_pb2
import proto.reddit_pb2_grpc as reddit_pb2_grpc
import queue
import time


class RedditServer(reddit_pb2_grpc.RedditService):
    def __init__(self) -> None:
        self.response_queue = queue.Queue()
        self.post_database = {}
        self.comment_database = {}
        self.monitor_id = {"post": set(), "comment": set()}

    def CheckScoreObserver(self, id, isPost):
        database = self.post_database
        field_name = "post"
        monitored_id = self.monitor_id["post"]

        if not isPost:
            database = self.comment_database
            field_name = "comment"
            monitored_id = self.monitor_id["comment"]

        if id in monitored_id:
            response = reddit_pb2.MonitorCommentUpdatesResponse(
                status=reddit_pb2.STATUS_OK,
                score=database[id][field_name].score,
            )
            response.__setattr__(field_name + "_id", id)
            self.response_queue.put(response)

    def check_post_id(self, post_id):
        if post_id not in self.post_database:
            print(f"Post ID {post_id} cannot be found")
            return False
        return True

    def check_comment_id(self, comment_id):
        if comment_id not in self.comment_database:
            print(f"Comment ID {comment_id} cannot be found")
            return False
        return True

    def get_top_comments(self, n, post_id=None, comment_id=None):
        if post_id is not None:
            if not self.check_post_id(post_id):
                return None
            comments = self.post_database[post_id]["child_comment_ids"]
        else:
            if not self.check_comment_id(comment_id):
                return None
            comments = self.comment_database[comment_id]["child_comment_ids"]
        # sort comments by score
        comments = sorted(
            comments,
            key=lambda comment_id: self.comment_database[comment_id]["comment"].score,
            reverse=True,
        )
        for i in range(len(comments)):
            comments[i] = self.comment_database[comments[i]]["comment"]
        return comments[:n]

    def CreatePost(self, request, context):
        post = request.post
        id = post.id = len(self.post_database) + 1
        post.score = 0
        post.post_state = reddit_pb2.POST_STATE_NORMAL
        self.post_database[id] = {"post": post, "child_comment_ids": set()}
        print(f"Created Post with ID {id}")
        return reddit_pb2.CreatePostResponse(post_id=id, status=reddit_pb2.STATUS_OK)

    def VotePost(self, request, context):
        print("Vote Post")
        id = request.post_id
        if not self.check_post_id(id):
            return reddit_pb2.VotePostResponse(status=reddit_pb2.STATUS_ID_NOT_FOUND)
        vote = 1 if (request.vote_type == reddit_pb2.VOTE_TYPE_UPVOTE) else -1
        self.post_database[id]["post"].score += vote
        self.CheckScoreObserver(id, True)
        return reddit_pb2.VoteCommentResponse(
            score=self.post_database[id]["post"].score, status=reddit_pb2.STATUS_OK
        )

    def GetPost(self, request, context):
        if not self.check_post_id(request.post_id):
            return reddit_pb2.GetPostResponse(status=reddit_pb2.STATUS_ID_NOT_FOUND)
        print(f"Get Post with ID {request.post_id}")
        return reddit_pb2.GetPostResponse(
            post=self.post_database[request.post_id]["post"], status=reddit_pb2.STATUS_OK
        )

    def CreateComment(self, request, context):
        comment = request.comment
        selected_post = comment.attached_post_id != 0

        if selected_post:
            if not self.check_post_id(comment.attached_post_id):
                print(f"Post ID {comment.attached_post_id} cannot be found")
                return reddit_pb2.CreateCommentResponse(
                    status=reddit_pb2.STATUS_ID_NOT_FOUND
                )
        else:
            if not self.check_comment_id(comment.attached_comment_id):
                print(f"Comment ID {comment.attached_comment_id} cannot be found")
                return reddit_pb2.CreateCommentResponse(
                    status=reddit_pb2.STATUS_ID_NOT_FOUND
                )

        # setup comment
        id = comment.id = len(self.comment_database) + 1
        comment.num_attached = comment.score = 0
        comment.comment_state = reddit_pb2.COMMENT_STATE_NORMAL
        self.comment_database[id] = {"comment": comment, "child_comment_ids": set()}

        # add attached comment to parent's attached comment list
        if not selected_post:
            parent_id = comment.attached_comment_id
            self.comment_database[parent_id]["child_comment_ids"].add(id)
            self.comment_database[parent_id]["comment"].num_attached += 1
        else:
            self.post_database[comment.attached_post_id]["child_comment_ids"].add(id)

        print(f"Created Comment with ID {id}")
        return reddit_pb2.CreateCommentResponse(
            comment_id=id, status=reddit_pb2.STATUS_OK
        )

    def VoteComment(self, request, context):
        print("Vote Comment")
        id = request.comment_id
        if not self.check_comment_id(id):
            print(f"Comment ID {id} cannot be found")
            return reddit_pb2.VoteCommentResponse(status=reddit_pb2.STATUS_ID_NOT_FOUND)
        if request.vote_type == reddit_pb2.VOTE_TYPE_UPVOTE:
            self.comment_database[id]["comment"].score += 1
        elif request.vote_type == reddit_pb2.VOTE_TYPE_DOWNVOTE:
            self.comment_database[id]["comment"].score -= 1

        self.CheckScoreObserver(id, False)
        return reddit_pb2.VoteCommentResponse(
            score=self.comment_database[id]["comment"].score,
            status=reddit_pb2.STATUS_OK,
        )

    def GetTopComments(self, request, context):
        print("Get Top Comments")
        print(request)
        if not self.check_post_id(request.post_id):
            return reddit_pb2.GetTopCommentsResponse(
                status=reddit_pb2.STATUS_ID_NOT_FOUND
            )
        comments = self.get_top_comments(request.n, post_id=request.post_id)
        if comments is None:
            return reddit_pb2.GetTopCommentsResponse(
                status=reddit_pb2.STATUS_ID_NOT_FOUND
            )
        return reddit_pb2.GetTopCommentsResponse(
            comments=comments[: request.n], status=reddit_pb2.STATUS_OK
        )

    def ExpandCommentBranch(self, request, context):
        print("Expand Comment Branch")
        if not self.check_comment_id(request.comment_id):
            return reddit_pb2.ExpandCommentBranchResponse(
                status=reddit_pb2.STATUS_ID_NOT_FOUND
            )
        comments = self.get_top_comments(request.n, comment_id=request.comment_id)
        if comments is None:
            return reddit_pb2.GetTopCommentsResponse(
                status=reddit_pb2.STATUS_ID_NOT_FOUND
            )
        for comment in comments:
            print("Expand:", comment)
            new_comments = self.get_top_comments(request.n, comment_id=comment.id)
            if new_comments is None:
                return reddit_pb2.GetTopCommentsResponse(
                    status=reddit_pb2.STATUS_ID_NOT_FOUND
                )
            comments.extend(new_comments)
        return reddit_pb2.ExpandCommentBranchResponse(
            comments=comments, status=reddit_pb2.STATUS_OK
        )

    def MonitorCommentUpdates(self, request_iterator, context):
        print("Monitor Comment Updates")
        for request in request_iterator:
            isPost = request.post_id != 0
            if isPost:
                if not self.check_post_id(request.post_id):
                    return reddit_pb2.MonitorCommentUpdatesResponse(
                        status=reddit_pb2.STATUS_ID_NOT_FOUND
                    )
                self.monitor_id["post"].add(request.post_id)
            else:
                if not self.check_comment_id(request.comment_id):
                    return reddit_pb2.MonitorCommentUpdatesResponse(
                        status=reddit_pb2.STATUS_ID_NOT_FOUND
                    )
                self.monitor_id["comment"].add(request.comment_id)
        duration = 10  # 10 seconds
        start_time = time.time()
        while time.time() - start_time < duration:
            # Yield responses from the queue as they become available
            yield self.response_queue.get()
        self.response_queue = queue.Queue()
        self.monitor_id = {"post": set(), "comment": set()}


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
