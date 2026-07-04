"""Anti-gaming heuristics: detects suspicious patterns in candidate solutions
that suggest gaming, memorization, or surface-level pattern-matching rather
than genuine problem-solving.

Typical usage:
    manifest = load_manifest("problems/my_problem/manifest.json")
    suspicion = check_solution("/path/to/candidate_solution.py", manifest)
    if suspicion["score"] > 0.7:
        logger.warning("Suspicious solution flagged")
"""

from typing import Any


def check_solution(solution_path: str, problem_manifest: dict[str, Any]) -> dict[str, Any]:
    """Inspect a candidate solution for signs of gaming or memorization.

    Heuristics may include:
    - Output only contains the exact visible sample test cases.
    - Solution is a lookup table rather than a general algorithm.
    - Solution hard-codes expected answers rather than computing them.
    - Unusual comment patterns (e.g., identical comments across different models).

    Args:
        solution_path: Path to the candidate solution file.
        problem_manifest: The problem manifest dictionary.

    Returns:
        A dictionary with:
        - "score": float between 0.0 (not suspicious) and 1.0 (highly suspicious).
        - "flags": list of strings describing specific concerns.
        - "details": additional information about what was checked.

    Raises:
        NotImplementedError: This function is not yet implemented.
    """
    raise NotImplementedError("check_solution is not yet implemented")