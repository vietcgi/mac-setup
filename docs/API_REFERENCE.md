# Mac-Setup API Reference

Complete API documentation for mac-setup v2.0 components.

---

## Configuration Engine API

### ConfigurationEngine Class

```python
from cli.config_engine import ConfigurationEngine

engine = ConfigurationEngine(project_root=None, logger=None)
```

#### Methods

##### load_defaults()
Load default configuration from schema.
```python
engine.load_defaults()
```

##### load_file(file_path, section=None)
Load configuration from YAML file.
```python
config = engine.load_file('~/.devkit/config.yaml')
```

##### load_environment_overrides()
Load configuration from environment variables (MAC_SETUP_*).
```python
overrides = engine.load_environment_overrides()
```

##### load_all(group=None, platform=None, local_config=None)
Load all configuration in priority order.
```python
config = engine.load_all(group="development", platform="macos")
```

##### get(key, default=None)
Get configuration value using dot notation.
```python
level = engine.get("global.logging.level")
roles = engine.get("global.enabled_roles", [])
```

##### set(key, value)
Set configuration value using dot notation.
```python
engine.set("global.logging.level", "debug")
```

##### validate()
Validate configuration against schema.
```python
is_valid, errors = engine.validate()
```

##### export(format_type)
Export configuration in YAML or JSON format.
```python
yaml_str = engine.export("yaml")
json_str = engine.export("json")
```

##### save(file_path)
Save current configuration to file.
```python
engine.save("~/.devkit/config.yaml")
```

##### get_enabled_roles()
Get list of enabled roles based on current configuration.
```python
roles = engine.get_enabled_roles()
```

##### get_role_config(role)
Get configuration for specific role.
```python
config = engine.get_role_config("shell")
```

---

## Plugin System API

### PluginInterface (Abstract Base Class)

```python
from cli.plugin_system import PluginInterface, HookInterface, HookContext

class MyPlugin(PluginInterface):
    name = "my_plugin"
    version = "1.0.0"
    description = "Description"

    def initialize(self) -> None:
        """Called when plugin is loaded."""
        pass

    def get_roles(self) -> Dict[str, Path]:
        """Return custom Ansible roles."""
        return {}

    def get_hooks(self) -> Dict[str, List[HookInterface]]:
        """Return hooks for various stages."""
        return {}

    def validate(self) -> tuple[bool, List[str]]:
        """Validate plugin. Return (is_valid, error_list)."""
        return True, []
```

### HookInterface (Abstract Base Class)

```python
from cli.plugin_system import HookInterface, HookContext

class MyHook(HookInterface):
    def execute(self, context: HookContext) -> bool:
        """Execute hook. Return True if successful."""
        return True
```

### HookContext (Data Class)

```python
@dataclass
class HookContext:
    stage: str                      # Hook stage name
    role: Optional[str] = None      # Role name
    task: Optional[str] = None      # Task name
    status: str = "running"         # Status: running, success, failed
    error: Optional[str] = None     # Error message if failed
    metadata: Dict[str, Any] = None # Additional context
```

### PluginLoader Class

```python
from cli.plugin_system import PluginLoader
from pathlib import Path

loader = PluginLoader(logger=None)
```

#### Methods

##### add_plugin_path(path)
Add directory to plugin search path.
```python
loader.add_plugin_path(Path.home() / ".mac-setup" / "plugins")
```

##### discover_plugins()
Auto-discover plugins in configured paths.
```python
discovered = loader.discover_plugins()  # Returns list of (path, module_name)
```

##### load_plugin(plugin_path, module_name)
Load a single plugin module.
```python
plugin = loader.load_plugin("/path/to/plugin.py", "plugin_name")
```

##### load_all(plugin_paths=None)
Discover and load all plugins.
```python
count = loader.load_all()
```

##### get_plugin(name)
Get plugin by name.
```python
plugin = loader.get_plugin("docker_dev")
```

##### list_plugins()
Get list of loaded plugin names.
```python
plugins = loader.list_plugins()
```

##### get_plugin_roles()
Get all custom roles from loaded plugins.
```python
roles = loader.get_plugin_roles()
```

##### execute_hooks(stage, context=None)
Execute all hooks for a given stage.
```python
context = HookContext(stage="pre_setup")
success = loader.execute_hooks("pre_setup", context)
```

##### get_plugin_info()
Get information about all loaded plugins.
```python
info = loader.get_plugin_info()
```

---

## Setup Wizard API

### SetupWizard Class

```python
from cli.setup_wizard import SetupWizard

wizard = SetupWizard(project_root=None)
```

#### Methods

##### run()
Run the interactive setup wizard.
```python
config = wizard.run()  # Returns Dict[str, Any]
```

##### save_config(file_path=None)
Save configuration to file.
```python
path = wizard.save_config("~/.devkit/config.yaml")
```

---

## Test Suite API

### TestSuite Class

```python
from tests.test_suite import TestSuite

suite = TestSuite(project_root=None)
```

#### Methods

##### run_all()
Run all test suites.
```python
exit_code = suite.run_all()  # Returns 0 for pass, 1 for fail
```

#### Test Result Class

```python
@dataclass
class TestResult:
    name: str
    status: TestStatus  # PASS, FAIL, SKIP, WARN
    message: str
    duration: float = 0.0
    details: Optional[str] = None
```

---

## Environment Variables

### Configuration Overrides

Configure mac-setup via environment variables using MAC_SETUP_ prefix:

```bash
# Simple values
MAC_SETUP_LOGGING_LEVEL=debug

# Arrays (comma-separated)
MAC_SETUP_ENABLED_ROLES=core,shell,editors

# Nested keys (double underscore)
MAC_SETUP_GLOBAL__LOGGING__LEVEL=debug
MAC_SETUP_GLOBAL__PERFORMANCE__PARALLEL_TASKS=8
```

---

## Configuration Schema

### Global Settings

```yaml
global:
  setup_name: string              # Friendly name
  setup_environment: string       # development/staging/production
  enabled_roles: [string]         # List of roles to enable
  disabled_roles: [string]        # List of roles to disable

  logging:
    enabled: boolean
    level: string                 # debug/info/warning/error
    file: string
    archive: boolean

  performance:
    parallel_tasks: integer
    timeout: integer              # Seconds
    cache_downloads: boolean

  backup:
    enabled: boolean
    path: string
    max_backups: integer
    compress: boolean

  verification:
    enabled: boolean
    run_after_setup: boolean
    detailed_report: boolean

  security:
    enable_ssh_setup: boolean
    enable_gpg_setup: boolean
    enable_audit_logging: boolean
    require_verification: boolean

  updates:
    check_for_updates: boolean
    auto_update_tools: boolean
    update_interval: string       # daily/weekly/monthly
```

---

## Command-Line Interfaces

### Configuration Engine CLI

```bash
python cli/config_engine.py [OPTIONS]

Options:
  --project-root PATH        Path to project root
  --group GROUP             Machine group
  --platform PLATFORM       Platform (macos/linux)
  --config PATH            Custom config file
  --get KEY                Get config value (dot notation)
  --set KEY VALUE          Set config value
  --validate               Validate configuration
  --export {yaml,json}     Export configuration
  --list-files             List loaded files
  --list-roles             List enabled roles
```

### Plugin System CLI

```bash
python cli/plugin_system.py [OPTIONS]

Options:
  --plugin-path PATH       Add plugin path
  --list                   List plugins
  --info                   Show plugin info
  --validate               Validate plugins
```

### Setup Wizard CLI

```bash
python cli/setup_wizard.py [OPTIONS]

Options:
  --skip-wizard           Skip interactive wizard
  --config PATH           Custom config file
  --project-root PATH     Path to project root
```

### Test Suite CLI

```bash
python tests/test_suite.py [OPTIONS]

Options:
  --project-root PATH     Path to project root
  --verbose, -v           Verbose output
```

---

## Exit Codes

### Configuration Engine
- 0: Success
- 1: Validation failed

### Plugin System
- 0: Success
- 1: Plugin loading failed

### Setup Wizard
- 0: Setup completed
- 1: Setup cancelled

### Test Suite
- 0: All tests passed
- 1: Some tests failed

---

## Error Handling

All components implement consistent error handling:

```python
try:
    result = operation()
except Exception as e:
    logger.error(f"Operation failed: {e}")
    # Graceful degradation or user notification
```

Errors are logged and reported clearly to the user.

---

## Best Practices

1. **Always validate** configurations before applying:
   ```python
   is_valid, errors = engine.validate()
   ```

2. **Use dot notation** for configuration access:
   ```python
   value = engine.get("global.logging.level")
   ```

3. **Load in order** - use load_all() for proper priority:
   ```python
   config = engine.load_all(group="dev", platform="macos")
   ```

4. **Implement error handling** in plugins:
   ```python
   def execute(self, context: HookContext) -> bool:
       try:
           # Your code
       except Exception as e:
           context.error = str(e)
           return False
   ```

5. **Save configuration** after changes:
   ```python
   engine.set("key", "value")
   engine.save("~/.devkit/config.yaml")
   ```

---

## See Also

- [MODULAR_ARCHITECTURE.md](MODULAR_ARCHITECTURE.md) - System design
- [PLUGIN_DEVELOPMENT_GUIDE.md](PLUGIN_DEVELOPMENT_GUIDE.md) - Plugin creation
- [MODULAR_README.md](../MODULAR_README.md) - Quick start guide
