# Plugin Development Guide

This guide explains how to create custom plugins and roles for mac-setup.

## Plugin System Overview

Plugins allow you to extend mac-setup with custom functionality without modifying core code.

### What Plugins Can Do

- Add custom Ansible roles
- Define hooks at various setup stages
- Customize configuration
- Add custom tasks and checks
- Extend functionality for specific needs

### Plugin Anatomy

A plugin must implement the `PluginInterface`:

```python
from cli.plugin_system import PluginInterface, HookInterface, HookContext
from pathlib import Path
from typing import Dict, List

class MyPlugin(PluginInterface):
    name = "my_plugin"
    version = "1.0.0"
    description = "My custom plugin"

    def initialize(self) -> None:
        """Called when plugin is loaded."""
        pass

    def get_roles(self) -> Dict[str, Path]:
        """Return custom Ansible roles provided by plugin."""
        return {
            "my_role": Path(__file__).parent / "roles" / "my_role"
        }

    def get_hooks(self) -> Dict[str, List[HookInterface]]:
        """Return hooks for various stages."""
        return {
            "pre_setup": [MyPreSetupHook()],
            "post_setup": [MyPostSetupHook()],
            "pre_role": [MyPreRoleHook()],
            "post_role": [MyPostRoleHook()],
        }

    def validate(self) -> tuple[bool, List[str]]:
        """Validate plugin configuration. Return (is_valid, error_list)."""
        return True, []
```

## Hook System

Hooks are called at various stages of the setup process:

### Hook Stages

1. **pre_setup**: Before any setup tasks
2. **pre_role**: Before each role
3. **post_role**: After each role
4. **post_setup**: After all setup tasks

### Hook Context

```python
@dataclass
class HookContext:
    stage: str              # "pre_setup", "post_setup", "pre_role", "post_role"
    role: Optional[str]     # Role name (for pre_role, post_role)
    task: Optional[str]     # Task name
    status: str             # "running", "success", "failed"
    error: Optional[str]    # Error message if failed
    metadata: Dict[str, Any]  # Additional context
```

### Implementing Hooks

```python
from cli.plugin_system import HookInterface, HookContext

class MyPreSetupHook(HookInterface):
    def execute(self, context: HookContext) -> bool:
        """
        Execute hook.

        Returns:
            True if successful, False to abort setup
        """
        print(f"Pre-setup hook starting...")

        # Perform validation
        if not self._validate_environment():
            context.error = "Environment validation failed"
            return False

        # Perform setup
        self._prepare_system()

        return True

    def _validate_environment(self) -> bool:
        """Validate environment before setup."""
        # Check required tools
        import subprocess
        try:
            subprocess.run(["git", "--version"], capture_output=True, check=True)
            return True
        except:
            return False

    def _prepare_system(self) -> None:
        """Prepare system for setup."""
        pass


class MyPostSetupHook(HookInterface):
    def execute(self, context: HookContext) -> bool:
        """Execute post-setup hook."""
        print(f"Post-setup hook completed setup: {context.status}")

        if context.status == "success":
            self._cleanup()
            self._verify()

        return True

    def _cleanup(self) -> None:
        """Cleanup after setup."""
        pass

    def _verify(self) -> None:
        """Verify setup completed successfully."""
        pass
```

## Creating Custom Roles

Plugins can provide custom Ansible roles:

### Role Structure

```
my_plugin/
├── roles/
│   └── my_role/
│       ├── tasks/
│       │   └── main.yml
│       ├── handlers/
│       │   └── main.yml
│       ├── templates/
│       ├── files/
│       ├── vars/
│       └── defaults/
├── __init__.py
└── my_plugin.py
```

### Example Role

```yaml
# roles/my_role/tasks/main.yml
---
- name: Install custom tools
  ansible.builtin.shell: |
    {{ homebrew_prefix }}/bin/brew install my-custom-tool
  changed_when: false
  tags: [my_role]

- name: Configure custom tool
  ansible.builtin.copy:
    content: |
      # My Custom Tool Configuration
      config_option: value
    dest: ~/.my_tool/config.yaml
    mode: '0644'
  tags: [my_role]

- name: Verify installation
  ansible.builtin.shell: my-custom-tool --version
  register: tool_version
  changed_when: false
  tags: [my_role]
```

## Example Plugins

### Plugin 1: Docker Development Plugin

```python
# ~/.devkit/plugins/docker_dev_plugin.py

from cli.plugin_system import PluginInterface, HookInterface, HookContext
from pathlib import Path
from typing import Dict, List


class DockerDevHook(HookInterface):
    def execute(self, context: HookContext) -> bool:
        if context.stage == "post_setup":
            print("Docker development setup complete!")
            print("Verify with: docker --version")
        return True


class DockerDevPlugin(PluginInterface):
    name = "docker_dev"
    version = "1.0.0"
    description = "Docker development environment setup"

    def initialize(self) -> None:
        print("Initializing Docker Dev plugin...")

    def get_roles(self) -> Dict[str, Path]:
        return {
            "docker_dev": Path(__file__).parent / "roles" / "docker_dev"
        }

    def get_hooks(self) -> Dict[str, List[HookInterface]]:
        return {
            "post_setup": [DockerDevHook()]
        }

    def validate(self) -> tuple[bool, List[str]]:
        errors = []

        # Validate Docker installation
        import subprocess
        try:
            subprocess.run(["docker", "--version"], capture_output=True, check=True)
        except:
            errors.append("Docker not found in PATH")

        return len(errors) == 0, errors
```

### Plugin 2: Custom Applications Plugin

```python
# ~/.devkit/plugins/custom_apps_plugin.py

from cli.plugin_system import PluginInterface, HookInterface, HookContext
from pathlib import Path
from typing import Dict, List
import subprocess


class CustomAppsPreSetupHook(HookInterface):
    def execute(self, context: HookContext) -> bool:
        print("Installing custom applications...")
        return True


class CustomAppsPlugin(PluginInterface):
    name = "custom_apps"
    version = "1.0.0"
    description = "Install custom applications"

    def initialize(self) -> None:
        self.custom_apps = {
            "figma": "figma-app",
            "slack": "slack",
            "discord": "discord",
        }

    def get_roles(self) -> Dict[str, Path]:
        return {
            "custom_apps": Path(__file__).parent / "roles" / "custom_apps"
        }

    def get_hooks(self) -> Dict[str, List[HookInterface]]:
        return {
            "pre_setup": [CustomAppsPreSetupHook()]
        }

    def validate(self) -> tuple[bool, List[str]]:
        return True, []
```

### Plugin 3: Configuration Backup Plugin

```python
# ~/.devkit/plugins/config_backup_plugin.py

from cli.plugin_system import PluginInterface, HookInterface, HookContext
from pathlib import Path
from typing import Dict, List
import shutil
from datetime import datetime


class ConfigBackupHook(HookInterface):
    def execute(self, context: HookContext) -> bool:
        if context.stage == "pre_setup":
            self._backup_configs()
        elif context.stage == "post_setup" and context.status == "failed":
            self._restore_configs()
        return True

    def _backup_configs(self) -> None:
        home = Path.home()
        backup_dir = home / ".mac-setup" / "config_backup" / datetime.now().isoformat()
        backup_dir.mkdir(parents=True, exist_ok=True)

        files_to_backup = [
            ".zshrc", ".bashrc", ".tmux.conf", ".config/nvim",
            ".config/Code/User/settings.json"
        ]

        for file in files_to_backup:
            src = home / file
            if src.exists():
                dst = backup_dir / file
                if src.is_dir():
                    shutil.copytree(src, dst, ignore=shutil.ignore_patterns('.git', '__pycache__'))
                else:
                    shutil.copy2(src, dst)

        print(f"Backup created at {backup_dir}")

    def _restore_configs(self) -> None:
        print("Restoring configuration from backup...")


class ConfigBackupPlugin(PluginInterface):
    name = "config_backup"
    version = "1.0.0"
    description = "Automatic configuration backup and restore"

    def initialize(self) -> None:
        pass

    def get_roles(self) -> Dict[str, Path]:
        return {}

    def get_hooks(self) -> Dict[str, List[HookInterface]]:
        return {
            "pre_setup": [ConfigBackupHook()],
            "post_setup": [ConfigBackupHook()],
        }

    def validate(self) -> tuple[bool, List[str]]:
        return True, []
```

## Installing Plugins

### From File System

```bash
# Create plugin directory
mkdir -p ~/.devkit/plugins

# Create plugin
cat > ~/.devkit/plugins/my_plugin.py << 'EOF'
# Your plugin code here
EOF

# Plugin is auto-discovered on next run
```

### From GitHub

```bash
# Clone plugin repository
git clone https://github.com/vietcgi/devkit-plugin.git ~/.devkit/plugins/my_plugin

# Or as submodule
cd /path/to/mac-setup
git submodule add https://github.com/vietcgi/devkit-plugin.git plugins/my_plugin
```

## Plugin Best Practices

### 1. Isolation

Keep plugins isolated from core code:

```python
# ✓ Good - Plugin has own directory
~/.devkit/plugins/my_plugin/
├── my_plugin.py
└── roles/

# ✗ Bad - Modifying core files
/Users/kevin/devkit/setup.yml  # Don't modify!
```

### 2. Error Handling

Always handle errors gracefully:

```python
def execute(self, context: HookContext) -> bool:
    try:
        # Your code here
        pass
    except Exception as e:
        context.error = str(e)
        return False
    return True
```

### 3. Logging

Use logging for debugging:

```python
import logging

logger = logging.getLogger("my_plugin")

def execute(self, context: HookContext) -> bool:
    logger.info("Hook executing...")
    logger.debug(f"Context: {context}")
    return True
```

### 4. Validation

Always validate configuration:

```python
def validate(self) -> tuple[bool, List[str]]:
    errors = []

    if not self._required_tool_available():
        errors.append("Required tool not found")

    if not self._valid_config():
        errors.append("Invalid configuration")

    return len(errors) == 0, errors
```

### 5. Documentation

Document your plugin:

```markdown
# My Plugin

## Description
What does your plugin do?

## Installation
How to install it?

## Configuration
How to configure it?

## Usage
How to use it?

## Requirements
What does it need?
```

## Testing Plugins

### Unit Tests

```python
# tests/test_my_plugin.py
import pytest
from my_plugin import MyPlugin


class TestMyPlugin:
    def test_plugin_loads(self):
        plugin = MyPlugin()
        assert plugin.name == "my_plugin"

    def test_validate_succeeds(self):
        plugin = MyPlugin()
        is_valid, errors = plugin.validate()
        assert is_valid
        assert len(errors) == 0

    def test_hooks_registered(self):
        plugin = MyPlugin()
        hooks = plugin.get_hooks()
        assert "pre_setup" in hooks
```

### Integration Tests

```bash
# Load plugin and run setup
python cli/plugin_system.py --list

# Verify plugin is loaded
python cli/plugin_system.py --info

# Run full test suite
python tests/test_suite.py
```

## Publishing Plugins

### GitHub Repository

```bash
# Create repository
git init my-mac-setup-plugin
cd my-mac-setup-plugin

# Structure
my-mac-setup-plugin/
├── my_plugin.py
├── roles/
├── tests/
├── docs/
└── README.md

# Push to GitHub
git remote add origin https://github.com/user/my-mac-setup-plugin
git push -u origin main
```

### Plugin Registry (Future)

Once we establish a plugin registry, you'll be able to:

```bash
# Install plugins from registry
mac-setup plugin install user/plugin-name

# Search for plugins
mac-setup plugin search keyword

# List installed plugins
mac-setup plugin list
```

## API Reference

### PluginInterface

```python
class PluginInterface(ABC):
    name: str                          # Plugin identifier
    version: str                       # Semantic version
    description: str                   # Human-readable description

    def initialize(self) -> None:
        """Called when plugin is loaded."""

    def get_roles(self) -> Dict[str, Path]:
        """Return custom Ansible roles. Maps role name to role path."""

    def get_hooks(self) -> Dict[str, List[HookInterface]]:
        """Return hooks. Maps stage name to list of hooks."""

    def validate(self) -> tuple[bool, List[str]]:
        """Validate plugin. Returns (is_valid, error_list)."""
```

### HookInterface

```python
class HookInterface(ABC):
    def execute(self, context: HookContext) -> bool:
        """Execute hook. Return True if successful."""
```

### HookContext

```python
@dataclass
class HookContext:
    stage: str                         # Hook stage name
    role: Optional[str]                # Role name (if applicable)
    task: Optional[str]                # Task name (if applicable)
    status: str                        # "running", "success", "failed"
    error: Optional[str]               # Error message (if failed)
    metadata: Dict[str, Any]           # Additional context
```

### PluginLoader

```python
class PluginLoader:
    def add_plugin_path(self, path: Path) -> None:
        """Add directory to plugin search path."""

    def discover_plugins(self) -> List[str]:
        """Auto-discover plugins. Returns list of discovered modules."""

    def load_plugin(self, plugin_path: str, module_name: str) -> Optional[PluginInterface]:
        """Load single plugin. Returns plugin instance or None."""

    def load_all(self, plugin_paths: Optional[List[Path]] = None) -> int:
        """Discover and load all plugins. Returns count of loaded plugins."""

    def get_plugin(self, name: str) -> Optional[PluginInterface]:
        """Get plugin by name."""

    def list_plugins(self) -> List[str]:
        """Get list of loaded plugin names."""

    def get_plugin_roles(self) -> Dict[str, Path]:
        """Get all custom roles from plugins."""

    def execute_hooks(self, stage: str, context: Optional[HookContext] = None) -> bool:
        """Execute hooks for stage. Returns True if all succeeded."""

    def get_plugin_info(self) -> Dict[str, Dict[str, Any]]:
        """Get info about all plugins."""
```

## Troubleshooting

### Plugin Not Loading

```python
# Check plugin syntax
python -m py_compile my_plugin.py

# Load and list plugins
python cli/plugin_system.py --list

# Show detailed info
python cli/plugin_system.py --info

# Check for errors in logs
tail -f ~/.devkit/logs/setup.log
```

### Hook Not Executing

1. Verify hook is registered in `get_hooks()`
2. Check hook stage name is correct
3. Ensure hook `execute()` returns `True`
4. Check logs for errors

### Role Not Found

1. Verify role directory exists
2. Check role name matches in `get_roles()`
3. Ensure role has `tasks/main.yml`
4. Verify Ansible can find role

## Getting Help

- Check plugin examples in `plugins/examples/`
- Review test suite for usage patterns
- Check documentation in `docs/`
- Report issues on GitHub
