"""
Tests for builtin rules
"""

import sys
from pathlib import Path


from claudelint.context import RepositoryContext
from claudelint.rule import Severity
from claudelint.rules.builtin.plugin_structure import (
    PluginJsonRequiredRule,
    PluginJsonValidRule,
    PluginNamingRule,
)
from claudelint.rules.builtin.command_format import (
    CommandNamingRule,
    CommandFrontmatterRule,
)
from claudelint.rules.builtin.marketplace import (
    MarketplaceRegistrationRule,
)


def test_plugin_json_required_passes(valid_plugin):
    """Test that valid plugin passes plugin.json requirement"""
    context = RepositoryContext(valid_plugin)
    rule = PluginJsonRequiredRule()
    violations = rule.check(context)
    assert len(violations) == 0


def test_plugin_json_required_fails(temp_dir):
    """Test that plugin without plugin.json fails"""
    plugin_dir = temp_dir / "bad-plugin"
    plugin_dir.mkdir()

    # Create .claude-plugin dir but no plugin.json inside
    claude_dir = plugin_dir / ".claude-plugin"
    claude_dir.mkdir()

    # Create commands dir so it looks like a plugin
    (plugin_dir / "commands").mkdir()

    context = RepositoryContext(plugin_dir)
    rule = PluginJsonRequiredRule()
    violations = rule.check(context)
    assert len(violations) == 1
    assert violations[0].severity == Severity.ERROR


def test_plugin_json_valid_passes(valid_plugin):
    """Test that valid plugin.json passes validation"""
    context = RepositoryContext(valid_plugin)
    rule = PluginJsonValidRule()
    violations = rule.check(context)
    assert len(violations) == 0


def test_plugin_naming_passes(valid_plugin):
    """Test that kebab-case plugin name passes"""
    context = RepositoryContext(valid_plugin)
    rule = PluginNamingRule()
    violations = rule.check(context)
    assert len(violations) == 0


def test_command_naming_passes(valid_plugin):
    """Test that kebab-case command names pass"""
    context = RepositoryContext(valid_plugin)
    rule = CommandNamingRule()
    violations = rule.check(context)
    assert len(violations) == 0


def test_command_frontmatter_passes(valid_plugin):
    """Test that valid command frontmatter passes"""
    context = RepositoryContext(valid_plugin)
    rule = CommandFrontmatterRule()
    violations = rule.check(context)
    assert len(violations) == 0


def test_marketplace_registration_passes(marketplace_repo):
    """Test that registered plugins pass marketplace check"""
    context = RepositoryContext(marketplace_repo)
    rule = MarketplaceRegistrationRule()
    violations = rule.check(context)
    assert len(violations) == 0


def test_marketplace_registration_fails(marketplace_repo):
    """Test that unregistered plugin fails marketplace check"""
    # Add a plugin that's not registered
    plugins_dir = marketplace_repo / "plugins"
    new_plugin = plugins_dir / "plugin-three"
    new_plugin.mkdir()

    claude_dir = new_plugin / ".claude-plugin"
    claude_dir.mkdir()

    import json

    with open(claude_dir / "plugin.json", "w") as f:
        json.dump(
            {
                "name": "plugin-three",
                "description": "Third plugin",
                "version": "1.0.0",
                "author": {"name": "Test"},
            },
            f,
        )

    context = RepositoryContext(marketplace_repo)
    rule = MarketplaceRegistrationRule()
    violations = rule.check(context)
    assert len(violations) == 1
    assert "plugin-three" in violations[0].message
