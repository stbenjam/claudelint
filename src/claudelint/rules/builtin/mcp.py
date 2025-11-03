"""
Rules for validating MCP (Model Context Protocol) configuration
"""

import json
from typing import List, Dict, Any
from pathlib import Path

from claudelint.rule import Rule, RuleViolation, Severity
from claudelint.context import RepositoryContext


class McpValidJsonRule(Rule):
    """Check that MCP configuration is valid JSON with proper structure"""

    @property
    def rule_id(self) -> str:
        return "mcp-valid-json"

    @property
    def description(self) -> str:
        return "MCP configuration must be valid JSON with proper mcpServers structure"

    def default_severity(self) -> Severity:
        return Severity.ERROR

    def check(self, context: RepositoryContext) -> List[RuleViolation]:
        violations = []

        for plugin_path in context.plugins:
            # Check for .mcp.json at plugin root
            mcp_json = plugin_path / ".mcp.json"
            if mcp_json.exists():
                violations.extend(self._validate_mcp_file(mcp_json))

            # Check for mcpServers in plugin.json
            plugin_json_path = plugin_path / ".claude-plugin" / "plugin.json"
            if plugin_json_path.exists():
                violations.extend(self._validate_plugin_json_mcp(plugin_json_path))

        return violations

    def _validate_mcp_file(self, mcp_json: Path) -> List[RuleViolation]:
        """Validate standalone .mcp.json file"""
        violations = []

        # Try to parse JSON
        try:
            with open(mcp_json, "r") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            violations.append(self.violation(f"Invalid JSON: {e}", file_path=mcp_json))
            return violations
        except IOError as e:
            violations.append(self.violation(f"Failed to read file: {e}", file_path=mcp_json))
            return violations

        # Validate structure
        violations.extend(self._validate_mcp_structure(data, mcp_json))

        return violations

    def _validate_plugin_json_mcp(self, plugin_json: Path) -> List[RuleViolation]:
        """Validate mcpServers field in plugin.json"""
        violations = []

        try:
            with open(plugin_json, "r") as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError):
            # If plugin.json is invalid, plugin-json-valid rule will catch it
            return violations

        # Only validate if mcpServers field exists
        if "mcpServers" not in data:
            return violations

        mcp_config = {"mcpServers": data["mcpServers"]}
        violations.extend(self._validate_mcp_structure(mcp_config, plugin_json))

        return violations

    def _validate_mcp_structure(self, data: Dict[str, Any], file_path: Path) -> List[RuleViolation]:
        """Validate MCP configuration structure"""
        violations = []

        if not isinstance(data, dict):
            violations.append(
                self.violation("MCP configuration must be a JSON object", file_path=file_path)
            )
            return violations

        if "mcpServers" not in data:
            violations.append(
                self.violation(
                    "MCP configuration must contain 'mcpServers' key",
                    file_path=file_path,
                )
            )
            return violations

        mcp_servers = data["mcpServers"]
        if not isinstance(mcp_servers, dict):
            violations.append(
                self.violation("'mcpServers' must be a JSON object", file_path=file_path)
            )
            return violations

        # Validate each server configuration
        for server_name, server_config in mcp_servers.items():
            if not isinstance(server_config, dict):
                violations.append(
                    self.violation(
                        f"MCP server '{server_name}' configuration must be an object",
                        file_path=file_path,
                    )
                )
                continue

            # Check for required 'command' field
            if "command" not in server_config:
                violations.append(
                    self.violation(
                        f"MCP server '{server_name}' must have a 'command' field",
                        file_path=file_path,
                    )
                )

            # Validate optional fields
            if "args" in server_config and not isinstance(server_config["args"], list):
                violations.append(
                    self.violation(
                        f"MCP server '{server_name}' 'args' must be an array",
                        file_path=file_path,
                    )
                )

            if "env" in server_config and not isinstance(server_config["env"], dict):
                violations.append(
                    self.violation(
                        f"MCP server '{server_name}' 'env' must be an object",
                        file_path=file_path,
                    )
                )

            if "cwd" in server_config and not isinstance(server_config["cwd"], str):
                violations.append(
                    self.violation(
                        f"MCP server '{server_name}' 'cwd' must be a string",
                        file_path=file_path,
                    )
                )

        return violations


class McpProhibitedRule(Rule):
    """Check that plugins do not enable MCP servers (security/policy rule)"""

    @property
    def rule_id(self) -> str:
        return "mcp-prohibited"

    @property
    def description(self) -> str:
        return "Plugins should not enable non-allowlisted MCP servers"

    def default_severity(self) -> Severity:
        return Severity.ERROR

    def check(self, context: RepositoryContext) -> List[RuleViolation]:
        violations = []
        # Get allowlist from config
        allowlist = set(self.config.get("allowlist", []))

        for plugin_path in context.plugins:
            # Check for .mcp.json at plugin root
            mcp_json = plugin_path / ".mcp.json"
            if mcp_json.exists():
                violations.extend(self._check_mcp_file(mcp_json, allowlist))

            # Check for mcpServers in plugin.json
            plugin_json_path = plugin_path / ".claude-plugin" / "plugin.json"
            if plugin_json_path.exists():
                violations.extend(self._check_plugin_json(plugin_json_path, allowlist))

        return violations

    def _check_mcp_file(self, mcp_json: Path, allowlist: set) -> List[RuleViolation]:
        """Check .mcp.json for non-allowlisted servers"""
        violations = []

        try:
            with open(mcp_json, "r") as f:
                data = json.load(f)

            if "mcpServers" in data:
                prohibited = self._get_prohibited_servers(data["mcpServers"], allowlist)
                if prohibited:
                    if allowlist:
                        violations.append(
                            self.violation(
                                f"Plugin defines non-allowlisted MCP servers: {', '.join(sorted(prohibited))}",
                                file_path=mcp_json,
                            )
                        )
                    else:
                        violations.append(
                            self.violation(
                                "Plugin defines MCP servers in .mcp.json",
                                file_path=mcp_json,
                            )
                        )
        except (json.JSONDecodeError, IOError):
            pass

        return violations

    def _check_plugin_json(self, plugin_json: Path, allowlist: set) -> List[RuleViolation]:
        """Check plugin.json for non-allowlisted servers"""
        violations = []

        try:
            with open(plugin_json, "r") as f:
                data = json.load(f)

            if "mcpServers" in data:
                prohibited = self._get_prohibited_servers(data["mcpServers"], allowlist)
                if prohibited:
                    if allowlist:
                        violations.append(
                            self.violation(
                                f"Plugin defines non-allowlisted MCP servers: {', '.join(sorted(prohibited))}",
                                file_path=plugin_json,
                            )
                        )
                    else:
                        violations.append(
                            self.violation(
                                "Plugin defines MCP servers in plugin.json",
                                file_path=plugin_json,
                            )
                        )
        except (json.JSONDecodeError, IOError):
            pass

        return violations

    def _get_prohibited_servers(self, mcp_servers: dict, allowlist: set) -> set:
        """
        Get set of server names that are not in the allowlist

        Args:
            mcp_servers: Dict of MCP server configurations
            allowlist: Set of allowed server names

        Returns:
            Set of prohibited server names
        """
        if not allowlist:
            # If no allowlist, all servers are prohibited
            return set(mcp_servers.keys())

        return set(mcp_servers.keys()) - allowlist
