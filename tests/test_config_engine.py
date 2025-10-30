#!/usr/bin/env python3
"""
Tests for ConfigurationEngine module.

Comprehensive tests to ensure:
- Configuration defaults are correctly loaded and validated
- Configuration merging works as expected
- Configuration validation catches errors
- All mutation points are covered
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Mock sys.argv to prevent argparse issues during import
sys.argv = ["pytest"]

from cli.config_engine import ConfigurationEngine, ConfigEnvironment, ConfigMetadata


@pytest.fixture
def temp_config_dir(tmp_path: Path) -> Path:
    """Create temporary config directory structure."""
    config_dir = tmp_path / ".config"
    config_dir.mkdir()
    (config_dir / "config.yaml").write_text("")
    return config_dir


@pytest.fixture
def config_engine(temp_config_dir: Path) -> ConfigurationEngine:
    """Create ConfigurationEngine instance for testing."""
    with patch.object(ConfigurationEngine, "load_all"):
        engine = ConfigurationEngine(project_root=temp_config_dir.parent)
    return engine


class TestConfigurationEngineDefaults:
    """Tests for default configuration loading."""

    def test_load_defaults_creates_global_config(self, config_engine: ConfigurationEngine) -> None:
        """Test that load_defaults creates global config section."""
        config_engine.load_defaults()
        assert "global" in config_engine.config
        assert isinstance(config_engine.config["global"], dict)

    def test_load_defaults_logging_config(self, config_engine: ConfigurationEngine) -> None:
        """Test logging configuration defaults are correct."""
        config_engine.load_defaults()
        logging_config = config_engine.config["global"]["logging"]

        assert logging_config["enabled"] is True  # Mutation: True -> False
        assert logging_config["level"] == "info"
        assert logging_config["archive"] is True  # Mutation: True -> False

    def test_load_defaults_performance_config(self, config_engine: ConfigurationEngine) -> None:
        """Test performance configuration defaults are correct."""
        config_engine.load_defaults()
        perf_config = config_engine.config["global"]["performance"]

        assert perf_config["parallel_tasks"] == 4
        assert perf_config["timeout"] == 300
        assert perf_config["cache_downloads"] is True  # Mutation: True -> False

    def test_load_defaults_backup_config(self, config_engine: ConfigurationEngine) -> None:
        """Test backup configuration defaults are correct."""
        config_engine.load_defaults()
        backup_config = config_engine.config["global"]["backup"]

        assert backup_config["enabled"] is True  # Mutation: True -> False
        assert backup_config["max_backups"] == 10
        assert backup_config["compress"] is True  # Mutation: True -> False

    def test_load_defaults_verification_config(self, config_engine: ConfigurationEngine) -> None:
        """Test verification configuration defaults are correct."""
        config_engine.load_defaults()
        verification_config = config_engine.config["global"]["verification"]

        assert verification_config["enabled"] is True  # Mutation: True -> False
        assert verification_config["run_after_setup"] is True  # Mutation: True -> False
        assert verification_config["detailed_report"] is True  # Mutation: True -> False

    def test_load_defaults_security_config(self, config_engine: ConfigurationEngine) -> None:
        """Test security configuration defaults are correct."""
        config_engine.load_defaults()
        security_config = config_engine.config["global"]["security"]

        assert security_config["enable_ssh_setup"] is False  # Mutation: False -> True
        assert security_config["enable_gpg_setup"] is False  # Mutation: False -> True
        assert security_config["enable_audit_logging"] is True  # Mutation: True -> False
        assert security_config["require_verification"] is False  # Mutation: False -> True

    def test_load_defaults_updates_config(self, config_engine: ConfigurationEngine) -> None:
        """Test updates configuration defaults are correct."""
        config_engine.load_defaults()
        updates_config = config_engine.config["global"]["updates"]

        assert updates_config["check_for_updates"] is True  # Mutation: True -> False
        assert updates_config["auto_update_tools"] is False  # Mutation: False -> True
        assert updates_config["update_interval"] == "weekly"

    def test_load_defaults_enabled_roles(self, config_engine: ConfigurationEngine) -> None:
        """Test that default enabled roles are set correctly."""
        config_engine.load_defaults()
        enabled_roles = config_engine.config["global"]["enabled_roles"]

        assert "core" in enabled_roles
        assert "shell" in enabled_roles
        assert "development" in enabled_roles
        assert isinstance(enabled_roles, list)
        assert len(enabled_roles) > 0

    def test_load_defaults_disabled_roles_empty(self, config_engine: ConfigurationEngine) -> None:
        """Test that default disabled roles list is empty."""
        config_engine.load_defaults()
        disabled_roles = config_engine.config["global"]["disabled_roles"]

        assert isinstance(disabled_roles, list)
        assert len(disabled_roles) == 0

    def test_load_defaults_plugins_config(self, config_engine: ConfigurationEngine) -> None:
        """Test plugins configuration defaults are correct."""
        config_engine.load_defaults()
        plugins_config = config_engine.config["plugins"]

        assert plugins_config["enabled"] is True
        assert plugins_config["load_custom"] is True
        assert isinstance(plugins_config["hooks"], dict)

    def test_load_defaults_creates_metadata(self, config_engine: ConfigurationEngine) -> None:
        """Test that load_defaults creates metadata entry."""
        config_engine.load_defaults()

        assert "defaults" in config_engine.metadata
        metadata = config_engine.metadata["defaults"]
        assert metadata.source == "schema"
        assert metadata.version == "1.0"

    def test_load_defaults_idempotent(self, config_engine: ConfigurationEngine) -> None:
        """Test that load_defaults can be called multiple times safely."""
        config_engine.load_defaults()
        first_config = config_engine.config.copy()

        config_engine.load_defaults()
        second_config = config_engine.config

        assert first_config["global"]["logging"]["enabled"] == second_config["global"]["logging"]["enabled"]


class TestConfigurationEngineValidation:
    """Tests for configuration validation."""

    def test_validate_and_secure_config_file_creates_with_secure_permissions(
        self, config_engine: ConfigurationEngine, tmp_path: Path
    ) -> None:
        """Test creating config file with secure permissions."""
        config_file = tmp_path / "config.yaml"
        assert not config_file.exists()

        config_engine.validate_and_secure_config_file(config_file)

        assert config_file.exists()
        # Check permissions are 0600
        assert (config_file.stat().st_mode & 0o777) == 0o600

    def test_validate_and_secure_config_file_existing(
        self, config_engine: ConfigurationEngine, tmp_path: Path
    ) -> None:
        """Test validating existing config file."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("test: config")
        config_file.chmod(0o644)  # Insecure permissions

        config_engine.validate_and_secure_config_file(config_file)

        # Permissions should be fixed
        assert (config_file.stat().st_mode & 0o777) == 0o600

    def test_validate_and_secure_config_file_returns_none(
        self, config_engine: ConfigurationEngine, tmp_path: Path
    ) -> None:
        """Test that validation returns None on success."""
        config_file = tmp_path / "config.yaml"
        result = config_engine.validate_and_secure_config_file(config_file)
        assert result is None


class TestConfigurationEngineInit:
    """Tests for ConfigurationEngine initialization."""

    def test_init_with_default_project_root(self, config_engine: ConfigurationEngine) -> None:
        """Test initialization with default project root."""
        assert config_engine.project_root is not None
        assert isinstance(config_engine.project_root, Path)

    def test_init_creates_logger(self, config_engine: ConfigurationEngine) -> None:
        """Test that initialization creates a logger."""
        assert config_engine.logger is not None
        assert hasattr(config_engine.logger, "info")

    def test_init_config_empty(self, config_engine: ConfigurationEngine) -> None:
        """Test that config is initially empty."""
        assert isinstance(config_engine.config, dict)
        assert len(config_engine.config) == 0

    def test_init_metadata_empty(self, config_engine: ConfigurationEngine) -> None:
        """Test that metadata is initially empty."""
        assert isinstance(config_engine.metadata, dict)
        assert len(config_engine.metadata) == 0

    def test_init_with_custom_logger(self, tmp_path: Path) -> None:
        """Test initialization with custom logger."""
        custom_logger = Mock()
        engine = ConfigurationEngine(project_root=str(tmp_path), logger=custom_logger)

        assert engine.logger is custom_logger


class TestConfigMetadata:
    """Tests for ConfigMetadata dataclass."""

    def test_config_metadata_creation(self) -> None:
        """Test creating ConfigMetadata."""
        metadata = ConfigMetadata(
            source="test.yaml", timestamp="2024-01-01T00:00:00", version="1.0"
        )

        assert metadata.source == "test.yaml"
        assert metadata.timestamp == "2024-01-01T00:00:00"
        assert metadata.version == "1.0"


class TestConfigEnvironment:
    """Tests for ConfigEnvironment enum."""

    def test_config_environment_development(self) -> None:
        """Test development environment value."""
        assert ConfigEnvironment.DEVELOPMENT.value == "development"

    def test_config_environment_staging(self) -> None:
        """Test staging environment value."""
        assert ConfigEnvironment.STAGING.value == "staging"

    def test_config_environment_production(self) -> None:
        """Test production environment value."""
        assert ConfigEnvironment.PRODUCTION.value == "production"
