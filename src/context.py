"""
Repository context detection and management
"""

from enum import Enum
from pathlib import Path
from typing import Optional, List, Dict, Any
import json


class RepositoryType(Enum):
    """Type of Claude plugin repository"""

    SINGLE_PLUGIN = "single-plugin"  # Single plugin at repo root
    MARKETPLACE = "marketplace"  # Marketplace with multiple plugins
    UNKNOWN = "unknown"  # Not a Claude plugin repo


class RepositoryContext:
    """
    Context information about the repository being linted

    Automatically detects repository type and gathers relevant metadata.
    """

    def __init__(self, root_path: Path, config=None):
        """
        Initialize repository context

        Args:
            root_path: Root directory of the repository
            config: Optional LinterConfig with plugin_directories
        """
        self.root_path = root_path.resolve()
        self.config = config
        self.repo_type = self._detect_type()
        self.marketplace_data = self._load_marketplace() if self.has_marketplace() else None
        self.plugins = self._discover_plugins()
        # Cache plugin.json data for each plugin
        self._plugin_data_cache: Dict[Path, Optional[Dict[str, Any]]] = {}

    def _detect_type(self) -> RepositoryType:
        """Detect the type of repository"""
        # Check for marketplace
        if (self.root_path / ".claude-plugin" / "marketplace.json").exists():
            return RepositoryType.MARKETPLACE

        # Check for single plugin at root (even without plugin.json so we can validate it)
        if (self.root_path / ".claude-plugin").exists():
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
            with open(marketplace_file, "r") as f:
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
            # Get plugin directories from config, or use defaults
            plugin_dirs = ["plugins", ".claude/plugins", ".claude-plugin/plugins"]
            if self.config and hasattr(self.config, "plugin_directories"):
                plugin_dirs = self.config.plugin_directories

            # Look for plugins in each configured directory
            for plugins_dir_name in plugin_dirs:
                plugins_dir = self.root_path / plugins_dir_name
                if plugins_dir.exists():
                    for item in plugins_dir.iterdir():
                        if item.is_dir() and not item.name.startswith("."):
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
                    with open(plugin_json, "r") as f:
                        data = json.load(f)
                        return data.get("name", plugin_path.name)
                except:
                    pass
            return plugin_path.name
        else:
            # Plugin in plugins/ directory
            return plugin_path.name

    def is_registered_in_marketplace(self, plugin_name: str) -> bool:
        """Check if a plugin is registered in marketplace.json"""
        if not self.marketplace_data or "plugins" not in self.marketplace_data:
            return False

        return any(p.get("name") == plugin_name for p in self.marketplace_data["plugins"])

    def get_plugin_data(self, plugin_path: Path) -> Optional[Dict[str, Any]]:
        """
        Get plugin.json data for a plugin, with caching

        Args:
            plugin_path: Path to the plugin directory

        Returns:
            Dict with plugin.json data, or None if not found/invalid
        """
        if plugin_path in self._plugin_data_cache:
            return self._plugin_data_cache[plugin_path]

        plugin_json = plugin_path / ".claude-plugin" / "plugin.json"
        if not plugin_json.exists():
            self._plugin_data_cache[plugin_path] = None
            return None

        try:
            with open(plugin_json, "r") as f:
                data = json.load(f)
                self._plugin_data_cache[plugin_path] = data
                return data
        except (json.JSONDecodeError, IOError):
            self._plugin_data_cache[plugin_path] = None
            return None

    def get_commands_dirs(self, plugin_path: Path) -> List[Path]:
        """
        Get all command directories for a plugin

        Checks plugin.json for custom paths, falls back to commands/

        Args:
            plugin_path: Path to the plugin directory

        Returns:
            List of paths to command directories
        """
        dirs = []
        plugin_data = self.get_plugin_data(plugin_path)

        # Check plugin.json for custom commands paths
        if plugin_data and "commands" in plugin_data:
            commands_config = plugin_data["commands"]
            if isinstance(commands_config, str):
                # Single path
                custom_path = plugin_path / commands_config.lstrip("./")
                if custom_path.exists() and custom_path.is_dir():
                    dirs.append(custom_path)
            elif isinstance(commands_config, list):
                # Multiple paths
                for cmd_path in commands_config:
                    if isinstance(cmd_path, str):
                        custom_path = plugin_path / cmd_path.lstrip("./")
                        if custom_path.exists() and custom_path.is_dir():
                            dirs.append(custom_path)

        # Always include default commands/ directory
        default_commands = plugin_path / "commands"
        if default_commands.exists() and default_commands not in dirs:
            dirs.append(default_commands)

        return dirs

    def get_agents_dirs(self, plugin_path: Path) -> List[Path]:
        """
        Get all agent directories for a plugin

        Checks plugin.json for custom paths, falls back to agents/

        Args:
            plugin_path: Path to the plugin directory

        Returns:
            List of paths to agent directories
        """
        dirs = []
        plugin_data = self.get_plugin_data(plugin_path)

        # Check plugin.json for custom agents paths
        if plugin_data and "agents" in plugin_data:
            agents_config = plugin_data["agents"]
            if isinstance(agents_config, str):
                custom_path = plugin_path / agents_config.lstrip("./")
                if custom_path.exists() and custom_path.is_dir():
                    dirs.append(custom_path)
            elif isinstance(agents_config, list):
                for agent_path in agents_config:
                    if isinstance(agent_path, str):
                        custom_path = plugin_path / agent_path.lstrip("./")
                        if custom_path.exists() and custom_path.is_dir():
                            dirs.append(custom_path)

        # Always include default agents/ directory
        default_agents = plugin_path / "agents"
        if default_agents.exists() and default_agents not in dirs:
            dirs.append(default_agents)

        return dirs

    def get_skills_dirs(self, plugin_path: Path) -> List[Path]:
        """
        Get all skills directories for a plugin

        Checks plugin.json for custom paths, falls back to skills/

        Args:
            plugin_path: Path to the plugin directory

        Returns:
            List of paths to skills directories
        """
        dirs = []
        plugin_data = self.get_plugin_data(plugin_path)

        # Check plugin.json for custom skills paths
        if plugin_data and "skills" in plugin_data:
            skills_config = plugin_data["skills"]
            if isinstance(skills_config, str):
                custom_path = plugin_path / skills_config.lstrip("./")
                if custom_path.exists() and custom_path.is_dir():
                    dirs.append(custom_path)
            elif isinstance(skills_config, list):
                for skill_path in skills_config:
                    if isinstance(skill_path, str):
                        custom_path = plugin_path / skill_path.lstrip("./")
                        if custom_path.exists() and custom_path.is_dir():
                            dirs.append(custom_path)

        # Always include default skills/ directory
        default_skills = plugin_path / "skills"
        if default_skills.exists() and default_skills not in dirs:
            dirs.append(default_skills)

        return dirs

    def get_hooks_path(self, plugin_path: Path) -> Optional[Path]:
        """
        Get hooks configuration path for a plugin

        Checks plugin.json for custom path, falls back to hooks/hooks.json

        Args:
            plugin_path: Path to the plugin directory

        Returns:
            Path to hooks configuration file, or None if not found
        """
        plugin_data = self.get_plugin_data(plugin_path)

        # Check plugin.json for custom hooks path
        if plugin_data and "hooks" in plugin_data:
            hooks_config = plugin_data["hooks"]
            if isinstance(hooks_config, str):
                custom_path = plugin_path / hooks_config.lstrip("./")
                if custom_path.exists() and custom_path.is_file():
                    return custom_path

        # Check default location
        default_hooks = plugin_path / "hooks" / "hooks.json"
        if default_hooks.exists():
            return default_hooks

        return None

    def __str__(self):
        """String representation of context"""
        return f"RepositoryContext(type={self.repo_type.value}, plugins={len(self.plugins)})"
