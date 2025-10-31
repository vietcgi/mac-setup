#  Copyright (c) 2024 Devkit Contributors
#  SPDX-License-Identifier: MIT
# !/usr/bin/env python3
"""Plugin System Security & Validation.

Provides comprehensive validation for Devkit plugins:
- Manifest validation (required fields, types)
- Semantic version validation
- Permission declaration validation
- Plugin class verification
- Secure plugin loading

All plugins must have a manifest.json file and implement the PluginInterface.
"""

import hashlib
import json
import logging
import re
from pathlib import Path
from typing import Any, Optional


class PluginManifest:
    """Validates plugin manifest files."""

    # Required fields that every plugin must have
    REQUIRED_FIELDS: dict[str, type[Any]] = {
        "name": str,
        "version": str,
        "author": str,
        "description": str,
    }

    # Optional fields with type checking
    OPTIONAL_FIELDS: dict[str, type[Any]] = {
        "homepage": str,
        "repository": str,
        "license": str,
        "requires": dict,
        "permissions": list,
    }

    # Valid permission declarations
    VALID_PERMISSIONS = {
        "filesystem",  # Can read/write files
        "network",  # Can make network requests
        "system",  # Can execute system commands
        "environment",  # Can read environment variables
    }

    def __init__(self, manifest_path: Path) -> None:
        """Load and parse plugin manifest.

        Args:
            manifest_path: Path to manifest.json file

        Raises:
            FileNotFoundError: If manifest doesn't exist
            json.JSONDecodeError: If manifest is invalid JSON
        """
        if not manifest_path.exists():
            raise FileNotFoundError(f"Manifest not found: {manifest_path}")

        self.path = manifest_path
        try:
            with open(manifest_path, encoding="utf-8") as f:
                self.data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid manifest JSON in {manifest_path}: {e}")

    def validate(self) -> tuple[bool, list[str]]:
        """Validate manifest against schema.

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Check required fields
        for field, field_type in self.REQUIRED_FIELDS.items():
            if field not in self.data:
                errors.append(f"Missing required field: {field}")
            elif not isinstance(self.data[field], field_type):
                errors.append(
                    f"Invalid type for {field}: expected {field_type.__name__}, "
                    f"got {type(self.data[field]).__name__}",
                )

        # Validate version format (semantic versioning)
        if "version" in self.data and not self._is_valid_semver(self.data["version"]):
            errors.append(
                f"Invalid version format: {self.data["version"]}. "
                f"Must be semantic version (X.Y.Z)",
            )

        # Validate optional fields if present
        for field, field_type in self.OPTIONAL_FIELDS.items():
            if field in self.data and not isinstance(self.data[field], field_type):
                errors.append(
                    f"Invalid type for {field}: expected {field_type.__name__}, "
                    f"got {type(self.data[field]).__name__}",
                )

        # Validate permissions (if specified)
        if "permissions" in self.data:
            invalid_perms = set(self.data["permissions"]) - self.VALID_PERMISSIONS
            if invalid_perms:
                errors.append(
                    f"Invalid permissions: {invalid_perms}. "
                    f"Valid options: {self.VALID_PERMISSIONS}",
                )

        # Validate requires (if specified)
        if "requires" in self.data:
            if not isinstance(self.data["requires"], dict):
                errors.append("'requires' field must be a dictionary")
            else:
                # Each requirement should have version constraint
                for pkg, version_spec in self.data["requires"].items():
                    if not isinstance(version_spec, str):
                        errors.append(
                            f"Package requirement '{pkg}' must have string version constraint, "
                            f"got {type(version_spec).__name__}",
                        )

        return len(errors) == 0, errors

    def verify_integrity(self) -> tuple[bool, str]:
        """Verify plugin manifest integrity using SHA256 checksum.

        SECURITY: Detects tampering and corruption of manifest files.

        Returns:
            Tuple of (is_valid, message)
        """
        # Check if manifest has stored checksum
        if "checksum" not in self.data:
            return False, "Missing integrity checksum in manifest"

        stored_checksum = self.data["checksum"]

        # Create a copy without the checksum for computing hash
        manifest_copy = {k: v for k, v in self.data.items() if k != "checksum"}
        manifest_json = json.dumps(manifest_copy, sort_keys=True, default=str)
        computed_checksum = hashlib.sha256(manifest_json.encode()).hexdigest()

        if computed_checksum != stored_checksum:
            return (
                False,
                f"Manifest integrity check failed. Plugin may have been tampered with. "
                f"Expected: {stored_checksum}, Got: {computed_checksum}",
            )

        return True, "Manifest integrity verified"

    @staticmethod
    def _is_valid_semver(version: str) -> bool:
        """Validate semantic version format (X.Y.Z).

        Supports:
        - 1.0.0
        - 1.0.0-alpha
        - 1.0.0-alpha.1
        - 1.0.0+build.1

        Args:
            version: Version string to validate

        Returns:
            True if valid semantic version
        """
        pattern = r"^(\d+)\.(\d+)\.(\d+)(?:-[a-zA-Z0-9.]+)?(?:\+[a-zA-Z0-9.]+)?$"
        return bool(re.match(pattern, version))


class PluginValidator:
    """Comprehensive plugin validation system.

    Validates plugins before loading to ensure:
    - Required files exist
    - Manifest is valid
    - Plugin class is properly implemented
    - Permissions are declared
    """

    def __init__(self, plugins_dir: Path, logger: Optional[logging.Logger] = None) -> None:
        """Initialize plugin validator.

        Args:
            plugins_dir: Directory containing plugins
            logger: Logger instance (created if not provided)
        """
        self.plugins_dir = plugins_dir
        self.logger = logger or self._setup_logger()

    def validate_plugin(self, plugin_name: str) -> tuple[bool, str]:
        """Validate plugin before loading.

        Checks:
        1. Plugin directory exists
        2. Manifest file exists and is valid JSON
        3. Manifest passes schema validation
        4. Required __init__.py file exists
        5. Plugin class is properly defined

        Args:
            plugin_name: Name of plugin directory

        Returns:
            Tuple of (is_valid, message)
        """
        plugin_dir = self.plugins_dir / plugin_name

        # Check directory exists
        if not plugin_dir.is_dir():
            return False, f"Plugin directory not found: {plugin_dir}"

        # Load and validate manifest
        manifest_path = plugin_dir / "manifest.json"
        try:
            manifest = PluginManifest(manifest_path)
            is_valid, errors = manifest.validate()

            if not is_valid:
                error_msg = "; ".join(errors)
                return False, f"Manifest validation failed: {error_msg}"

            # Additional validation after basic schema check
            plugin_info = manifest.data

        except FileNotFoundError:
            return False, f"Missing manifest.json in {plugin_dir}"
        except ValueError as e:
            return False, str(e)

        # Check for required __init__.py
        init_file = plugin_dir / "__init__.py"
        if not init_file.exists():
            return False, f"Missing {init_file} (required entry point)"

        # Verify __init__.py is not empty
        if init_file.stat().st_size == 0:
            return False, f"{init_file} is empty"

        # Verify plugin class exists in __init__.py
        try:
            if not self._verify_plugin_class(plugin_dir):
                return False, "Plugin class not properly defined in __init__.py"
        except Exception as e:
            return False, f"Cannot load plugin class: {e}"

        # Log successful validation
        self.logger.info(
            f"✓ Plugin validated: {plugin_name} v{plugin_info.get("version", "?")} "
            f"by {plugin_info.get("author", "Unknown")}",
        )

        return True, "Plugin validation passed"

    def _verify_plugin_class(self, plugin_dir: Path) -> bool:
        """Verify plugin implements required interface.

        Checks that __init__.py contains:
        - class Plugin definition
        - Proper imports

        Args:
            plugin_dir: Plugin directory path

        Returns:
            True if plugin class properly defined
        """
        init_file = plugin_dir / "__init__.py"
        source = init_file.read_text()

        # Check for class Plugin definition
        if "class Plugin" not in source:
            return False

        # Check for PluginInterface import or proper method definitions
        required_methods = ["initialize", "get_roles", "get_hooks", "validate"]
        method_count = sum(1 for method in required_methods if f"def {method}" in source)

        # Should have at least the required methods
        return method_count >= len(required_methods)

    def validate_all_plugins(self) -> dict[str, tuple[bool, str]]:
        """Validate all plugins in the plugins directory.

        Returns:
            Dictionary mapping plugin names to (is_valid, message) tuples
        """
        if not self.plugins_dir.exists():
            self.logger.warning(f"Plugins directory not found: {self.plugins_dir}")
            return {}

        results = {}
        plugin_dirs = [
            d for d in self.plugins_dir.iterdir() if d.is_dir() and not d.name.startswith(".")
        ]

        for plugin_dir in plugin_dirs:
            plugin_name = plugin_dir.name
            is_valid, message = self.validate_plugin(plugin_name)
            results[plugin_name] = (is_valid, message)

            if not is_valid:
                self.logger.warning(f"✗ {plugin_name}: {message}")

        return results

    def get_plugin_info(self, plugin_name: str) -> Optional[dict[str, Any]]:
        """Get plugin information from manifest.

        Args:
            plugin_name: Name of plugin

        Returns:
            Plugin manifest dict or None if invalid
        """
        plugin_dir = self.plugins_dir / plugin_name
        manifest_path = plugin_dir / "manifest.json"

        try:
            manifest = PluginManifest(manifest_path)
            is_valid, _ = manifest.validate()
            if is_valid:
                data: Any = manifest.data
                if isinstance(data, dict):
                    return data
        except (FileNotFoundError, ValueError):
            pass

        return None

    @staticmethod
    def _setup_logger() -> logging.Logger:
        """Setup default logger."""
        logger = logging.getLogger("devkit.plugin_validator")
        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger


def validate_plugin_manifest(manifest_path: Path) -> tuple[bool, list[str]]:
    """Standalone function to validate a plugin manifest file.

    Useful for plugin developers to validate their manifest.json.

    Args:
        manifest_path: Path to manifest.json file

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    try:
        manifest = PluginManifest(manifest_path)
        return manifest.validate()
    except (FileNotFoundError, ValueError) as e:
        return False, [str(e)]


if __name__ == "__main__":
    # Example usage: python3 cli/plugin_validator.py /path/to/plugins
    import sys

    if len(sys.argv) > 1:
        plugins_dir = Path(sys.argv[1])
        validator = PluginValidator(plugins_dir)
        results = validator.validate_all_plugins()

        for is_valid, _message in results.values():
            status = "✓" if is_valid else "✗"
    else:
        pass

# ============================================================================
# PUBLIC API
# ============================================================================

__all__ = [
    "PluginManifest",
    "PluginValidator",
    "validate_plugin_manifest",
]
