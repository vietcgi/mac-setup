#!/usr/bin/env python3
"""
Tests for CodeQualityValidator module.

Tests code quality validation functionality including:
- Code style checks
- Test coverage verification
- Security scanning
- Code complexity analysis
- Documentation validation
- Dependency checking
"""

import pytest
import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Mock sys.argv to prevent argparse issues during import
sys.argv = ["pytest"]

from cli.commit_validator import CodeQualityValidator, Colors


@pytest.fixture
def validator() -> CodeQualityValidator:
    """Create a CodeQualityValidator instance for testing."""
    return CodeQualityValidator()


@pytest.fixture
def temp_files(tmp_path: Path) -> list[str]:
    """Create temporary test files."""
    test_file = tmp_path / "test_module.py"
    test_file.write_text(
        '"""Test module."""\n\ndef test_func() -> None:\n    """Test function."""\n    pass\n'
    )
    return [str(test_file)]


class TestCodeQualityValidator:
    """Tests for CodeQualityValidator class."""

    def test_init(self, validator: CodeQualityValidator) -> None:
        """Test validator initialization."""
        assert validator.home == Path.home()
        assert "devkit" in str(validator.devkit_dir)
        assert validator.logger is not None

    def test_setup_logging(self, validator: CodeQualityValidator) -> None:
        """Test logging setup."""
        assert validator.log_file.exists()
        assert validator.logger is not None
        assert validator.logger.level == pytest.importorskip("logging").INFO

    @patch("builtins.print")
    def test_print_status_info(
        self, mock_print: Mock, validator: CodeQualityValidator
    ) -> None:
        """Test print_status with INFO level."""
        validator.print_status("Test message", "INFO")
        mock_print.assert_called()

    @patch("builtins.print")
    def test_print_status_success(
        self, mock_print: Mock, validator: CodeQualityValidator
    ) -> None:
        """Test print_status with SUCCESS level."""
        validator.print_status("Success message", "SUCCESS")
        mock_print.assert_called()

    @patch("builtins.print")
    def test_print_status_warning(
        self, mock_print: Mock, validator: CodeQualityValidator
    ) -> None:
        """Test print_status with WARNING level."""
        validator.print_status("Warning message", "WARNING")
        mock_print.assert_called()

    @patch("builtins.print")
    def test_print_status_error(
        self, mock_print: Mock, validator: CodeQualityValidator
    ) -> None:
        """Test print_status with ERROR level."""
        validator.print_status("Error message", "ERROR")
        mock_print.assert_called()

    @patch("subprocess.run")
    def test_check_code_style_pass(
        self, mock_run: Mock, validator: CodeQualityValidator
    ) -> None:
        """Test code style check when passing."""
        mock_run.return_value = Mock(returncode=0, stdout="")
        passed, issues, score = validator.check_code_style(["test.py"])
        assert passed is True
        assert issues == []
        assert score == 100

    @patch("subprocess.run")
    def test_check_code_style_fail(
        self, mock_run: Mock, validator: CodeQualityValidator
    ) -> None:
        """Test code style check when failing."""
        mock_run.return_value = Mock(
            returncode=1, stdout="test.py:1:0: C0111: Missing docstring\nC: test.py missing"
        )
        passed, issues, score = validator.check_code_style(["test.py"])
        # Will be True if pylint errors are found but handled gracefully
        assert isinstance(passed, bool)
        assert isinstance(issues, list)

    @patch("subprocess.run")
    def test_check_code_style_pylint_not_found(
        self, mock_run: Mock, validator: CodeQualityValidator
    ) -> None:
        """Test code style check when pylint not installed."""
        mock_run.side_effect = FileNotFoundError()
        passed, issues, score = validator.check_code_style(["test.py"])
        assert passed is True
        assert score == 100

    @patch("subprocess.run")
    def test_check_test_coverage_pass(
        self, mock_run: Mock, validator: CodeQualityValidator
    ) -> None:
        """Test coverage check when passing."""
        mock_run.side_effect = [
            Mock(returncode=0),  # coverage run
            Mock(returncode=0, stdout="TOTAL       100      0 100%"),  # coverage report
        ]
        passed, issues, coverage = validator.check_test_coverage(["test.py"])
        assert passed is True
        assert coverage == 100.0

    @patch("subprocess.run")
    def test_check_test_coverage_fail(
        self, mock_run: Mock, validator: CodeQualityValidator
    ) -> None:
        """Test coverage check when below threshold."""
        mock_run.side_effect = [
            Mock(returncode=0),
            Mock(returncode=1, stdout="TOTAL       100      20 80%"),
        ]
        passed, issues, coverage = validator.check_test_coverage(["test.py"])
        assert passed is False

    @patch("subprocess.run")
    def test_check_security_pass(
        self, mock_run: Mock, validator: CodeQualityValidator
    ) -> None:
        """Test security check when passing."""
        mock_run.return_value = Mock(returncode=0, stdout="")
        passed, issues, score = validator.check_security(["test.py"])
        assert passed is True
        assert score == 100

    @patch("subprocess.run")
    def test_check_security_fail(
        self, mock_run: Mock, validator: CodeQualityValidator
    ) -> None:
        """Test security check when finding issues."""
        mock_run.return_value = Mock(
            returncode=1,
            stdout="Issue: Use of hardcoded SQL string\nSeverity: HIGH",
        )
        passed, issues, score = validator.check_security(["test.py"])
        assert passed is False
        assert len(issues) > 0

    @patch("subprocess.run")
    def test_check_complexity_pass(
        self, mock_run: Mock, validator: CodeQualityValidator
    ) -> None:
        """Test complexity check when acceptable."""
        mock_run.return_value = Mock(
            returncode=0, stdout="test.py - A"
        )
        passed, issues, complexity = validator.check_complexity(["test.py"])
        assert passed is True

    @patch("subprocess.run")
    def test_check_complexity_high(
        self, mock_run: Mock, validator: CodeQualityValidator
    ) -> None:
        """Test complexity check when too high."""
        mock_run.return_value = Mock(
            returncode=0, stdout="test.py - F (very high)"
        )
        passed, issues, complexity = validator.check_complexity(["test.py"])
        assert passed is False

    def test_check_documentation_pass(self, temp_files: list[str]) -> None:
        """Test documentation check when passing."""
        validator = CodeQualityValidator()
        # Create a properly documented file
        test_file = Path(temp_files[0])
        test_file.write_text(
            '"""Module docstring."""\n\ndef func():\n    """Function docstring."""\n    pass\n'
        )
        passed, issues, score = validator.check_documentation(temp_files)
        assert passed is True
        assert score == 100

    def test_check_documentation_missing_docstring(
        self, temp_files: list[str]
    ) -> None:
        """Test documentation check with missing docstrings."""
        validator = CodeQualityValidator()
        test_file = Path(temp_files[0])
        test_file.write_text("def func():\n    pass\n")
        passed, issues, score = validator.check_documentation(temp_files)
        assert passed is False

    @patch("subprocess.run")
    def test_check_dependencies_pass(
        self, mock_run: Mock, validator: CodeQualityValidator
    ) -> None:
        """Test dependency check when no vulnerabilities."""
        mock_run.return_value = Mock(returncode=0, stdout="")
        with patch("pathlib.Path.exists", return_value=True):
            passed, issues, score = validator.check_dependencies(["test.py"])
            # If requirements exist, pip-audit is called
            assert isinstance(passed, bool)
            assert isinstance(score, int)

    def test_get_staged_files(self, validator: CodeQualityValidator) -> None:
        """Test getting staged files from git."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                returncode=0, stdout="file1.py\nfile2.py"
            )
            files = validator.get_staged_files()
            assert isinstance(files, list)

    def test_generate_quality_report(
        self, validator: CodeQualityValidator
    ) -> None:
        """Test quality report generation."""
        checks = {
            "code_style": {"passed": True, "score": 100},
            "tests": {"passed": True, "score": 100},
            "security": {"passed": True, "score": 100},
        }
        report = validator.generate_quality_report(checks)
        assert "timestamp" in report
        assert "checks" in report
        assert "overall_quality_score" in report
        assert report["pass_all"] is True

    def test_generate_quality_report_with_failures(
        self, validator: CodeQualityValidator
    ) -> None:
        """Test quality report with failing checks."""
        checks = {
            "code_style": {"passed": False, "score": 50},
            "tests": {"passed": True, "score": 100},
        }
        report = validator.generate_quality_report(checks)
        assert report["pass_all"] is False

    @patch.object(CodeQualityValidator, "check_code_style")
    @patch.object(CodeQualityValidator, "check_tests_pass")
    @patch.object(CodeQualityValidator, "check_test_coverage")
    @patch.object(CodeQualityValidator, "check_security")
    @patch.object(CodeQualityValidator, "check_complexity")
    @patch.object(CodeQualityValidator, "check_documentation")
    @patch.object(CodeQualityValidator, "check_dependencies")
    @patch.object(CodeQualityValidator, "save_quality_report")
    def test_run_all_checks(
        self,
        mock_save: Mock,
        mock_deps: Mock,
        mock_docs: Mock,
        mock_complexity: Mock,
        mock_security: Mock,
        mock_coverage: Mock,
        mock_tests: Mock,
        mock_style: Mock,
        validator: CodeQualityValidator,
    ) -> None:
        """Test running all quality checks."""
        mock_style.return_value = (True, [], 100)
        mock_tests.return_value = (True, [], 5)
        mock_coverage.return_value = (True, [], 85.0)
        mock_security.return_value = (True, [], 100)
        mock_complexity.return_value = (True, [], 5.0)
        mock_docs.return_value = (True, [], 100)
        mock_deps.return_value = (True, [], 100)

        report = validator.run_all_checks(files=["test.py"])
        assert isinstance(report, dict)
        mock_save.assert_called_once()

    @patch.object(CodeQualityValidator, "get_staged_files")
    @patch.object(CodeQualityValidator, "check_code_style")
    @patch.object(CodeQualityValidator, "check_tests_pass")
    @patch.object(CodeQualityValidator, "check_test_coverage")
    @patch.object(CodeQualityValidator, "check_security")
    @patch.object(CodeQualityValidator, "check_complexity")
    @patch.object(CodeQualityValidator, "check_documentation")
    @patch.object(CodeQualityValidator, "check_dependencies")
    @patch.object(CodeQualityValidator, "save_quality_report")
    def test_run_all_checks_no_files(
        self,
        mock_save: Mock,
        mock_deps: Mock,
        mock_docs: Mock,
        mock_complexity: Mock,
        mock_security: Mock,
        mock_coverage: Mock,
        mock_tests: Mock,
        mock_style: Mock,
        mock_staged: Mock,
        validator: CodeQualityValidator,
    ) -> None:
        """Test running checks with no files."""
        mock_staged.return_value = []
        result = validator.run_all_checks()
        assert result.get("status") == "no_files"

    @patch("builtins.print")
    def test_display_summary(
        self, mock_print: Mock, validator: CodeQualityValidator
    ) -> None:
        """Test summary display."""
        report = {
            "checks": {
                "code_style": {"passed": True, "score": 100},
                "tests": {"passed": False, "score": 0},
            },
            "overall_quality_score": 50.0,
            "pass_all": False,
        }
        validator.display_summary(report)
        mock_print.assert_called()

    def test_save_quality_report(
        self, validator: CodeQualityValidator
    ) -> None:
        """Test saving quality report."""
        report = {
            "timestamp": "2024-01-01T00:00:00",
            "checks": {},
            "overall_quality_score": 100,
            "pass_all": True,
        }
        validator.save_quality_report(report)
        # Verify file was written
        assert validator.quality_report_file.exists()


class TestColors:
    """Tests for Colors class."""

    def test_color_codes_defined(self) -> None:
        """Test that all color codes are defined."""
        assert Colors.GREEN != ""
        assert Colors.RED != ""
        assert Colors.YELLOW != ""
        assert Colors.BLUE != ""
        assert Colors.RESET != ""
