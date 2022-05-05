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
    code_line_count_thresh = 3
    
    @classmethod
    def check_text(cls, text):
        """
        Bot triggers if it finds valid python code that's 3 lines long... 
        
        or if it finds some sort of code that requires the next line to be indented e.g. if statement.
        
        """
    
        ilines = iter(text.splitlines())
        
        valid_code_line_count = 0

        for line in ilines:
            if not line or line.isspace():
                continue
                            
            found_block = False
            
            try:
                tree = ast.parse(line)
                valid_code_line_count += 1
            except IndentationError as e:  # must be in this order because IndentationError is a subclass of SyntaxError!
                if e.msg == 'expected an indented block':
                    found_block = True
                else:
                    valid_code_line_count = 0
            except SyntaxError as e:
                if e.msg == 'unexpected EOF while parsing':  
                    found_block = True# indented code.
                else:
                    valid_code_line_count = 0
            
            if found_block:                    
                next_line = next(ilines)
                
                while not next_line:
                    next_line = next(ilines) # ensures next line with content
                
                try:
                    ast.parse(next_line)
                    valid_code_line_count += 1
                except IndentationError:
                    return cls(text) # was probably code
                except SyntaxError:
                    valid_code_line_count = 0
                    continue
                    
            if valid_code_line_count >= cls.code_line_count_thresh:
                return cls(text)  # suffiencently long line of valid python code.

        return None


VALIDATORS = [MultipleInlineIssue, NoCodeBlockIssue, TripleBacktickCodeBlockIssue]
