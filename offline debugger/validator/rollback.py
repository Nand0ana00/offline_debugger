import logging
from typing import List, Dict

# ------------------------
# Logging Setup (deduplicated)
# ------------------------
logger = logging.getLogger("RollbackManager")
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    ch = logging.StreamHandler()
    formatter = logging.Formatter("[%(levelname)s] %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)


class RollbackManager:
    """
    Handles rollback recommendations and tracks rollback history.

    Improvements:
    ✔ Deduplicated logging
    ✔ Optional in-memory rollback cache
    """

    _rollback_cache: Dict[str, bool] = {}  # Tracks if rollback recommended per code hash

    def __init__(self):
        self.history: List[Dict[str, str]] = []

    def recommend(self, code_hash: str, reason: str) -> bool:
        """
        Determine if rollback is recommended.
        Caches decisions for repeated checks.
        """
        if code_hash in RollbackManager._rollback_cache:
            logger.info(f"Rollback decision retrieved from cache for {code_hash}")
            return RollbackManager._rollback_cache[code_hash]

        logger.warning(f"Rollback recommended for {code_hash}: {reason}")
        RollbackManager._rollback_cache[code_hash] = True
        self.history.append({"code_hash": code_hash, "reason": reason})
        return True

    def get_history(self) -> List[Dict[str, str]]:
        """Return all recorded rollback decisions."""
        return self.history