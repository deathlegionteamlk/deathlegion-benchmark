"""Orchestrates the end-to-end evaluation pipeline for a problem.

Typical usage:
    runner = Runner(problem_root="/path/to/problems")
    manifest = runner.load_problem("problem_id")
    result = runner.run_candidate(manifest, solution_path="/path/to/solution")
    grade_result = runner.grade(result)
    runner.record(grade_result)
"""

from typing import Any


class Runner:
    """Main evaluation orchestrator.

    Loads a problem manifest, runs a candidate solution through the
    appropriate grader, and records the result.
    """

    def __init__(self, problem_root: str = "problems") -> None:
        self.problem_root = problem_root

    def load_problem(self, problem_id: str) -> dict[str, Any]:
        """Load and validate a problem manifest by its unique ID.

        Args:
            problem_id: Unique identifier for the problem.

        Returns:
            The parsed manifest dictionary.

        Raises:
            NotImplementedError: This method is not yet implemented.
        """
        raise NotImplementedError("load_problem is not yet implemented")

    def run_candidate(self, manifest: dict[str, Any], solution_path: str) -> dict[str, Any]:
        """Execute a candidate solution against the problem's grader.

        Args:
            manifest: The problem manifest dictionary.
            solution_path: Path to the candidate solution file or directory.

        Returns:
            A result dictionary with pass/fail/partial status, runtime,
            resource usage, and failure category.

        Raises:
            NotImplementedError: This method is not yet implemented.
        """
        raise NotImplementedError("run_candidate is not yet implemented")

    def grade(self, result: dict[str, Any]) -> dict[str, Any]:
        """Apply the grader specified in the manifest to compute scores.

        Args:
            result: The raw execution result from run_candidate.

        Returns:
            The graded result with scores populated.

        Raises:
            NotImplementedError: This method is not yet implemented.
        """
        raise NotImplementedError("grade is not yet implemented")

    def record(self, grade_result: dict[str, Any]) -> None:
        """Persist the graded result (e.g., to a JSON log file).

        Args:
            grade_result: The fully graded result dictionary.

        Raises:
            NotImplementedError: This method is not yet implemented.
        """
        raise NotImplementedError("record is not yet implemented")