import time
from datetime import datetime

import issues
import utils
from utils import botlogger

import logging

handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logger = logging.getLogger('prawcore')
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)


@botlogger.catch
def main():
    botlogger.info('Bot started')
    reddit = utils.get_reddit()
    subreddit = reddit.subreddit(utils.SUBREDDIT)
    me = reddit.user.me().name.lower()
    
    comment_count = 0
    
    for submission in subreddit.stream.submissions():
        op = submission.author.name
    
        if any(comment.author.name.lower() == me for comment in submission.comments):
            botlogger.info(f"I've already commented on {op}'s post. Moving on.")
            continue
            
        time_created = datetime.fromtimestamp(submission.created_utc)
        
        if (datetime.now() - time_created) > utils.MAX_POST_AGE_DELTA:
            botlogger.info('No comment left due to age of post.')
            continue
        
        submission_text = submission.selftext
        
        issues_found = []
        
        for validator in issues.VALIDATORS:
            issue = validator.check_text(submission_text)
            
            if issue:
                issues_found.append(issue)
        
        if not issues_found:
            botlogger.info(f"No issues found in {op}'s post")
            continue
            
        botlogger.info(f"Issues found in {op}'s submission")
        
        for issue in issues_found:
            botlogger.info(issue)
                
        comment = utils.create_comment(op, issues_found)
        
        if not utils.READONLY:
            submission.reply(comment)
        else:
            botlogger.info(f"Would have created comment:\n\n{comment}\n\nbut READONLY={utils.READONLY}")
            
        comment_count += 1

        botlogger.info(f"Comment left on {op}'s post")
    
        time.sleep(10)  # comment cool-down, need karma!
        botlogger.info("Done sleeping for now.")


if __name__ == '__main__':
    main()
