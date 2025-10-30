"""
Tests for health checks and monitoring system.

Validates:
- Health check execution
- Status reporting
- Log monitoring
- Configuration verification
- System health assessment
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from cli.health_check import (  # noqa: E402
    HealthStatus,
    DependencyCheck,
    DiskSpaceCheck,
    ConfigurationCheck,
    LogCheck,
    SystemCheck,
    HealthMonitor,
    create_default_monitor,
)


class TestHealthStatus(unittest.TestCase):
    """Test HealthStatus constants."""

    def test_health_status_constants(self):
        """Test health status values."""
        self.assertEqual(HealthStatus.HEALTHY, "healthy")
        self.assertEqual(HealthStatus.WARNING, "warning")
        self.assertEqual(HealthStatus.CRITICAL, "critical")
        self.assertEqual(HealthStatus.UNKNOWN, "unknown")

    def test_all_statuses(self):
        """Test all statuses list."""
        self.assertEqual(len(HealthStatus.ALL_STATUSES), 4)
        self.assertIn(HealthStatus.HEALTHY, HealthStatus.ALL_STATUSES)
        self.assertIn(HealthStatus.WARNING, HealthStatus.ALL_STATUSES)
        self.assertIn(HealthStatus.CRITICAL, HealthStatus.ALL_STATUSES)
        self.assertIn(HealthStatus.UNKNOWN, HealthStatus.ALL_STATUSES)


class TestDependencyCheck(unittest.TestCase):
    """Test DependencyCheck."""

    def test_dependency_check_creation(self):
        """Test creating dependency check."""
        check = DependencyCheck(["bash", "git"])
        self.assertEqual(check.name, "Dependencies")
        self.assertEqual(check.tools, ["bash", "git"])

    def test_check_existing_dependencies(self):
        """Test checking for commonly available tools."""
        check = DependencyCheck(["bash", "ls", "echo"])
        status, message, details = check.run()

        # bash should exist on most systems
        self.assertIn(status, HealthStatus.ALL_STATUSES)
        self.assertIsNotNone(message)
        self.assertIn("installed", details)
        self.assertIn("missing", details)

    def test_check_nonexistent_dependencies(self):
        """Test checking for tools that probably don't exist."""
        check = DependencyCheck(["this_tool_definitely_does_not_exist_xyz"])
        status, message, details = check.run()

        self.assertEqual(status, HealthStatus.CRITICAL)
        self.assertIn("missing", details)
        self.assertEqual(len(details["missing"]), 1)

    def test_check_mixed_dependencies(self):
        """Test with mix of existing and missing tools."""
        check = DependencyCheck(["bash", "nonexistent_tool_xyz"])
        status, message, details = check.run()

        # Status should be warning since some are missing but some exist
        self.assertIn(status, [HealthStatus.WARNING, HealthStatus.CRITICAL])
        self.assertTrue(len(details["installed"]) > 0)
        self.assertTrue(len(details["missing"]) > 0)


class TestDiskSpaceCheck(unittest.TestCase):
    """Test DiskSpaceCheck."""

    def test_disk_space_check_creation(self):
        """Test creating disk space check."""
        check = DiskSpaceCheck(min_gb=5)
        self.assertEqual(check.name, "Disk Space")
        self.assertEqual(check.min_gb, 5)

    def test_disk_space_check_default(self):
        """Test disk space check with default parameters."""
        check = DiskSpaceCheck()
        self.assertEqual(check.min_gb, 5)

    def test_disk_space_check_run(self):
        """Test running disk space check."""
        check = DiskSpaceCheck(min_gb=1)
        status, message, details = check.run()

        self.assertIn(status, HealthStatus.ALL_STATUSES)
        self.assertIsNotNone(message)
        # Most systems should have at least 1GB
        self.assertIn(status, [HealthStatus.HEALTHY, HealthStatus.CRITICAL])

    def test_disk_space_high_requirement(self):
        """Test disk space check with high requirement."""
        check = DiskSpaceCheck(min_gb=1000000)
        status, message, details = check.run()

        # Should fail if asking for unrealistic amount
        self.assertNotEqual(status, HealthStatus.UNKNOWN)
        self.assertIn("available_gb", details)


class TestConfigurationCheck(unittest.TestCase):
    """Test ConfigurationCheck."""

    def setUp(self):
        """Set up temporary config file."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "config.yaml"

    def tearDown(self):
        """Clean up."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_config_check_creation(self):
        """Test creating configuration check."""
        check = ConfigurationCheck(self.config_path)
        self.assertEqual(check.name, "Configuration")
        self.assertEqual(check.config_path, self.config_path)

    def test_config_missing(self):
        """Test check when config doesn't exist."""
        check = ConfigurationCheck(self.config_path)
        status, message, details = check.run()

        self.assertEqual(status, HealthStatus.WARNING)
        self.assertFalse(details["exists"])

    def test_config_with_insecure_permissions(self):
        """Test check with insecure permissions."""
        # Create config with insecure permissions
        with open(self.config_path, "w") as f:
            f.write("global:\n  name: test\n")

        self.config_path.chmod(0o644)

        check = ConfigurationCheck(self.config_path)
        status, message, details = check.run()

        self.assertEqual(status, HealthStatus.WARNING)
        self.assertIn("permission", message.lower())

    def test_config_healthy(self):
        """Test check with healthy config."""
        # Create config with secure permissions
        with open(self.config_path, "w") as f:
            f.write("global:\n  name: test\n")

        self.config_path.chmod(0o600)

        check = ConfigurationCheck(self.config_path)
        status, message, details = check.run()

        self.assertEqual(status, HealthStatus.HEALTHY)
        self.assertEqual(details["permissions"], "600")


class TestLogCheck(unittest.TestCase):
    """Test LogCheck."""

    def setUp(self):
        """Set up temporary log file."""
        self.temp_dir = tempfile.mkdtemp()
        self.log_path = Path(self.temp_dir) / "setup.log"

    def tearDown(self):
        """Clean up."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_log_check_creation(self):
        """Test creating log check."""
        check = LogCheck(self.log_path)
        self.assertEqual(check.name, "Logs")
        self.assertEqual(check.log_file, self.log_path)

    def test_log_missing(self):
        """Test check when log doesn't exist."""
        check = LogCheck(self.log_path)
        status, message, details = check.run()

        self.assertEqual(status, HealthStatus.UNKNOWN)
        self.assertFalse(details["exists"])

    def test_log_healthy(self):
        """Test check with healthy log."""
        with open(self.log_path, "w") as f:
            f.write("INFO: Setup started\n")
            f.write("INFO: Installation complete\n")

        check = LogCheck(self.log_path)
        status, message, details = check.run()

        self.assertEqual(status, HealthStatus.HEALTHY)
        self.assertIn("lines", details)

    def test_log_with_warnings(self):
        """Test check with warnings in log."""
        with open(self.log_path, "w") as f:
            f.write("INFO: Setup started\n")
            f.write("WARNING: Package already installed\n")

        check = LogCheck(self.log_path)
        status, message, details = check.run()

        self.assertEqual(status, HealthStatus.WARNING)
        self.assertIn("warning", message.lower())

    def test_log_with_errors(self):
        """Test check with errors in log."""
        with open(self.log_path, "w") as f:
            f.write("INFO: Setup started\n")
            f.write("ERROR: Installation failed\n")
            f.write("ERROR: Rollback initiated\n")

        check = LogCheck(self.log_path)
        status, message, details = check.run()

        self.assertEqual(status, HealthStatus.CRITICAL)
        self.assertIn("error", message.lower())


class TestSystemCheck(unittest.TestCase):
    """Test SystemCheck."""

    def test_system_check_creation(self):
        """Test creating system check."""
        check = SystemCheck()
        self.assertEqual(check.name, "System")

    def test_system_check_run(self):
        """Test running system check."""
        check = SystemCheck()
        status, message, details = check.run()

        self.assertIn(status, HealthStatus.ALL_STATUSES)
        self.assertIsNotNone(message)
        self.assertIn("load_average", details)
        self.assertIn("cpu_count", details)


class TestHealthMonitor(unittest.TestCase):
    """Test HealthMonitor."""

    def setUp(self):
        """Set up test monitor."""
        self.monitor = HealthMonitor()

    def test_monitor_creation(self):
        """Test creating health monitor."""
        self.assertEqual(len(self.monitor.checks), 0)
        self.assertEqual(len(self.monitor.results), 0)

    def test_add_check(self):
        """Test adding health checks."""
        check1 = DependencyCheck(["bash"])
        check2 = SystemCheck()

        self.monitor.add_check(check1)
        self.monitor.add_check(check2)

        self.assertEqual(len(self.monitor.checks), 2)

    def test_run_all_checks(self):
        """Test running all checks."""
        self.monitor.add_check(DependencyCheck(["bash"]))
        self.monitor.add_check(SystemCheck())

        results = self.monitor.run_all()

        self.assertEqual(len(results), 2)
        self.assertIn("Dependencies", results)
        self.assertIn("System", results)

        for status, message, details in results.values():
            self.assertIn(status, HealthStatus.ALL_STATUSES)
            self.assertIsNotNone(message)
            self.assertIsInstance(details, dict)

    def test_overall_status_all_healthy(self):
        """Test overall status when all checks are healthy."""
        # Create checks that will be healthy
        check = SystemCheck()
        self.monitor.add_check(check)
        self.monitor.run_all()

        overall = self.monitor.get_overall_status()
        self.assertIn(overall, HealthStatus.ALL_STATUSES)

    def test_overall_status_with_critical(self):
        """Test overall status with critical failure."""
        self.monitor.add_check(DependencyCheck(["nonexistent_xyz"]))
        self.monitor.run_all()

        overall = self.monitor.get_overall_status()
        self.assertEqual(overall, HealthStatus.CRITICAL)

    def test_json_report(self):
        """Test JSON report generation."""
        self.monitor.add_check(SystemCheck())
        self.monitor.run_all()

        json_report = self.monitor.get_json_report()
        report = json.loads(json_report)

        self.assertIn("timestamp", report)
        self.assertIn("overall_status", report)
        self.assertIn("checks", report)
        self.assertTrue(len(report["checks"]) > 0)


class TestCreateDefaultMonitor(unittest.TestCase):
    """Test default monitor factory."""

    def test_create_default_monitor(self):
        """Test creating default monitor."""
        monitor = create_default_monitor()

        self.assertIsInstance(monitor, HealthMonitor)
        self.assertEqual(len(monitor.checks), 5)

        check_names = [check.name for check in monitor.checks]
        self.assertIn("Dependencies", check_names)
        self.assertIn("Disk Space", check_names)
        self.assertIn("Configuration", check_names)
        self.assertIn("Logs", check_names)
        self.assertIn("System", check_names)

    def test_default_monitor_runs(self):
        """Test running default monitor."""
        monitor = create_default_monitor()
        results = monitor.run_all()

        self.assertEqual(len(results), 5)

        overall = monitor.get_overall_status()
        self.assertIn(overall, HealthStatus.ALL_STATUSES)


if __name__ == "__main__":
    unittest.main()
