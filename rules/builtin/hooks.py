"""
Rules for validating hook files
"""

import json
from pathlib import Path
from typing import List

try:
    from src.rule import Rule, RuleViolation, Severity
    from src.context import RepositoryContext
except ImportError:
    from ...src.rule import Rule, RuleViolation, Severity
    from ...src.context import RepositoryContext


class HookValidationRule(Rule):
    """Check that hooks.json is valid and well-formed"""

    @property
    def rule_id(self) -> str:
        return "hook-validation"

    @property
    def description(self) -> str:
        return "Hook files must be valid JSON with proper structure"

    def default_severity(self) -> Severity:
        return Severity.ERROR

    def check(self, context: RepositoryContext) -> List[RuleViolation]:
        violations = []

        # Valid hook events based on Claude Code documentation
        valid_events = {
            "PreToolUse",
            "PostToolUse",
            "UserPromptSubmit",
            "Notification",
            "Stop",
            "SubagentStop",
            "SessionStart",
            "SessionEnd",
            "PreCompact",
        }

        # Valid hook types
        valid_types = {"command", "validation", "notification"}

        for plugin_path in context.plugins:
            hooks_file = plugin_path / "hooks" / "hooks.json"
            if not hooks_file.exists():
                # Also check for inline hooks in plugin.json
                plugin_json = plugin_path / ".claude-plugin" / "plugin.json"
                if plugin_json.exists():
                    try:
                        with open(plugin_json, "r") as f:
                            plugin_data = json.load(f)
                        if "hooks" in plugin_data:
                            # Validate inline hooks
                            self._validate_hooks_structure(
                                plugin_data, plugin_json, violations, valid_events, valid_types
                            )
                    except (json.JSONDecodeError, IOError):
                        pass  # Handled by other rules
                continue

            # Validate hooks.json file
            try:
                with open(hooks_file, "r") as f:
                    data = json.load(f)
            except json.JSONDecodeError as e:
                violations.append(
                    self.violation(f"Invalid JSON in hooks.json: {e}", file_path=hooks_file)
                )
                continue
            except IOError as e:
                violations.append(
                    self.violation(f"Failed to read hooks.json: {e}", file_path=hooks_file)
                )
                continue

            self._validate_hooks_structure(data, hooks_file, violations, valid_events, valid_types)

        return violations

    def _validate_hooks_structure(
        self, data: dict, file_path: Path, violations: List, valid_events: set, valid_types: set
    ):
        """Validate the structure of hooks configuration"""

        if "hooks" not in data:
            violations.append(
                self.violation("Missing 'hooks' key in hooks configuration", file_path=file_path)
            )
            return

        hooks = data["hooks"]
        if not isinstance(hooks, dict):
            violations.append(
                self.violation("'hooks' must be an object/dictionary", file_path=file_path)
            )
            return

        # Check each event
        for event_name, hook_list in hooks.items():
            # Validate event name
            if event_name not in valid_events:
                violations.append(
                    self.violation(
                        f"Unknown hook event '{event_name}'. Valid events: {', '.join(sorted(valid_events))}",
                        file_path=file_path,
                    )
                )

            # Validate hook list
            if not isinstance(hook_list, list):
                violations.append(
                    self.violation(f"Hook event '{event_name}' must be a list", file_path=file_path)
                )
                continue

            # Validate each hook in the list
            for i, hook_config in enumerate(hook_list):
                if not isinstance(hook_config, dict):
                    violations.append(
                        self.violation(
                            f"Hook #{i} in '{event_name}' must be an object", file_path=file_path
                        )
                    )
                    continue

                # Check for hooks array
                if "hooks" in hook_config:
                    if not isinstance(hook_config["hooks"], list):
                        violations.append(
                            self.violation(
                                f"'hooks' in '{event_name}' hook #{i} must be a list",
                                file_path=file_path,
                            )
                        )
                        continue

                    # Validate each individual hook
                    for j, individual_hook in enumerate(hook_config["hooks"]):
                        if not isinstance(individual_hook, dict):
                            violations.append(
                                self.violation(
                                    f"Hook #{j} in '{event_name}' must be an object",
                                    file_path=file_path,
                                )
                            )
                            continue

                        # Check for required 'type' field
                        if "type" not in individual_hook:
                            violations.append(
                                self.violation(
                                    f"Hook #{j} in '{event_name}' missing required 'type' field",
                                    file_path=file_path,
                                )
                            )
                            continue

                        hook_type = individual_hook["type"]
                        if hook_type not in valid_types:
                            violations.append(
                                self.violation(
                                    f"Unknown hook type '{hook_type}' in '{event_name}'. Valid types: {', '.join(sorted(valid_types))}",
                                    file_path=file_path,
                                )
                            )

                        # Validate command hooks have a command field
                        if hook_type == "command" and "command" not in individual_hook:
                            violations.append(
                                self.violation(
                                    f"Command hook in '{event_name}' missing 'command' field",
                                    file_path=file_path,
                                )
                            )
