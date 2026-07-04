"""Diff match grader: computes a structured diff between candidate and reference output."""

from abc import ABC, abstractmethod
from typing import Any


class Grader(ABC):
    """Abstract base class for all graders."""

    @abstractmethod
    def grade(self, solution_path: str, manifest: dict[str, Any]) -> dict[str, Any]:
        ...


class DiffMatchGrader(Grader):
    """Computes a line-by-line or token-by-token diff between candidate output
    and reference output. Assigns partial credit based on edit distance."""

    def grade(self, solution_path: str, manifest: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("DiffMatchGrader.grade is not yet implemented")