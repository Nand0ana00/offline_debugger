import ast

class SyntaxDetector:
    """
    Detects syntax errors like missing colons, unmatched parentheses
    """
    def __init__(self, code):
        self.code = code
        self.issues = []

    def run(self):
        try:
            ast.parse(self.code)
        except SyntaxError as e:
            msg = e.msg
            err_type = "SyntaxError"
            if "expected ':'" in msg:
                err_type = "MissingColon"
            elif "unexpected indent" in msg:
                err_type = "IndentationError"
            self.issues.append({
                "type": err_type,
                "message": msg,
                "line": e.lineno,
                "column": e.offset
            })
        return self.issues
