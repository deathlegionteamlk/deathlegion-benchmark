"""Agentic test suite grader: validates multi-step, multi-file agentic solutions
by running integration tests, verifying file modifications, and checking
that the fix resolves the referenced issue."""

from abc import ABC, abstractmethod
from typing import Any


class Grader(ABC):
    """Abstract base class for all graders."""

    @abstractmethod
    def grade(self, solution_path: str, manifest: dict[str, Any]) -> dict[str, Any]:
        ...


class AgenticTestSuiteGrader(Grader):
    """Runs a suite of integration-level tests for agentic (multi-file, repo-level)
    problems. Verifies that the solution correctly modifies the expected files,
    passes all pre-existing tests, and resolves the target issue."""

    def grade(self, solution_path: str, manifest: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("AgenticTestSuiteGrader.grade is not yet implemented")