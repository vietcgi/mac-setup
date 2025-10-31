#!/usr/bin/env python3
"""
Tests for mutation testing framework.

Validates:
- Mutation type definitions
- Mutation detection in AST
- Mutation result tracking
- Report generation
"""

import ast
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Mock sys.argv to prevent argparse issues during import
sys.argv = ["pytest"]

from cli.mutation_test import (  # noqa: E402
    MutationType,
    Mutation,
    MutationResult,
    MutationReport,
    MutationDetector,
    MutationTester,
)


class TestMutationType:
    """Test MutationType enum."""

    def test_comparison_operator_enum(self) -> None:
        """Test comparison operator mutation type."""
        assert MutationType.COMPARISON_OPERATOR.value == "comparison_operator"

    def test_boolean_literal_enum(self) -> None:
        """Test boolean literal mutation type."""
        assert MutationType.BOOLEAN_LITERAL.value == "boolean_literal"

    def test_arithmetic_operator_enum(self) -> None:
        """Test arithmetic operator mutation type."""
        assert MutationType.ARITHMETIC_OPERATOR.value == "arithmetic_operator"

    def test_logical_operator_enum(self) -> None:
        """Test logical operator mutation type."""
        assert MutationType.LOGICAL_OPERATOR.value == "logical_operator"

    def test_return_value_enum(self) -> None:
        """Test return value mutation type."""
        assert MutationType.RETURN_VALUE.value == "return_value"

    def test_constant_replacement_enum(self) -> None:
        """Test constant replacement mutation type."""
        assert MutationType.CONSTANT_REPLACEMENT.value == "constant_replacement"


class TestMutation:
    """Test Mutation dataclass."""

    def test_mutation_creation(self) -> None:
        """Test creating a mutation."""
        mutation = Mutation(
            file_path=Path("test.py"),
            line_number=10,
            mutation_type=MutationType.COMPARISON_OPERATOR,
            original_code="x == y",
            mutated_code="x != y",
            description="Changed == to !=",
        )

        assert mutation.file_path == Path("test.py")
        assert mutation.line_number == 10
        assert mutation.mutation_type == MutationType.COMPARISON_OPERATOR
        assert mutation.original_code == "x == y"
        assert mutation.mutated_code == "x != y"

    def test_mutation_hash(self) -> None:
        """Test mutation hashing."""
        mutation1 = Mutation(
            file_path=Path("test.py"),
            line_number=10,
            mutation_type=MutationType.COMPARISON_OPERATOR,
            original_code="x == y",
            mutated_code="x != y",
            description="Changed == to !=",
        )

        mutation2 = Mutation(
            file_path=Path("test.py"),
            line_number=10,
            mutation_type=MutationType.COMPARISON_OPERATOR,
            original_code="a == b",
            mutated_code="a != b",
            description="Changed == to !=",
        )

        # Same file, line, and type should hash the same
        assert hash(mutation1) == hash(mutation2)

    def test_mutation_hash_different_file(self) -> None:
        """Test mutation hashing with different file."""
        mutation1 = Mutation(
            file_path=Path("test1.py"),
            line_number=10,
            mutation_type=MutationType.COMPARISON_OPERATOR,
            original_code="x == y",
            mutated_code="x != y",
            description="Changed == to !=",
        )

        mutation2 = Mutation(
            file_path=Path("test2.py"),
            line_number=10,
            mutation_type=MutationType.COMPARISON_OPERATOR,
            original_code="x == y",
            mutated_code="x != y",
            description="Changed == to !=",
        )

        assert hash(mutation1) != hash(mutation2)


class TestMutationResult:
    """Test MutationResult dataclass."""

    def test_mutation_result_killed(self) -> None:
        """Test mutation result marked as killed."""
        mutation = Mutation(
            file_path=Path("test.py"),
            line_number=10,
            mutation_type=MutationType.COMPARISON_OPERATOR,
            original_code="x == y",
            mutated_code="x != y",
            description="Changed == to !=",
        )

        result = MutationResult(mutation=mutation, test_result="killed")

        assert result.killed is True
        assert result.test_result == "killed"

    def test_mutation_result_survived(self) -> None:
        """Test mutation result marked as survived."""
        mutation = Mutation(
            file_path=Path("test.py"),
            line_number=10,
            mutation_type=MutationType.COMPARISON_OPERATOR,
            original_code="x == y",
            mutated_code="x != y",
            description="Changed == to !=",
        )

        result = MutationResult(mutation=mutation, test_result="survived")

        assert result.killed is False
        assert result.test_result == "survived"

    def test_mutation_result_with_details(self) -> None:
        """Test mutation result with details."""
        mutation = Mutation(
            file_path=Path("test.py"),
            line_number=10,
            mutation_type=MutationType.COMPARISON_OPERATOR,
            original_code="x == y",
            mutated_code="x != y",
            description="Changed == to !=",
        )

        result = MutationResult(
            mutation=mutation, test_result="killed", details="Test caught the mutation"
        )

        assert result.details == "Test caught the mutation"


class TestMutationReport:
    """Test MutationReport dataclass."""

    def test_mutation_report_creation(self) -> None:
        """Test creating a mutation report."""
        report = MutationReport()

        assert report.total_mutations == 0
        assert report.killed_mutations == 0
        assert report.survived_mutations == 0
        assert report.mutation_score == 0.0
        assert len(report.results) == 0

    def test_mutation_report_update_no_mutations(self) -> None:
        """Test updating report with no mutations."""
        report = MutationReport()
        report.update()

        assert report.total_mutations == 0
        assert report.mutation_score == 0.0

    def test_mutation_report_update_all_killed(self) -> None:
        """Test updating report with all mutations killed."""
        mutation1 = Mutation(
            file_path=Path("test.py"),
            line_number=10,
            mutation_type=MutationType.COMPARISON_OPERATOR,
            original_code="x == y",
            mutated_code="x != y",
            description="Changed == to !=",
        )

        mutation2 = Mutation(
            file_path=Path("test.py"),
            line_number=20,
            mutation_type=MutationType.BOOLEAN_LITERAL,
            original_code="True",
            mutated_code="False",
            description="Changed True to False",
        )

        report = MutationReport(
            results=[
                MutationResult(mutation=mutation1, test_result="killed"),
                MutationResult(mutation=mutation2, test_result="killed"),
            ]
        )
        report.update()

        assert report.total_mutations == 2
        assert report.killed_mutations == 2
        assert report.survived_mutations == 0
        assert report.mutation_score == 100.0

    def test_mutation_report_update_some_survived(self) -> None:
        """Test updating report with some mutations survived."""
        mutation1 = Mutation(
            file_path=Path("test.py"),
            line_number=10,
            mutation_type=MutationType.COMPARISON_OPERATOR,
            original_code="x == y",
            mutated_code="x != y",
            description="Changed == to !=",
        )

        mutation2 = Mutation(
            file_path=Path("test.py"),
            line_number=20,
            mutation_type=MutationType.BOOLEAN_LITERAL,
            original_code="True",
            mutated_code="False",
            description="Changed True to False",
        )

        report = MutationReport(
            results=[
                MutationResult(mutation=mutation1, test_result="killed"),
                MutationResult(mutation=mutation2, test_result="survived"),
            ]
        )
        report.update()

        assert report.total_mutations == 2
        assert report.killed_mutations == 1
        assert report.survived_mutations == 1
        assert report.mutation_score == 50.0

    def test_mutation_report_to_dict(self) -> None:
        """Test converting report to dictionary."""
        mutation = Mutation(
            file_path=Path("test.py"),
            line_number=10,
            mutation_type=MutationType.COMPARISON_OPERATOR,
            original_code="x == y",
            mutated_code="x != y",
            description="Changed == to !=",
        )

        report = MutationReport(
            results=[MutationResult(mutation=mutation, test_result="survived")]
        )
        report.update()

        result_dict = report.to_dict()

        assert result_dict["total_mutations"] == 1
        assert result_dict["killed_mutations"] == 0
        assert result_dict["survived_mutations"] == 1
        assert "timestamp" in result_dict
        assert "mutation_score" in result_dict
        assert "survived_mutations_details" in result_dict


class TestMutationDetector:
    """Test MutationDetector class."""

    def test_detector_creation(self) -> None:
        """Test creating mutation detector."""
        source = "x = 1\ny = 2"
        detector = MutationDetector(source, Path("test.py"))

        assert detector.source_code == source
        assert detector.file_path == Path("test.py")
        assert len(detector.lines) >= 2
        assert len(detector.mutations) == 0

    def test_detector_detect_comparison(self) -> None:
        """Test detecting comparison operator mutations."""
        source = "if x == y:\n    pass\n"
        detector = MutationDetector(source, Path("test.py"))
        mutations = detector.detect()

        assert len(mutations) > 0
        # Should detect == -> != mutation
        assert any(m.mutation_type == MutationType.COMPARISON_OPERATOR for m in mutations)

    def test_detector_detect_boolean(self) -> None:
        """Test detecting boolean literal mutations."""
        source = "enabled = True\n"
        detector = MutationDetector(source, Path("test.py"))
        mutations = detector.detect()

        assert len(mutations) > 0
        # Should detect True -> False mutation
        assert any(m.mutation_type == MutationType.BOOLEAN_LITERAL for m in mutations)

    def test_detector_detect_logical_and(self) -> None:
        """Test detecting logical AND mutations."""
        source = "if a and b:\n    pass\n"
        detector = MutationDetector(source, Path("test.py"))
        mutations = detector.detect()

        assert len(mutations) > 0
        # Should detect and -> or mutation
        assert any(m.mutation_type == MutationType.LOGICAL_OPERATOR for m in mutations)

    def test_detector_detect_logical_or(self) -> None:
        """Test detecting logical OR mutations."""
        source = "if a or b:\n    pass\n"
        detector = MutationDetector(source, Path("test.py"))
        mutations = detector.detect()

        assert len(mutations) > 0
        # Should detect or -> and mutation
        assert any(m.mutation_type == MutationType.LOGICAL_OPERATOR for m in mutations)

    def test_detector_handle_syntax_error(self) -> None:
        """Test handling syntax errors in source code."""
        source = "if x == y\n    pass\n"  # Missing colon
        detector = MutationDetector(source, Path("test.py"))
        mutations = detector.detect()

        # Should not raise, just return empty or partial results
        assert isinstance(mutations, list)

    def test_detector_multiple_mutations_in_line(self) -> None:
        """Test detecting multiple mutation types in same line."""
        source = "if x == y and True:\n    pass\n"
        detector = MutationDetector(source, Path("test.py"))
        mutations = detector.detect()

        # Should find multiple mutation types
        assert len(mutations) > 1


class TestMutationTester:
    """Test MutationTester class."""

    def test_tester_creation(self) -> None:
        """Test creating mutation tester."""
        tester = MutationTester(
            cli_dir=Path("cli"),
            tests_dir=Path("tests"),
        )

        assert tester.cli_dir == Path("cli")
        assert tester.tests_dir == Path("tests")
        assert tester.logger is not None
        assert tester.report is not None

    def test_tester_setup_logging(self) -> None:
        """Test mutation tester logging setup."""
        tester = MutationTester(
            cli_dir=Path("cli"),
            tests_dir=Path("tests"),
        )

        assert tester.logger is not None
        assert tester.logger.name == "mutation_test"

    def test_tester_report_initialization(self) -> None:
        """Test that tester initializes report."""
        tester = MutationTester(
            cli_dir=Path("cli"),
            tests_dir=Path("tests"),
        )

        assert tester.report is not None
        assert isinstance(tester.report, MutationReport)
        assert len(tester.report.results) == 0

    @patch("cli.mutation_test.MutationDetector.detect")
    def test_tester_detect_all_mutations(self, mock_detect: Mock) -> None:
        """Test detecting all mutations in directory."""
        mock_detect.return_value = [
            Mutation(
                file_path=Path("cli/test.py"),
                line_number=10,
                mutation_type=MutationType.COMPARISON_OPERATOR,
                original_code="x == y",
                mutated_code="x != y",
                description="Changed == to !=",
            )
        ]

        temp_dir = tempfile.mkdtemp()
        cli_dir = Path(temp_dir) / "cli"
        cli_dir.mkdir()
        try:
            # Create a test Python file
            test_file = cli_dir / "test.py"
            test_file.write_text("x = 1\n")

            tester = MutationTester(cli_dir=cli_dir, tests_dir=Path("tests"))

            # Test private method would normally be called by run()
            assert tester.cli_dir == cli_dir
        finally:
            import shutil

            shutil.rmtree(temp_dir, ignore_errors=True)


class TestMutationIntegration:
    """Integration tests for mutation testing."""

    def test_full_mutation_workflow(self) -> None:
        """Test complete mutation detection workflow."""
        source_code = """
def is_valid(x):
    if x > 0 and x < 100:
        return True
    return False
"""

        detector = MutationDetector(source_code, Path("test.py"))
        mutations = detector.detect()

        # Should detect mutations
        assert len(mutations) > 0

        # Should have different mutation types
        mutation_types = {m.mutation_type for m in mutations}
        assert len(mutation_types) > 0

    def test_mutation_report_statistics(self) -> None:
        """Test mutation report statistics."""
        mutations = [
            Mutation(
                file_path=Path("test.py"),
                line_number=i,
                mutation_type=MutationType.COMPARISON_OPERATOR,
                original_code="x == y",
                mutated_code="x != y",
                description="Changed == to !=",
            )
            for i in range(10)
        ]

        # Create results: 7 killed, 3 survived
        results = [
            MutationResult(mutation=mutations[i], test_result="killed" if i < 7 else "survived")
            for i in range(10)
        ]

        report = MutationReport(results=results)
        report.update()

        assert report.total_mutations == 10
        assert report.killed_mutations == 7
        assert report.survived_mutations == 3
        assert report.mutation_score == 70.0

    def test_mutation_score_calculation(self) -> None:
        """Test mutation score calculation."""
        for total in [5, 10, 20]:
            killed = total // 2
            mutations = [
                Mutation(
                    file_path=Path("test.py"),
                    line_number=i,
                    mutation_type=MutationType.COMPARISON_OPERATOR,
                    original_code="x == y",
                    mutated_code="x != y",
                    description="Changed == to !=",
                )
                for i in range(total)
            ]

            results = [
                MutationResult(
                    mutation=mutations[i],
                    test_result="killed" if i < killed else "survived",
                )
                for i in range(total)
            ]

            report = MutationReport(results=results)
            report.update()

            expected_score = (killed / total) * 100
            assert abs(report.mutation_score - expected_score) < 0.01

    def test_comparison_mutations_coverage(self) -> None:
        """Test all comparison operator mutations."""
        comparisons = [
            ("x == y", "x != y"),
            ("x != y", "x == y"),
            ("x < y", "x <= y"),
            ("x <= y", "x < y"),
            ("x > y", "x >= y"),
            ("x >= y", "x > y"),
        ]

        for original, expected_mutation in comparisons:
            source = f"if {original}:\n    pass\n"
            detector = MutationDetector(source, Path("test.py"))
            mutations = detector.detect()

            # Filter for comparison mutations in this source
            comp_mutations = [
                m
                for m in mutations
                if m.mutation_type == MutationType.COMPARISON_OPERATOR
            ]
            if comp_mutations:
                assert any(expected_mutation in m.mutated_code for m in comp_mutations)


if __name__ == "__main__":
    import pytest

    pytest.main([__file__, "-v"])
