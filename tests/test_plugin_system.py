#!/usr/bin/env python3
"""
Tests for Plugin System module.

Tests plugin loading and execution including:
- Hook context creation
- Hook interface implementation
- Plugin discovery
- Plugin validation and loading
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import Optional

# Mock sys.argv to prevent argparse issues during import
sys.argv = ["pytest"]

from cli.plugin_system import HookContext, HookInterface, PluginInterface


class TestHookContext:
    """Tests for HookContext dataclass."""

    def test_hook_context_init(self) -> None:
        """Test HookContext initialization."""
        context = HookContext(
            stage="pre_setup",
            role="development",
            status="running"
        )
        assert context.stage == "pre_setup"
        assert context.role == "development"
        assert context.status == "running"
        assert context.task is None
        assert context.error is None
        assert context.metadata is None

    def test_hook_context_with_metadata(self) -> None:
        """Test HookContext with metadata."""
        metadata = {"key": "value"}
        context = HookContext(
            stage="post_setup",
            metadata=metadata
        )
        assert context.metadata == metadata

    def test_hook_context_with_error(self) -> None:
        """Test HookContext with error."""
        context = HookContext(
            stage="pre_setup",
            status="failed",
            error="Test error message"
        )
        assert context.status == "failed"
        assert context.error == "Test error message"

    def test_hook_context_with_task(self) -> None:
        """Test HookContext with task."""
        context = HookContext(
            stage="pre_role",
            role="development",
            task="setup_xcode"
        )
        assert context.task == "setup_xcode"

    def test_hook_context_defaults(self) -> None:
        """Test HookContext default values."""
        context = HookContext(stage="pre_setup")
        assert context.stage == "pre_setup"
        assert context.role is None
        assert context.task is None
        assert context.status == "running"
        assert context.error is None
        assert context.metadata is None


class TestHookInterface:
    """Tests for HookInterface abstract base class."""

    def test_hook_interface_cannot_instantiate(self) -> None:
        """Test that HookInterface cannot be instantiated directly."""
        with pytest.raises(TypeError):
            HookInterface()

    def test_hook_interface_subclass(self) -> None:
        """Test creating a HookInterface subclass."""
        class TestHook(HookInterface):
            def execute(self, context: HookContext) -> bool:
                return True

        hook = TestHook()
        assert hook is not None
        context = HookContext(stage="pre_setup")
        result = hook.execute(context)
        assert result is True

    def test_hook_interface_requires_execute(self) -> None:
        """Test that subclass must implement execute method."""
        with pytest.raises(TypeError):
            class IncompleteHook(HookInterface):
                pass

            IncompleteHook()


class TestPluginInterface:
    """Tests for PluginInterface abstract base class."""

    def test_plugin_interface_cannot_instantiate(self) -> None:
        """Test that PluginInterface cannot be instantiated directly."""
        with pytest.raises(TypeError):
            PluginInterface()

    def test_plugin_interface_subclass(self) -> None:
        """Test creating a PluginInterface subclass."""
        class TestPlugin(PluginInterface):
            name = "test-plugin"
            version = "1.0.0"
            description = "Test plugin"

            def initialize(self) -> None:
                pass

            def get_roles(self) -> dict[str, Path]:
                return {}

            def get_hooks(self) -> dict[str, list[HookInterface]]:
                return {}

            def validate(self) -> tuple[bool, list[str]]:
                return True, []

        plugin = TestPlugin()
        assert plugin is not None
        assert plugin.name == "test-plugin"

    def test_plugin_interface_hook_methods(self) -> None:
        """Test all hook methods in PluginInterface."""
        class TestPlugin(PluginInterface):
            name = "test-plugin"
            version = "1.0.0"
            description = "Test plugin"

            def initialize(self) -> None:
                self.initialized = True

            def get_roles(self) -> dict[str, Path]:
                return {"dev": Path("/tmp/dev")}

            def get_hooks(self) -> dict[str, list[HookInterface]]:
                return {}

            def validate(self) -> tuple[bool, list[str]]:
                return True, []

        plugin = TestPlugin()
        plugin.initialize()
        assert hasattr(plugin, "initialized")
        roles = plugin.get_roles()
        assert "dev" in roles
        valid, errors = plugin.validate()
        assert valid is True
        assert errors == []


class TestPluginHookExecution:
    """Tests for plugin hook execution."""

    def test_hook_execution_with_context_data(self) -> None:
        """Test hook execution with full context data."""
        class LoggingHook(HookInterface):
            def __init__(self) -> None:
                self.executed = False
                self.context_data: Optional[HookContext] = None

            def execute(self, context: HookContext) -> bool:
                self.executed = True
                self.context_data = context
                return True

        hook = LoggingHook()
        context = HookContext(
            stage="pre_setup",
            role="development",
            task="setup",
            metadata={"test": "data"}
        )
        result = hook.execute(context)
        assert result is True
        assert hook.executed is True
        assert hook.context_data == context

    def test_hook_error_handling(self) -> None:
        """Test hook error context."""
        class ErrorHook(HookInterface):
            def execute(self, context: HookContext) -> bool:
                if context.status == "failed":
                    return False
                return True

        hook = ErrorHook()
        error_context = HookContext(
            stage="pre_setup",
            status="failed",
            error="Setup failed"
        )
        result = hook.execute(error_context)
        assert result is False
        assert error_context.error == "Setup failed"

    def test_hook_role_specific_execution(self) -> None:
        """Test role-specific hook execution."""
        class RoleHook(HookInterface):
            def execute(self, context: HookContext) -> bool:
                if context.role == "development":
                    return True
                return False

        hook = RoleHook()
        dev_context = HookContext(stage="pre_role", role="development")
        prod_context = HookContext(stage="pre_role", role="production")

        assert hook.execute(dev_context) is True
        assert hook.execute(prod_context) is False


class TestPluginMetadata:
    """Tests for plugin metadata and context."""

    def test_hook_context_metadata_types(self) -> None:
        """Test various metadata types."""
        metadata = {
            "string": "value",
            "number": 42,
            "list": [1, 2, 3],
            "dict": {"nested": "value"},
        }
        context = HookContext(
            stage="pre_setup",
            metadata=metadata
        )
        assert context.metadata["string"] == "value"
        assert context.metadata["number"] == 42
        assert context.metadata["list"] == [1, 2, 3]
        assert context.metadata["dict"]["nested"] == "value"

    def test_hook_context_stage_values(self) -> None:
        """Test all valid stage values."""
        valid_stages = ["pre_setup", "post_setup", "pre_role", "post_role"]
        for stage in valid_stages:
            context = HookContext(stage=stage)
            assert context.stage == stage

    def test_hook_context_status_values(self) -> None:
        """Test various status values."""
        valid_statuses = ["running", "success", "failed"]
        for status in valid_statuses:
            context = HookContext(stage="pre_setup", status=status)
            assert context.status == status
