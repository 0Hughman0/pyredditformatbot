import pytest
import utils
from formatbot import *
from issues import *


text_multi_inline = '''
`x = 1`
`def func(p, n):`
    `pass`
'''

text_split_multiinline = '''
`x = 1`

Then a bit of text

`def func(p, n)`

This is fine.
'''


text_def = '''
x = 1
def func(p, n):
    pass

'''


text_try = '''
Pls hLP my codes!!!
try:
x = "FrEe homEwork Hlp"
except:
pass
'''


text_class = '''
x = 1
class MyClass:
    pass

'''


text_def = '''
Test post

def my_func():
    print("isn't indented")

ok
'''


text_for_loop = '''
Here is my issue 

for x, y, z in collection:
   print(x, y, z)
   
'''


text_while = '''
Test post

while True:
    print("isn't indented")

ok
'''


text_if = '''
Test post

if True:
    print("isn't indented")

ok
'''


text_with = '''
Test post

with open('some.txt') as fs:
    print("isn't indented")

ok
'''

text_match = '''
Test post

match 'I don't know the syntax!':
    print("isn't indented")

ok
'''

text_proper = '''
for tricking regex:
    def func(p):
        pass
    class MyClass:
        pass
    for x in y:
        pass
    try:
        x = True
    except:
        pass
'''


def test_reddit_auth():
    reddit = utils.get_reddit()
    login_name = reddit.user.me().name
    assert utils.USERNAME.lower() == login_name.lower()


def test_issues_regex():
    issue_block = NoCodeBlockIssue

    for test_text in [text_try, 
                      text_def, 
                      text_for_loop,
                      text_while,
                      text_if,
                      text_with,
                      text_match]:
        assert issue_block.check_text(test_text)
    
    assert not issue_block.check_text(text_proper)
    
    issue_inline = MultipleInlineIssue
    assert issue_inline.check_text(text_multi_inline)
    
    assert not issue_inline.check_text(text_proper)
    assert not issue_inline.check_text(text_split_multiinline)

