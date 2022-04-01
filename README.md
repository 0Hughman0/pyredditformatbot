# pyredditformatbot
A bot to show noobs the errors of their ways.

```
> git clone https://github.com/0Hughman0/pyredditformatbot
> cd pyredditformatbot
> pipenv install
> pipenv run python formatbot.py
```

Configuration (via environment variables):


| Name                   | Meaning                                                                                                           | Example                          | Default                         |
|------------------------|-------------------------------------------------------------------------------------------------------------------|----------------------------------|---------------------------------|
| `REDDIT_USERNAME`      | The bot's Reddit username                                                                                         | `"MrBotters"`                    |                                 |
| `REDDIT_PASSWORD`      | The bot's Reddit password                                                                                         | `"I love Mrs Botters"`           |                                 |
| `REDDIT_CLIENT_SECRET` | Your bot's [OAuth Client Secret](https://praw.readthedocs.io/en/stable/getting_started/authentication.html#oauth) | `"XYZABCDEFGHI..."`              |                                 |
| `REDDIT_USER_AGENT`    | [A suitable user agent](https://github.com/reddit-archive/reddit/wiki/API#rules) for your bot                     | `"Python:MyBot:0.1 (by u/MrMe)"` |                                 |
| `SUBREDDIT`            | The subreddit this bot comments in.                                                                               | `"learnpython"`                  |                                 |
| `MAX_POST_AGE_MINS`    | If the bot finds comments older than this age, it'll ignore them                                                  | `45`                             | `30`                            |
| `COMMENT_LIMIT`        | For testing. Will make this many posts before stopping.                                                           | `25`                             | `-1` (Interpreted as no limit!) |
| `DEBUG`                | Run program in Debug mode. Improves logging.                                                                      | `True`                           | `False`                         |
| `READONLY`             | Run program in read-only mode i.e. it won't actually post any comments.                                           | `False`                          | `False`                         |

The comment posted can be edited by changing the `comment.tmplt.md` file.

Based on the dormant project found [here](https://github.com/nicker-bocker/pyredditformatbot)
