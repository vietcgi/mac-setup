#!/usr/bin/env python3
"""
AI Commit Validator - Quality-First Validation System

Ensures AI-generated code meets quality standards before commits are made.
Focuses on code quality over speed.
"""

import os
import json
import subprocess
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import logging

# ANSI Colors
class Colors:
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    RESET = '\033[0m'


class CodeQualityValidator:
    """Validates code quality for AI-generated commits."""

    def __init__(self):
        self.home = Path.home()
        self.devkit_dir = self.home / ".devkit/git"
        self.devkit_dir.mkdir(parents=True, exist_ok=True)
        self.quality_report_file = self.devkit_dir / "quality_reports.jsonl"
        self.setup_logging()

    def setup_logging(self):
        """Setup logging for quality checks."""
        self.log_file = self.devkit_dir / "quality_checks.log"
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        handler = logging.FileHandler(self.log_file)
        formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def print_status(self, message: str, level: str = "INFO"):
        """Print colored status message."""
        colors = {
            "INFO": Colors.BLUE,
            "SUCCESS": Colors.GREEN,
            "WARNING": Colors.YELLOW,
            "ERROR": Colors.RED,
        }
        symbol = {
            "INFO": "ℹ",
            "SUCCESS": "✓",
            "WARNING": "⚠",
            "ERROR": "✗",
        }
        color = colors.get(level, Colors.RESET)
        sym = symbol.get(level, "•")

        print(f"{color}{sym} {message}{Colors.RESET}")
        self.logger.log(
            getattr(logging, level, logging.INFO),
            message.replace(Colors.RESET, '').replace(color, '')
        )

    # ========== QUALITY CHECK METHODS ==========

    def check_code_style(self, files: List[str]) -> Tuple[bool, List[str], int]:
        """Check Python code style (PEP 8, pylint)."""
        self.print_status("Checking code style (PEP 8)...", "INFO")
        issues = []
        score = 100

        for filepath in files:
            if not filepath.endswith('.py'):
                continue

            # Check with pylint
            try:
                result = subprocess.run(
                    ['pylint', '--disable=all', '--enable=C,E', filepath],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode != 0:
                    for line in result.stdout.split('\n'):
                        if 'C:' in line or 'E:' in line:
                            issues.append(f"{filepath}: {line}")
                            score -= 5

            except FileNotFoundError:
                self.print_status("pylint not installed, skipping style check", "WARNING")
                return True, [], 100
            except Exception as e:
                self.print_status(f"Style check error: {e}", "ERROR")
                return False, [str(e)], 0

        if issues:
            self.print_status(f"Found {len(issues)} style issues", "WARNING")
            return False, issues, max(0, score)

        self.print_status("Code style check passed", "SUCCESS")
        return True, [], 100

    def check_test_coverage(self, files: List[str]) -> Tuple[bool, List[str], float]:
        """Check test coverage (minimum 80%)."""
        self.print_status("Checking test coverage...", "INFO")

        try:
            result = subprocess.run(
                ['coverage', 'run', '-m', 'pytest', '--tb=short'],
                capture_output=True,
                text=True,
                timeout=30
            )

            # Get coverage report
            cov_result = subprocess.run(
                ['coverage', 'report', '--fail-under=80'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if cov_result.returncode == 0:
                # Extract coverage percentage
                for line in cov_result.stdout.split('\n'):
                    if 'TOTAL' in line:
                        match = re.search(r'(\d+)%', line)
                        if match:
                            coverage = float(match.group(1))
                            self.print_status(f"Test coverage: {coverage}%", "SUCCESS")
                            return True, [], coverage

            self.print_status("Test coverage below 80%", "ERROR")
            return False, [cov_result.stdout], 0

        except FileNotFoundError:
            self.print_status("coverage/pytest not installed, skipping", "WARNING")
            return True, [], 100
        except Exception as e:
            self.print_status(f"Coverage check error: {e}", "ERROR")
            return False, [str(e)], 0

    def check_security(self, files: List[str]) -> Tuple[bool, List[str], int]:
        """Check for security issues using bandit."""
        self.print_status("Checking security...", "INFO")
        issues = []
        score = 100

        try:
            python_files = [f for f in files if f.endswith('.py')]
            if not python_files:
                return True, [], 100

            result = subprocess.run(
                ['bandit', '-r', '-ll'] + python_files,
                capture_output=True,
                text=True,
                timeout=30
            )

            if 'Issue: ' in result.stdout:
                for line in result.stdout.split('\n'):
                    if 'Issue: ' in line or 'Severity: ' in line:
                        issues.append(line)
                        if 'HIGH' in line:
                            score -= 20
                        elif 'MEDIUM' in line:
                            score -= 10

            if issues:
                self.print_status(f"Found {len(issues)} security issues", "ERROR")
                return False, issues, max(0, score)

            self.print_status("Security check passed", "SUCCESS")
            return True, [], 100

        except FileNotFoundError:
            self.print_status("bandit not installed, skipping security check", "WARNING")
            return True, [], 100
        except Exception as e:
            self.print_status(f"Security check error: {e}", "ERROR")
            return False, [str(e)], 0

    def check_complexity(self, files: List[str]) -> Tuple[bool, List[str], float]:
        """Check code complexity using radon."""
        self.print_status("Checking code complexity...", "INFO")
        issues = []
        avg_complexity = 0

        try:
            python_files = [f for f in files if f.endswith('.py')]
            if not python_files:
                return True, [], 10  # Best complexity score

            result = subprocess.run(
                ['radon', 'cc', '-a'] + python_files,
                capture_output=True,
                text=True,
                timeout=30
            )

            complexities = []
            for line in result.stdout.split('\n'):
                if ' - ' in line and ('A' in line or 'B' in line or 'C' in line or 'D' in line or 'F' in line):
                    complexities.append(line)
                    # F = too complex, D = high, C = moderate
                    if 'F' in line:
                        issues.append(f"HIGH COMPLEXITY: {line}")
                        avg_complexity += 10
                    elif 'D' in line:
                        issues.append(f"Moderate complexity: {line}")
                        avg_complexity += 3

            if complexities:
                avg_complexity = avg_complexity / len(complexities) if complexities else 5

            if issues:
                self.print_status(f"Found {len(issues)} complexity issues", "WARNING")
                return len([i for i in issues if 'HIGH' in i]) == 0, issues, avg_complexity

            self.print_status("Code complexity acceptable", "SUCCESS")
            return True, [], avg_complexity

        except FileNotFoundError:
            self.print_status("radon not installed, skipping complexity check", "WARNING")
            return True, [], 5
        except Exception as e:
            self.print_status(f"Complexity check error: {e}", "ERROR")
            return False, [str(e)], 10

    def check_tests_pass(self, files: List[str]) -> Tuple[bool, List[str], int]:
        """Run tests to ensure they pass."""
        self.print_status("Running tests...", "INFO")

        try:
            result = subprocess.run(
                ['pytest', '-v', '--tb=short'],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                # Count passed tests
                passed = len(re.findall(r'PASSED', result.stdout))
                self.print_status(f"All tests passed ({passed} tests)", "SUCCESS")
                return True, [], passed
            else:
                # Extract failed tests
                failed = re.findall(r'FAILED.*', result.stdout)
                self.print_status(f"Tests failed ({len(failed)} failures)", "ERROR")
                return False, failed, 0

        except FileNotFoundError:
            self.print_status("pytest not installed, skipping tests", "WARNING")
            return True, [], 0
        except subprocess.TimeoutExpired:
            self.print_status("Tests timeout (>60s)", "ERROR")
            return False, ["Test execution timeout"], 0
        except Exception as e:
            self.print_status(f"Test error: {e}", "ERROR")
            return False, [str(e)], 0

    def check_documentation(self, files: List[str]) -> Tuple[bool, List[str], int]:
        """Check for code documentation and docstrings."""
        self.print_status("Checking documentation...", "INFO")
        issues = []
        score = 100

        for filepath in files:
            if not filepath.endswith('.py'):
                continue

            try:
                with open(filepath, 'r') as f:
                    content = f.read()

                # Check for module docstring
                if not (content.startswith('"""') or content.startswith("'''")):
                    issues.append(f"{filepath}: Missing module docstring")
                    score -= 10

                # Check for function docstrings
                functions = re.findall(r'def \w+\(.*?\):', content)
                for func in functions:
                    if f"{func}\n    \"\"\"" not in content and f"{func}\n    '''" not in content:
                        issues.append(f"{filepath}: Function missing docstring: {func}")
                        score -= 5

            except Exception as e:
                self.print_status(f"Documentation check error: {e}", "ERROR")
                return False, [str(e)], 0

        if issues:
            self.print_status(f"Found {len(issues)} documentation issues", "WARNING")
            return False, issues, max(0, score)

        self.print_status("Documentation check passed", "SUCCESS")
        return True, [], 100

    def check_dependencies(self, files: List[str]) -> Tuple[bool, List[str], int]:
        """Check for dependency issues."""
        self.print_status("Checking dependencies...", "INFO")
        issues = []

        # Check for requirements.txt or setup.py
        if not (Path("requirements.txt").exists() or Path("setup.py").exists()):
            return True, [], 100

        try:
            result = subprocess.run(
                ['pip-audit'],
                capture_output=True,
                text=True,
                timeout=30
            )

            if 'found' in result.stdout.lower():
                issues = result.stdout.split('\n')
                self.print_status(f"Found dependency vulnerabilities", "ERROR")
                return False, issues, 0

            self.print_status("Dependency check passed", "SUCCESS")
            return True, [], 100

        except FileNotFoundError:
            self.print_status("pip-audit not installed, skipping", "WARNING")
            return True, [], 100
        except Exception as e:
            self.print_status(f"Dependency check error: {e}", "ERROR")
            return False, [str(e)], 0

    # ========== INTEGRATION METHODS ==========

    def get_staged_files(self) -> List[str]:
        """Get list of staged files."""
        try:
            result = subprocess.run(
                ['git', 'diff', '--cached', '--name-only'],
                capture_output=True,
                text=True
            )
            return result.stdout.strip().split('\n')
        except Exception:
            return []

    def generate_quality_report(self, checks: Dict) -> Dict:
        """Generate comprehensive quality report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "checks": checks,
            "overall_quality_score": 0,
            "pass_all": True,
        }

        # Calculate scores
        scores = []
        for check_name, check_result in checks.items():
            if isinstance(check_result, dict):
                if 'score' in check_result:
                    scores.append(check_result['score'])
                if not check_result.get('passed', True):
                    report['pass_all'] = False

        if scores:
            report['overall_quality_score'] = sum(scores) / len(scores)

        return report

    def run_all_checks(self, files: Optional[List[str]] = None) -> Dict:
        """Run all quality checks."""
        print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
        print(f"{Colors.BLUE}AI CODE QUALITY VALIDATION{Colors.RESET}")
        print(f"{Colors.BLUE}{'='*60}{Colors.RESET}\n")

        if not files:
            files = self.get_staged_files()

        if not files or files == ['']:
            self.print_status("No files to check", "WARNING")
            return {"status": "no_files"}

        checks = {}

        # Run all checks
        print(f"{Colors.YELLOW}Running Quality Checks...{Colors.RESET}\n")

        # 1. Code Style
        passed, issues, score = self.check_code_style(files)
        checks['code_style'] = {
            'passed': passed,
            'score': score,
            'issues': issues
        }

        # 2. Tests
        passed, issues, count = self.check_tests_pass(files)
        checks['tests'] = {
            'passed': passed,
            'score': 100 if passed else 0,
            'test_count': count,
            'issues': issues
        }

        # 3. Test Coverage
        passed, issues, coverage = self.check_test_coverage(files)
        checks['coverage'] = {
            'passed': passed,
            'score': coverage,
            'issues': issues
        }

        # 4. Security
        passed, issues, score = self.check_security(files)
        checks['security'] = {
            'passed': passed,
            'score': score,
            'issues': issues
        }

        # 5. Complexity
        passed, issues, complexity = self.check_complexity(files)
        checks['complexity'] = {
            'passed': passed,
            'score': min(10, max(0, 10 - complexity)),
            'complexity_score': complexity,
            'issues': issues
        }

        # 6. Documentation
        passed, issues, score = self.check_documentation(files)
        checks['documentation'] = {
            'passed': passed,
            'score': score,
            'issues': issues
        }

        # 7. Dependencies
        passed, issues, score = self.check_dependencies(files)
        checks['dependencies'] = {
            'passed': passed,
            'score': score,
            'issues': issues
        }

        # Generate report
        report = self.generate_quality_report(checks)
        self.save_quality_report(report)

        # Display summary
        self.display_summary(report)

        return report

    def display_summary(self, report: Dict):
        """Display quality check summary."""
        print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
        print(f"{Colors.BLUE}Quality Check Summary{Colors.RESET}")
        print(f"{Colors.BLUE}{'='*60}{Colors.RESET}\n")

        for check_name, check_result in report['checks'].items():
            if isinstance(check_result, dict):
                status = "✓ PASS" if check_result.get('passed', False) else "✗ FAIL"
                color = Colors.GREEN if check_result.get('passed') else Colors.RED
                score = check_result.get('score', 0)
                print(f"{color}{status}{Colors.RESET} {check_name:20} ({score:.0f}%)")

        print(f"\n{Colors.YELLOW}Overall Quality Score: {report['overall_quality_score']:.1f}%{Colors.RESET}")

        if report['pass_all']:
            print(f"{Colors.GREEN}✓ ALL CHECKS PASSED - SAFE TO COMMIT{Colors.RESET}")
            return True
        else:
            print(f"{Colors.RED}✗ SOME CHECKS FAILED - FIX ISSUES BEFORE COMMIT{Colors.RESET}")
            return False

    def save_quality_report(self, report: Dict):
        """Save quality report to file."""
        with open(self.quality_report_file, 'a') as f:
            f.write(json.dumps(report) + '\n')


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate AI-generated code quality"
    )
    parser.add_argument(
        '--files',
        nargs='+',
        help="Specific files to check"
    )
    parser.add_argument(
        '--check',
        choices=['style', 'tests', 'coverage', 'security', 'complexity', 'docs', 'deps', 'all'],
        default='all',
        help="Specific check to run"
    )

    args = parser.parse_args()

    validator = CodeQualityValidator()
    report = validator.run_all_checks(files=args.files)

    # Exit with appropriate code
    exit_code = 0 if report.get('pass_all', True) else 1
    return exit_code


if __name__ == "__main__":
    import sys
    sys.exit(main())
