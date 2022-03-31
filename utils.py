import os

import configparser
from datetime import timedelta

import praw
import logging
from loguru import logger as botlogger


USERNAME = os.environ['REDDIT_USERNAME']
SUBREDDIT = os.environ['SUBREDDIT']
DEBUG = os.environ.get('DEBUG', 'false').lower() == 'true'
READONLY = DEBUG

COMMENT_LIMIT = int(os.environ.get('COMMENT_LIMIT', -1))
MAX_POST_AGE_DELTA = timedelta(minutes=int(os.environ['MAX_POST_AGE_MINS']))

with open('comment.tmplt.md') as fs:
    TEMPLATE = fs.read()
    
    
botlogger.add("formatbot.log", backtrace=True, level=(logging.DEBUG if DEBUG else logging.INFO))


@botlogger.catch
def get_reddit():
    reddit = praw.Reddit(
        client_id=os.environ['REDDIT_CLIENT_ID'],
        client_secret=os.environ['REDDIT_CLIENT_SECRET'],
        username=os.environ['REDDIT_USERNAME'],
        password=os.environ['REDDIT_PASSWORD'],
        user_agent=os.environ['REDDIT_USER_AGENT']
    )
    return reddit


@botlogger.catch
def create_comment(op, issues):
    issues_str = '\n'.join(f'{i}. {d}' for i, d in enumerate(issues, 1))
    return TEMPLATE.format(op=op, issues_str=issues_str)
