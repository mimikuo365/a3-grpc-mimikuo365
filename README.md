# a3-grpc-mimikuo365

python client.py create_post "hello" "I am mimi"  0
python client.py create_comment 1 "comment" "post" 1 # 1
python client.py create_comment 1 "comment" "post" 1 # 2
python client.py create_comment 1 "comment" "post" 1 # 3
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