"""
Tests for configuration management
"""

import sys
from pathlib import Path
import yaml


from claudelint.config import LinterConfig, find_config
from claudelint.context import RepositoryContext, RepositoryType


def test_default_config():
    """Test default configuration"""
    config = LinterConfig.default()
    assert "plugin-json-required" in config.rules
    assert config.rules["plugin-json-required"]["enabled"] is True
    assert config.rules["plugin-json-required"]["severity"] == "error"


def test_config_from_file(temp_dir):
    """Test loading configuration from file"""
    config_file = temp_dir / ".claudelint.yaml"
    config_data = {
        "rules": {"plugin-json-required": {"enabled": False, "severity": "warning"}},
        "strict": True,
    }

    with open(config_file, "w") as f:
        yaml.dump(config_data, f)

    config = LinterConfig.from_file(config_file)
    assert config.rules["plugin-json-required"]["enabled"] is False
    assert config.rules["plugin-json-required"]["severity"] == "warning"
    assert config.strict is True


def test_find_config(temp_dir):
    """Test config file discovery"""
    config_file = temp_dir / ".claudelint.yaml"
    config_file.touch()

    # Create a subdirectory
    subdir = temp_dir / "subdir"
    subdir.mkdir()

    # Should find config in parent directory
    found = find_config(subdir)
    assert found.resolve() == config_file.resolve()


def test_rule_enabled_for_context(valid_plugin):
    """Test context-aware rule enabling"""
    context = RepositoryContext(valid_plugin)
    config = LinterConfig.default()

    # marketplace-registration should be disabled for single plugin
    enabled = config.is_rule_enabled("marketplace-registration", context)
    assert enabled is False


def test_rule_enabled_auto(marketplace_repo):
    """Test 'auto' enabled rules"""
    context = RepositoryContext(marketplace_repo)
    config = LinterConfig.default()

    # marketplace-registration should be enabled for marketplace
    enabled = config.is_rule_enabled("marketplace-registration", context)
    assert enabled is True
