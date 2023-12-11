# a3-grpc-mimikuo365

python client.py create_post "hello" "I am mimi"  0
python client.py create_comment 1 "comment" "post" 1
python client.py create_comment 1 "comment" "post" 1
python client.py create_comment 1 "comment" "post" 1
python client.py vote_comment 1 2
python client.py vote_comment 1 2
python client.py vote_comment 2 2
python client.py get_top_comments 1 1
python client.py get_top_comments 1 2