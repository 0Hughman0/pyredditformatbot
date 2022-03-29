import os

import configparser
from datetime import timedelta

import praw
from loguru import logger as botlogger

botlogger.add("formatbot.log", backtrace=True)

USERNAME = os.environ['REDDIT_USERNAME']
SUBREDDIT = os.environ['SUBREDDIT']
READONLY = bool(os.environ.get('DEBUG', False))

MAX_POST_AGE_DELTA = timedelta(minutes=int(os.environ['MAX_POST_AGE_MINS']))

TEMPLATE = (
    "Hello u/{op}, I'm a bot that can assist you with code-formatting for reddit.\n"
    'I have detected the following potential issue(s) with your submission:\n\n'
    "{issues_str}\n\nIf I am correct then please follow [these instructions]"
    "(https://www.reddit.com/r/learnpython/wiki/faq#wiki_how_do_i_format_code.3F) "
    "to fix your code formatting. Thanks!"
)


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
