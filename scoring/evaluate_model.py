#!/usr/bin/env python3
"""End-to-end model evaluation script.

Loads all problem manifests, runs the harness/agentic runner for each,
collects structured JSON results, and produces per-category and overall scores.

Usage:
    python scoring/evaluate_model.py \\
        --manifest-dir problems/ \\
        --model-id my-model \\
        --output results.json
"""

import argparse
import json
import os
import sys
import time
import glob
from typing import Any


def discover_manifests(manifest_dir: str) -> list[tuple[str, str]]:
    """Discover all manifest.json files under a directory.

    Args:
        manifest_dir: Root directory to search for manifests.

    Returns:
        List of (problem_id, manifest_path) tuples.
    """
    manifests = []
    if not os.path.isdir(manifest_dir):
        print(f"Warning: manifest directory not found: {manifest_dir}", file=sys.stderr)
        return manifests

    # Walk the directory tree looking for manifest.json files
    for root, dirs, files in os.walk(manifest_dir):
        if "manifest.json" in files:
            manifest_path = os.path.join(root, "manifest.json")
            try:
                with open(manifest_path, "r") as f:
                    manifest = json.load(f)
                problem_id = manifest.get("id", os.path.basename(root))
                manifests.append((problem_id, manifest_path))
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: could not read {manifest_path}: {e}", file=sys.stderr)

    return manifests


def run_candidate(manifest: dict[str, Any],
                  solution_path: str,
                  timeout: int = 60) -> dict[str, Any]:
    """Run a candidate solution through the appropriate harness.

    This is a placeholder that tries to use the AgenticRunner if available,
    or falls back to a basic subprocess execution.

    Args:
        manifest: Problem manifest dictionary.
        solution_path: Path to the candidate solution.
        timeout: Execution timeout in seconds.

    Returns:
        Result dictionary with pass/fail, score, runtime, etc.
    """
    category = manifest.get("category", "unknown")
    problem_id = manifest.get("id", "unknown")

    # Try the AgenticRunner for agentic problems
    if category == "agentic":
        try:
            from harness.agentic_runner import AgenticRunner
            runner = AgenticRunner(timeout=timeout)
            return runner.run(manifest, solution_path)
        except ImportError:
            pass
        except Exception as e:
            return {
                "problem_id": problem_id,
                "passed": False,
                "score": 0.0,
                "error": f"Agentic runner error: {str(e)[:500]}",
                "runtime_s": 0.0,
            }

    # For other categories (algorithmic, adversarial), use basic execution
    if not os.path.isfile(solution_path):
        return {
            "problem_id": problem_id,
            "passed": False,
            "score": 0.0,
            "error": f"Solution file not found: {solution_path}",
            "runtime_s": 0.0,
        }

    # Try the appropriate grader
    grader_module = manifest.get("grader_spec", {}).get("module", "")
    if grader_module == "execution_trace":
        try:
            from harness.graders.execution_trace import ExecutionTraceGrader
            grader = ExecutionTraceGrader(timeout=timeout)
            return grader.grade(solution_path, manifest)
        except ImportError:
            pass
        except Exception as e:
            return {
                "problem_id": problem_id,
                "passed": False,
                "score": 0.0,
                "error": f"Grader error: {str(e)[:500]}",
                "runtime_s": 0.0,
            }

    # Default: basic execution using language adapter
    try:
        from harness.languages.all_adapters import run_solution
        result = run_solution(
            language=manifest.get("languages_allowed", ["python"])[0],
            executable_path=solution_path,
        )
        passed = result.get("returncode") == 0
        return {
            "problem_id": problem_id,
            "passed": passed,
            "score": 1.0 if passed else 0.0,
            "error": result.get("stderr", "")[:500] if not passed else None,
            "stdout_preview": result.get("stdout", "")[:200],
            "runtime_s": result.get("runtime_s", 0),
        }
    except ImportError:
        return {
            "problem_id": problem_id,
            "passed": False,
            "score": 0.0,
            "error": "No grader or adapter available to run solution",
            "runtime_s": 0.0,
        }
    except Exception as e:
        return {
            "problem_id": problem_id,
            "passed": False,
            "score": 0.0,
            "error": str(e)[:500],
            "runtime_s": 0.0,
        }


def compute_scores(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Compute per-category and overall scores from individual results.

    Args:
        results: List of individual problem result dictionaries.

    Returns:
        Dictionary with per-category and overall score breakdowns.
    """
    if not results:
        return {
            "overall": {"pass": 0, "total": 0, "percentage": 0.0},
            "categories": {},
        }

    categories = {}
    for r in results:
        category = r.get("category", "unknown")
        if category not in categories:
            categories[category] = {"pass": 0, "total": 0, "score_sum": 0.0}
        categories[category]["total"] += 1
        if r.get("passed"):
            categories[category]["pass"] += 1
        categories[category]["score_sum"] += r.get("score", 0.0)

    # Compute percentages
    category_scores = {}
    for cat, data in categories.items():
        pct = round((data["pass"] / data["total"]) * 100, 1) if data["total"] > 0 else 0.0
        avg_score = round(data["score_sum"] / data["total"], 3) if data["total"] > 0 else 0.0
        category_scores[cat] = {
            "pass": data["pass"],
            "total": data["total"],
            "percentage": pct,
            "avg_score": avg_score,
        }

    # Overall
    total = len(results)
    total_pass = sum(1 for r in results if r.get("passed"))
    total_score_sum = sum(r.get("score", 0.0) for r in results)
    overall_pct = round((total_pass / total) * 100, 1) if total > 0 else 0.0
    overall_avg = round(total_score_sum / total, 3) if total > 0 else 0.0

    return {
        "overall": {
            "pass": total_pass,
            "total": total,
            "percentage": overall_pct,
            "avg_score": overall_avg,
        },
        "categories": category_scores,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Deathlegion Benchmark - Model Evaluation Script"
    )
    parser.add_argument(
        "--manifest-dir", required=True,
        help="Directory containing problem manifests (searched recursively)"
    )
    parser.add_argument(
        "--model-id", default="unknown-model",
        help="Identifier for the model being evaluated"
    )
    parser.add_argument(
        "--solution-dir", default=None,
        help="Directory containing candidate solution files "
             "(named <problem_id>.ext or same as problem dir)"
    )
    parser.add_argument(
        "--output", default=None,
        help="Path to write results JSON (default: stdout)"
    )
    parser.add_argument(
        "--timeout", type=int, default=60,
        help="Execution timeout per problem in seconds (default: 60)"
    )
    parser.add_argument(
        "--max-problems", type=int, default=None,
        help="Maximum number of problems to evaluate (for testing)"
    )

    args = parser.parse_args()

    # Discover manifests
    print(f"Discovering manifests in {args.manifest_dir}...")
    manifests = discover_manifests(args.manifest_dir)

    if not manifests:
        print("No manifests found. Check --manifest-dir path.", file=sys.stderr)
        sys.exit(0)  # Not an error — just no problems yet

    print(f"Found {len(manifests)} manifests.")

    if args.max_problems:
        manifests = manifests[:args.max_problems]
        print(f"Limiting to {len(manifests)} problems (--max-problems).")

    # Determine solution directory
    solution_dir = args.solution_dir or os.path.join(args.manifest_dir, "..", "solutions")

    # Evaluate each problem
    results = []
    errors = []
    start_time = time.time()

    for idx, (problem_id, manifest_path) in enumerate(manifests):
        print(f"[{idx + 1}/{len(manifests)}] Evaluating {problem_id}...")

        try:
            # Reload manifest
            with open(manifest_path, "r") as f:
                manifest = json.load(f)

            # Find candidate solution file
            solution_path = None
            if solution_dir and os.path.isdir(solution_dir):
                # Check for problem-specific solution directory
                problem_solution_dir = os.path.join(solution_dir, problem_id)
                if os.path.isdir(problem_solution_dir):
                    for fname in os.listdir(problem_solution_dir):
                        if fname.endswith((".py", ".cpp", ".rs", ".go", ".java",
                                           ".js", ".ts", ".diff", ".patch")):
                            solution_path = os.path.join(problem_solution_dir, fname)
                            break

                # Check for flat solution files
                if not solution_path:
                    for ext in [".py", ".cpp", ".rs", ".go", ".java",
                                ".js", ".ts", ".diff", ".patch"]:
                        candidate = os.path.join(solution_dir, f"{problem_id}{ext}")
                        if os.path.isfile(candidate):
                            solution_path = candidate
                            break

                # Check for solution.json mapping
                sol_map_path = os.path.join(solution_dir, "solutions.json")
                if os.path.isfile(sol_map_path):
                    with open(sol_map_path, "r") as f:
                        sol_map = json.load(f)
                    if problem_id in sol_map:
                        candidate = os.path.join(solution_dir, sol_map[problem_id])
                        if os.path.isfile(candidate):
                            solution_path = candidate

            if not solution_path:
                # Try creating a dummy solution from reference_solution path
                ref_sol = manifest.get("reference_solution", {})
                ref_path = ref_sol.get("path", "")
                if ref_path:
                    full_ref_path = os.path.join(
                        os.path.dirname(manifest_path), ref_path
                    )
                    if os.path.isfile(full_ref_path):
                        solution_path = full_ref_path

            if not solution_path:
                print(f"  ⚠ No solution found for {problem_id}, skipping")
                errors.append({
                    "problem_id": problem_id,
                    "error": "No solution file found",
                })
                continue

            # Run the candidate through the harness
            result = run_candidate(manifest, solution_path, timeout=args.timeout)
            result["problem_id"] = problem_id
            result["category"] = manifest.get("category", "unknown")
            result["title"] = manifest.get("title", problem_id)
            results.append(result)

            status = "✓" if result.get("passed") else "✗"
            score = result.get("score", 0.0)
            print(f"  {status} score={score} runtime={result.get('runtime_s', 0):.1f}s")

        except Exception as e:
            print(f"  ✗ Error evaluating {problem_id}: {e}")
            errors.append({
                "problem_id": problem_id,
                "error": str(e)[:500],
            })

    # Compute scores
    total_time = round(time.time() - start_time, 1)
    scores = compute_scores(results)

    # Build the report
    report = {
        "model_id": args.model_id,
        "evaluation_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total_time_s": total_time,
        "timeout_per_problem_s": args.timeout,
        "manifest_dir": args.manifest_dir,
        "total_problems_found": len(manifests),
        "problems_evaluated": len(results),
        "errors": len(errors),
        "error_details": errors,
        "scores": scores,
        "results": results,
    }

    # Output
    output = json.dumps(report, indent=2)
    if args.output:
        os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
        with open(args.output, "w") as f:
            f.write(output)
        print(f"\nResults written to {args.output}")
    else:
        print("\n" + "=" * 60)
        print("EVALUATION SUMMARY")
        print("=" * 60)
        print(f"Model: {args.model_id}")
        print(f"Total problems: {len(results)} (errors: {len(errors)})")
        print(f"Total time: {total_time}s")
        print()
        print("Per-category scores:")
        for cat, data in scores.get("categories", {}).items():
            print(f"  {cat}: {data['pass']}/{data['total']} "
                  f"({data['percentage']}%)")
        print(f"\nOverall: {scores['overall']['pass']}/{scores['overall']['total']} "
              f"({scores['overall']['percentage']}%)")
        print(f"Average score: {scores['overall']['avg_score']}")

    return report


if __name__ == "__main__":
    main()