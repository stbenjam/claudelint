"""
Tests for hook validation rules
"""

import pytest
import json
from pathlib import Path

from claudelint.rules.builtin.hooks import HooksJsonValidRule
from claudelint.context import RepositoryContext


@pytest.fixture
def plugin_with_valid_hooks(temp_dir):
    """Create a plugin with valid hooks.json"""
    plugin_dir = temp_dir / "test-plugin"
    plugin_dir.mkdir()

    # Create plugin.json
    claude_dir = plugin_dir / ".claude-plugin"
    claude_dir.mkdir()
    (claude_dir / "plugin.json").write_text('{"name": "test-plugin"}')

    # Create hooks directory with valid hooks.json
    hooks_dir = plugin_dir / "hooks"
    hooks_dir.mkdir()

    hooks_config = {
        "hooks": {
            "PostToolUse": [
                {
                    "matcher": "Write|Edit",
                    "hooks": [
                        {"type": "command", "command": "${CLAUDE_PLUGIN_ROOT}/scripts/format.sh"}
                    ],
                }
            ],
            "PreToolUse": [
                {"matcher": ".*", "hooks": [{"type": "validation", "command": "echo 'validating'"}]}
            ],
        }
    }

    (hooks_dir / "hooks.json").write_text(json.dumps(hooks_config, indent=2))

    return plugin_dir


@pytest.fixture
def plugin_with_invalid_json(temp_dir):
    """Create a plugin with invalid JSON in hooks.json"""
    plugin_dir = temp_dir / "test-plugin"
    plugin_dir.mkdir()

    claude_dir = plugin_dir / ".claude-plugin"
    claude_dir.mkdir()
    (claude_dir / "plugin.json").write_text('{"name": "test-plugin"}')

    hooks_dir = plugin_dir / "hooks"
    hooks_dir.mkdir()

    # Invalid JSON
    (hooks_dir / "hooks.json").write_text('{"hooks": invalid json}')

    return plugin_dir


@pytest.fixture
def plugin_with_missing_hooks_key(temp_dir):
    """Create a plugin with hooks.json missing 'hooks' key"""
    plugin_dir = temp_dir / "test-plugin"
    plugin_dir.mkdir()

    claude_dir = plugin_dir / ".claude-plugin"
    claude_dir.mkdir()
    (claude_dir / "plugin.json").write_text('{"name": "test-plugin"}')

    hooks_dir = plugin_dir / "hooks"
    hooks_dir.mkdir()

    hooks_config = {"other_key": "value"}
    (hooks_dir / "hooks.json").write_text(json.dumps(hooks_config))

    return plugin_dir


@pytest.fixture
def plugin_with_invalid_event_type(temp_dir):
    """Create a plugin with invalid event type"""
    plugin_dir = temp_dir / "test-plugin"
    plugin_dir.mkdir()

    claude_dir = plugin_dir / ".claude-plugin"
    claude_dir.mkdir()
    (claude_dir / "plugin.json").write_text('{"name": "test-plugin"}')

    hooks_dir = plugin_dir / "hooks"
    hooks_dir.mkdir()

    hooks_config = {
        "hooks": {
            "InvalidEventType": [
                {"matcher": ".*", "hooks": [{"type": "command", "command": "echo test"}]}
            ]
        }
    }

    (hooks_dir / "hooks.json").write_text(json.dumps(hooks_config))

    return plugin_dir


@pytest.fixture
def plugin_with_missing_hook_type(temp_dir):
    """Create a plugin with hook configuration missing 'type' field"""
    plugin_dir = temp_dir / "test-plugin"
    plugin_dir.mkdir()

    claude_dir = plugin_dir / ".claude-plugin"
    claude_dir.mkdir()
    (claude_dir / "plugin.json").write_text('{"name": "test-plugin"}')

    hooks_dir = plugin_dir / "hooks"
    hooks_dir.mkdir()

    hooks_config = {
        "hooks": {
            "PostToolUse": [
                {
                    "matcher": ".*",
                    "hooks": [
                        {
                            "command": "echo test"
                            # Missing "type" field
                        }
                    ],
                }
            ]
        }
    }

    (hooks_dir / "hooks.json").write_text(json.dumps(hooks_config))

    return plugin_dir


@pytest.fixture
def plugin_without_hooks(temp_dir):
    """Create a plugin without hooks directory"""
    plugin_dir = temp_dir / "test-plugin"
    plugin_dir.mkdir()

    claude_dir = plugin_dir / ".claude-plugin"
    claude_dir.mkdir()
    (claude_dir / "plugin.json").write_text('{"name": "test-plugin"}')

    return plugin_dir


def test_valid_hooks_json(plugin_with_valid_hooks):
    """Test that valid hooks.json passes validation"""
    context = RepositoryContext(plugin_with_valid_hooks)
    rule = HooksJsonValidRule()
    violations = rule.check(context)
    assert len(violations) == 0


def test_invalid_json(plugin_with_invalid_json):
    """Test that invalid JSON is detected"""
    context = RepositoryContext(plugin_with_invalid_json)
    rule = HooksJsonValidRule()
    violations = rule.check(context)
    assert len(violations) == 1
    assert "Invalid JSON" in violations[0].message


def test_missing_hooks_key(plugin_with_missing_hooks_key):
    """Test that missing 'hooks' key is detected"""
    context = RepositoryContext(plugin_with_missing_hooks_key)
    rule = HooksJsonValidRule()
    violations = rule.check(context)
    assert len(violations) == 1
    assert "'hooks' key" in violations[0].message


def test_invalid_event_type(plugin_with_invalid_event_type):
    """Test that invalid event types are detected"""
    context = RepositoryContext(plugin_with_invalid_event_type)
    rule = HooksJsonValidRule()
    violations = rule.check(context)
    assert len(violations) == 1
    assert "Unknown event type" in violations[0].message


def test_missing_hook_type(plugin_with_missing_hook_type):
    """Test that missing 'type' field in hook is detected"""
    context = RepositoryContext(plugin_with_missing_hook_type)
    rule = HooksJsonValidRule()
    violations = rule.check(context)
    assert len(violations) == 1
    assert "'type' field" in violations[0].message


def test_no_hooks_directory(plugin_without_hooks):
    """Test that plugins without hooks directory don't trigger violations"""
    context = RepositoryContext(plugin_without_hooks)
    rule = HooksJsonValidRule()
    violations = rule.check(context)
    assert len(violations) == 0


def test_rule_metadata():
    """Test rule metadata"""
    rule = HooksJsonValidRule()
    assert rule.rule_id == "hooks-json-valid"
    assert "hooks" in rule.description.lower()
    assert rule.default_severity().value == "error"


def test_all_valid_event_types(temp_dir):
    """Test that all documented event types are accepted"""
    plugin_dir = temp_dir / "test-plugin"
    plugin_dir.mkdir()

    claude_dir = plugin_dir / ".claude-plugin"
    claude_dir.mkdir()
    (claude_dir / "plugin.json").write_text('{"name": "test-plugin"}')

    hooks_dir = plugin_dir / "hooks"
    hooks_dir.mkdir()

    # Test all valid event types
    valid_events = [
        "PreToolUse",
        "PostToolUse",
        "UserPromptSubmit",
        "Notification",
        "Stop",
        "SubagentStop",
        "SessionStart",
        "SessionEnd",
        "PreCompact",
    ]

    hooks_config = {"hooks": {}}
    for event in valid_events:
        hooks_config["hooks"][event] = [
            {"matcher": ".*", "hooks": [{"type": "command", "command": "echo test"}]}
        ]

    (hooks_dir / "hooks.json").write_text(json.dumps(hooks_config))

    context = RepositoryContext(plugin_dir)
    rule = HooksJsonValidRule()
    violations = rule.check(context)
    assert len(violations) == 0
