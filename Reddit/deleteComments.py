__author__ = 'SaleemSaddm'

import praw

useragent = ''
username = ''
password = ''

r = praw.Reddit(user_agent=useragent)
r.login(username, password)
user = r.get_redditor(username)

i = 1
for comment in user.get_comments(limit=None):
    print i, comment.body
    if i > 1:
        comment.delete()
    i+=1
