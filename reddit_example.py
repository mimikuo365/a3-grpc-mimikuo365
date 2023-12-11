from client import *


def setup_reddit(client):
    post_id = create_post(client, "post1", "user1")
    create_comment(client, 1, "comment1", "post", 1)  # Comment 1 attached to post 1
    create_comment(client, 1, "comment2", "post", 1)  # Comment 2 attached to post 1
    create_comment(client, 1, "comment3", "post", 1)  # Comment 3 attached to post 1

    create_comment(
        client, 1, "comment4", "comment", 1
    )  # Comment 4 attached to comment 1
    create_comment(
        client, 1, "comment5", "comment", 1
    )  # Comment 5 attached to comment 1

    vote_comment(client, 1, 1) # Comment 1 upvoted
    vote_comment(client, 2, 2) # Comment 2 downvoted
    vote_comment(client, 4, 2) # Comment 4 downvoted

    return post_id


def run_reddit(post_id, client):
    print("running reddit")
    get_post(client, post_id)
    expand_comment_branch(client, 1, 1)
    get_top_comments(client, 1, 2)


def run_example():
    client, channel = create_client()
    post_id = setup_reddit(client)
    run_reddit(post_id, client)
    close_channel(channel)


if __name__ == "__main__":
    run_example()
