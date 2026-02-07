from core.repo_loader import RepoLoader
from core.analyzer import Analyzer

class DebuggerEngine:
    """
    Integration Engine
    - Loads repo files
    - Runs Analyzer on each file
    - Aggregates all issues
    """

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

                all_issues.extend(issues)

            except Exception as e:
                all_issues.append({
                    "type": "EngineError",
                    "file": file_path,
                    "message": str(e)
                })

        return all_issues

