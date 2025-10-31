# claudelint

A configurable, rule-based linter for [Claude Code](https://docs.claude.com/en/docs/claude-code) plugins.

## Features

✨ **Context-Aware** - Automatically detects single plugin vs marketplace repositories  
🎯 **Rule-Based** - Enable/disable individual rules with configurable severity levels  
🔌 **Extensible** - Load custom rules from Python files  
📋 **Comprehensive** - Validates plugin structure, metadata, command format, and more  
🐳 **Containerized** - Run via Docker for consistent, isolated linting  
⚡ **Fast** - Efficient validation with clear, actionable output

## Installation

### Via pip (recommended)

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

## Configuration

Create `.claudelint.yaml` in your repository root:

```yaml
# Custom plugin directories (defaults shown)
plugin-directories:
  - plugins
  - .claude/plugins
  - .claude-plugin/plugins

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
    # Customize required sections (defaults shown)
    sections:
      - Name
      - Synopsis
      - Description
      - Implementation

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

### Customizing Plugin Discovery

By default, claudelint searches for plugins in these directories:
- `plugins/`
- `.claude/plugins/`
- `.claude-plugin/plugins/`

You can customize this in `.claudelint.yaml`:

```yaml
plugin-directories:
  - custom-plugins
  - src/plugins
```

### Customizing Command Sections

The `command-sections` rule validates that command files have specific sections. You can customize which sections are required:

```yaml
rules:
  command-sections:
    enabled: true
    severity: warning
    sections:
      - Name
      - Synopsis
      - Description
      - Implementation
      - Examples  # Add custom sections
```

## Builtin Rules

### Plugin Structure

| Rule ID | Description | Default Severity |
|---------|-------------|------------------|
| `plugin-json-required` | Plugin must have `.claude-plugin/plugin.json` | error |
| `plugin-json-valid` | Plugin.json must be valid with required fields | error |
| `plugin-naming` | Plugin names should use kebab-case | warning |
| `commands-dir-required` | Plugin should have a commands directory | warning (disabled by default) |
| `commands-exist` | Plugin should have at least one command file | info (disabled by default) |
| `plugin-readme` | Plugin should have a README.md file | warning |

### Command Format

| Rule ID | Description | Default Severity |
|---------|-------------|------------------|
| `command-naming` | Command files should use kebab-case | warning |
| `command-frontmatter` | Command files must have valid frontmatter | error |
| `command-sections` | Commands should have Name, Synopsis, Description, Implementation sections | warning |
| `command-name-format` | Command Name section should be `plugin:command` format | warning |

### Marketplace

| Rule ID | Description | Default Severity |
|---------|-------------|------------------|
| `marketplace-json-valid` | Marketplace.json must be valid JSON | error (auto) |
| `marketplace-registration` | Plugins must be registered in marketplace.json | error (auto) |

### Skills

| Rule ID | Description | Default Severity |
|---------|-------------|------------------|
| `skill-frontmatter` | SKILL.md files should have frontmatter | warning |

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
├── Containerfile        # Container image
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

