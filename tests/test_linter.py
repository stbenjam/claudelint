"""
Tests for main linter functionality
"""

import sys
from pathlib import Path


from claudelint.linter import ClaudeLinter
from claudelint.context import RepositoryContext
from claudelint.config import LinterConfig


def test_linter_passes_valid_plugin(valid_plugin):
    """Test that linter passes valid plugin"""
    context = RepositoryContext(valid_plugin)
    config = LinterConfig.default()
    linter = ClaudeLinter(context, config)

    violations = linter.run()
    errors, warnings, info = linter.get_counts(violations)

    assert errors == 0
    assert warnings == 0


def test_linter_passes_marketplace(marketplace_repo):
    """Test that linter passes valid marketplace"""
    context = RepositoryContext(marketplace_repo)
    config = LinterConfig.default()
    linter = ClaudeLinter(context, config)

    violations = linter.run()
    errors, warnings, info = linter.get_counts(violations)

    # Should have no errors (warnings are ok - e.g. missing README)
    assert errors == 0


def test_linter_detects_errors(temp_dir):
    """Test that linter detects errors in invalid plugin"""
    # Create a minimal plugin structure with missing plugin.json
    plugin_dir = temp_dir / "bad-plugin"
    plugin_dir.mkdir()

    # Create .claude-plugin dir but no plugin.json
    claude_dir = plugin_dir / ".claude-plugin"
    claude_dir.mkdir()

    context = RepositoryContext(plugin_dir)
    config = LinterConfig.default()

    # Enable plugin-json-required
    config.rules["plugin-json-required"] = {"enabled": True, "severity": "error"}

    linter = ClaudeLinter(context, config)
    violations = linter.run()
    errors, warnings, info = linter.get_counts(violations)

    # Should detect missing plugin.json as error
    assert errors > 0


def test_linter_respects_disabled_rules(valid_plugin):
    """Test that disabled rules are not checked"""
    context = RepositoryContext(valid_plugin)
    config = LinterConfig.default()

    # Disable all rules
    for rule_id in config.rules:
        config.rules[rule_id]["enabled"] = False

    linter = ClaudeLinter(context, config)

    # Should have no rules loaded
    assert len(linter.rules) == 0
