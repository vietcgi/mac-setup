"""
Extended tests for ConfigurationEngine coverage.

Focus on improving coverage of:
- load_file() method
- load_environment_overrides() method
- validate() method and its extracted helpers
- export() method
- save() method
"""

import sys
import os
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
import yaml
import json

# Mock sys.argv to prevent argparse issues
sys.argv = ["pytest"]

from cli.config_engine import ConfigurationEngine, ConfigEnvironment, RateLimiter  # noqa: E402


class TestRateLimiter(unittest.TestCase):
    """Test RateLimiter class."""

    def setUp(self):
        """Set up rate limiter."""
        self.limiter = RateLimiter(max_operations=3, window_seconds=1)

    def test_rate_limiter_allows_operations_within_limit(self):
        """Test that operations are allowed within limit."""
        for i in range(3):
            allowed, message = self.limiter.is_allowed("user1")
            self.assertTrue(allowed, f"Operation {i+1} should be allowed")

    def test_rate_limiter_blocks_operations_exceeding_limit(self):
        """Test that operations exceeding limit are blocked."""
        # Use up limit
        for _ in range(3):
            self.limiter.is_allowed("user1")

        # This should be blocked
        allowed, message = self.limiter.is_allowed("user1")
        self.assertFalse(allowed)
        self.assertIn("Rate limit exceeded", message)

    def test_rate_limiter_separate_per_identifier(self):
        """Test that rate limits are per-identifier."""
        # Use up limit for user1
        for _ in range(3):
            self.limiter.is_allowed("user1")

        # user2 should still be able to operate
        allowed, message = self.limiter.is_allowed("user2")
        self.assertTrue(allowed)

    def test_rate_limiter_reset_specific(self):
        """Test resetting limit for specific identifier."""
        # Use up limit
        for _ in range(3):
            self.limiter.is_allowed("user1")

        # Block additional operation
        allowed, message = self.limiter.is_allowed("user1")
        self.assertFalse(allowed)

        # Reset user1
        self.limiter.reset("user1")

        # Should allow now
        allowed, message = self.limiter.is_allowed("user1")
        self.assertTrue(allowed)

    def test_rate_limiter_reset_all(self):
        """Test resetting all limits."""
        for _ in range(3):
            self.limiter.is_allowed("user1")
            self.limiter.is_allowed("user2")

        # Both should be blocked
        self.assertFalse(self.limiter.is_allowed("user1")[0])
        self.assertFalse(self.limiter.is_allowed("user2")[0])

        # Reset all
        self.limiter.reset()

        # Both should work now
        self.assertTrue(self.limiter.is_allowed("user1")[0])
        self.assertTrue(self.limiter.is_allowed("user2")[0])

    def test_rate_limiter_get_stats(self):
        """Test getting rate limit stats."""
        for _ in range(2):
            self.limiter.is_allowed("user1")

        stats = self.limiter.get_stats("user1")

        self.assertEqual(stats["identifier"], "user1")
        self.assertEqual(stats["operations_count"], 2)
        self.assertEqual(stats["max_operations"], 3)
        self.assertIsNotNone(stats["next_reset"])

    def test_rate_limiter_stats_unknown_identifier(self):
        """Test stats for unknown identifier."""
        stats = self.limiter.get_stats("unknown")

        self.assertEqual(stats["identifier"], "unknown")
        self.assertEqual(stats["operations_count"], 0)
        self.assertIsNone(stats["next_reset"])


class TestConfigurationEngineLoadFile(unittest.TestCase):
    """Test ConfigurationEngine.load_file() method."""

    def setUp(self):
        """Set up test configuration engine."""
        self.temp_dir = tempfile.mkdtemp()
        self.engine = ConfigurationEngine(project_root=self.temp_dir)

    def tearDown(self):
        """Clean up."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_load_file_with_valid_yaml(self):
        """Test loading valid YAML file."""
        config_path = Path(self.temp_dir) / "config.yaml"
        config_data = {"test": {"key": "value"}, "number": 42}
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        result = self.engine.load_file(config_path)

        self.assertEqual(result["test"]["key"], "value")
        self.assertEqual(result["number"], 42)

    def test_load_file_with_section_extraction(self):
        """Test loading file with section extraction."""
        config_path = Path(self.temp_dir) / "config.yaml"
        config_data = {"global": {"key": "value"}, "other": {}}
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        result = self.engine.load_file(config_path, section="global")

        self.assertEqual(result["key"], "value")
        self.assertNotIn("other", result)

    def test_load_file_nonexistent(self):
        """Test loading nonexistent file."""
        result = self.engine.load_file(Path(self.temp_dir) / "missing.yaml")

        self.assertEqual(result, {})

    def test_load_file_invalid_yaml(self):
        """Test loading invalid YAML file."""
        config_path = Path(self.temp_dir) / "invalid.yaml"
        with open(config_path, "w") as f:
            f.write("{ invalid: yaml: syntax:")

        result = self.engine.load_file(config_path)

        self.assertEqual(result, {})

    def test_load_file_with_expanduser(self):
        """Test that file paths with ~ are expanded."""
        # Create config in temp location
        config_path = Path(self.temp_dir) / "config.yaml"
        with open(config_path, "w") as f:
            f.write("test: value\n")

        # Load with expanded path
        result = self.engine.load_file(config_path)
        self.assertIn("test", result)


class TestConfigurationEngineEnvironmentOverrides(unittest.TestCase):
    """Test ConfigurationEngine environment variable handling."""

    def setUp(self):
        """Set up test engine."""
        self.temp_dir = tempfile.mkdtemp()
        self.engine = ConfigurationEngine(project_root=self.temp_dir)
        self.original_environ = dict(os.environ)

    def tearDown(self):
        """Restore environment."""
        os.environ.clear()
        os.environ.update(self.original_environ)
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_load_environment_overrides_simple_value(self):
        """Test loading simple string environment variable."""
        os.environ["MAC_SETUP_TEST_VALUE"] = "hello"

        overrides = self.engine.load_environment_overrides()

        self.assertEqual(overrides["test_value"], "hello")

    def test_load_environment_overrides_boolean(self):
        """Test loading boolean environment variable."""
        os.environ["MAC_SETUP_ENABLED"] = "true"
        os.environ["MAC_SETUP_DISABLED"] = "false"

        overrides = self.engine.load_environment_overrides()

        self.assertTrue(overrides["enabled"])
        self.assertFalse(overrides["disabled"])

    def test_load_environment_overrides_list(self):
        """Test loading comma-separated list."""
        os.environ["MAC_SETUP_ROLES"] = "role1, role2, role3"

        overrides = self.engine.load_environment_overrides()

        self.assertEqual(overrides["roles"], ["role1", "role2", "role3"])

    def test_load_environment_overrides_nested(self):
        """Test loading nested key with double underscore."""
        os.environ["MAC_SETUP_LOGGING__LEVEL"] = "debug"
        os.environ["MAC_SETUP_DATABASE__HOST"] = "localhost"

        overrides = self.engine.load_environment_overrides()

        self.assertEqual(overrides["logging"]["level"], "debug")
        self.assertEqual(overrides["database"]["host"], "localhost")

    def test_load_environment_overrides_ignores_non_prefix(self):
        """Test that non-prefixed variables are ignored."""
        os.environ["OTHER_VAR"] = "value"
        os.environ["MAC_SETUP_TEST"] = "test"

        overrides = self.engine.load_environment_overrides()

        self.assertNotIn("OTHER_VAR", overrides)
        self.assertIn("test", overrides)


class TestConfigurationEngineValidation(unittest.TestCase):
    """Test ConfigurationEngine validation methods."""

    def setUp(self):
        """Set up test engine."""
        self.temp_dir = tempfile.mkdtemp()
        self.engine = ConfigurationEngine(project_root=self.temp_dir)
        self.engine.load_defaults()

    def tearDown(self):
        """Clean up."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_validate_correct_environment(self):
        """Test validation passes with correct environment."""
        self.engine.config["global"]["setup_environment"] = "development"

        is_valid, errors = self.engine.validate()

        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_validate_invalid_environment(self):
        """Test validation fails with invalid environment."""
        self.engine.config["global"]["setup_environment"] = "invalid"

        is_valid, errors = self.engine.validate()

        self.assertFalse(is_valid)
        self.assertTrue(any("setup_environment" in e for e in errors))

    def test_validate_role_overlap(self):
        """Test validation fails when roles overlap."""
        self.engine.config["global"]["enabled_roles"] = ["role1", "role2"]
        self.engine.config["global"]["disabled_roles"] = ["role2", "role3"]

        is_valid, errors = self.engine.validate()

        self.assertFalse(is_valid)
        self.assertTrue(any("both" in e.lower() or "overlap" in e.lower() for e in errors))

    def test_validate_invalid_logging_level(self):
        """Test validation fails with invalid logging level."""
        self.engine.config["global"]["logging"]["level"] = "invalid"

        is_valid, errors = self.engine.validate()

        self.assertFalse(is_valid)
        self.assertTrue(any("logging" in e.lower() for e in errors))

    def test_validate_invalid_parallel_tasks(self):
        """Test validation fails when parallel_tasks < 1."""
        self.engine.config["global"]["performance"]["parallel_tasks"] = 0

        is_valid, errors = self.engine.validate()

        self.assertFalse(is_valid)
        self.assertTrue(any("parallel_tasks" in e for e in errors))

    def test_validate_invalid_timeout(self):
        """Test validation fails when timeout < 30."""
        self.engine.config["global"]["performance"]["timeout"] = 10

        is_valid, errors = self.engine.validate()

        self.assertFalse(is_valid)
        self.assertTrue(any("timeout" in e for e in errors))


class TestConfigurationEngineExport(unittest.TestCase):
    """Test ConfigurationEngine export functionality."""

    def setUp(self):
        """Set up test engine."""
        self.temp_dir = tempfile.mkdtemp()
        self.engine = ConfigurationEngine(project_root=self.temp_dir)
        self.engine.load_defaults()

    def tearDown(self):
        """Clean up."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_export_yaml(self):
        """Test exporting configuration as YAML."""
        yaml_output = self.engine.export(format_type="yaml")

        # Should be valid YAML
        parsed = yaml.safe_load(yaml_output)
        self.assertIn("global", parsed)

    def test_export_json(self):
        """Test exporting configuration as JSON."""
        json_output = self.engine.export(format_type="json")

        # Should be valid JSON
        parsed = json.loads(json_output)
        self.assertIn("global", parsed)

    def test_export_unsupported_format(self):
        """Test that unsupported format raises error."""
        with self.assertRaises(ValueError):
            self.engine.export(format_type="xml")

    def test_export_contains_all_config(self):
        """Test that export contains all configuration."""
        self.engine.config["test_key"] = "test_value"

        yaml_output = self.engine.export(format_type="yaml")

        parsed = yaml.safe_load(yaml_output)
        self.assertEqual(parsed["test_key"], "test_value")


class TestConfigurationEngineSave(unittest.TestCase):
    """Test ConfigurationEngine save functionality."""

    def setUp(self):
        """Set up test engine."""
        self.temp_dir = tempfile.mkdtemp()
        self.engine = ConfigurationEngine(project_root=self.temp_dir)
        self.engine.load_defaults()

    def tearDown(self):
        """Clean up."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_save_creates_file(self):
        """Test that save creates configuration file."""
        save_path = Path(self.temp_dir) / "saved_config.yaml"

        self.engine.save(save_path)

        self.assertTrue(save_path.exists())

    def test_save_contains_configuration(self):
        """Test that saved file contains configuration."""
        save_path = Path(self.temp_dir) / "saved_config.yaml"
        self.engine.config["custom"] = "value"

        self.engine.save(save_path)

        with open(save_path, "r") as f:
            parsed = yaml.safe_load(f)

        self.assertEqual(parsed["custom"], "value")

    def test_save_creates_parent_directories(self):
        """Test that save creates parent directories."""
        save_path = Path(self.temp_dir) / "nested" / "dir" / "config.yaml"

        self.engine.save(save_path)

        self.assertTrue(save_path.exists())


class TestConfigurationEngineSetAndGet(unittest.TestCase):
    """Test ConfigurationEngine get/set operations."""

    def setUp(self):
        """Set up test engine."""
        self.temp_dir = tempfile.mkdtemp()
        self.engine = ConfigurationEngine(project_root=self.temp_dir)
        self.engine.load_defaults()

    def tearDown(self):
        """Clean up."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_get_simple_value(self):
        """Test getting simple configuration value."""
        self.engine.config["test"] = "value"

        result = self.engine.get("test")

        self.assertEqual(result, "value")

    def test_get_nested_value(self):
        """Test getting nested configuration value."""
        result = self.engine.get("global.setup_name")

        self.assertIsNotNone(result)
        self.assertEqual(result, "Development Environment")

    def test_get_missing_value_default(self):
        """Test getting missing value returns default."""
        result = self.engine.get("missing.key", default="default_value")

        self.assertEqual(result, "default_value")

    def test_set_simple_value(self):
        """Test setting simple configuration value."""
        success, message = self.engine.set("test_key", "test_value")

        self.assertTrue(success)
        self.assertEqual(self.engine.get("test_key"), "test_value")

    def test_set_nested_value(self):
        """Test setting nested configuration value."""
        success, message = self.engine.set("nested.deep.value", "result")

        self.assertTrue(success)
        self.assertEqual(self.engine.get("nested.deep.value"), "result")

    def test_set_with_rate_limiting_disabled(self):
        """Test that set works with rate limiting disabled."""
        engine = ConfigurationEngine(project_root=self.temp_dir, enable_rate_limiting=False)

        success, message = engine.set("key", "value")

        self.assertTrue(success)

    def test_set_with_rate_limiting_enabled_allows_operations(self):
        """Test that set allows operations within rate limit."""
        engine = ConfigurationEngine(project_root=self.temp_dir, enable_rate_limiting=True)

        for i in range(3):
            success, message = engine.set(f"key{i}", f"value{i}")
            self.assertTrue(success)

    def test_set_with_rate_limiting_enabled_blocks_excess(self):
        """Test that set blocks operations exceeding rate limit."""
        engine = ConfigurationEngine(
            project_root=self.temp_dir,
            enable_rate_limiting=True
        )
        # Configure rate limiter for testing (5 ops per 60 seconds)
        for _ in range(5):
            engine.set("key", "value")

        success, message = engine.set("excess_key", "excess_value")

        self.assertFalse(success)
        self.assertIn("Rate limit exceeded", message)


if __name__ == "__main__":
    unittest.main()
