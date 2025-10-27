"""
Main linter orchestration
"""

import importlib.util
import sys
from pathlib import Path
from typing import List, Dict, Type, Tuple

from .rule import Rule, RuleViolation, Severity
from .context import RepositoryContext
from .config import LinterConfig


class ClaudeLinter:
    """
    Main linter that orchestrates rule checking
    """
    
    def __init__(self, context: RepositoryContext, config: LinterConfig = None):
        """
        Initialize linter
        
        Args:
            context: Repository context
            config: Linter configuration (uses default if None)
        """
        self.context = context
        self.config = config or LinterConfig.default()
        self.rules: List[Rule] = []
        self._load_rules()
    
    def _load_rules(self):
        """Load all enabled rules"""
        # Load builtin rules
        self._load_builtin_rules()
        
        # Load custom rules
        for custom_rule_path in self.config.custom_rules:
            try:
                self._load_custom_rule(custom_rule_path)
            except Exception as e:
                print(f"Warning: Failed to load custom rule from {custom_rule_path}: {e}", 
                      file=sys.stderr)
    
    def _load_builtin_rules(self):
        """Load builtin rules from rules/builtin/"""
        try:
            # Import builtin rules - handle both package and script execution
            try:
                from rules.builtin import BUILTIN_RULES
            except ImportError:
                from ..rules.builtin import BUILTIN_RULES
            
            for rule_class in BUILTIN_RULES:
                # Create instance with config
                rule_instance = rule_class(self.config.get_rule_config(rule_class.rule_id))
                
                # Check if enabled for this context
                if self.config.is_rule_enabled(rule_instance.rule_id, self.context):
                    self.rules.append(rule_instance)
        
        except ImportError as e:
            print(f"Warning: Failed to load builtin rules: {e}", file=sys.stderr)
    
    def _load_custom_rule(self, rule_path: str):
        """
        Load a custom rule from a Python file
        
        Args:
            rule_path: Path to Python file containing Rule subclass
        """
        path = Path(rule_path).resolve()
        if not path.exists():
            raise FileNotFoundError(f"Custom rule file not found: {path}")
        
        # Load the module
        spec = importlib.util.spec_from_file_location("custom_rule", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Find Rule subclasses in the module
        for name in dir(module):
            obj = getattr(module, name)
            if (isinstance(obj, type) and 
                issubclass(obj, Rule) and 
                obj is not Rule):
                
                # Create instance
                rule_instance = obj(self.config.get_rule_config(obj.rule_id))
                
                # Check if enabled
                if self.config.is_rule_enabled(rule_instance.rule_id, self.context):
                    self.rules.append(rule_instance)
    
    def run(self) -> List[RuleViolation]:
        """
        Run all enabled rules
        
        Returns:
            List of all violations found
        """
        violations = []
        
        for rule in self.rules:
            try:
                rule_violations = rule.check(self.context)
                violations.extend(rule_violations)
            except Exception as e:
                print(f"Error running rule {rule.rule_id}: {e}", file=sys.stderr)
        
        return violations
    
    def get_counts(self, violations: List[RuleViolation]) -> Tuple[int, int, int]:
        """
        Count violations by severity
        
        Args:
            violations: List of violations
            
        Returns:
            Tuple of (errors, warnings, info)
        """
        errors = sum(1 for v in violations if v.severity == Severity.ERROR)
        warnings = sum(1 for v in violations if v.severity == Severity.WARNING)
        info = sum(1 for v in violations if v.severity == Severity.INFO)
        return errors, warnings, info
    
    def format_results(self, violations: List[RuleViolation], verbose: bool = False) -> str:
        """
        Format violations for display
        
        Args:
            violations: List of violations
            verbose: Show info-level messages
            
        Returns:
            Formatted string
        """
        errors, warnings, info = self.get_counts(violations)
        
        # Group by severity
        errors_list = [v for v in violations if v.severity == Severity.ERROR]
        warnings_list = [v for v in violations if v.severity == Severity.WARNING]
        info_list = [v for v in violations if v.severity == Severity.INFO]
        
        output = []
        
        # Print errors
        if errors_list:
            output.append("\n\033[91m\033[1mErrors:\033[0m")
            for v in errors_list:
                output.append(f"  {v}")
        
        # Print warnings
        if warnings_list:
            output.append("\n\033[93m\033[1mWarnings:\033[0m")
            for v in warnings_list:
                output.append(f"  {v}")
        
        # Print info (only in verbose)
        if verbose and info_list:
            output.append("\n\033[94m\033[1mInfo:\033[0m")
            for v in info_list:
                output.append(f"  {v}")
        
        # Summary
        output.append("\n\033[1mSummary:\033[0m")
        output.append(f"  \033[91mErrors:   {errors}\033[0m")
        output.append(f"  \033[93mWarnings: {warnings}\033[0m")
        if verbose:
            output.append(f"  \033[94mInfo:     {info}\033[0m")
        
        if errors == 0 and warnings == 0:
            output.append("\n\033[92m\033[1m✓ All checks passed!\033[0m")
        
        return "\n".join(output)

