import ast
import hashlib
from dataclasses import dataclass, asdict
from typing import List, Dict, Callable, Any

VALIDATOR_VERSION = "5.1.0"

# =======================
# PUBLIC RESULT CONTRACT
# =======================
@dataclass(frozen=True)
class ValidationResult:
    version: str
    status: str
    trust_score: int
    risk_level: str
    readiness: str
    warnings: List[str]
    errors: List[str]
    rollback_required: bool
    metrics: Dict[str, Any]
    categories: Dict[str, List[str]]  # new field for categorized issues

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# =======================
# POLICY DEFINITIONS
# =======================
SECURITY_BANNED_CALLS = {"eval", "exec", "compile", "__import__"}
MAX_REMOVAL_RATIO = 0.6
MIN_AST_NODES = 5

# Mapping keywords in messages to categories (from JSON schema)
ERROR_CATEGORIES = {
    "SyntaxError": "Syntax",
    "IndentationError": "Syntax",
    "Security violation": "Security",
    "Infinite loop risk": "Logic",
    "Bare except": "Reliability",
    "Structural regression": "Stability",
    "AST integrity": "Stability",
    "Undefined variable": "Semantic",
    "Unused variable": "Maintainability"
}


# =======================
# VALIDATOR CORE
# =======================
class CodeValidator:
    """
    Offline, deterministic Python static code validator.
    Categorizes errors and warnings per schema.
    """

    def __init__(self, original_code: str, fixed_code: str):
        self.original = original_code or ""
        self.fixed = fixed_code or ""

        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.metrics: Dict[str, Any] = {}
        self.categories: Dict[str, List[str]] = {cat: [] for cat in set(ERROR_CATEGORIES.values())}

        self._ast_cache: Dict[str, ast.AST] = {}

        self._phases: List[Callable[[], bool]] = [
            self._syntax_phase,
            self._ast_integrity_phase,
            self._structure_diff_phase,
            self._semantic_ast_phase,
            self._security_ast_phase,
            self._stability_phase,
        ]

    # =======================
    # UTILITIES
    # =======================
    def _parse_ast(self, code: str) -> ast.AST:
        if code not in self._ast_cache:
            self._ast_cache[code] = ast.parse(code)
        return self._ast_cache[code]

    def _fingerprint(self, code: str) -> str:
        return hashlib.sha256(code.encode("utf-8")).hexdigest()[:12]

    def _categorize_issue(self, message: str, is_error: bool = True):
        for key, cat in ERROR_CATEGORIES.items():
            if key in message:
                self.categories[cat].append(message)
                break
        else:
            # fallback
            self.categories["Other"] = self.categories.get("Other", [])
            self.categories["Other"].append(message)

    # =======================
    # VALIDATION PHASES
    # =======================
    def _syntax_phase(self) -> bool:
        try:
            self._parse_ast(self.fixed)
            self.metrics["syntax_ok"] = True
            return True
        except (SyntaxError, IndentationError) as e:
            msg = f"{type(e).__name__}: {e}"
            self.errors.append(msg)
            self._categorize_issue(msg)
            self.metrics["syntax_ok"] = False
            return False

    def _ast_integrity_phase(self) -> bool:
        tree = self._parse_ast(self.fixed)
        nodes = list(ast.walk(tree))
        self.metrics["ast_node_count"] = len(nodes)
        if len(nodes) < MIN_AST_NODES:
            msg = "AST integrity failure: code structure too small"
            self.errors.append(msg)
            self._categorize_issue(msg)
            return False
        return True

    def _structure_diff_phase(self) -> bool:
        orig_lines = len(self.original.splitlines())
        fixed_lines = len(self.fixed.splitlines())
        self.metrics.update({
            "original_lines": orig_lines,
            "fixed_lines": fixed_lines
        })

        if orig_lines == 0:
            return True

        removal_ratio = (orig_lines - fixed_lines) / max(orig_lines, 1)
        self.metrics["removal_ratio"] = round(removal_ratio, 2)
        if removal_ratio > MAX_REMOVAL_RATIO:
            msg = "Structural regression: excessive code removal"
            self.errors.append(msg)
            self._categorize_issue(msg)
            return False
        return True

    def _semantic_ast_phase(self) -> bool:
        tree = self._parse_ast(self.fixed)
        for node in ast.walk(tree):
            if isinstance(node, ast.While) and isinstance(node.test, ast.Constant) and node.test.value is True:
                if not any(isinstance(n, ast.Break) for n in ast.walk(node)):
                    msg = "Infinite loop risk: while True without break"
                    self.warnings.append(msg)
                    self._categorize_issue(msg, is_error=False)
            if isinstance(node, ast.ExceptHandler) and node.type is None:
                msg = "Bare except detected"
                self.warnings.append(msg)
                self._categorize_issue(msg, is_error=False)
        return True

    def _security_ast_phase(self) -> bool:
        tree = self._parse_ast(self.fixed)
        ok = True
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in SECURITY_BANNED_CALLS:
                    msg = f"Security violation: use of {node.func.id}()"
                    self.errors.append(msg)
                    self._categorize_issue(msg)
                    ok = False
        return ok

    def _stability_phase(self) -> bool:
        if self.fixed.count("\n") < 2:
            msg = "Very small script – review recommended"
            self.warnings.append(msg)
            self._categorize_issue(msg, is_error=False)
        return True

    # =======================
    # ANALYTICS
    # =======================
    def _risk_level(self) -> str:
        delta = abs(len(self.fixed) - len(self.original)) / max(len(self.original), 1)
        if delta > 0.6: return "CRITICAL"
        if delta > 0.3: return "HIGH"
        if delta > 0.1: return "MEDIUM"
        return "LOW"

    def _trust_score(self, phase_results: List[bool]) -> int:
        score = 100
        score -= phase_results.count(False) * 25
        score -= len(self.errors) * 12
        score -= len(self.warnings) * 6
        return max(score, 0)

    def _readiness(self, trust: int) -> str:
        if trust >= 90: return "Production Ready"
        if trust >= 70: return "Safe to Run"
        if trust >= 50: return "Needs Review"
        return "Unsafe"

    # =======================
    # PUBLIC ENTRY POINT
    # =======================
    def validate(self) -> ValidationResult:
        phase_results: List[bool] = [phase() for phase in self._phases]

        trust = self._trust_score(phase_results)
        risk = self._risk_level()
        readiness = self._readiness(trust)
        rollback_required = trust < 50 or not phase_results[0]

        self.metrics.update({
            "validator_version": VALIDATOR_VERSION,
            "trust_score": trust,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "original_hash": self._fingerprint(self.original),
            "fixed_hash": self._fingerprint(self.fixed),
        })

        return ValidationResult(
            version=VALIDATOR_VERSION,
            status="PASS" if not rollback_required else "FAIL",
            trust_score=trust,
            risk_level=risk,
            readiness=readiness,
            warnings=self.warnings,
            errors=self.errors,
            rollback_required=rollback_required,
            metrics=self.metrics,
            categories=self.categories
        )