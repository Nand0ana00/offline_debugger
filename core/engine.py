from core.repo_loader import RepoLoader
from core.analyzer import Analyzer
from fixer.fix_agent import FixAgent
from validator.validator import ValidationResult

import sys
class DebuggerEngine:
    """
    Integration Engine
    - Loads repo files
    - Runs Analyzer on each file
    - Aggregates all issues
    """

    SEVERITY_MAP = {
        "SyntaxError": "HIGH",
        "IndentationError": "HIGH",
        "UndefinedVariable": "HIGH",
        "UnusedVariable": "LOW",
        "DuplicateAssignment": "MEDIUM",
        "UnreachableCode": "MEDIUM",
    }

    def __init__(self, repo_path="."):
        self.repo_path = repo_path
        self.loader = RepoLoader(repo_path)

    def run(self):
        all_issues = []
        files = self.loader.load_python_files()

        for file_path in files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    code = f.read()

                analyzer = Analyzer(code)
                issues = analyzer.analyze()

                for issue in issues:
                    issue["file"] = file_path
                    issue["severity"] = self.SEVERITY_MAP.get(
                        issue.get("type"), "LOW"
                    )

                all_issues.extend(issues)

            except Exception as e:
                all_issues.append({
                    "type": "EngineError",
                    "file": file_path,
                    "message": str(e),
                    "severity": "HIGH"
                })

        return all_issues


if __name__ == "__main__":
    # default path
    repo_path = "."

    # if path is provided from terminal
    if len(sys.argv) > 1:
        repo_path = sys.argv[1]

    engine = DebuggerEngine(repo_path)
    issues = engine.run()

    print("=== DEBUGGER RESULTS ===")
    for issue in issues:
        print(f"\n[{issue['severity']}] {issue['type']}")
        print(f"File: {issue['file']}")
        print(f"Line: {issue.get('line', '-')}")
        print(f"Message: {issue['message']}")


