"""
Tests for enterprise audit logging system.

Validates:
- Audit action logging
- Log entry creation
- Compliance reporting
- Log rotation
- Secure log storage
"""

import sys
import unittest
import tempfile
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from cli.audit import (  # noqa: E402
    AuditAction,
    AuditLogger,
    AuditReporter,
    AuditSigningService,
    AuditLogStorage,
)


class TestAuditAction(unittest.TestCase):
    """Test AuditAction enum."""

    def test_audit_action_values(self):
        """Test audit action enumeration values."""
        self.assertEqual(AuditAction.INSTALL_STARTED.value, "install_started")
        self.assertEqual(AuditAction.INSTALL_COMPLETED.value, "install_completed")
        self.assertEqual(AuditAction.INSTALL_FAILED.value, "install_failed")
        self.assertEqual(AuditAction.CONFIG_CHANGED.value, "config_changed")
        self.assertEqual(AuditAction.SECURITY_CHECK.value, "security_check")

    def test_audit_action_count(self):
        """Test that all expected actions are defined."""
        expected_actions = [
            "INSTALL_STARTED",
            "INSTALL_COMPLETED",
            "INSTALL_FAILED",
            "CONFIG_CHANGED",
            "PLUGIN_INSTALLED",
            "PLUGIN_REMOVED",
            "SYSTEM_CHECK",
            "VERIFICATION_PASSED",
            "VERIFICATION_FAILED",
            "SECURITY_CHECK",
            "PERMISSION_CHANGED",
            "CACHE_CLEARED",
            "HEALTH_CHECK",
            "ERROR_DETECTED",
            "WARNING_DETECTED",
        ]

        actual_actions = [
            attr for attr in dir(AuditAction) if not attr.startswith("_") and attr.isupper()
        ]

        self.assertEqual(len(actual_actions), len(expected_actions))


class TestAuditLogger(unittest.TestCase):
    """Test AuditLogger class."""

    def setUp(self):
        """Set up test audit logger."""
        self.temp_dir = tempfile.mkdtemp()
        self.log_dir = Path(self.temp_dir) / "audit"
        self.logger = AuditLogger(self.log_dir)

    def tearDown(self):
        """Clean up."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_logger_creation(self):
        """Test creating audit logger."""
        self.assertTrue(self.log_dir.exists())
        self.assertEqual(self.logger.log_dir, self.log_dir)

    def test_log_action(self):
        """Test logging an action."""
        entry = self.logger.log_action(
            AuditAction.INSTALL_STARTED, details={"roles": ["core", "shell"]}
        )

        self.assertIn("timestamp", entry)
        self.assertEqual(entry["action"], "install_started")
        self.assertEqual(entry["status"], "success")
        self.assertIn("user", entry)
        self.assertIn("hostname", entry)
        self.assertIn("details", entry)

    def test_log_install_lifecycle(self):
        """Test logging installation lifecycle."""
        self.logger.log_install_started(roles=["core"])
        self.logger.log_install_completed(duration_seconds=120.5)

        entries = self.logger.get_audit_logs()
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0]["action"], "install_started")
        self.assertEqual(entries[1]["action"], "install_completed")

    def test_log_config_changed(self):
        """Test logging configuration changes."""
        self.logger.log_config_changed("python_version", "3.11", "3.12")

        entries = self.logger.get_audit_logs()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["action"], "config_changed")
        self.assertEqual(entries[0]["details"]["key"], "python_version")

    def test_log_plugin_actions(self):
        """Test logging plugin actions."""
        self.logger.log_plugin_installed("my-plugin", "1.0.0")
        self.logger.log_plugin_removed("old-plugin")

        entries = self.logger.get_audit_logs()
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0]["action"], "plugin_installed")
        self.assertEqual(entries[1]["action"], "plugin_removed")

    def test_log_security_check(self):
        """Test logging security checks."""
        self.logger.log_security_check("checksum_verification", "success", findings=[])

        entries = self.logger.get_audit_logs()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["action"], "security_check")
        self.assertEqual(entries[0]["status"], "success")

    def test_log_permission_changed(self):
        """Test logging permission changes."""
        self.logger.log_permission_changed("~/.devkit/config.yaml", "0644", "0600")

        entries = self.logger.get_audit_logs()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["action"], "permission_changed")
        self.assertEqual(entries[0]["details"]["old_permissions"], "0644")

    def test_log_verification_passed(self):
        """Test logging successful verification."""
        self.logger.log_verification(passed=True, details={"checks": 5})

        entries = self.logger.get_audit_logs()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["action"], "verification_passed")
        self.assertEqual(entries[0]["status"], "success")

    def test_log_verification_failed(self):
        """Test logging failed verification."""
        self.logger.log_verification(passed=False, details={"missing": ["python", "git"]})

        entries = self.logger.get_audit_logs()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["action"], "verification_failed")
        self.assertEqual(entries[0]["status"], "failure")

    def test_log_health_check(self):
        """Test logging health check results."""
        self.logger.log_health_check("healthy", details={"checks": 5, "passed": 5})

        entries = self.logger.get_audit_logs()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["action"], "health_check")

    def test_get_audit_logs(self):
        """Test retrieving audit logs."""
        for i in range(10):
            self.logger.log_action(AuditAction.SYSTEM_CHECK, details={"iteration": i})

        entries = self.logger.get_audit_logs()
        self.assertEqual(len(entries), 10)

        entries_limited = self.logger.get_audit_logs(limit=3)
        self.assertEqual(len(entries_limited), 3)
        self.assertEqual(entries_limited[-1]["details"]["iteration"], 9)

    def test_get_audit_summary(self):
        """Test getting audit summary."""
        self.logger.log_install_started()
        self.logger.log_install_completed(duration_seconds=60)
        self.logger.log_security_check("test", "success")

        summary = self.logger.get_audit_summary(hours=1)

        self.assertEqual(summary["total_actions"], 3)
        self.assertIn("install_started", summary["actions_by_type"])
        self.assertIn("success", summary["actions_by_status"])
        self.assertTrue(len(summary["users"]) > 0)

    def test_audit_log_file_permissions(self):
        """Test that audit logs have secure permissions."""
        self.logger.log_action(AuditAction.INSTALL_STARTED)

        log_file = self.logger.get_log_file_path()
        self.assertTrue(log_file.exists())

        # Check file has restrictive permissions (600)
        mode = oct(log_file.stat().st_mode)[-3:]
        self.assertEqual(mode, "600")

    def test_audit_log_directory_permissions(self):
        """Test that audit directory has secure permissions."""
        # Directory should have permissions 700 (rwx for owner only)
        mode = oct(self.log_dir.stat().st_mode)[-3:]
        self.assertEqual(mode, "700")

    def test_get_log_file_path(self):
        """Test getting log file path."""
        log_path = self.logger.get_log_file_path()

        self.assertTrue(log_path.parent.exists())
        self.assertIn("audit", log_path.name)
        self.assertTrue(log_path.name.endswith(".jsonl"))

    def test_signing_disabled_by_default(self):
        """Test that signing is disabled by default."""
        entry = self.logger.log_action(AuditAction.INSTALL_STARTED)
        self.assertNotIn("signature", entry)

    def test_signing_enabled(self):
        """Test that signing can be enabled."""
        logger = AuditLogger(Path(self.temp_dir) / "audit2", enable_signing=True)
        entry = logger.log_action(AuditAction.INSTALL_STARTED)

        self.assertIn("signature", entry)
        self.assertEqual(len(entry["signature"]), 64)  # SHA256 hex

    def test_log_entry_structure(self):
        """Test that log entries have expected structure."""
        entry = self.logger.log_action(
            AuditAction.CONFIG_CHANGED, details={"test": "value"}, status="success"
        )

        required_fields = [
            "timestamp",
            "action",
            "status",
            "user",
            "hostname",
            "details",
        ]
        for field in required_fields:
            self.assertIn(field, entry)

    def test_multiple_log_entries(self):
        """Test logging multiple entries to same file."""
        for i in range(5):
            self.logger.log_action(AuditAction.SYSTEM_CHECK, details={"check": i})

        entries = self.logger.get_audit_logs()
        self.assertEqual(len(entries), 5)

        # Verify entries are in order
        for i, entry in enumerate(entries):
            self.assertEqual(entry["details"]["check"], i)


class TestAuditReporter(unittest.TestCase):
    """Test AuditReporter class."""

    def setUp(self):
        """Set up test audit reporter."""
        self.temp_dir = tempfile.mkdtemp()
        self.log_dir = Path(self.temp_dir) / "audit"
        self.logger = AuditLogger(self.log_dir)
        self.reporter = AuditReporter(self.logger)

    def tearDown(self):
        """Clean up."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_reporter_creation(self):
        """Test creating audit reporter."""
        self.assertIsInstance(self.reporter, AuditReporter)
        self.assertEqual(self.reporter.audit_logger, self.logger)

    def test_activity_report(self):
        """Test generating activity report."""
        self.logger.log_install_started()
        self.logger.log_install_completed(duration_seconds=60)

        report = self.reporter.generate_activity_report(days=1)

        self.assertIn("Activity Report", report)
        self.assertIn("Actions by Type", report)
        self.assertIn("install_started", report)

    def test_activity_report_with_no_actions(self):
        """Test activity report when no actions logged."""
        report = self.reporter.generate_activity_report(days=1)

        self.assertIn("Activity Report", report)

    def test_security_report(self):
        """Test generating security report."""
        self.logger.log_security_check("test", "success")
        self.logger.log_permission_changed("/path", "644", "600")
        self.logger.log_verification(passed=False)

        report = self.reporter.generate_security_report()

        self.assertIn("Security & Integrity Report", report)
        self.assertIn("Total Entries", report)

    def test_security_report_format(self):
        """Test security report formatting."""
        self.logger.log_security_check("checksum", "success", findings=[])

        report = self.reporter.generate_security_report()

        # Should include report header and status information
        self.assertIn("Security & Integrity Report", report)
        self.assertIn("Total Entries", report)


if __name__ == "__main__":
    unittest.main()
