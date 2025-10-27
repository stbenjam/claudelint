"""
Pytest fixtures and configuration
"""

import json
import pytest
from pathlib import Path
import tempfile
import shutil


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing"""
    tmp = tempfile.mkdtemp()
    yield Path(tmp)
    shutil.rmtree(tmp)


@pytest.fixture
def valid_plugin(temp_dir):
    """Create a valid plugin structure"""
    plugin_dir = temp_dir / "test-plugin"
    plugin_dir.mkdir()
    
    # Create .claude-plugin/plugin.json
    claude_dir = plugin_dir / ".claude-plugin"
    claude_dir.mkdir()
    
    plugin_json = {
        "name": "test-plugin",
        "description": "A test plugin",
        "version": "1.0.0",
        "author": {"name": "Test Author"}
    }
    
    with open(claude_dir / "plugin.json", 'w') as f:
        json.dump(plugin_json, f)
    
    # Create commands directory with a valid command
    commands_dir = plugin_dir / "commands"
    commands_dir.mkdir()
    
    command_content = """---
description: A test command
---

## Name
test-plugin:test-command

## Synopsis
```
/test-plugin:test-command [args]
```

## Description
This is a test command.

## Implementation
1. Do something
2. Return result
"""
    
    with open(commands_dir / "test-command.md", 'w') as f:
        f.write(command_content)
    
    # Create README
    with open(plugin_dir / "README.md", 'w') as f:
        f.write("# Test Plugin\n\nA test plugin for testing.")
    
    return plugin_dir


@pytest.fixture
def marketplace_repo(temp_dir):
    """Create a marketplace repository structure"""
    # Create marketplace.json
    claude_dir = temp_dir / ".claude-plugin"
    claude_dir.mkdir()
    
    marketplace_json = {
        "name": "test-marketplace",
        "owner": {"name": "Test Owner"},
        "plugins": [
            {
                "name": "plugin-one",
                "source": "./plugins/plugin-one",
                "description": "First plugin"
            },
            {
                "name": "plugin-two",
                "source": "./plugins/plugin-two",
                "description": "Second plugin"
            }
        ]
    }
    
    with open(claude_dir / "marketplace.json", 'w') as f:
        json.dump(marketplace_json, f)
    
    # Create plugins directory
    plugins_dir = temp_dir / "plugins"
    plugins_dir.mkdir()
    
    # Create two plugins
    for plugin_name in ["plugin-one", "plugin-two"]:
        plugin_dir = plugins_dir / plugin_name
        plugin_dir.mkdir()
        
        # Create plugin.json
        plugin_claude_dir = plugin_dir / ".claude-plugin"
        plugin_claude_dir.mkdir()
        
        plugin_json = {
            "name": plugin_name,
            "description": f"Test {plugin_name}",
            "version": "1.0.0",
            "author": {"name": "Test Author"}
        }
        
        with open(plugin_claude_dir / "plugin.json", 'w') as f:
            json.dump(plugin_json, f)
        
        # Create commands
        commands_dir = plugin_dir / "commands"
        commands_dir.mkdir()
        
        with open(commands_dir / "test.md", 'w') as f:
            f.write(f"""---
description: Test command
---

## Name
{plugin_name}:test

## Synopsis
```
/{plugin_name}:test
```

## Description
Test command

## Implementation
Do something
""")
    
    return temp_dir

