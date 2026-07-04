#!/usr/bin/env python3
"""SWE-bench-style agentic task runner.

Clones a Git repo, checks out the pre-fix commit SHA, runs a candidate
solution, measures the resulting diff patch, and compares it against the
ground-truth fix_merge_sha.

Usage:
    python -m harness.agentic_runner \\
        --manifest problems/agentic/some_problem/manifest.json \\
        --solution /path/to/candidate_patch.diff \\
        --timeout 60
"""

import argparse
import json
import os
import subprocess
import sys
import time
import tempfile
import shutil
from typing import Any, Optional


class AgenticRunner:
    """SWE-bench-style agentic task runner.

    Orchestrates the full agentic evaluation pipeline:
    1. Load and validate the problem manifest
    2. Clone the source repo at the pre-fix SHA
    3. Apply the candidate solution (patch or direct file)
    4. Measure the resulting patch via git diff
    5. Compare against the ground-truth fix_merge_sha
    6. Return structured evaluation results
    """

    def __init__(
        self,
        timeout: int = 120,
        memory_limit_mb: Optional[int] = None,
        work_dir: str = "/tmp",
    ):
        self.timeout = timeout
        self.memory_limit_mb = memory_limit_mb
        self.work_dir = work_dir

    def load_manifest(self, manifest_path: str) -> dict[str, Any]:
        """Load and validate a problem manifest.

        Args:
            manifest_path: Path to the manifest.json file.

        Returns:
            Parsed manifest dictionary.

        Raises:
            FileNotFoundError: If manifest doesn't exist.
            json.JSONDecodeError: If manifest isn't valid JSON.
        """
        if not os.path.isfile(manifest_path):
            raise FileNotFoundError(f"Manifest not found: {manifest_path}")

        with open(manifest_path, "r") as f:
            manifest = json.load(f)

        required_fields = ["id", "source_repo", "pre_fix_sha", "fix_merge_sha",
                           "files_touched", "category"]
        for field in required_fields:
            if field not in manifest:
                raise ValueError(f"Manifest missing required field: {field}")

        return manifest

    def clone_repo(self, repo_url: str, sha: str, target_dir: str) -> dict:
        """Clone a repository and checkout a specific commit.

        Args:
            repo_url: Git repository URL.
            sha: Commit SHA to checkout.
            target_dir: Local directory to clone into.

        Returns:
            Dict with success status and any error message.
        """
        start = time.time()
        try:
            # Try shallow clone first
            result = subprocess.run(
                ["git", "clone", "--depth", "1", repo_url, target_dir],
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": f"Clone failed: {result.stderr[:500]}",
                    "runtime_s": round(time.time() - start, 3),
                }

            # Checkout the specific SHA
            result = subprocess.run(
                ["git", "-C", target_dir, "checkout", sha],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode != 0:
                # Try fetching the specific commit
                fetch_cmd = ["git", "-C", target_dir, "fetch", "--depth", "1",
                             "origin", sha]
                subprocess.run(fetch_cmd, capture_output=True, text=True, timeout=60)
                result = subprocess.run(
                    ["git", "-C", target_dir, "checkout", sha],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

            return {
                "success": result.returncode == 0,
                "error": result.stderr[:500] if result.returncode != 0 else None,
                "runtime_s": round(time.time() - start, 3),
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Clone/checkout timed out after {self.timeout}s",
                "runtime_s": float(self.timeout),
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)[:500],
                "runtime_s": round(time.time() - start, 3),
            }

    def apply_candidate(self, repo_dir: str, solution_path: str,
                        files_touched: list[str]) -> dict:
        """Apply a candidate solution to the cloned repo.

        Supports two modes:
        - Direct file replacement: solution_path is a source file matching
          one of the files_touched.
        - Patch application: solution_path is a git diff patch.

        Args:
            repo_dir: Path to the cloned repository.
            solution_path: Path to the candidate solution (file or patch).
            files_touched: List of files the solution should modify.

        Returns:
            Dict with success status and details.
        """
        start = time.time()

        if not os.path.isfile(solution_path):
            return {
                "success": False,
                "error": f"Solution file not found: {solution_path}",
                "runtime_s": round(time.time() - start, 3),
            }

        with open(solution_path, "r") as f:
            content = f.read()

        # Detect if it's a patch file
        is_patch = content.startswith("diff ") or content.startswith("---")

        try:
            if is_patch:
                # Apply as a git patch
                result = subprocess.run(
                    ["git", "-C", repo_dir, "apply", "-"],
                    input=content,
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                return {
                    "success": result.returncode == 0,
                    "error": result.stderr[:500] if result.returncode != 0 else None,
                    "method": "patch",
                    "runtime_s": round(time.time() - start, 3),
                }
            else:
                # Direct file replacement — find the matching file in the repo
                filename = os.path.basename(solution_path)
                matched = False
                for touched_file in files_touched:
                    if os.path.basename(touched_file) == filename:
                        dest_path = os.path.join(repo_dir, touched_file)
                        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                        shutil.copy2(solution_path, dest_path)
                        matched = True
                        break

                if not matched:
                    # Try to find the file by just copying to matching path
                    for touched_file in files_touched:
                        dest_path = os.path.join(repo_dir, touched_file)
                        if os.path.exists(os.path.dirname(dest_path)):
                            shutil.copy2(solution_path, dest_path)
                            matched = True
                            break

                if not matched:
                    # Default: just copy to the first touched file path
                    if files_touched:
                        dest_path = os.path.join(repo_dir, files_touched[0])
                        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                        shutil.copy2(solution_path, dest_path)
                        matched = True

                return {
                    "success": True,
                    "error": None,
                    "method": "file_replace",
                    "runtime_s": round(time.time() - start, 3),
                }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Patch application timed out",
                "runtime_s": round(time.time() - start, 3),
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)[:500],
                "runtime_s": round(time.time() - start, 3),
            }

    def get_working_diff(self, repo_dir: str) -> dict:
        """Get the git diff of the working tree after applying the candidate.

        Args:
            repo_dir: Path to the cloned repository.

        Returns:
            Dict with diff_stat, diff_detail, modified_files list, and patch_size.
        """
        start = time.time()
        try:
            # Get diff stat
            stat_result = subprocess.run(
                ["git", "-C", repo_dir, "diff", "--stat"],
                capture_output=True,
                text=True,
                timeout=15,
            )
            diff_stat = stat_result.stdout

            # Get the full diff
            diff_result = subprocess.run(
                ["git", "-C", repo_dir, "diff"],
                capture_output=True,
                text=True,
                timeout=15,
            )
            diff_detail = diff_result.stdout

            # Parse modified files
            modified_files = []
            for line in diff_stat.strip().split("\n"):
                line = line.strip()
                if line and "|" in line:
                    parts = line.split("|")
                    if parts:
                        filename = parts[0].strip()
                        modified_files.append(filename)

            return {
                "success": True,
                "diff_stat": diff_stat,
                "diff_detail": diff_detail,
                "modified_files": modified_files,
                "patch_size_bytes": len(diff_detail),
                "runtime_s": round(time.time() - start, 3),
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Git diff timed out",
                "runtime_s": round(time.time() - start, 3),
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)[:500],
                "runtime_s": round(time.time() - start, 3),
            }

    def compare_with_ground_truth(self, repo_dir: str, fix_merge_sha: str) -> dict:
        """Compare the candidate's diff with the ground-truth fix merge SHA.

        Checks if the candidate's changes match the changes in the ground-truth
        commit by computing their intersection.

        Args:
            repo_dir: Path to the cloned repository.
            fix_merge_sha: The ground-truth fix merge commit SHA.

        Returns:
            Dict with comparison results.
        """
        start = time.time()
        try:
            # Verify the ground-truth SHA exists
            check_cmd = ["git", "-C", repo_dir, "cat-file", "-e", fix_merge_sha]
            check_result = subprocess.run(check_cmd, capture_output=True, text=True)

            if check_result.returncode != 0:
                return {
                    "success": False,
                    "error": f"Ground-truth SHA {fix_merge_sha} not found in repo",
                    "match": False,
                    "runtime_s": round(time.time() - start, 3),
                }

            # Get the candidate diff
            candidate_diff = subprocess.run(
                ["git", "-C", repo_dir, "diff"],
                capture_output=True,
                text=True,
                timeout=15,
            ).stdout

            # Get the ground-truth diff (diff between pre-fix parent and fix merge)
            parent_sha = fix_merge_sha + "^1"  # First parent
            ground_truth_diff = subprocess.run(
                ["git", "-C", repo_dir, "diff", parent_sha, fix_merge_sha],
                capture_output=True,
                text=True,
                timeout=15,
            ).stdout

            # Compare: check if candidate diff is a valid fix by measuring overlap
            candidate_lines = set(candidate_diff.split("\n"))
            ground_truth_lines = set(ground_truth_diff.split("\n"))

            # Lines that start with +/- are actual changes (excluding @@ headers)
            candidate_changes = {
                l for l in candidate_lines
                if l.startswith("+") or l.startswith("-")
            }
            ground_truth_changes = {
                l for l in ground_truth_lines
                if l.startswith("+") or l.startswith("-")
            }

            if not ground_truth_changes:
                return {
                    "success": True,
                    "match": False,
                    "error": "Ground-truth diff is empty",
                    "overlap_pct": 0.0,
                    "candidate_changes": len(candidate_changes),
                    "ground_truth_changes": 0,
                    "runtime_s": round(time.time() - start, 3),
                }

            overlap = candidate_changes & ground_truth_changes
            overlap_pct = round(
                len(overlap) / len(ground_truth_changes) * 100, 1
            )

            return {
                "success": True,
                "match": overlap_pct >= 80.0,  # 80% overlap = match
                "overlap_pct": overlap_pct,
                "candidate_changes": len(candidate_changes),
                "ground_truth_changes": len(ground_truth_changes),
                "overlapping_changes": len(overlap),
                "runtime_s": round(time.time() - start, 3),
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)[:500],
                "match": False,
                "runtime_s": round(time.time() - start, 3),
            }

    def run(self, manifest: dict[str, Any], solution_path: str) -> dict[str, Any]:
        """Execute the full agentic evaluation pipeline.

        Args:
            manifest: Problem manifest dictionary.
            solution_path: Path to the candidate solution file.

        Returns:
            Structured evaluation result with all pipeline steps.
        """
        total_start = time.time()

        source_repo = manifest["source_repo"]
        pre_fix_sha = manifest["pre_fix_sha"]
        fix_merge_sha = manifest["fix_merge_sha"]
        files_touched = manifest.get("files_touched", [])
        problem_id = manifest.get("id", "unknown")

        # Create a working directory
        repo_dir = tempfile.mkdtemp(prefix=f"agentic_{problem_id}_")

        try:
            # Step 1: Clone repo at pre-fix SHA
            clone_result = self.clone_repo(source_repo, pre_fix_sha, repo_dir)
            if not clone_result["success"]:
                return {
                    "problem_id": problem_id,
                    "passed": False,
                    "score": 0.0,
                    "error": f"Clone failed: {clone_result['error']}",
                    "steps": {"clone": clone_result},
                    "total_runtime_s": round(time.time() - total_start, 3),
                }

            # Step 2: Apply candidate solution
            apply_result = self.apply_candidate(repo_dir, solution_path, files_touched)
            if not apply_result["success"]:
                return {
                    "problem_id": problem_id,
                    "passed": False,
                    "score": 0.0,
                    "error": f"Apply failed: {apply_result['error']}",
                    "steps": {"clone": clone_result, "apply": apply_result},
                    "total_runtime_s": round(time.time() - total_start, 3),
                }

            # Step 3: Get the working diff
            diff_result = self.get_working_diff(repo_dir)
            if not diff_result["success"]:
                return {
                    "problem_id": problem_id,
                    "passed": False,
                    "score": 0.0,
                    "error": f"Diff failed: {diff_result['error']}",
                    "steps": {"clone": clone_result, "apply": apply_result,
                              "diff": diff_result},
                    "total_runtime_s": round(time.time() - total_start, 3),
                }

            # Step 4: Compare with ground-truth
            comparison = self.compare_with_ground_truth(repo_dir, fix_merge_sha)

            passed = comparison.get("match", False)
            score = 1.0 if passed else 0.0

            return {
                "problem_id": problem_id,
                "passed": passed,
                "score": score,
                "error": None,
                "steps": {
                    "clone": {
                        "success": clone_result["success"],
                        "runtime_s": clone_result.get("runtime_s", 0),
                    },
                    "apply": {
                        "success": apply_result["success"],
                        "method": apply_result.get("method", ""),
                        "runtime_s": apply_result.get("runtime_s", 0),
                    },
                    "diff": {
                        "success": diff_result["success"],
                        "modified_files": diff_result.get("modified_files", []),
                        "patch_size_bytes": diff_result.get("patch_size_bytes", 0),
                        "runtime_s": diff_result.get("runtime_s", 0),
                    },
                    "comparison": comparison,
                },
                "details_summary": (
                    f"Modified {len(diff_result.get('modified_files', []))} files, "
                    f"patch size {diff_result.get('patch_size_bytes', 0)} bytes, "
                    f"overlap {comparison.get('overlap_pct', 0)}% with ground truth"
                ),
                "total_runtime_s": round(time.time() - total_start, 3),
            }

        except Exception as e:
            return {
                "problem_id": problem_id,
                "passed": False,
                "score": 0.0,
                "error": f"Unexpected error: {str(e)[:500]}",
                "total_runtime_s": round(time.time() - total_start, 3),
            }
        finally:
            # Cleanup
            shutil.rmtree(repo_dir, ignore_errors=True)

    def evaluate(self, manifest_path: str, solution_path: str) -> dict[str, Any]:
        """Convenience method: load manifest, run evaluation.

        Args:
            manifest_path: Path to the manifest.json file.
            solution_path: Path to the candidate solution file.

        Returns:
            Structured evaluation result.
        """
        manifest = self.load_manifest(manifest_path)
        return self.run(manifest, solution_path)


def main():
    parser = argparse.ArgumentParser(
        description="Deathlegion Agentic Task Runner (SWE-bench style)"
    )
    parser.add_argument(
        "--manifest", required=True,
        help="Path to the problem manifest.json"
    )
    parser.add_argument(
        "--solution", required=True,
        help="Path to the candidate solution file (patch or source)"
    )
    parser.add_argument(
        "--timeout", type=int, default=120,
        help="Timeout in seconds for clone/checkout operations (default: 120)"
    )
    parser.add_argument(
        "--memory-limit", type=int, default=None,
        help="Memory limit in MB (not enforced on git operations)"
    )
    parser.add_argument(
        "--output", help="Path to write JSON results (default: stdout)"
    )

    args = parser.parse_args()

    runner = AgenticRunner(
        timeout=args.timeout,
        memory_limit_mb=args.memory_limit,
    )

    try:
        result = runner.evaluate(args.manifest, args.solution)
        output = json.dumps(result, indent=2)

        if args.output:
            with open(args.output, "w") as f:
                f.write(output)
            print(f"Results written to {args.output}")
        else:
            print(output)

        # Exit with appropriate code
        sys.exit(0 if result.get("passed") else 1)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()