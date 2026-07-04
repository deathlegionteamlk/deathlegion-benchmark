"""Aggregation of per-problem scores into per-category and overall percentages.

Typical usage:
    results = [
        {"problem_id": "p1", "category": "algorithmic", "status": "pass", "score": 1.0},
        {"problem_id": "p2", "category": "agentic", "status": "fail", "score": 0.0},
        ...
    ]
    report = aggregate(results)
    # report == {
    #     "algorithmic": {"pass": 5, "total": 5, "percentage": 100.0},
    #     "agentic": {"pass": 3, "total": 5, "percentage": 60.0},
    #     ...
    # }
"""

from typing import Any


def aggregate(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate per-problem results into per-category and overall percentages.

    Args:
        results: A list of result dictionaries, each containing at minimum
            'problem_id', 'category', 'status', and 'score' keys.

    Returns:
        A dictionary with per-category summaries (pass/total/percentage) and
        an overall summary.

    Raises:
        NotImplementedError: This function is not yet implemented.
    """
    raise NotImplementedError("aggregate is not yet implemented")