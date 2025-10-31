#  Copyright (c) 2024 Devkit Contributors
#  SPDX-License-Identifier: MIT
# !/usr/bin/env python3
"""Mac-Setup Plugin System.

Allows users to extend mac-setup with custom roles, hooks, and tasks.
Plugins can be defined in ~/.mac-setup/plugins/ and are auto-discovered.

SECURITY: All plugins are validated before loading using PluginValidator.
Plugins must have a valid manifest.json and implement PluginInterface.
"""

import importlib.util
import logging
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

# Security: Import validator
from .plugin_validator import PluginValidator


@dataclass
class HookContext:
    """Context passed to hooks."""

    stage: str  # "pre_setup", "post_setup", "pre_role", "post_role"
    role: Optional[str] = None
    task: Optional[str] = None
    status: str = "running"  # "running", "success", "failed"
    error: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None


class HookInterface(ABC):
    """Base class for plugin hooks."""

    @abstractmethod
    def execute(self, context: HookContext) -> bool:
        """Execute hook.

        Args:
            context: Hook execution context

        Returns:
            True if successful, False otherwise
        """


class PluginInterface(ABC):
    """Base class for mac-setup plugins."""

    name: str
    version: str
    description: str

    @abstractmethod
    def initialize(self) -> None:
        """Initialize plugin."""

    @abstractmethod
    def get_roles(self) -> dict[str, Path]:
        """Get custom roles provided by plugin.

        Returns:
            Dictionary mapping role names to role directories
        """

    @abstractmethod
    def get_hooks(self) -> dict[str, list[HookInterface]]:
        """Get hooks for various stages.

        Returns:
            Dictionary mapping stage names to lists of hooks
        """

    @abstractmethod
    def validate(self) -> tuple[bool, list[str]]:
        """Validate plugin configuration.

        Returns:
            Tuple of (is_valid, error_list)
        """


class PluginLoader:
    """Loads and manages mac-setup plugins.

    Searches for plugins in:
    1. ~/.mac-setup/plugins/ (user plugins)
    2. ./plugins/ (project plugins)
    """

    def __init__(self, logger: Optional[logging.Logger] = None) -> None:
        """Initialize plugin loader.

        Args:
            logger: Logger instance
        """
        self.logger = logger or self._setup_logger()
        self.plugins: dict[str, PluginInterface] = {}
        self.hooks: dict[str, list[HookInterface]] = {}
        self.plugin_paths: list[Path] = []

    def _setup_logger(self) -> logging.Logger:
        """Setup default logger."""
        logger = logging.getLogger("mac-setup.plugins")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(levelname)s: %(message)s")
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def add_plugin_path(self, path: Path) -> None:
        """Add directory to plugin search path."""
        path = Path(path).expanduser()
        if path.exists() and path.is_dir():
            self.plugin_paths.append(path)
            self.logger.debug(f"Added plugin path: {path}")
        else:
            self.logger.warning(f"Plugin path not found: {path}")

    def discover_plugins(self) -> list[tuple[str, str]]:
        """Auto-discover plugins in configured paths.

        Returns:
            List of discovered plugin (path, module_name) tuples
        """
        discovered: list[tuple[str, str]] = []

        for plugin_dir in self.plugin_paths:
            if not plugin_dir.exists():
                continue

            # Look for Python modules and packages
            for item in plugin_dir.iterdir():
                if item.name.startswith("_"):
                    continue

                if item.is_file() and item.suffix == ".py":
                    # Python file plugin
                    module_name = item.stem
                    discovered.append((str(item), module_name))

                elif item.is_dir() and (item / "__init__.py").exists():
                    # Python package plugin
                    module_name = item.name
                    discovered.append((str(item), module_name))

        self.logger.info(f"Discovered {len(discovered)} plugins")
        return discovered

    def load_plugin(self, plugin_path: str, module_name: str) -> Optional[PluginInterface]:
        """Load a single plugin module with security validation.

        SECURITY: Before loading, validates:
        1. Plugin manifest exists and is valid
        2. Plugin implements PluginInterface
        3. Plugin integrity is verified

        Args:
            plugin_path: Path to plugin file or directory
            module_name: Module name

        Returns:
            Loaded plugin instance or None
        """
        try:
            # SECURITY: Validate plugin before loading
            plugin_dir = Path(plugin_path)
            validator = PluginValidator(plugin_dir.parent)
            is_valid, message = validator.validate_plugin(module_name)

            if not is_valid:
                self.logger.error(f"Plugin validation failed for {module_name}: {message}")
                return None

            # SECURITY: Verify manifest integrity (detect tampering)
            manifest_path = plugin_dir / "manifest.json"
            if manifest_path.exists():
                from .plugin_validator import PluginManifest

                try:
                    manifest = PluginManifest(manifest_path)
                    integrity_valid, integrity_message = manifest.verify_integrity()
                    if not integrity_valid:
                        self.logger.error(
                            f"Plugin integrity check failed for {module_name}: {integrity_message}",
                        )
                        return None
                    self.logger.debug(f"Plugin integrity verified for {module_name}")
                except Exception as e:
                    self.logger.exception(
                        f"Failed to verify plugin integrity for {module_name}: {e}",
                    )
                    return None

            self.logger.debug(f"Plugin validation passed for {module_name}")

            # Create a proper module name with namespace
            full_module_name = f"mac_setup_plugins.{module_name}"

            # Load the module
            spec = importlib.util.spec_from_file_location(full_module_name, plugin_path)
            if not spec or not spec.loader:
                self.logger.error(f"Could not load spec for {module_name}")
                return None

            module = importlib.util.module_from_spec(spec)
            sys.modules[full_module_name] = module
            spec.loader.exec_module(module)

            # Look for plugin class
            for item_name in dir(module):
                item = getattr(module, item_name)
                if (
                    isinstance(item, type)
                    and issubclass(item, PluginInterface)
                    and item is not PluginInterface
                ):
                    plugin_instance = item()
                    plugin_instance.initialize()

                    is_valid, errors = plugin_instance.validate()
                    if not is_valid:
                        self.logger.warning(f"Plugin {module_name} validation failed: {errors}")
                        return None

                    self.logger.info(
                        f"Loaded plugin: {plugin_instance.name} v{plugin_instance.version}",
                    )
                    return plugin_instance

            self.logger.warning(f"No PluginInterface found in {module_name}")
            return None

        except Exception as e:
            self.logger.exception(f"Error loading plugin {module_name}: {e}")
            return None

    def load_all(self, plugin_paths: Optional[list[Path]] = None) -> int:
        """Discover and load all plugins.

        Args:
            plugin_paths: Optional list of paths to search

        Returns:
            Number of successfully loaded plugins
        """
        # Add default paths
        if not plugin_paths:
            plugin_paths = [
                Path.home() / ".mac-setup" / "plugins",
                Path(__file__).parent.parent / "plugins",
            ]

        for path in plugin_paths:
            self.add_plugin_path(path)

        # Discover plugins
        discovered = self.discover_plugins()

        # Load each plugin
        loaded = 0
        for plugin_path_str, module_name_str in discovered:
            plugin = self.load_plugin(plugin_path_str, module_name_str)
            if plugin:
                self.plugins[plugin.name] = plugin
                loaded += 1

                # Register hooks
                for stage, hooks in plugin.get_hooks().items():
                    if stage not in self.hooks:
                        self.hooks[stage] = []
                    self.hooks[stage].extend(hooks)

        self.logger.info(f"Successfully loaded {loaded}/{len(discovered)} plugins")
        return loaded

    def get_plugin(self, name: str) -> Optional[PluginInterface]:
        """Get plugin by name."""
        return self.plugins.get(name)

    def list_plugins(self) -> list[str]:
        """List loaded plugin names."""
        return list(self.plugins.keys())

    def get_plugin_roles(self) -> dict[str, Path]:
        """Get all custom roles from loaded plugins."""
        roles = {}
        for plugin in self.plugins.values():
            roles.update(plugin.get_roles())
        return roles

    def execute_hooks(self, stage: str, context: Optional[HookContext] = None) -> bool:
        """Execute all hooks for a given stage.

        Args:
            stage: Hook stage name
            context: Hook context

        Returns:
            True if all hooks succeeded, False otherwise
        """
        if not context:
            context = HookContext(stage=stage)

        hooks = self.hooks.get(stage, [])
        if not hooks:
            return True

        self.logger.debug(f"Executing {len(hooks)} hooks for stage: {stage}")

        for hook in hooks:
            try:
                if not hook.execute(context):
                    self.logger.warning(f"Hook failed for stage {stage}")
                    context.status = "failed"
                    return False
            except Exception as e:
                self.logger.exception(f"Hook execution error: {e}")
                context.error = str(e)
                context.status = "failed"
                return False

        context.status = "success"
        return True

    def get_plugin_info(self) -> dict[str, dict[str, Any]]:
        """Get information about all loaded plugins."""
        info = {}
        for name, plugin in self.plugins.items():
            info[name] = {
                "version": plugin.version,
                "description": plugin.description,
                "roles": len(plugin.get_roles()),
                "hooks": sum(len(h) for h in plugin.get_hooks().values()),
            }
        return info


class BuiltinHook(HookInterface):
    """Base class for builtin hooks."""

    def __init__(self, name: str) -> None:
        self.name = name

    def execute(self, context: HookContext) -> bool:
        """Execute hook."""
        return True


class SimplePlugin(PluginInterface):
    """Example simple plugin for reference.

    Users can create their own plugins by extending PluginInterface.
    """

    name = "example"
    version = "1.0.0"
    description = "Example plugin"

    def initialize(self) -> None:
        """Initialize plugin."""

    def get_roles(self) -> dict[str, Path]:
        """Return custom roles."""
        return {}

    def get_hooks(self) -> dict[str, list[HookInterface]]:
        """Return hooks."""
        return {}

    def validate(self) -> tuple[bool, list[str]]:
        """Validate plugin."""
        return True, []


def main() -> None:
    """CLI interface for plugin system."""
    import argparse

    parser = argparse.ArgumentParser(description="Mac-Setup Plugin System")
    parser.add_argument("--plugin-path", action="append", help="Add plugin path")
    parser.add_argument("--list", action="store_true", help="List plugins")
    parser.add_argument("--info", action="store_true", help="Show plugin info")
    parser.add_argument("--validate", action="store_true", help="Validate plugins")

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    # Create loader
    loader = PluginLoader()

    # Add custom paths
    if args.plugin_path:
        for path in args.plugin_path:
            loader.add_plugin_path(Path(path))

    # Load plugins
    loader.load_all()

    # Handle commands
    if args.list:
        plugins = loader.list_plugins()
        for _plugin in plugins:
            pass

    elif args.info:
        loader.get_plugin_info()

    elif args.validate:
        # All plugins are validated during load
        pass

    else:
        # Default: show summary
        plugins = loader.list_plugins()


if __name__ == "__main__":
    main()

# ============================================================================
# PUBLIC API
# ============================================================================

__all__ = [
    "HookContext",
    "HookInterface",
    "PluginInterface",
    "PluginLoader",
    "BuiltinHook",
    "SimplePlugin",
]
