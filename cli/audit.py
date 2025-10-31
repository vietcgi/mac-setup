#  Copyright (c) 2024 Devkit Contributors
#  SPDX-License-Identifier: MIT
"""Enterprise audit logging system for Devkit.

Provides:
- Comprehensive action logging
- User activity tracking
- Change auditing
- Compliance reporting
- Secure log storage

Architecture (Refactored - Phase 2):
- AuditAction: Enum for audit event types
- AuditSigningService: Cryptographic signing and verification
- AuditLogStorage: File I/O and permission management
- AuditLogger: Orchestrates logging with specific action types
- AuditReporter: Generates reports and summaries
"""

import os
import hmac
import json
import shutil
import hashlib
import logging
import operator
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Optional


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


class AuditSigningService:
    """Handles cryptographic signing and verification of audit entries."""

    def __init__(self, log_dir: Path, hmac_key: Optional[bytes] = None) -> None:
        """Initialize signing service.

        Args:
            log_dir: Directory for audit logs
            hmac_key: HMAC secret key (auto-generated if not provided)
        """
        self.log_dir = log_dir
        self.hmac_key = hmac_key
        self.logger = logging.getLogger(__name__)

        if not hmac_key:
            self.hmac_key = self._load_or_create_hmac_key()

    def _load_or_create_hmac_key(self) -> bytes:
        """Load HMAC key from secure storage or create a new one.

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
            except OSError as e:
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
        except OSError as e:
            self.logger.exception(f"Failed to store HMAC key: {e}")

        return key

    def sign_entry(self, entry: dict[str, Any]) -> str:
        """Create HMAC-SHA256 cryptographic signature for audit entry.

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
        return hmac.new(
            self.hmac_key,
            entry_json.encode(),
            hashlib.sha256,
        ).hexdigest()

    def verify_signature(self, entry: dict[str, Any]) -> bool:
        """Verify HMAC-SHA256 signature of an audit log entry.

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
            computed_signature = self.sign_entry(entry_copy)
            return hmac.compare_digest(computed_signature, stored_signature)
        except (TypeError, ValueError) as e:
            self.logger.exception(f"Error verifying signature: {e}")
            return False


class AuditLogStorage:
    """Handles file I/O, permissions, and rotation of audit logs."""

    def __init__(self, log_dir: Path) -> None:
        """Initialize log storage.

        Args:
            log_dir: Directory for audit logs
        """
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = log_dir / f"audit-{datetime.now().strftime("%Y%m%d")}.jsonl"
        self.logger = logging.getLogger(__name__)
        self._ensure_secure_permissions()

    def _ensure_secure_permissions(self) -> None:
        """Ensure audit log directory has secure permissions (700)."""
        try:
            self.log_dir.chmod(0o700)
            if self.log_file.exists():
                self.log_file.chmod(0o600)
        except OSError as e:
            self.logger.warning(f"Could not set audit log permissions: {e}")

    def write_entry(self, entry: dict[str, Any]) -> None:
        """Write audit entry to log file.

        Args:
            entry: Audit entry dictionary

        Raises:
            OSError: If unable to write to log file
        """
        try:
            # Ensure log directory exists and is secure
            self.log_dir.mkdir(parents=True, exist_ok=True)

            # Write entry with atomic append
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
            self._ensure_secure_permissions()
        except json.JSONEncodeError as e:
            self.logger.exception(
                f"Failed to serialize audit entry: {e}. Entry may contain non-serializable data.",
            )
        except OSError as e:
            self.logger.exception(
                f"Failed to write audit log: {e}. Check disk space and permissions.",
            )

    def read_entries(self, limit: Optional[int] = None) -> list[dict[str, Any]]:
        """Read audit log entries from file.

        Args:
            limit: Maximum number of entries (default all)

        Returns:
            List of audit log entries
        """
        entries = []

        try:
            if not self.log_file.exists():
                return entries

            with open(self.log_file, encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    if line.strip():
                        try:
                            entry = json.loads(line)
                            entries.append(entry)
                        except json.JSONDecodeError as e:
                            self.logger.warning(
                                f"Skipping invalid JSON on line {line_num}: {e}. "
                                f"Entry may be corrupt.",
                            )
                            continue
        except (OSError, UnicodeDecodeError) as e:
            self.logger.warning(f"Failed to read audit logs: {e}")

        if limit:
            entries = entries[-limit:]

        return entries

    def get_log_file_path(self) -> Path:
        """Get current audit log file path."""
        return self.log_file

    def rotate_logs(self, days: int = 90) -> None:
        """Rotate audit logs by archiving old ones.

        Args:
            days: Archive logs older than this many days (default 90)
        """
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y%m%d")
            archive_dir = self.log_dir / "archive"
            archive_dir.mkdir(exist_ok=True)

            for log_file in self.log_dir.glob("audit-*.jsonl"):
                file_date = log_file.stem.replace("audit-", "")
                if file_date < cutoff_date:
                    archive_path = archive_dir / log_file.name
                    shutil.move(str(log_file), str(archive_path))
                    self.logger.info(f"Archived log file: {log_file.name}")
        except OSError as e:
            self.logger.exception(f"Failed to rotate logs: {e}")


class AuditLogger:
    """Enterprise audit logging system with cryptographic security."""

    def __init__(
        self,
        log_dir: Optional[Path] = None,
        enable_signing: bool = False,
        hmac_key: Optional[bytes] = None,
    ) -> None:
        """Initialize audit logger.

        Args:
            log_dir: Directory for audit logs (default ~/.devkit/audit)
            enable_signing: Enable cryptographic signing of logs using HMAC
            hmac_key: HMAC secret key (auto-generated if enable_signing=True and not provided)
        """
        self.log_dir = log_dir or Path.home() / ".devkit" / "audit"
        self.enable_signing = enable_signing
        self.logger = logging.getLogger(__name__)

        # Initialize storage and signing services
        self.storage = AuditLogStorage(self.log_dir)
        self.signing_service: Optional[AuditSigningService] = None
        if enable_signing:
            self.signing_service = AuditSigningService(self.log_dir, hmac_key)

    def log_action(
        self,
        action: AuditAction,
        details: Optional[dict[str, Any]] = None,
        user: Optional[str] = None,
        status: str = "success",
    ) -> dict[str, Any]:
        """Log an action to the audit log.

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
        if self.enable_signing and self.signing_service:
            entry["signature"] = self.signing_service.sign_entry(entry)

        # Write to log file
        self.storage.write_entry(entry)
        return entry

    def log_install_started(
        self,
        roles: Optional[list[str]] = None,
        details: Optional[dict] = None,
    ) -> dict:
        """Log installation start."""
        return self.log_action(
            AuditAction.INSTALL_STARTED,
            details={"roles": roles or [], **(details or {})},
        )

    def log_install_completed(
        self,
        duration_seconds: float,
        details: Optional[dict] = None,
    ) -> dict:
        """Log successful installation."""
        return self.log_action(
            AuditAction.INSTALL_COMPLETED,
            details={"duration_seconds": duration_seconds, **(details or {})},
        )

    def log_install_failed(self, error: str, details: Optional[dict] = None) -> dict:
        """Log failed installation."""
        return self.log_action(
            AuditAction.INSTALL_FAILED,
            details={"error": error, **(details or {})},
            status="failure",
        )

    def log_config_changed(
        self,
        key: str,
        old_value: Any,
        new_value: Any,
    ) -> dict:
        """Log configuration change."""
        return self.log_action(
            AuditAction.CONFIG_CHANGED,
            details={
                "key": key,
                "old_value": str(old_value),
                "new_value": str(new_value),
            },
        )

    def log_plugin_installed(self, plugin_name: str, version: str) -> dict:
        """Log plugin installation."""
        return self.log_action(
            AuditAction.PLUGIN_INSTALLED,
            details={"plugin": plugin_name, "version": version},
        )

    def log_plugin_removed(self, plugin_name: str) -> dict:
        """Log plugin removal."""
        return self.log_action(
            AuditAction.PLUGIN_REMOVED,
            details={"plugin": plugin_name},
        )

    def log_security_check(
        self,
        check_name: str,
        status: str,
        findings: Optional[list[str]] = None,
    ) -> dict:
        """Log security check."""
        return self.log_action(
            AuditAction.SECURITY_CHECK,
            details={"check": check_name, "findings": findings or []},
            status=status,
        )

    def log_permission_changed(
        self,
        path: str,
        old_perms: str,
        new_perms: str,
    ) -> dict[str, Any]:
        """Log permission change."""
        return self.log_action(
            AuditAction.PERMISSION_CHANGED,
            details={
                "path": path,
                "old_permissions": old_perms,
                "new_permissions": new_perms,
            },
        )

    def log_verification(
        self,
        passed: bool,
        details: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Log setup verification."""
        action = AuditAction.VERIFICATION_PASSED if passed else AuditAction.VERIFICATION_FAILED
        return self.log_action(
            action,
            details=details,
            status="success" if passed else "failure",
        )

    def log_health_check(
        self,
        status: str,
        details: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Log health check result."""
        return self.log_action(
            AuditAction.HEALTH_CHECK,
            details=details,
            status=status,
        )

    def get_log_file_path(self) -> Path:
        """Get current audit log file path."""
        return self.storage.get_log_file_path()

    def get_audit_logs(
        self,
        limit: Optional[int] = None,
        verify_signatures: bool = False,
    ) -> list[dict[str, Any]]:
        """Get audit log entries.

        Args:
            limit: Maximum number of entries (default all)
            verify_signatures: If True, only return entries with valid signatures

        Returns:
            List of audit log entries
        """
        entries = self.storage.read_entries(limit)

        # Filter by signature validity if requested
        if verify_signatures and self.signing_service:
            filtered_entries = []
            for entry in entries:
                if entry.get("signature"):
                    if self.signing_service.verify_signature(entry):
                        filtered_entries.append(entry)
                    else:
                        self.logger.warning(
                            f"Audit entry has invalid signature: {entry.get("timestamp")}",
                        )
            return filtered_entries

        return entries

    def validate_log_integrity(self) -> dict[str, Any]:
        """Validate integrity of all audit log entries.

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
        entries = self.storage.read_entries()

        valid_count = 0
        invalid_count = 0
        unsigned_count = 0
        invalid_timestamps = []

        for entry in entries:
            if "signature" not in entry:
                unsigned_count += 1
            elif self.signing_service and self.signing_service.verify_signature(entry):
                valid_count += 1
            else:
                invalid_count += 1
                invalid_timestamps.append(entry.get("timestamp", "unknown"))
                self.logger.error(f"Tampering detected in audit entry: {entry.get("timestamp")}")

        return {
            "total_entries": len(entries),
            "valid_entries": valid_count,
            "invalid_entries": invalid_count,
            "unsigned_entries": unsigned_count,
            "tampering_detected": invalid_count > 0,
            "invalid_entry_timestamps": invalid_timestamps,
        }

    def rotate_logs(self) -> None:
        """Rotate audit logs by archiving old ones."""
        self.storage.rotate_logs()

    def get_audit_summary(self, hours: int = 24) -> dict[str, Any]:
        """Get summary of audit log for given time period.

        Args:
            hours: Look back hours (default 24)

        Returns:
            Summary statistics
        """
        cutoff = datetime.now() - timedelta(hours=hours)
        entries = self.storage.read_entries()

        summary: dict[str, Any] = {
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

                summary["total_actions"] = int(summary["total_actions"]) + 1
                action = entry.get("action", "unknown")
                status = entry.get("status", "unknown")
                user = entry.get("user", "unknown")

                actions_by_type = summary["actions_by_type"]
                actions_by_type[action] = actions_by_type.get(action, 0) + 1

                actions_by_status = summary["actions_by_status"]
                actions_by_status[status] = actions_by_status.get(status, 0) + 1

                users = summary["users"]
                users.add(user)
            except (KeyError, TypeError) as e:
                self.logger.debug(f"Error parsing audit entry: {e}")

        users_set = summary["users"]
        summary["users"] = list(users_set)
        return summary


class AuditReporter:
    """Generates reports from audit logs."""

    def __init__(self, audit_logger: AuditLogger) -> None:
        """Initialize report generator.

        Args:
            audit_logger: AuditLogger instance
        """
        self.audit_logger = audit_logger
        self.logger = logging.getLogger(__name__)

    def generate_activity_report(self, days: int = 30) -> str:
        """Generate activity report for given time period.

        Args:
            days: Number of days to report on

        Returns:
            Formatted activity report
        """
        cutoff = datetime.now() - timedelta(days=days)
        entries = self.audit_logger.get_audit_logs()

        report_lines = [
            f"Activity Report - Last {days} Days",
            "=" * 50,
            "",
        ]

        action_counts: dict[str, int] = {}
        user_counts: dict[str, int] = {}

        for entry in entries:
            try:
                entry_time = datetime.fromisoformat(entry.get("timestamp", ""))
                if entry_time < cutoff:
                    continue

                action = entry.get("action", "unknown")
                user = entry.get("user", "unknown")

                action_counts[action] = action_counts.get(action, 0) + 1
                user_counts[user] = user_counts.get(user, 0) + 1
            except (KeyError, TypeError) as e:
                self.logger.debug(f"Error parsing entry: {e}")

        report_lines.append("Actions by Type:")
        for action, count in sorted(
            action_counts.items(),
            key=operator.itemgetter(1),
            reverse=True,
        ):
            report_lines.append(f"  {action}: {count}")

        report_lines.extend(("", "Activity by User:"))
        for user, count in sorted(user_counts.items(), key=operator.itemgetter(1), reverse=True):
            report_lines.append(f"  {user}: {count}")

        return "\n".join(report_lines)

    def generate_security_report(self) -> str:
        """Generate security and integrity report.

        Returns:
            Formatted security report
        """
        integrity = self.audit_logger.validate_log_integrity()

        report_lines = [
            "Security & Integrity Report",
            "=" * 50,
            "",
            f"Total Entries: {integrity["total_entries"]}",
            f"Valid Entries: {integrity["valid_entries"]}",
            f"Invalid Entries: {integrity["invalid_entries"]}",
            f"Unsigned Entries: {integrity["unsigned_entries"]}",
            f"Tampering Detected: {integrity["tampering_detected"]}",
            "",
        ]

        if integrity["invalid_entry_timestamps"]:
            report_lines.append("⚠️ Invalid Entries at:")
            for timestamp in integrity["invalid_entry_timestamps"]:
                report_lines.append(f"  - {timestamp}")

        return "\n".join(report_lines)


# ============================================================================
# PUBLIC API
# ============================================================================


__all__ = [
    "AuditLogStorage",
    "AuditLogger",
    "AuditReporter",
    "AuditSigningService",
]
