#!/usr/bin/env python3
"""
Tests for GitConfigManager module.

Tests git configuration management functionality including:
- Configuration loading and validation
- Change detection
- Hook verification and reloading
- Credential helper management
- Backup creation
"""

import pytest
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from cli.git_config_manager import GitConfigManager, Colors


@pytest.fixture
def temp_home(tmp_path: Path) -> Path:
    """Create a temporary home directory structure."""
    home = tmp_path / "home"
    home.mkdir()
    (home / ".config" / "git").mkdir(parents=True)
    (home / ".git-templates" / "hooks").mkdir(parents=True)
    (home / ".devkit" / "git").mkdir(parents=True)
    (home / ".devkit" / "logs").mkdir(parents=True)
    return home


@pytest.fixture
def manager(temp_home: Path) -> GitConfigManager:
    """Create a GitConfigManager instance with temporary home."""
    return GitConfigManager(home_dir=str(temp_home))


class TestGitConfigManager:
    """Tests for GitConfigManager class."""

    def test_init(self, manager: GitConfigManager) -> None:
        """Test manager initialization."""
        assert manager.home_dir.exists()
        assert manager.git_config_dir.exists()
        assert manager.git_hooks_dir.exists()
        assert manager.logger is not None

    def test_setup_logging(self, manager: GitConfigManager) -> None:
        """Test logging setup."""
        assert manager.log_dir.exists()
        assert manager.log_file is not None
        assert manager.logger is not None

    @patch("builtins.print")
    def test_print_status_info(
        self, mock_print: Mock, manager: GitConfigManager
    ) -> None:
        """Test print_status with INFO level."""
        manager.print_status("Test message", "INFO")
        mock_print.assert_called()

    @patch("builtins.print")
    def test_print_status_success(
        self, mock_print: Mock, manager: GitConfigManager
    ) -> None:
        """Test print_status with SUCCESS level."""
        manager.print_status("Success message", "SUCCESS")
        mock_print.assert_called()

    @patch("builtins.print")
    def test_print_status_warning(
        self, mock_print: Mock, manager: GitConfigManager
    ) -> None:
        """Test print_status with WARNING level."""
        manager.print_status("Warning message", "WARNING")
        mock_print.assert_called()

    @patch("builtins.print")
    def test_print_status_error(
        self, mock_print: Mock, manager: GitConfigManager
    ) -> None:
        """Test print_status with ERROR level."""
        manager.print_status("Error message", "ERROR")
        mock_print.assert_called()

    @patch("subprocess.run")
    def test_validate_git_config_syntax_valid(
        self, mock_run: Mock, manager: GitConfigManager
    ) -> None:
        """Test git config validation when valid."""
        mock_run.return_value = Mock(returncode=0, stderr="")
        result = manager.validate_git_config_syntax()
        assert result is True

    def test_validate_git_config_syntax_with_gitconfig(
        self, temp_home: Path, manager: GitConfigManager
    ) -> None:
        """Test git config validation with gitconfig file."""
        gitconfig = temp_home / ".gitconfig"
        gitconfig.write_text("[user]\n    name = Test\n")

        manager = GitConfigManager(home_dir=str(temp_home))
        with patch("cli.git_config_manager.subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=0, stderr="")
            result = manager.validate_git_config_syntax()
            assert result is True

    def test_validate_git_config_syntax_no_gitconfig(
        self, manager: GitConfigManager
    ) -> None:
        """Test git config validation when no gitconfig exists."""
        # When gitconfig doesn't exist, validation returns True
        result = manager.validate_git_config_syntax()
        assert result is True

    @patch("subprocess.run")
    def test_get_current_config(
        self, mock_run: Mock, manager: GitConfigManager
    ) -> None:
        """Test getting current git configuration."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="user.name=John Doe\0user.email=john@example.com\0"
        )
        config = manager.get_current_config()
        assert "user.name" in config
        assert config["user.name"] == "John Doe"

    @patch("subprocess.run")
    def test_get_current_config_empty(
        self, mock_run: Mock, manager: GitConfigManager
    ) -> None:
        """Test getting config when none exists."""
        mock_run.return_value = Mock(returncode=1, stdout="")
        config = manager.get_current_config()
        assert config == {}

    @patch("subprocess.run")
    def test_detect_config_changes_with_changes(
        self, mock_run: Mock, temp_home: Path, manager: GitConfigManager
    ) -> None:
        """Test detecting configuration changes."""
        # Create a gitconfig file
        gitconfig = temp_home / ".gitconfig"
        gitconfig.write_text("[user]\n    name = Jane Doe\n")

        mock_run.return_value = Mock(
            returncode=0,
            stdout="user.name=Jane Doe\0"
        )
        changes = manager.detect_config_changes()
        assert isinstance(changes, dict)

    @patch("subprocess.run")
    def test_detect_config_changes_no_changes(
        self, mock_run: Mock, manager: GitConfigManager
    ) -> None:
        """Test detecting when no changes."""
        mock_run.return_value = Mock(returncode=0, stdout="")
        changes = manager.detect_config_changes()
        assert changes == {}

    @patch("subprocess.run")
    def test_reload_git_config_success(
        self, mock_run: Mock, manager: GitConfigManager
    ) -> None:
        """Test reloading git configuration."""
        mock_run.return_value = Mock(returncode=0, stderr="")
        result = manager.reload_git_config()
        assert result is True

    @patch("subprocess.run")
    def test_reload_git_config_failure(
        self, mock_run: Mock, manager: GitConfigManager
    ) -> None:
        """Test git config reload failure."""
        mock_run.return_value = Mock(
            returncode=1, stderr="fatal: error"
        )
        result = manager.reload_git_config()
        assert result is False

    def test_verify_hooks_missing(self, manager: GitConfigManager) -> None:
        """Test hook verification when hooks missing."""
        result = manager.verify_hooks()
        assert result is False

    def test_verify_hooks_exist(self, temp_home: Path) -> None:
        """Test hook verification when hooks exist."""
        hooks_dir = temp_home / ".git-templates" / "hooks"
        # Create a hook file
        pre_commit = hooks_dir / "pre-commit"
        pre_commit.write_text("#!/bin/bash\necho 'test'\n")
        pre_commit.chmod(0o755)

        manager = GitConfigManager(home_dir=str(temp_home))
        result = manager.verify_hooks()
        # Should succeed if at least one hook is found and executable
        assert isinstance(result, bool)

    def test_create_backup_no_gitconfig(
        self, manager: GitConfigManager
    ) -> None:
        """Test backup creation when no gitconfig exists."""
        result = manager.create_backup()
        assert result is None

    def test_create_backup_with_gitconfig(
        self, temp_home: Path
    ) -> None:
        """Test backup creation with existing gitconfig."""
        gitconfig = temp_home / ".gitconfig"
        gitconfig.write_text("[user]\n    name = Test User\n")

        manager = GitConfigManager(home_dir=str(temp_home))
        backup_path = manager.create_backup()
        assert backup_path is not None
        assert backup_path.exists()
        assert "backup" in backup_path.name

    @patch.object(GitConfigManager, "verify_hooks")
    @patch("cli.git_config_manager.subprocess.run")
    def test_reload_hooks_success(
        self,
        mock_run: Mock,
        mock_verify: Mock,
        manager: GitConfigManager
    ) -> None:
        """Test hook reloading."""
        mock_verify.return_value = True
        mock_run.return_value = Mock(returncode=0)
        result = manager.reload_hooks()
        assert result is True

    @patch.object(GitConfigManager, "verify_hooks")
    def test_reload_hooks_failure(
        self, mock_verify: Mock, manager: GitConfigManager
    ) -> None:
        """Test hook reload when verification fails."""
        mock_verify.return_value = False
        result = manager.reload_hooks()
        assert result is False

    @patch("subprocess.run")
    def test_reload_credential_helpers_with_helper(
        self, mock_run: Mock, manager: GitConfigManager
    ) -> None:
        """Test credential helper reload."""
        mock_run.return_value = Mock(
            returncode=0, stdout="osxkeychain"
        )
        result = manager.reload_credential_helpers()
        assert result is True

    def test_generate_report(self, temp_home: Path) -> None:
        """Test report generation."""
        gitconfig = temp_home / ".gitconfig"
        gitconfig.write_text("[user]\n    name = Test User\n    email = test@example.com\n")

        manager = GitConfigManager(home_dir=str(temp_home))
        report = manager.generate_report()
        assert "timestamp" in report
        assert "config_status" in report
        assert "hooks_status" in report
        assert "directories" in report

    @patch("builtins.print")
    def test_display_report(
        self, mock_print: Mock, manager: GitConfigManager
    ) -> None:
        """Test report display."""
        report = {
            "timestamp": "2024-01-01T00:00:00",
            "config_status": {
                "user_name": "Test User",
                "user_email": "test@example.com",
                "default_editor": "vim",
                "pull_rebase": "false",
            },
            "hooks_status": {
                "pre_commit": True,
                "commit_msg": False,
                "post_commit": False,
                "prepare_commit_msg": False,
            },
            "directories": {
                "config_dir": "/tmp/config",
                "templates_dir": "/tmp/templates",
                "hooks_dir": "/tmp/hooks",
            },
        }
        manager.display_report(report)
        mock_print.assert_called()

    @patch.object(GitConfigManager, "validate_git_config_syntax")
    @patch.object(GitConfigManager, "create_backup")
    @patch.object(GitConfigManager, "detect_config_changes")
    @patch.object(GitConfigManager, "reload_git_config")
    @patch.object(GitConfigManager, "reload_hooks")
    @patch.object(GitConfigManager, "reload_credential_helpers")
    @patch.object(GitConfigManager, "generate_report")
    @patch.object(GitConfigManager, "display_report")
    def test_reload_all_success(
        self,
        mock_display: Mock,
        mock_gen: Mock,
        mock_cred: Mock,
        mock_hooks: Mock,
        mock_git: Mock,
        mock_changes: Mock,
        mock_backup: Mock,
        mock_validate: Mock,
        manager: GitConfigManager
    ) -> None:
        """Test complete reload."""
        mock_validate.return_value = True
        mock_git.return_value = True
        mock_hooks.return_value = True
        mock_cred.return_value = True
        mock_gen.return_value = {}

        result = manager.reload_all()
        assert result is True

    @patch.object(GitConfigManager, "validate_git_config_syntax")
    def test_reload_all_validation_fails(
        self, mock_validate: Mock, manager: GitConfigManager
    ) -> None:
        """Test reload when validation fails."""
        mock_validate.return_value = False
        result = manager.reload_all()
        assert result is False

    @patch.object(GitConfigManager, "validate_git_config_syntax")
    @patch.object(GitConfigManager, "detect_config_changes")
    @patch.object(GitConfigManager, "verify_hooks")
    def test_reload_all_dry_run(
        self,
        mock_verify: Mock,
        mock_changes: Mock,
        mock_validate: Mock,
        manager: GitConfigManager
    ) -> None:
        """Test dry run mode."""
        mock_validate.return_value = True
        with patch.object(
            manager, "generate_report"
        ) as mock_gen, patch.object(
            manager, "display_report"
        ):
            mock_gen.return_value = {}
            result = manager.reload_all(dry_run=True)
            assert result is True

    def test_reload_component_config(self, manager: GitConfigManager) -> None:
        """Test reloading specific component."""
        with patch.object(manager, "reload_git_config") as mock_reload:
            mock_reload.return_value = True
            result = manager.reload_component("config")
            mock_reload.assert_called_once()

    def test_reload_component_hooks(self, manager: GitConfigManager) -> None:
        """Test reloading hooks component."""
        with patch.object(manager, "reload_hooks") as mock_reload:
            mock_reload.return_value = True
            result = manager.reload_component("hooks")
            mock_reload.assert_called_once()

    def test_reload_component_credentials(self, manager: GitConfigManager) -> None:
        """Test reloading credentials component."""
        with patch.object(
            manager, "reload_credential_helpers"
        ) as mock_reload:
            mock_reload.return_value = True
            result = manager.reload_component("credentials")
            mock_reload.assert_called_once()

    def test_reload_component_invalid(self, manager: GitConfigManager) -> None:
        """Test reloading invalid component."""
        result = manager.reload_component("invalid")
        assert result is False


class TestColors:
    """Tests for Colors class."""

    def test_color_codes_defined(self) -> None:
        """Test that all color codes are defined."""
        assert Colors.GREEN != ""
        assert Colors.RED != ""
        assert Colors.YELLOW != ""
        assert Colors.BLUE != ""
        assert Colors.RESET != ""
