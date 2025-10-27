"""
Repository context detection and management
"""

from enum import Enum
from pathlib import Path
from typing import Optional, List, Dict, Any
import json


class RepositoryType(Enum):
    """Type of Claude plugin repository"""
    SINGLE_PLUGIN = "single-plugin"     # Single plugin at repo root
    MARKETPLACE = "marketplace"         # Marketplace with multiple plugins
    UNKNOWN = "unknown"                 # Not a Claude plugin repo


class RepositoryContext:
    """
    Context information about the repository being linted
    
    Automatically detects repository type and gathers relevant metadata.
    """
    
    def __init__(self, root_path: Path):
        """
        Initialize repository context
        
        Args:
            root_path: Root directory of the repository
        """
        self.root_path = root_path.resolve()
        self.repo_type = self._detect_type()
        self.marketplace_data = self._load_marketplace() if self.has_marketplace() else None
        self.plugins = self._discover_plugins()
    
    def _detect_type(self) -> RepositoryType:
        """Detect the type of repository"""
        # Check for marketplace
        if (self.root_path / ".claude-plugin" / "marketplace.json").exists():
            return RepositoryType.MARKETPLACE
        
        # Check for single plugin at root
        if (self.root_path / ".claude-plugin" / "plugin.json").exists():
            return RepositoryType.SINGLE_PLUGIN
        
        # Check for plugins directory (marketplace without registration)
        if (self.root_path / "plugins").exists():
            return RepositoryType.MARKETPLACE
        
        return RepositoryType.UNKNOWN
    
    def has_marketplace(self) -> bool:
        """Check if repository has a marketplace"""
        return (self.root_path / ".claude-plugin" / "marketplace.json").exists()
    
    def _load_marketplace(self) -> Optional[Dict[str, Any]]:
        """Load marketplace.json if it exists"""
        marketplace_file = self.root_path / ".claude-plugin" / "marketplace.json"
        if not marketplace_file.exists():
            return None
        
        try:
            with open(marketplace_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None
    
    def _discover_plugins(self) -> List[Path]:
        """Discover all plugin directories in the repository"""
        plugins = []
        
        if self.repo_type == RepositoryType.SINGLE_PLUGIN:
            # The root is the plugin
            plugins.append(self.root_path)
        
        elif self.repo_type == RepositoryType.MARKETPLACE:
            # Look for plugins in plugins/ directory
            plugins_dir = self.root_path / "plugins"
            if plugins_dir.exists():
                for item in plugins_dir.iterdir():
                    if item.is_dir() and not item.name.startswith('.'):
                        # Check if it has .claude-plugin or commands directory
                        if (item / ".claude-plugin").exists() or (item / "commands").exists():
                            plugins.append(item)
        
        return plugins
    
    def get_plugin_name(self, plugin_path: Path) -> str:
        """Get the name of a plugin from its path"""
        if plugin_path == self.root_path:
            # Single plugin at root - check plugin.json for name
            plugin_json = plugin_path / ".claude-plugin" / "plugin.json"
            if plugin_json.exists():
                try:
                    with open(plugin_json, 'r') as f:
                        data = json.load(f)
                        return data.get('name', plugin_path.name)
                except:
                    pass
            return plugin_path.name
        else:
            # Plugin in plugins/ directory
            return plugin_path.name
    
    def is_registered_in_marketplace(self, plugin_name: str) -> bool:
        """Check if a plugin is registered in marketplace.json"""
        if not self.marketplace_data or 'plugins' not in self.marketplace_data:
            return False
        
        return any(
            p.get('name') == plugin_name 
            for p in self.marketplace_data['plugins']
        )
    
    def __str__(self):
        """String representation of context"""
        return f"RepositoryContext(type={self.repo_type.value}, plugins={len(self.plugins)})"

