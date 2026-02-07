import os

class RepoLoader:
    def __init__(self, repo_path):
        self.repo_path = repo_path

    def load_python_files(self):
        python_files = []

        for root, dirs, files in os.walk(self.repo_path):
            # Skip unnecessary directories
            dirs[:] = [d for d in dirs if d not in ("__pycache__", ".git")]

            for file in files:
                if file.endswith(".py"):
                    python_files.append(os.path.join(root, file))

        return python_files

