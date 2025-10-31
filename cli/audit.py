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
import hmac
import os


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

    def __init__(self, log_dir: Optional[Path] = None, enable_signing: bool = False, hmac_key: Optional[bytes] = None):
        """
        Initialize audit logger.

        Args:
            log_dir: Directory for audit logs (default ~/.devkit/audit)
            enable_signing: Enable cryptographic signing of logs using HMAC
            hmac_key: HMAC secret key (auto-generated if enable_signing=True and not provided)
        """
        self.log_dir = log_dir or Path.home() / ".devkit" / "audit"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.enable_signing = enable_signing
        self.logger = logging.getLogger(__name__)

        # Initialize HMAC key for signing
        self.hmac_key = hmac_key
        if enable_signing and not hmac_key:
            self.hmac_key = self._load_or_create_hmac_key()

        # Set up file logging
        log_file = self.log_dir / f"audit-{datetime.now().strftime('%Y%m%d')}.jsonl"
        self.log_file = log_file
        self._ensure_secure_permissions()

    def _load_or_create_hmac_key(self) -> bytes:
        """
        Load HMAC key from secure storage or create a new one.

        SECURITY: HMAC key is stored in ~/.devkit/.hmac_key with 0600 permissions.
        This key is used for cryptographic signing of audit logs.

        Returns:
            HMAC secret key (32 bytes)
        """
        key_file = self.log_dir / ".hmac_key"

        # Try to load existing key
        if key_file.exists():
            try:
                with open(key_file, "rb") as f:
                    key = f.read()
                    if len(key) == 32:  # Validate key length
                        return key
            except Exception as e:
                self.logger.warning(f"Failed to load HMAC key, generating new one: {e}")

        # Generate new HMAC key (256 bits = 32 bytes)
        key = os.urandom(32)

        # Store key securely
        try:
            key_file.parent.mkdir(parents=True, exist_ok=True)
            with open(key_file, "wb") as f:
                f.write(key)
            key_file.chmod(0o600)  # Owner read/write only
            self.logger.info("Generated new HMAC key for audit log signing")
        except Exception as e:
            self.logger.error(f"Failed to store HMAC key: {e}")

        return key

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
        Create HMAC-SHA256 cryptographic signature for audit entry.

        SECURITY: Uses HMAC with a secret key (not just SHA256 hash).
        This prevents tampering: attackers cannot forge signatures without the key.

        Args:
            entry: Audit entry dictionary

        Returns:
            HMAC-SHA256 signature in hexadecimal format
        """
        if not self.hmac_key:
            raise RuntimeError("HMAC signing enabled but no key available")

        entry_json = json.dumps(entry, sort_keys=True, default=str)
        signature = hmac.new(
            self.hmac_key,
            entry_json.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature

    def verify_signature(self, entry: Dict[str, Any]) -> bool:
        """
        Verify HMAC-SHA256 signature of an audit log entry.

        SECURITY: Detects tampering by verifying entry hasn't been modified.

        Args:
            entry: Audit log entry with signature field

        Returns:
            True if signature is valid, False otherwise
        """
        if "signature" not in entry:
            return False

        if not self.hmac_key:
            self.logger.warning("Cannot verify signature: HMAC key not available")
            return False

        stored_signature = entry["signature"]
        # Create a copy without the signature for verification
        entry_copy = {k: v for k, v in entry.items() if k != "signature"}

        try:
            computed_signature = self._sign_entry(entry_copy)
            return hmac.compare_digest(computed_signature, stored_signature)
        except Exception as e:
            self.logger.error(f"Error verifying signature: {e}")
            return False

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
        return self.log_action(AuditAction.PLUGIN_REMOVED, details={"plugin": plugin_name})

    def log_security_check(
        self, check_name: str, status: str, findings: Optional[List[str]] = None
    ) -> Dict:
        """Log security check."""
        return self.log_action(
            AuditAction.SECURITY_CHECK,
            details={"check": check_name, "findings": findings or []},
            status=status,
        )

    def log_permission_changed(self, path: str, old_perms: str, new_perms: str) -> Dict[str, Any]:
        """Log permission change."""
        return self.log_action(
            AuditAction.PERMISSION_CHANGED,
            details={
                "path": path,
                "old_permissions": old_perms,
                "new_permissions": new_perms,
            },
        )

    def log_verification(self, passed: bool, details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Log setup verification."""
        action = AuditAction.VERIFICATION_PASSED if passed else AuditAction.VERIFICATION_FAILED
        return self.log_action(action, details=details, status="success" if passed else "failure")

    def log_health_check(self, status: str, details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Log health check result."""
        return self.log_action(AuditAction.HEALTH_CHECK, details=details, status=status)

    def get_log_file_path(self) -> Path:
        """Get current audit log file path."""
        return self.log_file

    def get_audit_logs(self, limit: Optional[int] = None, verify_signatures: bool = False) -> List[Dict[str, Any]]:
        """
        Get audit log entries.

        Args:
            limit: Maximum number of entries (default all)
            verify_signatures: If True, only return entries with valid signatures

        Returns:
            List of audit log entries
        """
        entries = []

        try:
            with open(self.log_file, "r") as f:
                for line in f:
                    if line.strip():
                        entry = json.loads(line)

                        # Skip if signature verification requested and entry has invalid signature
                        if verify_signatures and entry.get("signature"):
                            if not self.verify_signature(entry):
                                self.logger.warning(f"Audit entry has invalid signature: {entry.get('timestamp')}")
                                continue

                        entries.append(entry)
        except Exception as e:
            self.logger.warning(f"Failed to read audit logs: {e}")

        if limit:
            entries = entries[-limit:]

        return entries

    def validate_log_integrity(self) -> Dict[str, Any]:
        """
        Validate integrity of all audit log entries.

        SECURITY: Checks that all entries have valid HMAC signatures.
        Returns report of any tampering detected.

        Returns:
            Dictionary with validation results:
            {
                "total_entries": int,
                "valid_entries": int,
                "invalid_entries": int,
                "unsigned_entries": int,
                "tampering_detected": bool,
                "invalid_entry_timestamps": List[str]
            }
        """
        entries = []
        try:
            with open(self.log_file, "r") as f:
                for line in f:
                    if line.strip():
                        entries.append(json.loads(line))
        except Exception as e:
            self.logger.error(f"Failed to read audit logs for validation: {e}")
            return {
                "total_entries": 0,
                "valid_entries": 0,
                "invalid_entries": 0,
                "unsigned_entries": 0,
                "tampering_detected": False,
                "invalid_entry_timestamps": [],
                "error": str(e)
            }

        valid_count = 0
        invalid_count = 0
        unsigned_count = 0
        invalid_timestamps = []

        for entry in entries:
            if "signature" not in entry:
                unsigned_count += 1
            elif self.verify_signature(entry):
                valid_count += 1
            else:
                invalid_count += 1
                invalid_timestamps.append(entry.get("timestamp", "unknown"))
                self.logger.error(f"Tampering detected in audit entry: {entry.get('timestamp')}")

        return {
            "total_entries": len(entries),
            "valid_entries": valid_count,
            "invalid_entries": invalid_count,
            "unsigned_entries": unsigned_count,
            "tampering_detected": invalid_count > 0,
            "invalid_entry_timestamps": invalid_timestamps
        }

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

        summary: dict[str, int | dict[str, int] | set[str] | list[str]] = {
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

                total_actions = summary["total_actions"]
                if isinstance(total_actions, int):
                    summary["total_actions"] = total_actions + 1
                action = entry.get("action", "unknown")
                status = entry.get("status", "unknown")
                user = entry.get("user", "unknown")

                actions_by_type = summary["actions_by_type"]
                if isinstance(actions_by_type, dict):
                    actions_by_type[action] = actions_by_type.get(action, 0) + 1

                actions_by_status = summary["actions_by_status"]
                if isinstance(actions_by_status, dict):
                    actions_by_status[status] = actions_by_status.get(status, 0) + 1

                users = summary["users"]
                if isinstance(users, set):
                    users.add(user)
            except Exception as e:
                self.logger.debug(f"Error parsing audit entry: {e}")

        users_set = summary["users"]
        if isinstance(users_set, set):
            summary["users"] = list(users_set)
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
