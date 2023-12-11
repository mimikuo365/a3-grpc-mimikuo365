import unittest
from unittest.mock import MagicMock
from reddit_example import run_reddit


class TestRedditExample(unittest.TestCase):
    def test_run_reddit(self):
        # Create a mock client
        post_id = 1
        client = MagicMock()
        client.create_post.return_value = post_id

        # Call the function under test
        run_reddit(post_id, client)

        # Assert that the get_post API was called once with the correct arguments
        client.get_post.assert_called_once_with(post_id)

        # Assert that the expand_comment_branch API was called once with the correct arguments
        client.expand_comment_branch.assert_called_once_with(1, 1)

        # Assert that the get_top_comments API was called once with the correct arguments
        client.get_top_comments.assert_called_once_with(1, 2)


if __name__ == "__main__":
    unittest.main()
