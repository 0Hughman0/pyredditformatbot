import re
from utils import botlogger

class _BaseIssue:
    _pattern = None
    _description = None
    
    def __init__(self, text):
        self.text = text
    
    @classmethod
    def check_text(cls, text):
        if cls._pattern.search(text):
            return cls(text)
        return None

    def __str__(self):
        return self._description


class MultipleInlineIssue(_BaseIssue):
    _description = "Inline formatting (`` `my code` ``) used across multiple lines of code. This can mess with indentation."
    _pattern = re.compile(r'(?:\s*?`.*?`\s*?[\n]+){2,}', re.MULTILINE)
    
    
class TripleBacktickCodeBlockIssue(_BaseIssue):
    _description = "Use of triple backtick/ curlywhirly code blocks (` ``` ` ) or (`~~~`). These may not render correctly on all Reddit clients."
    _pattern = re.compile(r'^(```(?:[^`]*?\n){3,}?```|~~~(?:[^~]*?\n){3,}?~~~)', re.MULTILINE)  # turns out reddit actually sometimes renders ```code``` correctly!



class NoCodeBlockIssue(_BaseIssue):
    _description = "Python code found in submission text that's not formatted as code."
    _pattern = re.compile(r'''
        ^(?:                        # any of the following is on the left-hand margin (not four spaces in)
            try                     # try block
            |class\s.*?             # class detection
            |def\s.*?\(.*?\)        # function detection
            |for\s.*?\sin\s.*?      # for loop detection
            |while\s.*?             # while loop detection
            |if\s.*?                # if block detection
            |with\s.*?              # with block detection
            |match\s.*?             # match block detection
        ):                          # END NON-CAPTURE GROUP -- literal colon
        ''', re.VERBOSE | re.MULTILINE)


VALIDATORS = [MultipleInlineIssue, NoCodeBlockIssue, TripleBacktickCodeBlockIssue]
