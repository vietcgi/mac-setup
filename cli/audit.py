"""
Enterprise audit logging system for Devkit.

Provides:
- Comprehensive action logging
- User activity tracking
- Change auditing
- Compliance reporting
- Secure log storage
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from enum import Enum
import hashlib


class AuditAction(Enum):
    """Audit action types."""

    INSTALL_STARTED = "install_started"
    INSTALL_COMPLETED = "install_completed"
    INSTALL_FAILED = "install_failed"
    CONFIG_CHANGED = "config_changed"
    PLUGIN_INSTALLED = "plugin_installed"
    PLUGIN_REMOVED = "plugin_removed"
    SYSTEM_CHECK = "system_check"
    VERIFICATION_PASSED = "verification_passed"
    VERIFICATION_FAILED = "verification_failed"
    SECURITY_CHECK = "security_check"
    PERMISSION_CHANGED = "permission_changed"
    CACHE_CLEARED = "cache_cleared"
    HEALTH_CHECK = "health_check"
    ERROR_DETECTED = "error_detected"
    WARNING_DETECTED = "warning_detected"


class AuditLogger:
    """Enterprise audit logging system."""

    def __init__(self, log_dir: Optional[Path] = None, enable_signing: bool = False):
        """
        Initialize audit logger.

        Args:
            log_dir: Directory for audit logs (default ~/.devkit/audit)
            enable_signing: Enable cryptographic signing of logs
        """
        self.log_dir = log_dir or Path.home() / ".devkit" / "audit"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.enable_signing = enable_signing
        self.logger = logging.getLogger(__name__)

        # Set up file logging
        log_file = self.log_dir / f"audit-{datetime.now().strftime('%Y%m%d')}.jsonl"
        self.log_file = log_file
        self._ensure_secure_permissions()

    def _ensure_secure_permissions(self) -> None:
        """Ensure audit log directory has secure permissions (700)."""
        try:
            self.log_dir.chmod(0o700)
            if self.log_file.exists():
                self.log_file.chmod(0o600)
        except Exception as e:
            self.logger.warning(f"Could not set audit log permissions: {e}")

    def _sign_entry(self, entry: Dict[str, Any]) -> str:
        """
        Create cryptographic signature for audit entry.

        Args:
            entry: Audit entry dictionary

        Returns:
            SHA256 hash signature of entry JSON
        """
        entry_json = json.dumps(entry, sort_keys=True, default=str)
        return hashlib.sha256(entry_json.encode()).hexdigest()

    def log_action(
        self,
        action: AuditAction,
        details: Optional[Dict[str, Any]] = None,
        user: Optional[str] = None,
        status: str = "success",
    ) -> Dict[str, Any]:
        """
        Log an action to the audit log.

        Args:
            action: Action type
            details: Additional details
            user: User performing action (default: current user)
            status: Action status (success, failure, warning)

        Returns:
            Audit log entry
        """
        import os

        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action.value,
            "status": status,
            "user": user or os.getenv("USER", "unknown"),
            "hostname": os.uname()[1],
            "details": details or {},
        }

        # Add signature if enabled
        if self.enable_signing:
            entry["signature"] = self._sign_entry(entry)

        # Write to log file
        try:
            with open(self.log_file, "a") as f:
                f.write(json.dumps(entry) + "\n")
            self._ensure_secure_permissions()
        except Exception as e:
            self.logger.error(f"Failed to write audit log: {e}")

        return entry

    def log_install_started(
        self, roles: Optional[List[str]] = None, details: Optional[Dict] = None
    ) -> Dict:
        """Log installation start."""
        return self.log_action(
            AuditAction.INSTALL_STARTED,
            details={"roles": roles or [], **(details or {})},
        )

    def log_install_completed(
        self, duration_seconds: float, details: Optional[Dict] = None
    ) -> Dict:
        """Log successful installation."""
        return self.log_action(
            AuditAction.INSTALL_COMPLETED,
            details={"duration_seconds": duration_seconds, **(details or {})},
        )

    def log_install_failed(self, error: str, details: Optional[Dict] = None) -> Dict:
        """Log failed installation."""
        return self.log_action(
            AuditAction.INSTALL_FAILED,
            details={"error": error, **(details or {})},
            status="failure",
        )

    def log_config_changed(self, key: str, old_value: Any, new_value: Any) -> Dict:
        """Log configuration change."""
        return self.log_action(
            AuditAction.CONFIG_CHANGED,
            details={
                "key": key,
                "old_value": str(old_value),
                "new_value": str(new_value),
            },
        )

    def log_plugin_installed(self, plugin_name: str, version: str) -> Dict:
        """Log plugin installation."""
        return self.log_action(
            AuditAction.PLUGIN_INSTALLED,
            details={"plugin": plugin_name, "version": version},
        )

    def log_plugin_removed(self, plugin_name: str) -> Dict:
        """Log plugin removal."""
        return self.log_action(
            AuditAction.PLUGIN_REMOVED, details={"plugin": plugin_name}
        )

    def log_security_check(
        self, check_name: str, status: str, findings: Optional[List[str]] = None
    ) -> Dict:
        """Log security check."""
        return self.log_action(
            AuditAction.SECURITY_CHECK,
            details={"check": check_name, "findings": findings or []},
            status=status,
        )

    def log_permission_changed(self, path: str, old_perms: str, new_perms: str) -> Dict:
        """Log permission change."""
        return self.log_action(
            AuditAction.PERMISSION_CHANGED,
            details={
                "path": path,
                "old_permissions": old_perms,
                "new_permissions": new_perms,
            },
        )

    def log_verification(self, passed: bool, details: Optional[Dict] = None) -> Dict:
        """Log setup verification."""
        action = (
            AuditAction.VERIFICATION_PASSED
            if passed
            else AuditAction.VERIFICATION_FAILED
        )
        return self.log_action(
            action, details=details, status="success" if passed else "failure"
        )

    def log_health_check(self, status: str, details: Optional[Dict] = None) -> Dict:
        """Log health check result."""
        return self.log_action(AuditAction.HEALTH_CHECK, details=details, status=status)

    def get_log_file_path(self) -> Path:
        """Get current audit log file path."""
        return self.log_file

    def get_audit_logs(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get audit log entries.

        Args:
            limit: Maximum number of entries (default all)

        Returns:
            List of audit log entries
        """
        entries = []

        try:
            with open(self.log_file, "r") as f:
                for line in f:
                    if line.strip():
                        entries.append(json.loads(line))
        except Exception as e:
            self.logger.warning(f"Failed to read audit logs: {e}")

        if limit:
            entries = entries[-limit:]

        return entries

    def get_audit_summary(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get summary of audit log for given time period.

        Args:
            hours: Look back hours (default 24)

        Returns:
            Summary statistics
        """
        from datetime import timedelta

        cutoff = datetime.now() - timedelta(hours=hours)
        entries = self.get_audit_logs()

        summary = {
            "total_actions": 0,
            "actions_by_type": {},
            "actions_by_status": {},
            "users": set(),
            "time_period_hours": hours,
        }

        for entry in entries:
            try:
                entry_time = datetime.fromisoformat(entry.get("timestamp", ""))
                if entry_time < cutoff:
                    continue

                summary["total_actions"] += 1
                action = entry.get("action", "unknown")
                status = entry.get("status", "unknown")
                user = entry.get("user", "unknown")

                summary["actions_by_type"][action] = (
                    summary["actions_by_type"].get(action, 0) + 1
                )
                summary["actions_by_status"][status] = (
                    summary["actions_by_status"].get(status, 0) + 1
                )
                summary["users"].add(user)
            except Exception as e:
                self.logger.debug(f"Error parsing audit entry: {e}")

        summary["users"] = list(summary["users"])
        return summary

    def rotate_logs(self) -> None:
        """Rotate audit logs by archiving old ones."""
        try:
            import shutil
            from datetime import datetime, timedelta

            cutoff_date = (datetime.now() - timedelta(days=90)).strftime("%Y%m%d")
            archive_dir = self.log_dir / "archive"
            archive_dir.mkdir(exist_ok=True)

            for log_file in self.log_dir.glob("audit-*.jsonl"):
                # Extract date from filename
                date_str = log_file.name.replace("audit-", "").replace(".jsonl", "")
                if date_str < cutoff_date:
                    archive_path = archive_dir / log_file.name
                    shutil.move(str(log_file), str(archive_path))
                    self.logger.info(f"Archived audit log: {log_file.name}")
        except Exception as e:
            self.logger.warning(f"Failed to rotate audit logs: {e}")


class ComplianceReport:
    """Generate compliance reports from audit logs."""

    def __init__(self, audit_logger: AuditLogger):
        """
        Initialize compliance report generator.

        Args:
            audit_logger: AuditLogger instance
        """
        self.audit_logger = audit_logger

    def generate_activity_report(self, days: int = 30) -> str:
        """
        Generate user activity report.

        Args:
            days: Report period in days

        Returns:
            Formatted report string
        """
        summary = self.audit_logger.get_audit_summary(hours=days * 24)

        report = f"""
ACTIVITY REPORT - Last {days} Days
{'=' * 60}

Total Actions: {summary['total_actions']}
Active Users: {len(summary['users'])} ({', '.join(summary['users'])})

Actions by Type:
"""
        for action, count in sorted(
            summary["actions_by_type"].items(), key=lambda x: x[1], reverse=True
        ):
            report += f"  {action}: {count}\n"

        report += "\nActions by Status:\n"
        for status, count in sorted(
            summary["actions_by_status"].items(), key=lambda x: x[1], reverse=True
        ):
            report += f"  {status}: {count}\n"

        return report

    def generate_security_report(self) -> str:
        """Generate security events report."""
        entries = self.audit_logger.get_audit_logs()

        security_events = [
            e
            for e in entries
            if e.get("action")
            in [
                AuditAction.SECURITY_CHECK.value,
                AuditAction.PERMISSION_CHANGED.value,
                AuditAction.VERIFICATION_FAILED.value,
            ]
        ]

        report = f"""
SECURITY REPORT
{'=' * 60}

Security Events: {len(security_events)}

Recent Events:
"""
        for event in security_events[-10:]:
            timestamp = event.get("timestamp", "unknown")
            action = event.get("action", "unknown")
            status = event.get("status", "unknown")
            report += f"  {timestamp} | {action} | {status}\n"

        return report
