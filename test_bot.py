import os
from pathlib import Path
import datetime

import pytest
import utils
from formatbot import get_submission_info, UncheckableSubmission
from issues import NoCodeBlockIssue, MultipleInlineIssue, TripleBacktickCodeBlockIssue


@pytest.fixture
def reddit_testing(monkeypatch):
    monkeypatch.setenv('SUBREDDIT', 'testingground4bots')
    return utils.get_reddit()


@pytest.fixture
def comment_maker(reddit_testing):
    testing_sub = reddit_testing.subreddit('testingground4bots')
    
    def comment_maker(title, text):
        title = 'PyRedditFormatBotTesting - ' + title
        return testing_sub.submit(title=title, selftext=text)
        
    return comment_maker


@pytest.fixture
def comment_getter(reddit_testing):
    def comment_getter(id_):
        return reddit_testing.submission(id=id_)

    return comment_getter
    

def test_reddit_auth():
    reddit = utils.get_reddit()
    login_name = reddit.user.me().name
    assert utils.USERNAME.lower() == login_name.lower()


def test_issues_regex():
    no_codeblock_cases = {file.name[:-3]: Path(file).read_text() for file in 
                      os.scandir('comment_cases/NoCodeBlock')}
    multi_inline_cases = {file.name[:-3]: Path(file).read_text() for file in os.scandir(                
                      'comment_cases/MultipleInline')}
    triple_backtick_cases = {file.name[:-3]: Path(file).read_text() for file in os.scandir(
                         'comment_cases/TripleBacktick')}

    valid_comments = {file.name[:-3]: Path(file).read_text() for file in os.scandir(
                         'comment_cases/valid_comments')}

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


def test_submission_info_getter(comment_getter, comment_maker, monkeypatch):
    me = utils.USERNAME
    normal_submission = comment_getter('tyfrrt')
    
    text, op = get_submission_info(normal_submission, me)
    
    assert text == "Test text"
    assert op == me
    
    deleted_sub = comment_getter('tyfvah')
    
    with pytest.raises(UncheckableSubmission):
        text, op = get_submission_info(deleted_sub, me)

    deleted_account = comment_getter('p0kmw8')

    with pytest.raises(UncheckableSubmission):
        text, op = get_submission_info(deleted_sub, me)

    # make a new submission and validate

    new_submission = comment_maker('new submission', 'Test text')

    text, op = get_submission_info(new_submission, me)

    assert text == "Test text"
    assert op == me

    # make max age to be zero
    
    monkeypatch.setattr('utils.MAX_POST_AGE_DELTA', datetime.timedelta())

    # assert it's no longer happy.
    
    with pytest.raises(UncheckableSubmission):
        text, op = get_submission_info(new_submission, me)

