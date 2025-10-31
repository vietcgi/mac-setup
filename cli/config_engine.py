#!/usr/bin/env python3
"""
Mac-Setup Configuration Engine

Handles loading, validating, merging, and managing configuration from multiple sources.
Supports YAML configuration files, environment variables, and runtime overrides.
"""

import os
import yaml
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import sys
from datetime import datetime, timedelta
from collections import deque

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


class ConfigEnvironment(Enum):
    """Configuration environment types."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class RateLimiter:
    """
    Rate limiter for sensitive configuration operations.

    SECURITY: Prevents abuse and brute-force attacks by limiting
    the number of sensitive operations (like config changes) within
    a time window.

    Default: Max 5 operations per 60 seconds
    """

    def __init__(self, max_operations: int = 5, window_seconds: int = 60):
        """
        Initialize rate limiter.

        Args:
            max_operations: Maximum operations allowed in time window
            window_seconds: Time window in seconds
        """
        self.max_operations = max_operations
        self.window_seconds = window_seconds
        self.operations: Dict[str, deque] = {}

    def is_allowed(self, identifier: str) -> Tuple[bool, str]:
        """
        Check if operation is allowed for given identifier.

        Args:
            identifier: User, IP, or operation identifier

        Returns:
            Tuple of (is_allowed, message)
        """
        now = datetime.now()

        # Initialize operation list if needed
        if identifier not in self.operations:
            self.operations[identifier] = deque()

        # Remove old operations outside time window
        operations = self.operations[identifier]
        window_start = now - timedelta(seconds=self.window_seconds)

        while operations and operations[0] < window_start:
            operations.popleft()

        # Check if within limit
        if len(operations) < self.max_operations:
            operations.append(now)
            remaining = self.max_operations - len(operations)
            return True, f"Operation allowed ({remaining} remaining)"

        # Rate limit exceeded
        oldest_op = operations[0]
        reset_time = oldest_op + timedelta(seconds=self.window_seconds)
        wait_seconds = (reset_time - now).total_seconds()

        return False, (
            f"Rate limit exceeded: {len(operations)}/{self.max_operations} "
            f"operations in {self.window_seconds}s window. "
            f"Please wait {wait_seconds:.1f} seconds."
        )

    def reset(self, identifier: Optional[str] = None) -> None:
        """
        Reset rate limit for identifier or all identifiers.

        Args:
            identifier: Identifier to reset (None resets all)
        """
        if identifier:
            self.operations.pop(identifier, None)
        else:
            self.operations.clear()

    def get_stats(self, identifier: str) -> Dict[str, Any]:
        """
        Get rate limit statistics for identifier.

        Returns:
            Dictionary with operation count and reset time
        """
        if identifier not in self.operations:
            return {
                "identifier": identifier,
                "operations_count": 0,
                "max_operations": self.max_operations,
                "window_seconds": self.window_seconds,
                "next_reset": None
            }

        operations = self.operations[identifier]
        now = datetime.now()

        next_reset = None
        if operations:
            oldest_op = operations[0]
            next_reset = (oldest_op + timedelta(seconds=self.window_seconds)).isoformat()

        return {
            "identifier": identifier,
            "operations_count": len(operations),
            "max_operations": self.max_operations,
            "window_seconds": self.window_seconds,
            "next_reset": next_reset
        }


@dataclass
class ConfigMetadata:
    """Metadata about a configuration."""

    source: str  # File path or "environment", "cli", "default"
    timestamp: str
    version: str


class ConfigurationEngine:
    """
    Main configuration engine for mac-setup.

    Loads configuration from multiple sources in priority order:
    1. CLI arguments (highest priority)
    2. Environment variables
    3. Local config file (~/.mac-setup/config.yaml)
    4. Group config (config/groups/{group}.yaml)
    5. Role configs (config/roles/{role}.yaml)
    6. Platform config (config/platforms/{platform}.yaml)
    7. Schema defaults (lowest priority)
    """

    def __init__(
        self,
        project_root: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
        enable_rate_limiting: bool = False,
    ):
        """
        Initialize configuration engine.

        Args:
            project_root: Path to mac-setup project root
            logger: Logger instance
            enable_rate_limiting: Enable rate limiting on sensitive operations
        """
        self.project_root = Path(project_root or Path(__file__).parent.parent)
        self.logger = logger or self._setup_logger()
        self.config: Dict[str, Any] = {}
        self.metadata: Dict[str, ConfigMetadata] = {}
        self._loaded_files: List[Path] = []

        # Rate limiting for sensitive operations
        self.enable_rate_limiting = enable_rate_limiting
        self.rate_limiter = RateLimiter(max_operations=5, window_seconds=60)

    def _setup_logger(self) -> logging.Logger:
        """Setup default logger."""
        logger = logging.getLogger("mac-setup.config")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(levelname)s: %(message)s")
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def validate_and_secure_config_file(self, config_path: Path) -> None:
        """
        Validate and secure configuration file permissions.

        Config files may contain sensitive data (API keys, tokens, etc.)
        and must have restrictive permissions (0600 - user read/write only).

        Args:
            config_path: Path to configuration file

        Raises:
            PermissionError: If file is owned by different user
            OSError: If unable to fix permissions
        """
        if not config_path.exists():
            # Create with secure permissions (0600)
            config_path.parent.mkdir(parents=True, exist_ok=True)
            config_path.touch(mode=0o600)
            self.logger.debug(f"Created {config_path} with secure permissions (0600)")
            return

        # Get file stats
        try:
            stat_info = config_path.stat()
        except OSError as e:
            self.logger.error(f"Cannot access config file: {e}")
            raise

        # Verify ownership - file must be owned by current user
        current_uid = os.getuid()
        if stat_info.st_uid != current_uid:
            raise PermissionError(
                f"Config file {config_path} is owned by different user "
                f"(uid: {stat_info.st_uid}, current: {current_uid}). "
                f"This could be a security risk."
            )

        # Check file permissions
        file_mode = stat_info.st_mode & 0o777
        if file_mode != 0o600:
            self.logger.warning(
                f"Config file {config_path} has insecure permissions: {oct(file_mode)}"
            )
            self.logger.info("Fixing permissions to 0600 (user read/write only)...")

            try:
                config_path.chmod(0o600)
                self.logger.info(f"✓ Fixed config permissions for {config_path}")
            except OSError as e:
                self.logger.error(f"Cannot fix file permissions: {e}")
                raise PermissionError(f"Unable to fix permissions on {config_path}: {e}")

    def load_defaults(self) -> None:
        """Load default configuration from schema."""
        self.logger.debug("Loading default configuration")
        defaults = {
            "global": {
                "setup_name": "Development Environment",
                "setup_environment": "development",
                "enabled_roles": [
                    "core",
                    "shell",
                    "editors",
                    "languages",
                    "development",
                    "containers",
                    "cloud",
                ],
                "disabled_roles": [],
                "logging": {
                    "enabled": True,
                    "level": "info",
                    "file": "~/.mac-setup/logs/setup.log",
                    "archive": True,
                },
                "performance": {
                    "parallel_tasks": 4,
                    "timeout": 300,
                    "cache_downloads": True,
                },
                "backup": {
                    "enabled": True,
                    "path": "~/.mac-setup/backups",
                    "max_backups": 10,
                    "compress": True,
                },
                "verification": {
                    "enabled": True,
                    "run_after_setup": True,
                    "detailed_report": True,
                },
                "security": {
                    "enable_ssh_setup": False,
                    "enable_gpg_setup": False,
                    "enable_audit_logging": True,
                    "require_verification": False,
                },
                "updates": {
                    "check_for_updates": True,
                    "auto_update_tools": False,
                    "update_interval": "weekly",
                },
            },
            "roles": {},
            "groups": {},
            "platforms": {},
            "plugins": {
                "enabled": True,
                "load_custom": True,
                "custom_path": "~/.mac-setup/plugins",
                "hooks": {},
            },
        }
        self.config = defaults
        self.metadata["defaults"] = ConfigMetadata(
            source="schema",
            timestamp=self._get_timestamp(),
            version="1.0",
        )

    def load_file(self, file_path: str | Path, section: Optional[str] = None) -> Dict[str, Any]:
        """
        Load configuration from YAML file.

        Args:
            file_path: Path to configuration file
            section: Optional section to extract (e.g., "global", "shell")

        Returns:
            Loaded configuration dictionary
        """
        path = Path(file_path).expanduser()
        if not path.exists():
            self.logger.warning(f"Configuration file not found: {path}")
            return {}

        try:
            with open(path, "r") as f:
                config = yaml.safe_load(f) or {}
            self._loaded_files.append(path)
            self.logger.debug(f"Loaded config from {path}")

            if section and section in config:
                config = config[section]

            return config
        except yaml.YAMLError as e:
            self.logger.error(f"Invalid YAML in {path}: {e}")
            return {}
        except Exception as e:
            self.logger.error(f"Error loading {path}: {e}")
            return {}

    def load_environment_overrides(self) -> Dict[str, Any]:
        """
        Load configuration from environment variables.

        Supports variables like:
        - MAC_SETUP_ENABLED_ROLES=core,shell,editors
        - MAC_SETUP_LOGGING_LEVEL=debug
        """
        overrides: dict[str, Any] = {}
        prefix = "MAC_SETUP_"

        for key, value in os.environ.items():
            if not key.startswith(prefix):
                continue

            # Convert MAC_SETUP_ENABLED_ROLES to enabled_roles
            config_key = key[len(prefix) :].lower()

            # Parse value (handle arrays and booleans)
            parsed_value: str | bool | list[str]
            if value.lower() in ("true", "false"):
                parsed_value = value.lower() == "true"
            elif "," in value:
                parsed_value = [v.strip() for v in value.split(",")]
            else:
                parsed_value = value

            # Nested keys use double underscore: MAC_SETUP_LOGGING__LEVEL
            if "__" in config_key:
                parts = config_key.split("__")
                current: Any = overrides
                for part in parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                current[parts[-1]] = parsed_value
            else:
                overrides[config_key] = parsed_value

        if overrides:
            self.logger.debug(f"Loaded environment overrides: {overrides}")
            self.metadata["environment"] = ConfigMetadata(
                source="environment",
                timestamp=self._get_timestamp(),
                version="1.0",
            )

        return overrides

    def load_all(
        self,
        group: Optional[str] = None,
        platform: Optional[str] = None,
        local_config: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Load all configuration in priority order.

        Args:
            group: Machine group (development, design, qa, sre)
            platform: Platform (macos, linux)
            local_config: Path to local config file

        Returns:
            Merged configuration dictionary
        """
        self.logger.info("Loading configuration...")

        # 1. Load defaults
        self.load_defaults()

        # 2. Load platform-specific config
        if platform:
            platform_config = self.load_file(
                self.project_root / "config" / "platforms" / f"{platform}.yaml"
            )
            self._deep_merge(self.config, platform_config)
            self.logger.debug(f"Merged platform config: {platform}")

        # 3. Load group config
        if group:
            group_config = self.load_file(self.project_root / "config" / "groups" / f"{group}.yaml")
            self._deep_merge(self.config, group_config)
            self.logger.debug(f"Merged group config: {group}")

        # 4. Load global config from project
        global_config = self.load_file(self.project_root / "config" / "config.yaml")
        self._deep_merge(self.config, global_config)

        # 5. Load local user config
        if local_config:
            local = self.load_file(local_config)
            self._deep_merge(self.config, local)
        else:
            # Try default local config location
            local = self.load_file(Path.home() / ".mac-setup" / "config.yaml")
            if local:
                self._deep_merge(self.config, local)

        # 6. Load environment variable overrides
        env_overrides = self.load_environment_overrides()
        self._deep_merge(self.config, {"global": env_overrides})

        self.logger.info(f"Configuration loaded from {len(self._loaded_files)} files")
        return self.config

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-notation key.

        Examples:
            config.get("global.logging.level")
            config.get("roles.shell.enabled", True)
        """
        keys = key.split(".")
        value = self.config

        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value: Any, user_id: Optional[str] = None) -> Tuple[bool, str]:
        """
        Set configuration value by dot-notation key.

        SECURITY: Applies rate limiting to prevent abuse of config changes.

        Examples:
            success, msg = config.set("global.logging.level", "debug")
            success, msg = config.set("roles.shell.enabled", True)

        Args:
            key: Configuration key in dot notation
            value: New value
            user_id: User identifier for rate limiting (default: current user)

        Returns:
            Tuple of (success, message)
        """
        # Check rate limit if enabled
        if self.enable_rate_limiting:
            user = user_id or os.getenv("USER", "unknown")
            allowed, message = self.rate_limiter.is_allowed(user)

            if not allowed:
                self.logger.warning(f"Rate limit: {message}")
                return False, message

        keys = key.split(".")
        target = self.config

        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]

        target[keys[-1]] = value
        self.logger.debug(f"Set {key} = {value}")
        return True, "Configuration updated"

    def validate(self) -> Tuple[bool, List[str]]:
        """
        Validate configuration against schema.

        Returns:
            Tuple of (is_valid, error_list)
        """
        errors = []

        # Validate global settings
        valid_environments = ["development", "staging", "production"]
        if self.get("global.setup_environment") not in valid_environments:
            errors.append(f"Invalid setup_environment: {self.get('global.setup_environment')}")

        # Validate enabled/disabled roles don't overlap
        enabled = set(self.get("global.enabled_roles", []))
        disabled = set(self.get("global.disabled_roles", []))
        overlap = enabled & disabled
        if overlap:
            errors.append(f"Roles in both enabled and disabled: {overlap}")

        # Validate logging level
        valid_levels = ["debug", "info", "warning", "error"]
        if self.get("global.logging.level") not in valid_levels:
            errors.append(f"Invalid logging level: {self.get('global.logging.level')}")

        # Validate performance settings
        if self.get("global.performance.parallel_tasks", 1) < 1:
            errors.append("parallel_tasks must be >= 1")

        if self.get("global.performance.timeout", 30) < 30:
            errors.append("timeout must be >= 30 seconds")

        return len(errors) == 0, errors

    def export(self, format_type: str = "yaml") -> str:
        """
        Export configuration in specified format.

        Args:
            format_type: "yaml" or "json"

        Returns:
            Formatted configuration string
        """
        if format_type == "json":
            return json.dumps(self.config, indent=2)
        elif format_type == "yaml":
            yaml_str = yaml.dump(self.config, default_flow_style=False)
            return yaml_str if yaml_str is not None else ""
        else:
            raise ValueError(f"Unsupported format: {format_type}")

    def save(self, file_path: str | Path) -> None:
        """Save current configuration to file."""
        path = Path(file_path).expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w") as f:
            f.write(self.export("yaml"))

        self.logger.info(f"Configuration saved to {path}")

    def _deep_merge(self, base: Dict, override: Dict) -> None:
        """Deep merge override into base dictionary."""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value

    @staticmethod
    def _get_timestamp() -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime

        return datetime.now().isoformat()

    def list_loaded_files(self) -> List[str]:
        """Get list of loaded configuration files."""
        return [str(f) for f in self._loaded_files]

    def get_enabled_roles(self) -> List[str]:
        """Get list of enabled roles based on current configuration."""
        enabled = self.get("global.enabled_roles", [])
        disabled = self.get("global.disabled_roles", [])
        return [r for r in enabled if r not in disabled]

    def get_role_config(self, role: str) -> Dict[str, Any]:
        """Get configuration for specific role."""
        role_config: Any = self.get(f"roles.{role}", {})
        if isinstance(role_config, dict):
            config_value: Any = role_config.get("config", {})
            return config_value if isinstance(config_value, dict) else {}
        return {}

    def get_rate_limit_stats(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get rate limiting statistics for user.

        Args:
            user_id: User identifier (default: current user)

        Returns:
            Rate limit statistics
        """
        user = user_id or os.getenv("USER", "unknown")
        return self.rate_limiter.get_stats(user)

    def reset_rate_limit(self, user_id: Optional[str] = None) -> None:
        """
        Reset rate limit for user or all users.

        Args:
            user_id: User identifier (None resets all)
        """
        self.rate_limiter.reset(user_id)


def main():
    """CLI interface for configuration engine."""
    import argparse

    parser = argparse.ArgumentParser(description="Mac-Setup Configuration Engine")
    parser.add_argument("--project-root", default=str(Path(__file__).parent.parent))
    parser.add_argument("--group", help="Machine group")
    parser.add_argument("--platform", default="macos", help="Platform (macos/linux)")
    parser.add_argument("--config", help="Custom config file path")
    parser.add_argument("--get", help="Get config value (dot notation)")
    parser.add_argument("--set", nargs=2, metavar=("KEY", "VALUE"), help="Set config value")
    parser.add_argument("--validate", action="store_true", help="Validate configuration")
    parser.add_argument("--export", choices=["yaml", "json"], help="Export configuration")
    parser.add_argument("--list-files", action="store_true", help="List loaded files")
    parser.add_argument("--list-roles", action="store_true", help="List enabled roles")

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")

    # Create engine and load config
    engine = ConfigurationEngine(args.project_root)
    engine.load_all(group=args.group, platform=args.platform, local_config=args.config)

    # Handle various commands
    if args.validate:
        is_valid, errors = engine.validate()
        if is_valid:
            print("✓ Configuration is valid")
            sys.exit(0)
        else:
            print("✗ Configuration errors:")
            for error in errors:
                print(f"  - {error}")
            sys.exit(1)

    elif args.get:
        value = engine.get(args.get)
        print(yaml.dump({args.get: value}, default_flow_style=False))

    elif args.set:
        success, message = engine.set(args.set[0], args.set[1])
        if success:
            engine.save(Path.home() / ".mac-setup" / "config.yaml")
            print(f"✓ {message}")
        else:
            print(f"✗ {message}")
            sys.exit(1)

    elif args.list_files:
        print("Loaded configuration files:")
        for f in engine.list_loaded_files():
            print(f"  - {f}")

    elif args.list_roles:
        print("Enabled roles:")
        for role in engine.get_enabled_roles():
            print(f"  - {role}")

    elif args.export:
        print(engine.export(args.export))

    else:
        # Default: show summary
        is_valid, errors = engine.validate()
        print(f"Environment: {engine.get('global.setup_environment')}")
        print(f"Enabled roles: {len(engine.get_enabled_roles())}")
        print(f"Valid: {is_valid}")
        if errors:
            print(f"Errors: {len(errors)}")


if __name__ == "__main__":
    main()
