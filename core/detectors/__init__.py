# detectors/__init__.py
# Make detectors a Python package and import all detectors

from .syntax import SyntaxDetector
from .indentation import IndentationDetector
from .undefined_var import UndefinedVarDetector
from .unused_var import UnusedVarDetector
from .duplicate_assign import DuplicateAssignDetector
from .unreachable import UnreachableCodeDetector

# Optional: define __all__ for cleaner imports
__all__ = [
    "SyntaxDetector",
    "IndentationDetector",
    "UndefinedVarDetector",
    "UnusedVarDetector",
    "DuplicateAssignDetector",
    "UnreachableCodeDetector"
]
