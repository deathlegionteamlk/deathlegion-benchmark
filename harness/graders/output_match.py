"""Output match grader: compares the candidate's output against expected outputs
using exact or fuzzy matching."""

from abc import ABC, abstractmethod
from typing import Any


class Grader(ABC):
    """Abstract base class for all graders."""

    @abstractmethod
    def grade(self, solution_path: str, manifest: dict[str, Any]) -> dict[str, Any]:
        ...


class OutputMatchGrader(Grader):
    """Compares candidate output to expected reference outputs.

    Supports exact, normalized (whitespace-insensitive), and
    tolerance-based (floating-point) comparisons.
    """

    def grade(self, solution_path: str, manifest: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("OutputMatchGrader.grade is not yet implemented")