import os
from pathlib import Path
import datetime
import logging
import time

import pytest
from loguru import logger
from _pytest.logging import LogCaptureFixture

import utils
from formatbot import get_submission_info, UncheckableSubmission, main
from issues import NoCodeBlockIssue, MultipleInlineIssue, TripleBacktickCodeBlockIssue


SUBMISSION_CASES = Path('submission_cases')


@pytest.fixture
def caplog(caplog: LogCaptureFixture):  # see https://loguru.readthedocs.io/en/stable/resources/migration.html#making-things-work-with-pytest-and-caplog
    handler_id = logger.add(caplog.handler, format="{message}")
    yield caplog
    logger.remove(handler_id)


@pytest.fixture
def reddit_testing(monkeypatch):
    monkeypatch.setattr('utils.SUBREDDIT', 'testingground4bots')
    monkeypatch.setattr('utils.READONLY', False)
    return utils.get_reddit()


@pytest.fixture
def submission_maker(reddit_testing):
    testing_sub = reddit_testing.subreddit('testingground4bots')
    
    def sub_maker(title, text):
        title = 'PyRedditFormatBotTesting - ' + title
        return testing_sub.submit(title=title, selftext=text)
        
    return sub_maker


@pytest.fixture
def submission_getter(reddit_testing):
    def sub_getter(id_):
        return reddit_testing.submission(id=id_)

    return sub_getter
    

def test_reddit_auth(monkeypatch):
    monkeypatch.setattr('utils.READONLY', False)
    reddit = utils.get_reddit()
    assert reddit.read_only is False
    
    monkeypatch.setattr('utils.READONLY', True)
    reddit = utils.get_reddit()
    assert reddit.read_only is True



def test_issues_regex():
    no_codeblock_cases = {file.name[:-3]: Path(file).read_text() for file in 
                      os.scandir(SUBMISSION_CASES / 'NoCodeBlock')}
    multi_inline_cases = {file.name[:-3]: Path(file).read_text() for file in os.scandir(                
                      SUBMISSION_CASES / 'MultipleInline')}
    triple_backtick_cases = {file.name[:-3]: Path(file).read_text() for file in os.scandir(
                         SUBMISSION_CASES / 'TripleBacktick')}

    valid_comments = {file.name[:-3]: Path(file).read_text() for file in os.scandir(
                         SUBMISSION_CASES / 'valid_submissions')}

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


def test_submission_info_getter(submission_getter, submission_maker, monkeypatch):
    me = utils.USERNAME

    new_submission = submission_maker('new submission', 'Test text')
    text = get_submission_info(new_submission, me)
    
    assert text == "Test text"
    
    deleted_sub = submission_getter('tyfvah')
    
    with pytest.raises(UncheckableSubmission):
        text = get_submission_info(deleted_sub, me)

    deleted_account = submission_getter('p0kmw8')

    with pytest.raises(UncheckableSubmission):
        text = get_submission_info(deleted_sub, me)
    
    # make max age to be zero
    
    monkeypatch.setattr('utils.MAX_POST_AGE_DELTA', datetime.timedelta())

    # assert it's no longer happy.
    
    with pytest.raises(UncheckableSubmission):
        text = get_submission_info(new_submission, me)


@pytest.mark.slow
def test_bot_logic(submission_maker, submission_getter, caplog, monkeypatch):
    caplog.set_level(logging.DEBUG)

    # test valid submission
    valid_submission_text = (SUBMISSION_CASES / 'valid_submissions' / 'valid_submission.md').read_text()

    valid_submission = submission_maker('test bot logic valid comment', valid_submission_text)

    main(submission_stream=[valid_submission])
    
    assert any([("No issues found in OP's post" in record.getMessage()) for record in caplog.records])
    
    caplog.clear()

    # test invalid submission

    invalid_submission_text = (SUBMISSION_CASES / 'NoCodeBlock' / 'text_for_loop.md').read_text()
    
    invalid_submission = submission_maker('test bot logic invalid comment', invalid_submission_text)

    main(submission_stream=[invalid_submission])
    
    assert any([("Comment left on OP's post" in record.getMessage()) for record in caplog.records])

    caplog.clear()

    # test not commenting twice

    time.sleep(10)  # oh shit, comment above needs time to appear.
    already_commented_submission = submission_getter(invalid_submission.id)
    
    main(submission_stream=[already_commented_submission])
    
    assert any([("I've already commented on OP's post. Moving on." in record.getMessage()) for record in caplog.records])

    # test comment limit
    

    monkeypatch.setattr('utils.COMMENT_LIMIT', -1)


    main(submission_stream=[invalid_submission, invalid_submission])

