"""
claudelint - A configurable linter for Claude Code plugins
"""

__version__ = "0.3.2"

from .rule import Rule, RuleViolation, Severity
from .context import RepositoryContext

__all__ = [
    "__version__",
    "Rule",
    "RuleViolation",
    "Severity",
    "RepositoryContext",
]
