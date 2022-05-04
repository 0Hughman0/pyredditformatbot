import ast
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
    _description = "Use of triple backtick/ curlywhirly code blocks (```` ``` ```` or `~~~`). These may not render correctly on all Reddit clients."
    _pattern = re.compile(r'^(```(?:[^`]*?\n){3,}?```|~~~(?:[^~]*?\n){3,}?~~~)', re.MULTILINE)  # turns out reddit actually sometimes renders ```code``` correctly!



class NoCodeBlockIssue(_BaseIssue):
    _description = "Python code found in submission text that's not formatted as code."
    
    @classmethod
    def check_text(cls, text):
    
        ilines = iter(text.splitlines())
        
        for line in ilines:
            if not line:
                continue
                            
            found_block = False
            
            try:
                tree = ast.parse(line)
            except IndentationError as e:  # must be in this order because IndentationError is a subclass of SyntaxError!
                if e.msg == 'expected an indented block':
                    found_block = True
            except SyntaxError as e:
                if e.msg == 'unexpected EOF while parsing':  
                    found_block = True# indented code.
            
            if found_block:                    
                next_line = next(ilines)
                
                while not next_line:
                    next_line = next(ilines) # ensures next line with content
                
                try:
                    ast.parse(next_line)
                except IndentationError:
                    return cls(text) # was probably code
                except SyntaxError:
                    continue

        return None


VALIDATORS = [MultipleInlineIssue, NoCodeBlockIssue, TripleBacktickCodeBlockIssue]
