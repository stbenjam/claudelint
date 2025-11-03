"""
Rules for validating hook configuration
"""

import json
from typing import List, Dict, Any

from claudelint.rule import Rule, RuleViolation, Severity
from claudelint.context import RepositoryContext

# Valid hook event types
_VALID_HOOK_EVENTS = {
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


class HooksJsonValidRule(Rule):
    """Check that hooks.json is valid JSON with proper structure"""

    @property
    def rule_id(self) -> str:
        return "hooks-json-valid"

    @property
    def description(self) -> str:
        return "hooks.json must be valid JSON with proper hook configuration structure"

    def default_severity(self) -> Severity:
        return Severity.ERROR

    def check(self, context: RepositoryContext) -> List[RuleViolation]:
        violations = []

        for plugin_path in context.plugins:
            hooks_dir = plugin_path / "hooks"
            if not hooks_dir.exists():
                continue

            hooks_json = hooks_dir / "hooks.json"
            if not hooks_json.exists():
                continue

            # Try to parse JSON
            try:
                with open(hooks_json, "r") as f:
                    data = json.load(f)
            except json.JSONDecodeError as e:
                violations.append(self.violation(f"Invalid JSON: {e}", file_path=hooks_json))
                continue
            except IOError as e:
                violations.append(self.violation(f"Failed to read file: {e}", file_path=hooks_json))
                continue

            # Validate structure
            if not isinstance(data, dict):
                violations.append(
                    self.violation("hooks.json must be a JSON object", file_path=hooks_json)
                )
                continue

            if "hooks" not in data:
                violations.append(
                    self.violation("hooks.json must contain a 'hooks' key", file_path=hooks_json)
                )
                continue

            hooks = data["hooks"]
            if not isinstance(hooks, dict):
                violations.append(
                    self.violation("'hooks' must be a JSON object", file_path=hooks_json)
                )
                continue

            # Validate event types
            for event_type, hook_configs in hooks.items():
                if event_type not in _VALID_HOOK_EVENTS:
                    violations.append(
                        self.violation(
                            f"Unknown event type '{event_type}'. Valid types: {', '.join(sorted(_VALID_HOOK_EVENTS))}",
                            file_path=hooks_json,
                        )
                    )

                if not isinstance(hook_configs, list):
                    violations.append(
                        self.violation(
                            f"Event '{event_type}' must have an array of hook configurations",
                            file_path=hooks_json,
                        )
                    )
                    continue

                for idx, hook_config in enumerate(hook_configs):
                    if not isinstance(hook_config, dict):
                        violations.append(
                            self.violation(
                                f"Event '{event_type}[{idx}]' configuration must be an object",
                                file_path=hooks_json,
                            )
                        )
                        continue

                    # Validate hook configuration has required 'hooks' array
                    if "hooks" not in hook_config:
                        violations.append(
                            self.violation(
                                f"Event '{event_type}[{idx}]' must have a 'hooks' array",
                                file_path=hooks_json,
                            )
                        )
                        continue

                    hook_list = hook_config["hooks"]
                    if not isinstance(hook_list, list):
                        violations.append(
                            self.violation(
                                f"Event '{event_type}[{idx}].hooks' must be an array",
                                file_path=hooks_json,
                            )
                        )
                        continue

                    # Validate each hook has a type
                    for hook_idx, hook in enumerate(hook_list):
                        if not isinstance(hook, dict):
                            violations.append(
                                self.violation(
                                    f"Event '{event_type}[{idx}].hooks[{hook_idx}]' must be an object",
                                    file_path=hooks_json,
                                )
                            )
                            continue

                        if "type" not in hook:
                            violations.append(
                                self.violation(
                                    f"Event '{event_type}[{idx}].hooks[{hook_idx}]' must have a 'type' field",
                                    file_path=hooks_json,
                                )
                            )

        return violations
