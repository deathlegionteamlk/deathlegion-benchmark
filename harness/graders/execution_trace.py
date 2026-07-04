"""Execution trace grader: validates the internal execution trace of the candidate
solution (e.g., checks that certain data structures were used, that bounds
were checked, or that the algorithm followed a specific approach)."""

from abc import ABC, abstractmethod
from typing import Any


class Grader(ABC):
    """Abstract base class for all graders."""

    @abstractmethod
    def grade(self, solution_path: str, manifest: dict[str, Any]) -> dict[str, Any]:
        ...


class ExecutionTraceGrader(Grader):
    """Analyzes execution traces (e.g., logs, profiling data, instrumented output)
    to verify solution properties beyond simple pass/fail."""

    def grade(self, solution_path: str, manifest: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("ExecutionTraceGrader.grade is not yet implemented")