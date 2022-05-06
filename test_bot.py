import os
from pathlib import Path
import datetime
import logging
import time
from unittest.mock import Mock

import pytest
from loguru import logger
from _pytest.logging import LogCaptureFixture

import utils
from formatbot import get_submission_info, UncheckableSubmission, main
from issues import VALIDATORS


SUBMISSION_CASES = Path('submission_cases')    


@pytest.fixture
def caplog(caplog: LogCaptureFixture):  # see https://loguru.readthedocs.io/en/stable/resources/migration.html#making-things-work-with-pytest-and-caplog
    handler_id = logger.add(caplog.handler, format="{message}")
    yield caplog
    logger.remove(handler_id)


@pytest.fixture
def mock_reddit(monkeypatch):
    reddit = utils.get_reddit()
    reddit.read_only = True
    reddit._mock_submissions = {}
    
    def mock_submission_getter(id):
        return reddit._mock_submissions[id]
    
    reddit.submission = Mock()
    reddit.submission.side_effect = mock_submission_getter
    
    return reddit


@pytest.fixture
def submission_maker(mock_reddit):
    
    def sub_maker(title, text):
        title = 'PyRedditFormatBotTesting - ' + title
        
        mock_sub = Mock()
        mock_sub.title = title
        mock_sub.selftext = text
        mock_sub.created_utc = datetime.datetime.now().timestamp()
        mock_sub.comments = []
        
        def save_reply(reply):
            mock_reply = Mock()
            mock_reply.author.name = utils.USERNAME
            mock_sub.comments.append(mock_reply)
        
        mock_sub.reply.side_effect = save_reply
        
        mock_reddit._mock_submissions[mock_sub] = mock_sub
        
        return mock_sub
        
    return sub_maker


@pytest.fixture
def submission_getter(mock_reddit):
    def sub_getter(id_):
        return mock_reddit.submission(id=id_)

    return sub_getter
    
    
@pytest.fixture(params=VALIDATORS)
def validator_test_cases(request):
    validator = request.param
    return validator, {file.name[:-3]: Path(file).read_text() for file in 
                      os.scandir(SUBMISSION_CASES / validator.__name__)}
    

def test_reddit_auth(monkeypatch):
    monkeypatch.setattr('utils.READONLY', False)
    reddit = utils.get_reddit()
    assert reddit.read_only is False
    
    monkeypatch.setattr('utils.READONLY', True)
    reddit = utils.get_reddit()
    assert reddit.read_only is True


def test_validators(validator_test_cases):
    validator, validator_test_cases = validator_test_cases

    valid_comments = {file.name[:-3]: Path(file).read_text(encoding='utf-8') for file in os.scandir(
                         SUBMISSION_CASES / 'valid_submissions')}
                         
    # No code block
    for test_text in validator_test_cases.values():
        assert validator.check_text(test_text)
    
    for valid_comment in valid_comments.values():
        assert validator.check_text(valid_comment) is None


def test_submission_info_getter(submission_getter, submission_maker, monkeypatch):
    me = utils.USERNAME

    new_submission = submission_maker('new submission', 'Test text')
    text = get_submission_info(new_submission, me)
    
    assert text == "Test text"
    
    deleted_sub = submission_maker('deleted sub', None)
    deleted_sub.author = None
    
    with pytest.raises(UncheckableSubmission):
        text = get_submission_info(deleted_sub, me)

    deleted_account = submission_maker('deleted account', 'some text')

    with pytest.raises(UncheckableSubmission):
        text = get_submission_info(deleted_sub, me)
    
    # make max age too old
    
    new_submission.created_utc -= (2 * utils.MAX_POST_AGE_DELTA).total_seconds()

    # assert it's no longer happy.
    
    with pytest.raises(UncheckableSubmission):
        text = get_submission_info(new_submission, me)


def test_bot_valid_submission(submission_maker, submission_getter):
    valid_submission_text = (SUBMISSION_CASES / 'valid_submissions' / 'valid_submission.md').read_text()
    valid_submission = submission_maker('test bot logic valid comment', valid_submission_text)

    main(submission_stream=[valid_submission])
    
    assert not valid_submission.reply.called
    

def test_bot_invalid_submission(submission_maker, submission_getter):
    invalid_submission_text = (SUBMISSION_CASES / 'NoCodeBlockIssue' / 'text_for_loop.md').read_text()
    invalid_submission = submission_maker('test bot logic invalid comment', invalid_submission_text)

    main(submission_stream=[invalid_submission])
    
    assert invalid_submission.reply.called


def test_bot_comment_once(submission_maker, submission_getter, caplog):
    # test not commenting twice

    invalid_submission_text = (SUBMISSION_CASES / 'NoCodeBlockIssue' / 'text_for_loop.md').read_text()
    invalid_submission = submission_maker('test bot logic invalid comment', invalid_submission_text)
    
    main(submission_stream=[invalid_submission])

    main(submission_stream=[invalid_submission])
    
    assert invalid_submission.reply.call_count == 1
    assert any([("I've already commented on OP's post. Moving on." in record.getMessage()) for record in caplog.records])


def test_bot_comment_limit(submission_maker, submission_getter, caplog, monkeypatch):
    # test comment limit, unlimited
    monkeypatch.setattr('utils.COMMENT_LIMIT', -1)
    
    invalid_submission_text = (SUBMISSION_CASES / 'NoCodeBlockIssue' / 'text_for_loop.md').read_text()
    invalid_submission = submission_maker('test bot logic invalid comment', invalid_submission_text)
    extra_submission = submission_maker('test bot logic invalid comment', invalid_submission_text)

    main(submission_stream=[invalid_submission, extra_submission])

    assert extra_submission.reply.called
    
    extra_submission.comments.clear() # remove replies
    invalid_submission.comments.clear() # remove replies
    extra_submission.reply.reset_mock() # forget it's been replied to above
    
    monkeypatch.setattr('utils.COMMENT_LIMIT', 1)
    
    main(submission_stream=[invalid_submission, extra_submission])
    
    assert not extra_submission.reply.called
    