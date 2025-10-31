"""
Configuration management for claudelint
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List, TYPE_CHECKING
from dataclasses import dataclass, field

if TYPE_CHECKING:
    from .context import RepositoryContext


@dataclass
class LinterConfig:
    """Configuration for the linter"""

    rules: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    custom_rules: List[str] = field(default_factory=list)
    exclude_patterns: List[str] = field(default_factory=list)
    strict: bool = False
    plugin_directories: List[str] = field(
        default_factory=lambda: ["plugins", ".claude/plugins", ".claude-plugin/plugins"]
    )

    @classmethod
    def from_file(cls, config_path: Path) -> "LinterConfig":
        """
        Load configuration from a .claudelint.yaml file

        Args:
            config_path: Path to configuration file

        Returns:
            LinterConfig instance
        """
        if not config_path.exists():
            return cls()

        try:
            with open(config_path, "r") as f:
                data = yaml.safe_load(f) or {}
        except (yaml.YAMLError, IOError) as e:
            raise ValueError(f"Failed to load config from {config_path}: {e}")

        return cls(
            rules=data.get("rules", {}),
            custom_rules=data.get("custom-rules", []),
            exclude_patterns=data.get("exclude", []),
            strict=data.get("strict", False),
            plugin_directories=data.get(
                "plugin-directories", ["plugins", ".claude/plugins", ".claude-plugin/plugins"]
            ),
        )

    @classmethod
    def default(cls) -> "LinterConfig":
        """Create default configuration with all builtin rules enabled"""
        return cls(
            rules={
                # Plugin structure rules
                "plugin-json-required": {"enabled": True, "severity": "error"},
                "plugin-json-valid": {"enabled": True, "severity": "error"},
                "plugin-naming": {"enabled": True, "severity": "warning"},
                "commands-dir-required": {
                    "enabled": False,
                    "severity": "warning",
                },  # Optional - plugins can have just skills/hooks
                "commands-exist": {
                    "enabled": False,
                    "severity": "info",
                },  # Optional - plugins can have just skills/hooks
                # Command format rules
                "command-naming": {"enabled": True, "severity": "warning"},
                "command-frontmatter": {"enabled": True, "severity": "error"},
                "command-sections": {
                    "enabled": True,
                    "severity": "warning",
                    "sections": ["Name", "Synopsis", "Description", "Implementation"],
                },
                "command-name-format": {"enabled": True, "severity": "warning"},
                # Marketplace rules (auto-enabled for marketplace repos)
                "marketplace-json-valid": {"enabled": "auto", "severity": "error"},
                "marketplace-registration": {"enabled": "auto", "severity": "error"},
                # Documentation rules
                "plugin-readme": {"enabled": True, "severity": "warning"},
                # Skills rules
                "skill-frontmatter": {"enabled": True, "severity": "warning"},
                # Agent rules
                "agent-frontmatter": {"enabled": True, "severity": "warning"},
                # Hook rules
                "hook-validation": {"enabled": True, "severity": "error"},
            }
        )

    def get_rule_config(self, rule_id: str) -> Dict[str, Any]:
        """
        Get configuration for a specific rule

        Args:
            rule_id: Rule identifier

        Returns:
            Rule configuration dict
        """
        return self.rules.get(rule_id, {})

    def is_rule_enabled(self, rule_id: str, context: "RepositoryContext") -> bool:
        """
        Check if a rule is enabled for the given context

        Args:
            rule_id: Rule identifier
            context: Repository context

        Returns:
            True if rule should run
        """
        rule_config = self.get_rule_config(rule_id)
        enabled = rule_config.get("enabled", True)

        # Handle 'auto' - enabled only for marketplace repos
        if enabled == "auto":
            from .context import RepositoryType

            return context.repo_type == RepositoryType.MARKETPLACE

        return bool(enabled)

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary for serialization"""
        return {
            "rules": self.rules,
            "custom-rules": self.custom_rules,
            "exclude": self.exclude_patterns,
            "strict": self.strict,
            "plugin-directories": self.plugin_directories,
        }

    def save(self, config_path: Path):
        """Save configuration to file"""
        with open(config_path, "w") as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False, sort_keys=False)


def find_config(start_path: Path) -> Optional[Path]:
    """
    Find .claudelint.yaml by walking up the directory tree

    Args:
        start_path: Starting directory

    Returns:
        Path to config file, or None if not found
    """
    current = start_path.resolve()

    while current != current.parent:
        config_file = current / ".claudelint.yaml"
        if config_file.exists():
            return config_file

        # Also check .yml extension
        config_file = current / ".claudelint.yml"
        if config_file.exists():
            return config_file

        current = current.parent

    return None
