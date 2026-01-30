# fixer/__init__.py

from .auto_fixer import apply_all_fixes
from .fix_agent import FixAgent

# This defines what is "public" when someone imports your folder
__all__ = ['apply_all_fixes', 'FixAgent']