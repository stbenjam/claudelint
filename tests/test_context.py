"""
Tests for repository context detection
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.context import RepositoryContext, RepositoryType


def test_single_plugin_detection(valid_plugin):
    """Test detection of single plugin repository"""
    context = RepositoryContext(valid_plugin)
    assert context.repo_type == RepositoryType.SINGLE_PLUGIN
    assert len(context.plugins) == 1
    assert context.plugins[0].resolve() == valid_plugin.resolve()


def test_marketplace_detection(marketplace_repo):
    """Test detection of marketplace repository"""
    context = RepositoryContext(marketplace_repo)
    assert context.repo_type == RepositoryType.MARKETPLACE
    assert len(context.plugins) == 2
    assert context.has_marketplace()


def test_plugin_name_extraction(valid_plugin):
    """Test plugin name extraction"""
    context = RepositoryContext(valid_plugin)
    name = context.get_plugin_name(valid_plugin)
    assert name == "test-plugin"


def test_marketplace_registration(marketplace_repo):
    """Test marketplace registration check"""
    context = RepositoryContext(marketplace_repo)
    assert context.is_registered_in_marketplace("plugin-one")
    assert context.is_registered_in_marketplace("plugin-two")
    assert not context.is_registered_in_marketplace("plugin-three")


def test_unknown_repository(temp_dir):
    """Test detection of unknown repository type"""
    context = RepositoryContext(temp_dir)
    assert context.repo_type == RepositoryType.UNKNOWN
    assert len(context.plugins) == 0

