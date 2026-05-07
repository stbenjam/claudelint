> **This project has been renamed to [skillsaw](https://github.com/stbenjam/skillsaw).** This repository is no longer maintained. Please use `skillsaw` for all new installations — the `claudelint` PyPI package and Docker image will continue to work as aliases but will not receive updates.

[![PyPI version](https://badge.fury.io/py/claudelint.svg)](https://badge.fury.io/py/claudelint)
[![PyPI Downloads](https://img.shields.io/pypi/dm/claudelint)](https://pypi.org/project/claudelint/)
[![Tests](https://github.com/stbenjam/claudelint/workflows/Tests/badge.svg)](https://github.com/stbenjam/claudelint/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/stbenjam/claudelint/branch/main/graph/badge.svg)](https://codecov.io/gh/stbenjam/claudelint)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python Versions](https://img.shields.io/pypi/pyversions/claudelint.svg)](https://pypi.org/project/claudelint/)

# claudelint

A configurable, rule-based linter for [Claude Code](https://docs.claude.com/en/docs/claude-code) [plugins](https://docs.claude.com/en/docs/claude-code/plugins) and [plugin marketplaces](https://docs.claude.com/en/docs/claude-code/plugin-marketplaces).

## Features

✨ **Context-Aware** - Automatically detects single plugin vs marketplace repositories  
🎯 **Rule-Based** - Enable/disable individual rules with configurable severity levels  
🔌 **Extensible** - Load custom rules from Python files  
📋 **Comprehensive** - Validates plugin structure, metadata, command format, and more  
🐳 **Containerized** - Run via Docker for consistent, isolated linting  
⚡ **Fast** - Efficient validation with clear, actionable output

## Installation

### Via uvx (easiest - no install required)

```bash
# From git (works before PyPI release)
uvx --from 'git+https://github.com/stbenjam/claudelint' claudelint

# Once published to PyPI, simply:
uvx claudelint

# With specific path
uvx --from 'git+https://github.com/stbenjam/claudelint' claudelint /path/to/plugin
```

### Via pip (recommended for regular use)

```bash
pip install claudelint
```

### From source

```bash
git clone https://github.com/stbenjam/claudelint.git
cd claudelint
pip install -e .
```

### Using Docker

```bash
docker pull ghcr.io/stbenjam/claudelint:latest

# Run on current directory
docker run -v $(pwd):/workspace ghcr.io/stbenjam/claudelint
```

## Quick Start

```bash
# Lint current directory
claudelint

# Lint specific directory
claudelint /path/to/plugin

# Verbose output
claudelint -v

# Strict mode (warnings as errors)
claudelint --strict

# Generate default config
claudelint --init

# List all available rules
claudelint --list-rules
```

## Repository Types

claudelint automatically detects your repository structure:

### Single Plugin
```
my-plugin/
├── .claude-plugin/
│   └── plugin.json
├── commands/
│   └── my-command.md
└── README.md
```

### Marketplace (Multiple Plugins)

claudelint supports multiple marketplace structures per the [Claude Code specification](https://docs.claude.com/en/docs/claude-code/plugin-marketplaces):

#### Traditional Structure (plugins/ directory)
```
marketplace/
├── .claude-plugin/
│   └── marketplace.json
└── plugins/
    ├── plugin-one/
    │   ├── .claude-plugin/
    │   └── commands/
    └── plugin-two/
        ├── .claude-plugin/
        └── commands/
```

#### Flat Structure (root-level plugin)
```
marketplace/
├── .claude-plugin/
│   └── marketplace.json    # source: "./"
├── commands/                # Plugin components at root
│   └── my-command.md
└── skills/
    └── my-skill/
```

#### Custom Paths
```
marketplace/
├── .claude-plugin/
│   └── marketplace.json    # source: "./custom/my-plugin"
└── custom/
    └── my-plugin/
        ├── commands/
        └── skills/
```

#### Mixed Structures
Plugins from `plugins/`, custom paths, and remote sources can coexist in one marketplace. Only local sources are validated.

## Marketplace Features

### Flexible Plugin Sources

claudelint understands all [plugin source types](https://docs.claude.com/en/docs/claude-code/plugin-marketplaces#plugin-sources) and validates any sources that resolve to local paths:

- **Relative paths**: `"source": "./"` (flat structure), `"source": "./custom/path"`
- **GitHub repositories**: `"source": {"source": "github", "repo": "owner/repo"}`
- **Git URLs**: `"source": {"source": "url", "url": "https://..."}`

Remote sources (GitHub, git URLs) are logged and skipped during local validation. They are valid per spec but cannot be checked until the plugin is fetched locally.

### Strict Mode

The `strict` field in marketplace entries controls validation behavior:

```json5
{
  "name": "my-plugin",
  "source": "./",
  "strict": false,    // plugin.json becomes optional
  "description": "Plugin description can be in marketplace.json"
}
```

When `strict: false`:
- `plugin.json` is optional
- Marketplace entry serves as the complete plugin manifest
- Plugin metadata is validated from marketplace.json
- Skills, commands, and other components work normally

When `strict: true` (default):
- `plugin.json` is required
- Marketplace entry supplements plugin.json metadata

## Configuration

Create `.claudelint.yaml` in your repository root:

```yaml
# Enable/disable rules
rules:
  plugin-json-required:
    enabled: true
    severity: error
  
  plugin-naming:
    enabled: true
    severity: warning
  
  command-sections:
    enabled: true
    severity: warning
  
  # 'auto' enables only for marketplace repos
  marketplace-registration:
    enabled: auto
    severity: error

# Load custom rules
custom-rules:
  - ./my-custom-rules.py

# Exclude patterns
exclude:
  - "**/node_modules/**"
  - "**/.git/**"

# Treat warnings as errors
strict: false
```

### Generating Default Config

```bash
claudelint --init
```

This creates `.claudelint.yaml` with all builtin rules enabled.

## Builtin Rules

### Plugin Structure

| Rule ID | Description | Default Severity | Notes |
|---------|-------------|------------------|-------|
| `plugin-json-required` | Plugin must have `.claude-plugin/plugin.json` | error | Skipped when `strict: false` in marketplace |
| `plugin-json-valid` | Plugin.json must be valid with required fields | error | |
| `plugin-naming` | Plugin names should use kebab-case | warning | |
| `commands-dir-required` | Plugin should have a commands directory | warning (disabled by default) | |
| `commands-exist` | Plugin should have at least one command file | info (disabled by default) | |
| `plugin-readme` | Plugin should have a README.md file | warning | |

### Command Format

| Rule ID | Description | Default Severity |
|---------|-------------|------------------|
| `command-naming` | Command files should use kebab-case | warning |
| `command-frontmatter` | Command files must have valid frontmatter | error |
| `command-sections` | Commands should have Name, Synopsis, Description, Implementation sections | warning |
| `command-name-format` | Command Name section should be `plugin:command` format | warning |

### Marketplace

| Rule ID | Description | Default Severity | Notes |
|---------|-------------|------------------|-------|
| `marketplace-json-valid` | Marketplace.json must be valid JSON | error (auto) | |
| `marketplace-registration` | Plugins must be registered in marketplace.json | error (auto) | Supports flat structures, custom paths, and remote sources |

### Skills

| Rule ID | Description | Default Severity |
|---------|-------------|------------------|
| `skill-frontmatter` | SKILL.md files should have frontmatter | warning |

### Agents

| Rule ID | Description | Default Severity |
|---------|-------------|------------------|
| `agent-frontmatter` | Agent files must have valid frontmatter with description and capabilities | error |

### Hooks

| Rule ID | Description | Default Severity |
|---------|-------------|------------------|
| `hooks-json-valid` | hooks.json must be valid JSON with proper hook configuration structure | error |

### MCP (Model Context Protocol)

| Rule ID | Description | Default Severity | Notes |
|---------|-------------|------------------|-------|
| `mcp-valid-json` | MCP configuration must be valid JSON with proper mcpServers structure | error | Validates both `.mcp.json` and `mcpServers` in `plugin.json` |
| `mcp-prohibited` | Plugins should not enable MCP servers | error (disabled by default) | Security/policy rule - enable to prohibit MCP usage |

## Custom Rules

Create custom validation rules by extending the `Rule` base class:

```python
# my_custom_rules.py
from pathlib import Path
from typing import List
from claudelint import Rule, RuleViolation, Severity, RepositoryContext

class NoTodoCommentsRule(Rule):
    @property
    def rule_id(self) -> str:
        return "no-todo-comments"
    
    @property
    def description(self) -> str:
        return "Command files should not contain TODO comments"
    
    def default_severity(self) -> Severity:
        return Severity.WARNING
    
    def check(self, context: RepositoryContext) -> List[RuleViolation]:
        violations = []
        
        for plugin_path in context.plugins:
            commands_dir = plugin_path / "commands"
            if not commands_dir.exists():
                continue
            
            for cmd_file in commands_dir.glob("*.md"):
                with open(cmd_file, 'r') as f:
                    content = f.read()
                    if 'TODO' in content:
                        violations.append(
                            self.violation(
                                "Found TODO comment in command file",
                                file_path=cmd_file
                            )
                        )
        
        return violations
```

Then reference it in `.claudelint.yaml`:

```yaml
custom-rules:
  - ./my_custom_rules.py

rules:
  no-todo-comments:
    enabled: true
    severity: warning
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Lint Claude Plugins

on: [pull_request, push]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.x'
      
      - name: Install claudelint
        run: pip install claudelint
      
      - name: Run linter
        run: claudelint --strict
```

### GitLab CI

```yaml
lint-plugins:
  image: python:3.11
  script:
    - pip install claudelint
    - claudelint --strict
```

### Docker

```bash
docker run -v $(pwd):/workspace -w /workspace ghcr.io/stbenjam/claudelint --strict
```

## Exit Codes

- `0` - Success (no errors, or warnings only in non-strict mode)
- `1` - Failure (errors found, or warnings in strict mode)

## Examples

### Example Output

```
Linting Claude plugins in: /path/to/marketplace

Errors:
  ✗ ERROR [plugins/git/.claude-plugin/plugin.json]: Missing plugin.json
  ✗ ERROR [.claude-plugin/marketplace.json]: Plugin 'new-plugin' not registered

Warnings:
  ⚠ WARNING [plugins/utils]: Missing README.md (recommended)
  ⚠ WARNING [plugins/jira/commands/solve.md]: Missing recommended section '## Implementation'

Summary:
  Errors:   2
  Warnings: 2
```

### Disabling Specific Rules

```yaml
rules:
  plugin-readme:
    enabled: false  # Don't require README files
  
  command-sections:
    enabled: false  # Don't check for specific sections
```

### Changing Severity

```yaml
rules:
  plugin-naming:
    severity: error  # Make naming violations errors instead of warnings
  
  command-name-format:
    severity: info   # Downgrade to info level
```

## Development

### Running Tests

```bash
pytest tests/
```

### Building Docker Image

```bash
docker build -t claudelint .
```

### Project Structure

```
claudelint/
├── src/
│   ├── rule.py          # Base Rule class
│   ├── context.py       # Repository detection
│   ├── config.py        # Configuration management
│   └── linter.py        # Main linter orchestration
├── rules/
│   └── builtin/         # Builtin validation rules
├── tests/               # Test suite
├── examples/            # Example configs and custom rules
├── claudelint           # CLI entry point
├── Dockerfile           # Container image
└── pyproject.toml       # Package metadata
```

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

Apache 2.0 - See [LICENSE](LICENSE) for details.

## See Also

- [Claude Code Documentation](https://docs.claude.com/en/docs/claude-code)
- [Claude Code Plugins Reference](https://docs.claude.com/en/docs/claude-code/plugins-reference)
- [AI Helpers Marketplace](https://github.com/openshift-eng/ai-helpers) - Example repository using claudelint

## Support

- **Issues**: https://github.com/stbenjam/claudelint/issues
- **Discussions**: https://github.com/stbenjam/claudelint/discussions

