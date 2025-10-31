# Mac-Setup Modular Architecture

## Overview

Mac-Setup has been refactored into a fully modular, plugin-based architecture that allows complete customization and extensibility. This document describes the system design and how to use it.

## Core Components

### 1. Configuration Engine (`cli/config_engine.py`)

The configuration engine manages all setup settings from multiple sources with clear priority order:

```
CLI Arguments (highest)
  ↓
Environment Variables (MAC_SETUP_*)
  ↓
Local User Config (~/.devkit/config.yaml)
  ↓
Group Config (config/groups/{group}.yaml)
  ↓
Role Config (config/roles/{role}.yaml)
  ↓
Platform Config (config/platforms/{platform}.yaml)
  ↓
Schema Defaults (lowest)
```

#### Configuration Schema

See `config/schema.yaml` for the complete schema definition.

#### Usage Examples

```python
from cli.config_engine import ConfigurationEngine

# Load configuration
engine = ConfigurationEngine(project_root="/path/to/devkit")
config = engine.load_all(group="development", platform="macos")

# Get values (dot notation)
log_level = engine.get("global.logging.level")
enabled_roles = engine.get("global.enabled_roles")

# Set values
engine.set("global.logging.level", "debug")

# Validate
is_valid, errors = engine.validate()

# Export
yaml_output = engine.export("yaml")
json_output = engine.export("json")

# Save
engine.save("~/.devkit/config.yaml")
```

#### Environment Variables

Configure via environment variables using the `MAC_SETUP_` prefix:

```bash
# Simple values
MAC_SETUP_LOGGING_LEVEL=debug

# Arrays (comma-separated)
MAC_SETUP_ENABLED_ROLES=core,shell,editors,development

# Nested keys (double underscore)
MAC_SETUP_GLOBAL__LOGGING__LEVEL=debug
MAC_SETUP_GLOBAL__PERFORMANCE__PARALLEL_TASKS=8
```

### 2. Plugin System (`cli/plugin_system.py`)

The plugin system enables extending devkit with custom functionality.

#### Creating Plugins

```python
from cli.plugin_system import PluginInterface, HookInterface, HookContext

class MyPlugin(PluginInterface):
    name = "my_plugin"
    version = "1.0.0"
    description = "My custom plugin"

    def initialize(self) -> None:
        """Initialize plugin"""
        pass

    def get_roles(self) -> Dict[str, Path]:
        """Return custom Ansible roles"""
        return {
            "custom_role": Path(__file__).parent / "roles" / "custom_role"
        }

    def get_hooks(self) -> Dict[str, List[HookInterface]]:
        """Return hooks for various stages"""
        return {
            "pre_setup": [MyPreSetupHook()],
            "post_setup": [MyPostSetupHook()],
        }

    def validate(self) -> tuple[bool, List[str]]:
        """Validate plugin configuration"""
        return True, []


class MyPreSetupHook(HookInterface):
    def execute(self, context: HookContext) -> bool:
        """Execute before setup"""
        print(f"Pre-setup: {context.stage}")
        return True
```

#### Plugin Directories

Plugins are auto-discovered from:

```
~/.devkit/plugins/          # User plugins
./plugins/                       # Project plugins
```

#### Plugin Loading

```python
from cli.plugin_system import PluginLoader

loader = PluginLoader()
loader.add_plugin_path(Path.home() / ".devkit" / "plugins")
loaded_count = loader.load_all()

# Get plugin roles
custom_roles = loader.get_plugin_roles()

# Execute hooks
context = HookContext(stage="pre_setup")
loader.execute_hooks("pre_setup", context)
```

### 3. Role-Based Architecture

Roles are organized by functionality:

```
ansible/roles/
├── core/              # Base system, Homebrew, paths
├── shell/             # Zsh, Fish, PowerShell
├── editors/           # Neovim, VS Code, JetBrains
├── languages/         # Node, Python, Go, Ruby
├── containers/        # Docker, Kubernetes
├── cloud/             # AWS, Azure, GCP tools
├── security/          # SSH, GPG, audit logging
├── development/       # Git, formatters, linters
├── databases/         # PostgreSQL, MongoDB, Redis
├── macos/             # macOS-specific features
├── linux/             # Linux-specific features
└── custom/            # User-defined roles
```

#### Role Structure

Each role follows standard Ansible structure:

```
role_name/
├── tasks/
│   └── main.yml           # Role tasks
├── handlers/
│   └── main.yml           # Event handlers
├── templates/
│   └── *.j2               # Jinja2 templates
├── files/
│   └── *                  # Static files
├── vars/
│   └── main.yml           # Role variables
└── defaults/
    └── main.yml           # Default variables
```

#### Role Tags

Each role supports tags for selective execution:

```bash
# Install only shell role
ansible-playbook setup.yml --tags shell

# Install multiple roles
ansible-playbook setup.yml --tags "core,shell,editors"

# Skip specific role
ansible-playbook setup.yml --skip-tags security
```

### 4. Setup Wizard (`cli/setup_wizard.py`)

Interactive CLI for first-time configuration:

```bash
python cli/setup_wizard.py
```

#### Features

- Step-by-step configuration
- Role selection with descriptions
- Shell preference (Zsh, Fish)
- Editor selection (Neovim, VS Code, JetBrains)
- Security options (SSH, GPG)
- Backup configuration
- Settings confirmation

#### Programmatic Usage

```python
from cli.setup_wizard import SetupWizard

wizard = SetupWizard(project_root="/path/to/devkit")
config = wizard.run()
config_file = wizard.save_config("~/.devkit/config.yaml")
```

### 5. Test Suite (`tests/test_suite.py`)

Comprehensive testing framework:

```bash
python tests/test_suite.py
```

#### Test Categories

- **Configuration Tests**: Validates config engine and files
- **Ansible Tests**: Syntax checking and linting
- **Role Tests**: Role structure and validity
- **Plugin Tests**: Plugin system functionality
- **Verification Tests**: Required tools availability

#### Programmatic Usage

```python
from tests.test_suite import TestSuite

suite = TestSuite(project_root="/path/to/devkit")
exit_code = suite.run_all()
```

## Configuration Files

### Main Playbook (`setup.yml`)

The main entry point that orchestrates all roles:

```yaml
---
- name: Setup Development Environment
  hosts: all
  gather_facts: yes

  vars_files:
    - config/config.yaml

  pre_tasks:
    - name: Load configuration
      include_role:
        name: core

  roles:
    - role: core
      tags: [core]
    - role: shell
      when: "'shell' in enabled_roles"
      tags: [shell]
    - role: editors
      when: "'editors' in enabled_roles"
      tags: [editors]
    - role: languages
      when: "'languages' in enabled_roles"
      tags: [languages]
    # ... additional roles

  post_tasks:
    - name: Run verification
      include_role:
        name: verification
      when: verify_after_setup
```

### Inventory (`inventory.yml`)

Fleet management with groups:

```yaml
all:
  children:
    development:
      hosts:
        dev-machine-1:
        dev-machine-2:
    design:
      hosts:
        design-station:
    qa:
      hosts:
        qa-box:
    sre:
      hosts:
        devops-1:
        devops-2:
```

### Group Variables (`group_vars/`)

Override configuration per group:

```yaml
# group_vars/sre.yml
enabled_roles:
  - core
  - shell
  - languages
  - containers
  - cloud
  - security
  - development

disabled_roles: []

logging:
  level: debug
```

### Host Variables (`host_vars/`)

Override configuration per machine:

```yaml
# host_vars/special-machine.yml
enabled_roles:
  - core
  - shell
  - editors
  - languages

security:
  enable_ssh_setup: true
  enable_gpg_setup: true
```

### Role Configuration (`config/roles/`)

Role-specific configuration:

```yaml
# config/roles/shell.yml
shell:
  config:
    shell_choice: zsh
    install_plugins: true
    theme: powerlevel10k
```

### Platform Configuration (`config/platforms/`)

Platform-specific overrides:

```yaml
# config/platforms/macos.yml
platforms:
  macos:
    enabled_roles:
      - core
      - shell
      - editors
      - macos
    role_configs:
      macos:
        dock_apps:
          - /Applications/Finder.app
          - /Applications/Terminal.app
```

## Workflow

### 1. Initial Setup

```bash
# Interactive setup with wizard
./bootstrap.sh

# Or configure manually
python cli/setup_wizard.py
```

### 2. Run Setup

```bash
# Run all enabled roles
ansible-playbook -i inventory.yml setup.yml

# Run specific roles
ansible-playbook -i inventory.yml setup.yml --tags "core,shell,editors"

# Dry-run (check mode)
ansible-playbook -i inventory.yml setup.yml --check

# Verbose output
ansible-playbook -i inventory.yml setup.yml -vvv
```

### 3. Verify Installation

```bash
# Run verification suite
./verify-setup.sh

# Run tests
python tests/test_suite.py
```

### 4. Customize

#### Create Custom Role

```bash
mkdir -p ansible/roles/my_custom/tasks
cat > ansible/roles/my_custom/tasks/main.yml << 'EOF'
- name: My custom task
  debug:
    msg: "Running custom role"
EOF
```

#### Create Plugin

```bash
mkdir -p ~/.devkit/plugins
cat > ~/.devkit/plugins/my_plugin.py << 'EOF'
from cli.plugin_system import PluginInterface

class MyPlugin(PluginInterface):
    name = "my_plugin"
    version = "1.0.0"
    description = "My plugin"

    # ... implement methods
EOF
```

#### Override Configuration

```bash
# Create user config
cat > ~/.devkit/config.yaml << 'EOF'
global:
  logging:
    level: debug
  enabled_roles:
    - core
    - shell
    - editors
EOF
```

## Extensibility

### Adding Custom Roles

1. Create role directory under `ansible/roles/`
2. Add `tasks/main.yml` with your tasks
3. Enable in configuration

### Adding Plugins

1. Create plugin class extending `PluginInterface`
2. Implement required methods
3. Place in `~/.devkit/plugins/`
4. Auto-discovered on startup

### Adding Hooks

1. Create hook class extending `HookInterface`
2. Implement `execute(context)` method
3. Register in plugin's `get_hooks()`
4. Hooks are called at appropriate stages

### Custom Brewfiles

```bash
# Per-role Brewfile
ansible/roles/my_role/files/Brewfile

# Per-group Brewfile
config/groups/my_group/Brewfile
```

## Performance Optimization

### Parallel Execution

```yaml
global:
  performance:
    parallel_tasks: 8
```

### Caching

```yaml
global:
  performance:
    cache_downloads: true
```

### Selective Execution

```bash
# Only install core and shell (faster)
ansible-playbook setup.yml --tags "core,shell"

# Skip slow tasks
ansible-playbook setup.yml --skip-tags "gui_apps"
```

## Troubleshooting

### Configuration Issues

```bash
# Validate configuration
python cli/config_engine.py --validate

# Export configuration
python cli/config_engine.py --export yaml

# Get specific value
python cli/config_engine.py --get global.enabled_roles
```

### Role Issues

```bash
# Run specific role with verbose output
ansible-playbook setup.yml --tags shell -vvv

# Dry-run before executing
ansible-playbook setup.yml --tags shell --check

# Check role syntax
ansible-playbook --syntax-check setup.yml
```

### Plugin Issues

```bash
# List loaded plugins
python cli/plugin_system.py --list

# Show plugin info
python cli/plugin_system.py --info

# Validate plugins
python cli/plugin_system.py --validate
```

### Test Issues

```bash
# Run tests with verbose output
python tests/test_suite.py -v

# Run specific test category
python tests/test_suite.py --verbose
```

## Best Practices

1. **Use Configuration**: Leverage `config/config.yaml` for customization
2. **Group Overrides**: Use `group_vars/` for team configurations
3. **Host Overrides**: Use `host_vars/` for machine-specific settings
4. **Plugins**: Create plugins for custom extensions (don't modify core)
5. **Testing**: Run tests before and after major changes
6. **Backups**: Enable backups in configuration
7. **Verification**: Run verification after setup
8. **Documentation**: Document custom roles and plugins
9. **Version Control**: Track config changes in git
10. **Incremental**: Use tags to apply changes incrementally

## Architecture Decisions (ADRs)

### ADR-001: Modular Role-Based Architecture

**Decision**: Split monolithic playbook into modular roles for:

- Reusability
- Testability
- Customization
- Maintainability

### ADR-002: Configuration Priority Chain

**Decision**: Use configuration priority chain instead of single file:

- Enables CLI overrides
- Supports environment variables
- Allows group and host overrides
- Maintains sensible defaults

### ADR-003: Plugin System for Extensibility

**Decision**: Implement plugin system instead of forking:

- Users can add custom functionality
- No need to modify core code
- Easy distribution of custom extensions
- Clear plugin API

## Getting Help

- **Documentation**: See `docs/` directory
- **Examples**: See `config/` directory
- **Tests**: Run `python tests/test_suite.py`
- **Logs**: Check `~/.devkit/logs/setup.log`
