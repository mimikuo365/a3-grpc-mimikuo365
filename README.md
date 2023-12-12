# a3-grpc-mimikuo365

This repo consists a toy example of how a reddit service can be provide using gRPC.

## Structure

- [client.py](client.py): This consists the client class for accessing the service.
- [server.py](server.py): This consists the server implementation when APIs are triggered.
- [reddit_example.py](reddit_example.py): This consists an example application that uses the client class to access the service.
- [test_reddit_example.py](test_reddit_example.py): This consists a test to verify reddit_example.py.
- [proto/reddit.proto](proto/reddit.proto): This consists the protocol buffer definition for this service.

## How to Run

- Compile Protobuf: Run ```protoc -I=proto --python_out=proto proto/reddit.proto``` in terminal.
- Server: Run ```python server.py``` in terminal.
- Client: Run ```python client.py``` with different arguments to trigger different APIs. The list of arguments include
  - `create_post <title> <text> <subreddit_id>`
  - `vote_post <post_id> <vote_type>`
  - `get_post <post_id>`
  - `create_comment <author_id> <text> <parent_type> <parent_id>`
  - `vote_comment <comment_id> <vote_type>`
  - `get_top_comments <post_id> <n>`
  - `expand_comment_branch <comment_id> <n>`
  - `monitor_comment_updates <post_id> <comment_id_1> <comment_id_2>...`

## Example Commends to Test

```bash
python client.py create_post "hello" "I am mimi"  0
python client.py create_comment 1 "comment" "post" 1 # 1
python client.py create_comment 1 "comment" "comment" 1 # 4
python client.py create_comment 1 "comment" "comment" 1 # 5
python client.py create_comment 1 "comment" "comment" 1 # 6
python client.py create_comment 1 "comment" "comment" 4 # 7
python client.py create_comment 1 "comment" "comment" 4 # 8
python client.py create_comment 1 "comment" "comment" 5 # 9
python client.py create_comment 1 "comment" "comment" 5 # 10
python client.py create_comment 1 "comment" "comment" 6 # 11
python client.py create_comment 1 "comment" "comment" 6 # 12
python client.py vote_comment 1 2
python client.py vote_comment 1 2
python client.py vote_comment 2 2
python client.py vote_comment 4 2
python client.py vote_comment 4 2
python client.py vote_comment 4 2
python client.py vote_comment 5 2
python client.py vote_comment 5 2
python client.py vote_comment 8 2
python client.py vote_comment 10 2
python client.py vote_comment 12 2
python client.py get_top_comments 1 1
python client.py get_top_comments 1 2
python client.py expand_comment_branch 1 1 # return id 6, 11
python client.py expand_comment_branch 1 2 # return id 5, 6, 9, 10, 11, 12
python client.py monitor_comment_updates 1 1 2 3
```

Expected results will be 
```bash
[CreatePost] Created Post with ID 1
[CreateComment] Created Comment with ID 1
[CreateComment] Created Comment with ID 2
[CreateComment] Created Comment with ID 3
[CreateComment] Created Comment with ID 4
[CreateComment] Created Comment with ID 5
[CreateComment] Created Comment with ID 6
[CreateComment] Created Comment with ID 7
[CreateComment] Created Comment with ID 8
[CreateComment] Created Comment with ID 9
[CreateComment] Created Comment with ID 10
[VoteComment] Downvoted for Comment 1. Score is now -1
[VoteComment] Downvoted for Comment 1. Score is now -2
[VoteComment] Downvoted for Comment 2. Score is now -1
[VoteComment] Downvoted for Comment 4. Score is now -1
[VoteComment] Downvoted for Comment 4. Score is now -2
[VoteComment] Downvoted for Comment 4. Score is now -3
[VoteComment] Downvoted for Comment 5. Score is now -1
[VoteComment] Downvoted for Comment 5. Score is now -2
[VoteComment] Downvoted for Comment 8. Score is now -1
[VoteComment] Downvoted for Comment 10. Score is now -1
[VoteComment] Failed to vote for Comment 12
[GetTopComments] Reddit client received: [id: 1
text: "comment"
author_id: 1
score: -2
comment_state: COMMENT_STATE_NORMAL
attached_post_id: 1
num_attached: 3
]
[GetTopComments] Reddit client received: [id: 1
text: "comment"
author_id: 1
score: -2
comment_state: COMMENT_STATE_NORMAL
attached_post_id: 1
num_attached: 3
]
[ExpandCommentBranch] Reddit client received: [id: 3
text: "comment"
author_id: 1
comment_state: COMMENT_STATE_NORMAL
attached_comment_id: 1
]
[ExpandCommentBranch] Reddit client received: [id: 3
text: "comment"
author_id: 1
comment_state: COMMENT_STATE_NORMAL
attached_comment_id: 1
, id: 2
text: "comment"
author_id: 1
score: -1
comment_state: COMMENT_STATE_NORMAL
attached_comment_id: 1
]
```