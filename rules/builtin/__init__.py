"""
Builtin linting rules for Claude Code plugins
"""

from .plugin_structure import (
    PluginJsonRequiredRule,
    PluginJsonValidRule,
    PluginNamingRule,
    CommandsDirRequiredRule,
    CommandsExistRule,
    PluginReadmeRule,
    PluginMetadataCompletenessRule,
)

from .command_format import (
    CommandNamingRule,
    CommandFrontmatterRule,
    CommandSectionsRule,
    CommandNameFormatRule,
)

from .marketplace import (
    MarketplaceJsonValidRule,
    MarketplaceRegistrationRule,
)

from .skills import (
    SkillFrontmatterRule,
)

from .agents import (
    AgentFrontmatterRule,
)

from .hooks import (
    HookValidationRule,
)


# All builtin rules
BUILTIN_RULES = [
    # Plugin structure
    PluginJsonRequiredRule,
    PluginJsonValidRule,
    PluginNamingRule,
    CommandsDirRequiredRule,
    CommandsExistRule,
    PluginReadmeRule,
    PluginMetadataCompletenessRule,
    # Command format
    CommandNamingRule,
    CommandFrontmatterRule,
    CommandSectionsRule,
    CommandNameFormatRule,
    # Marketplace
    MarketplaceJsonValidRule,
    MarketplaceRegistrationRule,
    # Skills
    SkillFrontmatterRule,
    # Agents
    AgentFrontmatterRule,
    # Hooks
    HookValidationRule,
]


__all__ = [
    "BUILTIN_RULES",
    # Export individual rules too
    "PluginJsonRequiredRule",
    "PluginJsonValidRule",
    "PluginNamingRule",
    "CommandsDirRequiredRule",
    "CommandsExistRule",
    "PluginReadmeRule",
    "PluginMetadataCompletenessRule",
    "CommandNamingRule",
    "CommandFrontmatterRule",
    "CommandSectionsRule",
    "CommandNameFormatRule",
    "MarketplaceJsonValidRule",
    "MarketplaceRegistrationRule",
    "SkillFrontmatterRule",
    "AgentFrontmatterRule",
    "HookValidationRule",
]
