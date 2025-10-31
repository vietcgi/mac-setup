"""
Extended tests for plugin_system module.

Focus on improving coverage for:
- PluginLoader initialization and plugin path management
- Plugin discovery functionality
- Hook context and interface implementations
- Error handling and validation
"""

import sys
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import unittest

# Mock sys.argv
sys.argv = ["pytest"]

from cli.plugin_system import (  # noqa: E402
    PluginLoader,
    PluginInterface,
    HookInterface,
    HookContext,
)


class TestHookContext(unittest.TestCase):
    """Test HookContext dataclass."""

    def test_hook_context_creation_minimal(self):
        """Test creating hook context with minimal parameters."""
        ctx = HookContext(stage="pre_setup")

        self.assertEqual(ctx.stage, "pre_setup")
        self.assertIsNone(ctx.role)
        self.assertIsNone(ctx.task)
        self.assertEqual(ctx.status, "running")
        self.assertIsNone(ctx.error)

    def test_hook_context_creation_full(self):
        """Test creating hook context with all parameters."""
        metadata = {"key": "value"}
        ctx = HookContext(
            stage="post_role",
            role="shell",
            task="install_zsh",
            status="success",
            error=None,
            metadata=metadata,
        )

        self.assertEqual(ctx.stage, "post_role")
        self.assertEqual(ctx.role, "shell")
        self.assertEqual(ctx.task, "install_zsh")
        self.assertEqual(ctx.status, "success")
        self.assertEqual(ctx.metadata, metadata)

    def test_hook_context_failed_status(self):
        """Test hook context with failed status."""
        ctx = HookContext(
            stage="pre_setup",
            status="failed",
            error="Something went wrong",
        )

        self.assertEqual(ctx.status, "failed")
        self.assertEqual(ctx.error, "Something went wrong")


class TestPluginLoader(unittest.TestCase):
    """Test PluginLoader class."""

    def setUp(self):
        """Set up test plugin loader."""
        self.temp_dir = tempfile.mkdtemp()
        self.loader = PluginLoader()

    def tearDown(self):
        """Clean up."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_plugin_loader_initialization(self):
        """Test initializing plugin loader."""
        self.assertIsNotNone(self.loader)
        self.assertIsNotNone(self.loader.logger)
        self.assertEqual(len(self.loader.plugins), 0)
        self.assertEqual(len(self.loader.hooks), 0)
        self.assertEqual(len(self.loader.plugin_paths), 0)

    def test_plugin_loader_with_custom_logger(self):
        """Test initializing loader with custom logger."""
        custom_logger = Mock()
        loader = PluginLoader(logger=custom_logger)

        self.assertEqual(loader.logger, custom_logger)

    def test_add_plugin_path_valid(self):
        """Test adding valid plugin path."""
        plugin_dir = Path(self.temp_dir) / "plugins"
        plugin_dir.mkdir()

        self.loader.add_plugin_path(plugin_dir)

        self.assertIn(plugin_dir, self.loader.plugin_paths)

    def test_add_plugin_path_nonexistent(self):
        """Test adding non-existent plugin path."""
        missing_path = Path(self.temp_dir) / "missing"

        self.loader.add_plugin_path(missing_path)

        self.assertNotIn(missing_path, self.loader.plugin_paths)

    def test_add_plugin_path_not_directory(self):
        """Test adding file instead of directory."""
        file_path = Path(self.temp_dir) / "file.txt"
        file_path.touch()

        self.loader.add_plugin_path(file_path)

        self.assertNotIn(file_path, self.loader.plugin_paths)

    def test_add_plugin_path_with_tilde(self):
        """Test adding plugin path with tilde expansion."""
        # Create a path with tilde (though it won't exist)
        with patch("pathlib.Path.exists", return_value=True), \
             patch("pathlib.Path.is_dir", return_value=True):
            self.loader.add_plugin_path("~/test_plugins")
            # Should have attempted to add

    def test_discover_plugins_empty_directory(self):
        """Test discovering plugins in empty directory."""
        plugin_dir = Path(self.temp_dir) / "plugins"
        plugin_dir.mkdir()
        self.loader.add_plugin_path(plugin_dir)

        discovered = self.loader.discover_plugins()

        self.assertEqual(len(discovered), 0)

    def test_discover_plugins_with_python_file(self):
        """Test discovering Python file plugin."""
        plugin_dir = Path(self.temp_dir) / "plugins"
        plugin_dir.mkdir()

        # Create a Python plugin file
        plugin_file = plugin_dir / "my_plugin.py"
        plugin_file.write_text("# Plugin code")

        self.loader.add_plugin_path(plugin_dir)
        discovered = self.loader.discover_plugins()

        self.assertEqual(len(discovered), 1)
        path, module_name = discovered[0]
        self.assertEqual(module_name, "my_plugin")
        self.assertTrue(path.endswith("my_plugin.py"))

    def test_discover_plugins_with_package(self):
        """Test discovering Python package plugin."""
        plugin_dir = Path(self.temp_dir) / "plugins"
        plugin_dir.mkdir()

        # Create a Python package plugin
        pkg_dir = plugin_dir / "my_plugin_pkg"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("# Package code")

        self.loader.add_plugin_path(plugin_dir)
        discovered = self.loader.discover_plugins()

        self.assertEqual(len(discovered), 1)
        path, module_name = discovered[0]
        self.assertEqual(module_name, "my_plugin_pkg")

    def test_discover_plugins_ignores_private(self):
        """Test that private files are ignored."""
        plugin_dir = Path(self.temp_dir) / "plugins"
        plugin_dir.mkdir()

        # Create private plugin (should be ignored)
        (plugin_dir / "_private_plugin.py").write_text("# Private")

        # Create normal plugins
        (plugin_dir / "public_plugin1.py").write_text("# Public 1")
        (plugin_dir / "public_plugin2.py").write_text("# Public 2")

        self.loader.add_plugin_path(plugin_dir)
        discovered = self.loader.discover_plugins()

        # Should discover 2 public plugins, not 3
        self.assertEqual(len(discovered), 2)
        module_names = {name for _, name in discovered}
        self.assertEqual(module_names, {"public_plugin1", "public_plugin2"})

    def test_discover_plugins_nonexistent_path(self):
        """Test discovering plugins with non-existent path."""
        missing_path = Path(self.temp_dir) / "missing"
        self.loader.plugin_paths.append(missing_path)  # Add directly

        discovered = self.loader.discover_plugins()

        self.assertEqual(len(discovered), 0)

    def test_discover_plugins_multiple_paths(self):
        """Test discovering plugins in multiple paths."""
        plugin_dir1 = Path(self.temp_dir) / "plugins1"
        plugin_dir2 = Path(self.temp_dir) / "plugins2"
        plugin_dir1.mkdir()
        plugin_dir2.mkdir()

        (plugin_dir1 / "plugin1.py").write_text("# Plugin 1")
        (plugin_dir2 / "plugin2.py").write_text("# Plugin 2")

        self.loader.add_plugin_path(plugin_dir1)
        self.loader.add_plugin_path(plugin_dir2)

        discovered = self.loader.discover_plugins()

        self.assertEqual(len(discovered), 2)
        module_names = {name for _, name in discovered}
        self.assertEqual(module_names, {"plugin1", "plugin2"})

    def test_load_plugin_with_validation_error(self):
        """Test loading plugin with validation error."""
        # Mock validator to fail
        with patch("cli.plugin_system.PluginValidator") as mock_validator_class:
            mock_validator = Mock()
            mock_validator.validate_plugin.return_value = (False, "Invalid plugin")
            mock_validator_class.return_value = mock_validator

            result = self.loader.load_plugin("/path/to/plugin.py", "bad_plugin")

            self.assertIsNone(result)

    def test_load_plugin_missing_module(self):
        """Test loading non-existent plugin."""
        result = self.loader.load_plugin("/nonexistent/plugin.py", "missing")

        self.assertIsNone(result)

    def test_get_plugin_nonexistent(self):
        """Test getting non-loaded plugin."""
        result = self.loader.get_plugin("nonexistent_plugin")

        self.assertIsNone(result)

    def test_list_plugins_empty(self):
        """Test listing plugins when none loaded."""
        plugins = self.loader.list_plugins()

        self.assertEqual(plugins, [])

    def test_list_plugins_with_plugins(self):
        """Test listing loaded plugins."""
        # Add mock plugins
        mock_plugin1 = Mock(spec=PluginInterface)
        mock_plugin1.name = "plugin1"
        mock_plugin2 = Mock(spec=PluginInterface)
        mock_plugin2.name = "plugin2"

        self.loader.plugins["plugin1"] = mock_plugin1
        self.loader.plugins["plugin2"] = mock_plugin2

        plugins = self.loader.list_plugins()

        self.assertEqual(len(plugins), 2)
        self.assertIn("plugin1", plugins)
        self.assertIn("plugin2", plugins)

    def test_get_plugin_roles_empty(self):
        """Test getting plugin roles when no plugins loaded."""
        roles = self.loader.get_plugin_roles()

        self.assertEqual(roles, {})

    def test_get_plugin_roles_with_plugins(self):
        """Test getting plugin roles from loaded plugins."""
        # Create mock plugins with roles
        mock_plugin = Mock(spec=PluginInterface)
        roles = {"shell": Path("/tmp/shell"), "editors": Path("/tmp/editors")}
        mock_plugin.get_roles.return_value = roles

        self.loader.plugins["test_plugin"] = mock_plugin

        plugin_roles = self.loader.get_plugin_roles()

        self.assertIn("shell", plugin_roles)
        self.assertIn("editors", plugin_roles)

    def test_execute_hooks_empty(self):
        """Test executing hooks when none registered."""
        ctx = HookContext(stage="pre_setup")
        result = self.loader.execute_hooks("pre_setup", ctx)

        self.assertTrue(result)

    def test_get_plugin_info_empty(self):
        """Test getting plugin info when no plugins loaded."""
        info = self.loader.get_plugin_info()

        self.assertEqual(info, {})

    def test_get_plugin_info_with_plugins(self):
        """Test getting plugin information."""
        # Create mock plugin
        mock_plugin = Mock(spec=PluginInterface)
        mock_plugin.version = "1.0.0"
        mock_plugin.description = "Test plugin"
        mock_plugin.get_roles.return_value = {"role1": Path("/tmp/role1")}
        mock_plugin.get_hooks.return_value = {"pre_setup": [Mock()]}

        self.loader.plugins["test_plugin"] = mock_plugin

        info = self.loader.get_plugin_info()

        self.assertIn("test_plugin", info)
        self.assertEqual(info["test_plugin"]["version"], "1.0.0")
        self.assertEqual(info["test_plugin"]["description"], "Test plugin")
        self.assertEqual(info["test_plugin"]["roles"], 1)
        self.assertEqual(info["test_plugin"]["hooks"], 1)


class TestPluginInterfaces(unittest.TestCase):
    """Test plugin interface implementations."""

    def test_hook_interface_is_abstract(self):
        """Test that HookInterface is abstract."""
        with self.assertRaises(TypeError):
            HookInterface()

    def test_plugin_interface_is_abstract(self):
        """Test that PluginInterface is abstract."""
        with self.assertRaises(TypeError):
            PluginInterface()

    def test_hook_interface_implementation(self):
        """Test implementing HookInterface."""

        class TestHook(HookInterface):
            def execute(self, context: HookContext) -> bool:
                return True

        hook = TestHook()
        ctx = HookContext(stage="pre_setup")

        self.assertTrue(hook.execute(ctx))

    def test_plugin_interface_implementation(self):
        """Test implementing PluginInterface."""

        class TestPlugin(PluginInterface):
            name = "test"
            version = "1.0"
            description = "Test"

            def initialize(self):
                pass

            def get_roles(self):
                return {}

            def get_hooks(self):
                return {}

            def validate(self):
                return True, []

        plugin = TestPlugin()

        self.assertEqual(plugin.name, "test")
        self.assertEqual(plugin.version, "1.0")
        self.assertTrue(plugin.validate()[0])


class TestLoadAll(unittest.TestCase):
    """Test load_all functionality."""

    def setUp(self):
        """Set up test loader."""
        self.temp_dir = tempfile.mkdtemp()
        self.loader = PluginLoader()

    def tearDown(self):
        """Clean up."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_load_all_no_plugins(self):
        """Test load_all with no plugins found."""
        plugin_dir = Path(self.temp_dir) / "plugins"
        plugin_dir.mkdir()
        self.loader.add_plugin_path(plugin_dir)

        count = self.loader.load_all([plugin_dir])

        self.assertEqual(count, 0)

    def test_load_all_default_paths(self):
        """Test load_all with default paths."""
        # This will use default paths, which likely don't exist
        count = self.loader.load_all()

        # Should not raise exception
        self.assertGreaterEqual(count, 0)


if __name__ == "__main__":
    unittest.main()
