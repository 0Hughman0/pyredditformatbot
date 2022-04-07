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


def get_submission_info(submission, me):
    if submission.author is None:
        raise UncheckableSubmission("OP seems to have deleted account, skipping")

    op = submission.author.name

    if any(comment.author.name.lower() == me for comment in submission.comments if comment.author):  # comment.author needed because people delete their accounts!
        raise UncheckableSubmission(f"I've already commented on {op}'s post. Moving on.")
        
    time_created = datetime.fromtimestamp(submission.created_utc)

    if (datetime.now() - time_created) > utils.MAX_POST_AGE_DELTA:
        raise UncheckableSubmission('No comment left due to age of post.')

    submission_text = submission.selftext

    if submission_text is None:  # might not be possible
        raise UncheckableSubmission("OP seems to have deleted post, skipping")
        
    return submission_text, op
    
    
def get_issues(submission_text):
    issues_found = []

    for validator in issues.VALIDATORS:
        issue = validator.check_text(submission_text)
        
        if issue:
            issues_found.append(issue)
    
    return issues_found


@botlogger.catch
def main():
    botlogger.info('Bot started')
    reddit = utils.get_reddit()
    subreddit = reddit.subreddit(utils.SUBREDDIT)
    me = reddit.user.me().name.lower()
    
    comment_count = 0
    
    for submission in subreddit.stream.submissions():
        botlogger.debug(f"Checking submission {submission}")
        
        try:
            submission_text, op = get_submission_info(submission, me)
        except UncheckableSubmission as error:
            botlogger.debug(error)
            continue

        botlogger.debug(f"Checking post text:\n\n{submission_text}")
        
        issues_found = get_issues(submission_text)
                    
        if not issues_found:
            botlogger.debug(f"No issues found in {op}'s post")
            continue
            
        botlogger.info(f"Issues found in {op}'s submission")
        
        for issue in issues_found:
            botlogger.info(issue)
    
        comment = utils.create_comment(op, issues_found)

        if not utils.READONLY:
            submission.reply(comment)
        else:
            botlogger.debug(f"Would have created comment:\n\n{comment}\n\nbut READONLY={utils.READONLY}")
        
        comment_count += 1

        botlogger.info(f"Comment left on {op}'s post")

        if (utils.COMMENT_LIMIT != -1) and (comment_count >= utils.COMMENT_LIMIT):
            botlogger.debug(f"Reached comment limit, heading to bed")
            break


if __name__ == '__main__':
    main()
