from service.client import RedditClient


def setup_reddit(client):
    post_id = client.create_post("post1", "user1")
    client.create_comment(1, "comment1", "post", 1)  # Comment 1 attached to post 1
    client.create_comment(1, "comment2", "post", 1)  # Comment 2 attached to post 1
    client.create_comment(1, "comment3", "post", 1)  # Comment 3 attached to post 1

    client.create_comment(
        1, "comment4", "comment", 1
    )  # Comment 4 attached to comment 1
    client.create_comment(
        1, "comment5", "comment", 1
    )  # Comment 5 attached to comment 1

    client.vote_comment(1, 1)  # Comment 1 upvoted
    client.vote_comment(2, 2)  # Comment 2 downvoted
    client.vote_comment(4, 2)  # Comment 4 downvoted

    return post_id


def run_reddit(post_id, client):
    print("running reddit")
    client.get_post(post_id)
    response = client.get_top_comments(1, 2)
    print(response)
    print("===========================")
    comment_id = response.comments[0].id
    return client.expand_comment_branch(comment_id, 1)


def run_example():
    client = RedditClient()
    post_id = setup_reddit(client)
    run_reddit(post_id, client)


if __name__ == "__main__":
    run_example()
