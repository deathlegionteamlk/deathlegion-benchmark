"""Unit test grader: runs a suite of unit tests against the candidate solution."""

from abc import ABC, abstractmethod
from typing import Any


class Grader(ABC):
    """Abstract base class for all graders."""

    @abstractmethod
    def grade(self, solution_path: str, manifest: dict[str, Any]) -> dict[str, Any]:
        """Grade a candidate solution.

        Args:
            solution_path: Path to the candidate solution.
            manifest: The problem manifest dictionary.

        Returns:
            A dictionary with pass/fail/partial status and score details.
        """
        ...


class UnitTestGrader(Grader):
    """Runs a predefined suite of unit tests against the candidate solution."""

    def grade(self, solution_path: str, manifest: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("UnitTestGrader.grade is not yet implemented")