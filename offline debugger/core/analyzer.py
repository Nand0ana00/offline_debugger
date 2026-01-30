import ast
from core.detectors import (
    SyntaxDetector,
    IndentationDetector,
    UndefinedVarDetector,
    UnusedVarDetector,
    DuplicateAssignDetector,
    UnreachableCodeDetector
)

class Analyzer:
    """
    Core Analyzer Engine
    - Parses code with AST
    - Runs all detectors
    - Returns a structured list of issues
    """

    def __init__(self, code):
        self.code = code
        self.tree = None
        self.issues = []

    # -------------------------------------------------
    # Step 1: Parse code into AST
    # -------------------------------------------------
    def parse(self):
        try:
            self.tree = ast.parse(self.code)
            return True
        except SyntaxError as e:
            # Run SyntaxDetector if parse fails
            syntax_issues = SyntaxDetector(self.code).run()
            self.issues.extend(syntax_issues)
            return False

    # -------------------------------------------------
    # Step 2: Run all detectors
    # -------------------------------------------------
    def run_detectors(self):
        if not self.tree:
            return

        detectors = [
            UndefinedVarDetector(self.tree),
            UnusedVarDetector(self.tree),
            DuplicateAssignDetector(self.tree),
            UnreachableCodeDetector(self.tree),
            IndentationDetector(self.code)
        ]

        for detector in detectors:
            self.issues.extend(detector.run())

    # -------------------------------------------------
    # Step 3: Main API
    # -------------------------------------------------
    def analyze(self):
        """
        Analyze the code and return all issues
        """
        if self.parse():
            self.run_detectors()
        return self.issues


# -------------------------------------------------
# Quick test (standalone)
# -------------------------------------------------
if __name__ == "__main__":
    sample_code = """
x = 10
y = 0
print(z)  # undefined
x = 5    # duplicate
while True:
    print(x / y)  # runtime risk (division by zero)
def func(a, b, c, d, e, f, g):
    pass
"""
    analyzer = Analyzer(sample_code)
    results = analyzer.analyze()
    for issue in results:
        print(issue)
