"""Health checks and monitoring for Devkit installation.

Provides:
- System health status verification
- Component health checking
- Log monitoring and parsing
- Health metrics collection
- Detailed health reporting
"""

import json
import logging
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


class HealthStatus:
    """Health status enumeration."""

    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"

    ALL_STATUSES = [HEALTHY, WARNING, CRITICAL, UNKNOWN]


class HealthCheck:
    """Base class for all health checks."""

    def __init__(self, name: str, description: str = "") -> None:
        """Initialize health check.

        Args:
            name: Check name
            description: Check description
        """
        self.name = name
        self.description = description
        self.logger = logging.getLogger(__name__)

    def run(self) -> tuple[str, str, dict[str, Any]]:
        """Run the health check.

        Returns:
            Tuple of (status, message, details)
            - status: one of HealthStatus values
            - message: human-readable message
            - details: additional details dict
        """
        raise NotImplementedError


class DependencyCheck(HealthCheck):
    """Check if required dependencies are installed."""

    def __init__(self, tools: list[str]) -> None:
        """Initialize dependency check.

        Args:
            tools: List of tools to check for
        """
        super().__init__("Dependencies", "Check required tools are installed")
        self.tools = tools

    def run(self) -> tuple[str, str, dict]:
        """Check if all dependencies are available."""
        missing = []
        installed = []

        for tool in self.tools:
            try:
                result = subprocess.run(
                    ["which", tool],
                    capture_output=True,
                    timeout=2,
                    check=False,
                )
                if result.returncode == 0:
                    installed.append(tool)
                else:
                    missing.append(tool)
            except Exception as e:
                self.logger.debug(f"Failed to check {tool}: {e}")
                missing.append(tool)

        if not missing:
            return (
                HealthStatus.HEALTHY,
                f"All {len(installed)} dependencies installed",
                {"installed": installed, "missing": []},
            )
        if len(missing) <= len(installed):
            return (
                HealthStatus.WARNING,
                f"{len(missing)} of {len(self.tools)} dependencies missing",
                {"installed": installed, "missing": missing},
            )
        return (
            HealthStatus.CRITICAL,
            f"Most dependencies missing ({len(missing)}/{len(self.tools)})",
            {"installed": installed, "missing": missing},
        )


class DiskSpaceCheck(HealthCheck):
    """Check available disk space."""

    def __init__(self, min_gb: int = 5) -> None:
        """Initialize disk space check.

        Args:
            min_gb: Minimum required GB (default 5)
        """
        super().__init__("Disk Space", f"Check {min_gb}GB free space available")
        self.min_gb = min_gb

    def run(self) -> tuple[str, str, dict]:
        """Check available disk space."""
        try:
            result = subprocess.run(
                ["df", "-B1G", "/"],
                capture_output=True,
                timeout=2,
                text=True,
                check=True,
            )

            lines = result.stdout.strip().split("\n")
            if len(lines) < 2:
                return (HealthStatus.UNKNOWN, "Could not parse disk space", {})

            # Parse df output
            parts = lines[1].split()
            available_gb = int(parts[3].rstrip("G"))

            if available_gb >= self.min_gb:
                return (
                    HealthStatus.HEALTHY,
                    f"{available_gb}GB free space available",
                    {"available_gb": available_gb, "minimum_gb": self.min_gb},
                )
            return (
                HealthStatus.CRITICAL,
                f"Only {available_gb}GB free (need {self.min_gb}GB)",
                {"available_gb": available_gb, "minimum_gb": self.min_gb},
            )
        except Exception as e:
            return (
                HealthStatus.UNKNOWN,
                f"Failed to check disk space: {e}",
                {"error": str(e)},
            )


class ConfigurationCheck(HealthCheck):
    """Check configuration file health."""

    def __init__(self, config_path: Optional[Path] = None) -> None:
        """Initialize configuration check.

        Args:
            config_path: Path to config file (default ~/.devkit/config.yaml)
        """
        super().__init__("Configuration", "Check configuration file integrity")
        self.config_path = config_path or Path.home() / ".devkit" / "config.yaml"

    def run(self) -> tuple[str, str, dict]:
        """Check configuration file."""
        if not self.config_path.exists():
            return (
                HealthStatus.WARNING,
                f"Configuration file not found: {self.config_path}",
                {"path": str(self.config_path), "exists": False},
            )

        try:
            # Check file permissions
            mode = self.config_path.stat().st_mode
            perms = oct(mode)[-3:]

            if perms != "600":
                return (
                    HealthStatus.WARNING,
                    f"Config has insecure permissions: {perms} (should be 600)",
                    {"path": str(self.config_path), "permissions": perms},
                )

            # Try to parse YAML
            with open(self.config_path, encoding="utf-8") as f:
                content = f.read()
                if "global:" not in content:
                    return (
                        HealthStatus.WARNING,
                        "Configuration missing 'global' section",
                        {"path": str(self.config_path)},
                    )

            return (
                HealthStatus.HEALTHY,
                f"Configuration healthy: {self.config_path}",
                {
                    "path": str(self.config_path),
                    "permissions": perms,
                    "size": self.config_path.stat().st_size,
                },
            )

        except Exception as e:
            return (
                HealthStatus.WARNING,
                f"Failed to check configuration: {e}",
                {"path": str(self.config_path), "error": str(e)},
            )


class LogCheck(HealthCheck):
    """Check system logs for errors."""

    def __init__(self, log_file: Optional[Path] = None, look_back_hours: int = 24) -> None:
        """Initialize log check.

        Args:
            log_file: Path to log file (default ~/.devkit/logs/setup.log)
            look_back_hours: How many hours back to check (default 24)
        """
        super().__init__("Logs", f"Check logs for errors (last {look_back_hours}h)")
        self.log_file = log_file or Path.home() / ".devkit" / "logs" / "setup.log"
        self.look_back_hours = look_back_hours

    def run(self) -> tuple[str, str, dict]:
        """Check log file for errors."""
        if not self.log_file.exists():
            return (
                HealthStatus.UNKNOWN,
                f"Log file not found: {self.log_file}",
                {"path": str(self.log_file), "exists": False},
            )

        try:
            with open(self.log_file, encoding="utf-8") as f:
                lines = f.readlines()

            errors = []
            warnings = []

            for line in lines:
                if "ERROR" in line.upper():
                    errors.append(line.strip())
                elif "WARNING" in line.upper():
                    warnings.append(line.strip())

            # Keep only recent entries
            errors = errors[-10:]  # Last 10 errors
            warnings = warnings[-10:]  # Last 10 warnings

            if not errors and not warnings:
                return (
                    HealthStatus.HEALTHY,
                    "No errors in logs",
                    {"path": str(self.log_file), "lines": len(lines)},
                )
            if errors:
                return (
                    HealthStatus.CRITICAL,
                    f"Found {len(errors)} errors in logs",
                    {
                        "path": str(self.log_file),
                        "error_count": len(errors),
                        "recent_errors": errors[:3],
                    },
                )
            return (
                HealthStatus.WARNING,
                f"Found {len(warnings)} warnings in logs",
                {
                    "path": str(self.log_file),
                    "warning_count": len(warnings),
                    "recent_warnings": warnings[:3],
                },
            )

        except Exception as e:
            return (
                HealthStatus.UNKNOWN,
                f"Failed to check logs: {e}",
                {"path": str(self.log_file), "error": str(e)},
            )


class SystemCheck(HealthCheck):
    """Check overall system health."""

    def __init__(self) -> None:
        """Initialize system check."""
        super().__init__("System", "Check overall system health")

    def run(self) -> tuple[str, str, dict]:
        """Check system health."""
        try:
            # Check if system is responsive
            result = subprocess.run(
                ["uname", "-a"],
                capture_output=True,
                timeout=2,
                text=True,
                check=True,
            )

            uname = result.stdout.strip()

            # Check load average
            import os

            load_avg = os.getloadavg()

            # Simple heuristic: if load is too high, flag it
            cpu_count = os.cpu_count() or 1
            load_ratio = load_avg[0] / cpu_count

            if load_ratio > 2.0:
                status = HealthStatus.WARNING
                message = f"High system load: {load_avg[0]:.2f} (critical: {load_ratio:.2f})"
            else:
                status = HealthStatus.HEALTHY
                message = f"System healthy: {uname[:40]}..."

            return (
                status,
                message,
                {
                    "load_average": list(load_avg),
                    "cpu_count": cpu_count,
                    "load_ratio": round(load_ratio, 2),
                },
            )

        except Exception as e:
            return (
                HealthStatus.UNKNOWN,
                f"Failed to check system: {e}",
                {"error": str(e)},
            )


class HealthMonitor:
    """Orchestrate and manage all health checks."""

    def __init__(self) -> None:
        """Initialize health monitor."""
        self.checks: list[HealthCheck] = []
        self.results: dict[str, tuple[str, str, dict]] = {}
        self.logger = logging.getLogger(__name__)

    def add_check(self, check: HealthCheck) -> None:
        """Add a health check."""
        self.checks.append(check)

    def run_all(self) -> dict[str, tuple[str, str, dict]]:
        """Run all health checks.

        Returns:
            Dict mapping check names to (status, message, details)
        """
        self.results = {}

        for check in self.checks:
            try:
                status, message, details = check.run()
                self.results[check.name] = (status, message, details)
                self.logger.debug(f"{check.name}: {status} - {message}")
            except Exception as e:
                self.logger.exception(f"Health check {check.name} failed: {e}")
                self.results[check.name] = (
                    HealthStatus.UNKNOWN,
                    f"Check failed: {e}",
                    {"error": str(e)},
                )

        return self.results

    def get_overall_status(self) -> str:
        """Get overall health status based on all checks."""
        if not self.results:
            return HealthStatus.UNKNOWN

        statuses = [status for status, _, _ in self.results.values()]

        if HealthStatus.CRITICAL in statuses:
            return HealthStatus.CRITICAL
        if HealthStatus.WARNING in statuses:
            return HealthStatus.WARNING
        if all(s == HealthStatus.HEALTHY for s in statuses):
            return HealthStatus.HEALTHY
        return HealthStatus.UNKNOWN

    def print_report(self) -> None:
        """Print health check report."""
        if not self.results:
            return

        self.get_overall_status()

        # Status emoji

        for _status, _message, details in self.results.values():
            if details:
                for value in details.values():
                    if isinstance(value, list) and len(value) > 3:
                        pass
                    else:
                        pass

    def get_json_report(self) -> str:
        """Get health check report as JSON."""
        checks_dict: dict[str, dict[str, Any]] = {}

        for check_name, (status, message, details) in self.results.items():
            checks_dict[check_name] = {
                "status": status,
                "message": message,
                "details": details,
            }

        report: dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": self.get_overall_status(),
            "checks": checks_dict,
        }

        return json.dumps(report, indent=2)


def create_default_monitor() -> HealthMonitor:
    """Create health monitor with default checks."""
    monitor = HealthMonitor()

    # Add default checks
    monitor.add_check(DependencyCheck(["bash", "git", "python3", "brew"]))
    monitor.add_check(DiskSpaceCheck(min_gb=5))
    monitor.add_check(ConfigurationCheck())
    monitor.add_check(LogCheck())
    monitor.add_check(SystemCheck())

    return monitor
