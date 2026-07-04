"""Self-tests for the harness itself.

These tests validate the harness logic independently of any benchmark problem
content. They ensure the Runner, SubprocessRunner, and scoring utilities
behave correctly.
"""

import unittest


class TestRunner(unittest.TestCase):
    """Placeholder test case for the Runner class."""

    def test_load_problem_raises_not_implemented(self) -> None:
        """Runner.load_problem should raise NotImplementedError."""
        from harness.runner import Runner
        runner = Runner()
        with self.assertRaises(NotImplementedError):
            runner.load_problem("dummy_problem")

    def test_run_candidate_raises_not_implemented(self) -> None:
        """Runner.run_candidate should raise NotImplementedError."""
        from harness.runner import Runner
        runner = Runner()
        with self.assertRaises(NotImplementedError):
            runner.run_candidate({}, "/fake/path")

    def test_grade_raises_not_implemented(self) -> None:
        """Runner.grade should raise NotImplementedError."""
        from harness.runner import Runner
        runner = Runner()
        with self.assertRaises(NotImplementedError):
            runner.grade({})

    def test_record_raises_not_implemented(self) -> None:
        """Runner.record should raise NotImplementedError."""
        from harness.runner import Runner
        runner = Runner()
        with self.assertRaises(NotImplementedError):
            runner.record({})


class TestSubprocessRunner(unittest.TestCase):
    """Placeholder test case for the SubprocessRunner class."""

    def test_run_raises_not_implemented(self) -> None:
        """SubprocessRunner.run should raise NotImplementedError."""
        from harness.sandbox.subprocess_runner import SubprocessRunner
        runner = SubprocessRunner()
        with self.assertRaises(NotImplementedError):
            runner.run(["echo", "hello"])


class TestGrader(unittest.TestCase):
    """Placeholder test case for grader modules."""

    def test_unit_test_grader_raises_not_implemented(self) -> None:
        """UnitTestGrader.grade should raise NotImplementedError."""
        from harness.graders.unit_test import UnitTestGrader
        grader = UnitTestGrader()
        with self.assertRaises(NotImplementedError):
            grader.grade("/fake/path", {})


class TestAggregate(unittest.TestCase):
    """Placeholder test case for scoring aggregation."""

    def test_aggregate_raises_not_implemented(self) -> None:
        """aggregate() should raise NotImplementedError."""
        from scoring.aggregate import aggregate
        with self.assertRaises(NotImplementedError):
            aggregate([])


class TestAntiGaming(unittest.TestCase):
    """Placeholder test case for anti-gaming checks."""

    def test_check_solution_raises_not_implemented(self) -> None:
        """check_solution() should raise NotImplementedError."""
        from scoring.anti_gaming import check_solution
        with self.assertRaises(NotImplementedError):
            check_solution("/fake/path", {})


if __name__ == "__main__":
    unittest.main()