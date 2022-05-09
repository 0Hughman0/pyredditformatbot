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


def iter_clean_lines(ilines):
    for line in ilines:
        if not line or line.isspace():
            continue
        else:
            yield line


def is_code(text):
    try:
        tree = ast.parse(text)
        return tree
    except IndentationError as e:  # must be in this order because IndentationError is a subclass of SyntaxError!
        if e.msg == 'expected an indented block':
            return True
    except SyntaxError as e:
        if e.msg == 'unexpected EOF while parsing':  
            return True
    
    return False


class NoCodeBlockIssue(_BaseIssue):
    _description = "Python code found in submission text that's not formatted as code."
    code_line_count_thresh = 3
    
    indented_nodes = (ast.FunctionDef, 
                      ast.AsyncFunctionDef, 
                      ast.ClassDef, 
                      ast.For,
                      ast.AsyncFor,
                      ast.While,
                      ast.If,
                      ast.With,
                      ast.AsyncWith,
                      ast.Try)
    
    @classmethod
    def check_text(cls, text):
        """
        Bot triggers if it finds valid python code that's code_line_count_thresh lines long... 
        
        or if it finds some sort of code that requires the next line to be indented e.g. if statement.
        
        """
    
        ilines = iter(text.splitlines())
        
        valid_code_line_count = 0

        i_clean_lines = iter_clean_lines(ilines)
        for line in i_clean_lines:
            if not is_code(line):
                continue
            
            block = [line]
            
            for i in range(cls.code_line_count_thresh - 1):  # -1 cuz additional lines to [line]
                try:
                    next_line = next(i_clean_lines)
                except StopIteration: # end of text
                    break
                
                block.append(next_line)  # build up block
                
                tree = is_code('\n'.join(block))
                
                if not tree: # invalid code
                    break
                elif isinstance(tree, bool):  # new line is probably incomplete statement
                    continue
                elif any(isinstance(node, cls.indented_nodes) for node in tree.body):
                    return cls(text) # code is valid ill-formatted and indented, must fix!
                
            else:
                return cls(text) # sufficiently long block of ill-formatted code.

        return None


VALIDATORS = [MultipleInlineIssue, NoCodeBlockIssue, TripleBacktickCodeBlockIssue]
