import time
from datetime import datetime

import issues
import utils
from utils import botlogger

import logging

handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG if utils.DEBUG else logging.INFO)
logger = logging.getLogger('prawcore')
logger.setLevel(logging.DEBUG if utils.DEBUG else logging.INFO)
logger.addHandler(handler)


class UncheckableSubmission(Exception):
    pass

class NoIssuesFound(Exception):
    pass


def get_submission_info(submission, me):
    if submission.author is None:
        raise UncheckableSubmission("OP seems to have deleted account, skipping")    

    if any((comment.author.name == me) for comment in submission.comments if comment.author):  # comment.author needed because people delete their accounts!
        raise UncheckableSubmission("I've already commented on OP's post. Moving on.")
    
    time_created = datetime.fromtimestamp(submission.created_utc)

    if (datetime.now() - time_created) > utils.MAX_POST_AGE_DELTA:
        raise UncheckableSubmission("No comment left due to age of post.")

    submission_text = submission.selftext

    if submission_text is None:  # might not be possible
        raise UncheckableSubmission("OP seems to have deleted post, skipping")
        
    return submission_text
    
    
def get_issues(submission_text):
    issues_found = []

    for validator in issues.VALIDATORS:
        issue = validator.check_text(submission_text)
        
        if issue:
            issues_found.append(issue)
    
    return issues_found


def check_submission_text(submission_text):
    issues_found = get_issues(submission_text)
                
    if not issues_found:
        raise NoIssuesFound("No issues found in OP's post")

    return issues_found
    

@botlogger.catch
def main(submission_stream=None):
    botlogger.info('Bot started')
    reddit = utils.get_reddit()
    subreddit = reddit.subreddit(utils.SUBREDDIT)
    me = utils.USERNAME
    
    comment_count = 0

    if submission_stream is None:
        submission_stream = subreddit.stream.submissions()
    
    for submission in submission_stream:
        botlogger.info(f"Checking submission {submission}")
        try:
            submission_text = get_submission_info(submission, me)

            botlogger.debug(f"Checking post text:\n\n{submission_text}")
            
            issues_found = check_submission_text(submission_text)

            for issue in issues_found:
                botlogger.debug(f"Issue found in OPs post: {issue}")

            comment = utils.create_comment(issues_found)
            submission.reply(comment)

        except (UncheckableSubmission, NoIssuesFound) as error:
            botlogger.debug(error)
            continue

        botlogger.info(f"Comment left on OP's post")
        
        comment_count += 1

        if (utils.COMMENT_LIMIT != -1) and (comment_count >= utils.COMMENT_LIMIT):
            botlogger.debug("Reached comment limit, heading to bed")
            break


if __name__ == '__main__':
    main()
