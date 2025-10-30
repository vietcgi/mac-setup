#!/usr/bin/env python3
"""
Example Docker Development Plugin

Demonstrates how to create a custom plugin that extends mac-setup.
This plugin sets up Docker and Kubernetes development environment.
"""

import subprocess
from pathlib import Path
from typing import Dict, List

# These imports assume cli module is in path
try:
    from cli.plugin_system import PluginInterface, HookInterface, HookContext
except ImportError:
    import sys

    sys.path.insert(0, str(Path(__file__).parent.parent / "cli"))
    from plugin_system import PluginInterface, HookInterface, HookContext


class DockerDevPreSetupHook(HookInterface):
    """Pre-setup hook for Docker development."""

    def execute(self, context: HookContext) -> bool:
        """Check prerequisites before setup."""
        print("Docker Dev Plugin: Checking prerequisites...")

        # Check if running on supported OS
        import platform

        if platform.system() not in ("Darwin", "Linux"):
            context.error = "Docker Dev plugin only supports macOS and Linux"
            return False

        print("  ✓ System compatibility check passed")
        return True


class DockerDevPostSetupHook(HookInterface):
    """Post-setup hook for Docker development."""

    def execute(self, context: HookContext) -> bool:
        """Verify Docker setup after installation."""
        print("Docker Dev Plugin: Verifying installation...")

        try:
            # Check Docker installation
            result = subprocess.run(
                ["docker", "--version"], capture_output=True, timeout=5, check=True
            )
            print(f"  ✓ Docker installed: {result.stdout.decode().strip()}")

            # Check Docker daemon
            result = subprocess.run(
                ["docker", "ps"], capture_output=True, timeout=5, check=True
            )
            print("  ✓ Docker daemon is running")

            # Check Kubernetes
            result = subprocess.run(
                ["kubectl", "version", "--client"],
                capture_output=True,
                timeout=5,
                check=True,
            )
            print(f"  ✓ kubectl installed: {result.stdout.decode().split()[3]}")

            return True

        except (
            FileNotFoundError,
            subprocess.TimeoutExpired,
            subprocess.CalledProcessError,
        ) as e:
            context.error = f"Docker verification failed: {e}"
            return False


class DockerDevPlugin(PluginInterface):
    """Docker development environment plugin."""

    name = "docker_dev"
    version = "1.0.0"
    description = "Docker and Kubernetes development environment setup"

    def __init__(self):
        """Initialize plugin instance."""
        pass

    def initialize(self) -> None:
        """Initialize plugin."""
        print("Docker Dev Plugin initialized")

    def get_roles(self) -> Dict[str, Path]:
        """Return custom Ansible roles."""
        # In a real plugin, this would point to actual role directories
        plugin_dir = Path(__file__).parent
        return {"docker_dev": plugin_dir / "roles" / "docker_dev"}

    def get_hooks(self) -> Dict[str, List[HookInterface]]:
        """Return hooks for various stages."""
        return {
            "pre_setup": [DockerDevPreSetupHook()],
            "post_setup": [DockerDevPostSetupHook()],
        }

    def validate(self) -> tuple[bool, List[str]]:
        """Validate plugin configuration."""
        errors = []

        # In production, validate configuration files, required tools, etc.
        # For this example, we'll just do basic validation

        return len(errors) == 0, errors


# Export plugin class for auto-discovery
__all__ = ["DockerDevPlugin"]

if __name__ == "__main__":
    # Test plugin when run directly
    plugin = DockerDevPlugin()
    print(f"\nPlugin: {plugin.name}")
    print(f"Version: {plugin.version}")
    print(f"Description: {plugin.description}")

    is_valid, errors = plugin.validate()
    print(f"\nValidation: {'✓ PASS' if is_valid else '✗ FAIL'}")
    if errors:
        for error in errors:
            print(f"  - {error}")

    print(f"\nRoles provided: {len(plugin.get_roles())}")
    for role_name in plugin.get_roles():
        print(f"  - {role_name}")

    print(f"\nHooks registered: {len(plugin.get_hooks())}")
    for stage, hooks in plugin.get_hooks().items():
        print(f"  - {stage}: {len(hooks)} hook(s)")
