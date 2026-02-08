class IndentationDetector:
    """
    Detects improper indentation by scanning code line by line
    """
    def __init__(self, code):
        self.code = code
        self.issues = []

    def run(self):
        stack = [0]  # Indentation levels
        lines = self.code.split("\n")

        for lineno, line in enumerate(lines, start=1):
            stripped = line.lstrip()
            if not stripped:
                continue  # skip empty lines
            indent = len(line) - len(stripped)
            if indent > stack[-1] + 4:
                self.issues.append({
                    "type": "IndentationError",
                    "message": "Unexpected indentation",
                    "line": lineno
                })
            if indent > stack[-1]:
                stack.append(indent)
            elif indent < stack[-1]:
                while stack and indent < stack[-1]:
                    stack.pop()
        return self.issues
