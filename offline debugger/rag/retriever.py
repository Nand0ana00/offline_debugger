import json
from pathlib import Path
from typing import Optional, Dict, Any, List
import logging

# ------------------------
# Logging Setup (deduplicated)
# ------------------------
logger = logging.getLogger("Retriever")
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    ch = logging.StreamHandler()
    formatter = logging.Formatter("[%(levelname)s] %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)


class KnowledgeRetriever:
    """
    Loads and retrieves static knowledge about code issues
    from a JSON file for offline code validation.

    Improvements:
    ✔ Deduplicated logging
    ✔ Cached JSON data in memory
    """

    _json_cache: Optional[Dict[str, Dict[str, Any]]] = None  # class-level cache

    def __init__(self, path: Optional[str] = None):
        """
        Initialize retriever with JSON path.
        Defaults to 'knowledge.json' in same directory.
        """
        self.path = Path(path) if path else Path(__file__).parent / "knowledge.json"
        self.db: Dict[str, Dict[str, Any]] = {}
        self._load()

    def _load(self):
        # Use class-level cache if already loaded
        if KnowledgeRetriever._json_cache:
            self.db = KnowledgeRetriever._json_cache
            logger.info(f"Knowledge database loaded from cache: {len(self.db)} entries")
            return

        if not self.path.exists():
            logger.error(f"Knowledge file not found at: {self.path}")
            raise FileNotFoundError(f"Knowledge file not found: {self.path}")
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                self.db = json.load(f)
            KnowledgeRetriever._json_cache = self.db  # cache it
            logger.info(f"Knowledge database loaded: {len(self.db)} entries")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            raise

    def get(self, issue_key: str) -> Optional[Dict[str, Any]]:
        """Retrieve issue metadata by key (e.g., 'SyntaxError')."""
        return self.db.get(issue_key)

    def all_keys(self) -> List[str]:
        """Return all issue keys in the knowledge base."""
        return list(self.db.keys())

    def search_by_category(self, category: str) -> Dict[str, Dict[str, Any]]:
        """Return all issues matching a given category (e.g., 'Security')."""
        return {k: v for k, v in self.db.items() if v.get("category") == category}

    def get_explanations(self, issues: List[str]) -> Dict[str, str]:
        """
        Return human-readable short explanations for a list of detected issues.
        """
        explanations = {}
        for issue in issues:
            data = self.db.get(issue)
            if data:
                explanations[issue] = data.get("explanation", {}).get("short", "No explanation available")
            else:
                explanations[issue] = "Unknown issue"
        return explanations