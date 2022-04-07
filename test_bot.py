import os
from pathlib import Path

import pytest
import utils
from formatbot import *
from issues import NoCodeBlockIssue, MultipleInlineIssue, TripleBacktickCodeBlockIssue


no_codeblock_cases = {file.name[:-3]: Path(file).read_text() for file in 
                      os.scandir('comment_cases/NoCodeBlock')}
multi_inline_cases = {file.name[:-3]: Path(file).read_text() for file in os.scandir(                
                      'comment_cases/MultipleInline')}
triple_backtick_cases = {file.name[:-3]: Path(file).read_text() for file in os.scandir(
                         'comment_cases/TripleBacktick')}

valid_comments = {file.name[:-3]: Path(file).read_text() for file in os.scandir(
                         'comment_cases/valid_comments')}


def test_reddit_auth():
    reddit = utils.get_reddit()
    login_name = reddit.user.me().name
    assert utils.USERNAME.lower() == login_name.lower()


def test_issues_regex():
    # No code block
    for test_text in no_codeblock_cases.values():
        assert NoCodeBlockIssue.check_text(test_text)
    
    for valid_comment in valid_comments.values():
        assert NoCodeBlockIssue.check_text(valid_comment) is None

    # multiple inline
    for test_text in multi_inline_cases.values():
        assert MultipleInlineIssue.check_text(test_text)
    
    for valid_comment in valid_comments.values():
        assert MultipleInlineIssue.check_text(valid_comment) is None
    
    # triple backticks 
    for test_text in triple_backtick_cases.values():
        assert TripleBacktickCodeBlockIssue.check_text(test_text)
    
    for valid_comment in valid_comments.values():
        assert TripleBacktickCodeBlockIssue.check_text(valid_comment) is None
