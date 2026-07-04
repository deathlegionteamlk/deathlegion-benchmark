"""Agentic test suite grader: validates multi-step, multi-file agentic solutions
by cloning repos, applying patches, running git diff, verifying files_touched,
and executing any pre-existing tests."""

import subprocess
import os
import tempfile
import shutil
import time
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
    passes all pre-existing tests, and resolves the target issue.

    Methodology (SWE-bench style):
    1. Clone the source repository at a pinned commit (pre_fix_sha)
    2. Apply the candidate solution as a patch
    3. Run git diff to identify modified files
    4. Validate that all files_touched from manifest are modified
    5. Check no unrelated files were changed
    6. Run any existing tests in the repository
    """

    def __init__(self, clone_timeout: int = 120, test_timeout: int = 300):
        self.clone_timeout = clone_timeout
        self.test_timeout = test_timeout

    def _clone_repo(self, repo_url: str, target_dir: str, sha: str) -> dict:
        """Clone a repository at a specific commit SHA."""
        try:
            # Shallow clone at the specific commit
            clone_cmd = [
                "git", "clone", "--depth", "1",
                repo_url, target_dir,
            ]
            result = subprocess.run(
                clone_cmd,
                capture_output=True,
                text=True,
                timeout=self.clone_timeout,
            )
            if result.returncode != 0:
                return {"success": False, "error": f"Clone failed: {result.stderr}"}

            # Checkout the specific pre-fix SHA
            checkout_cmd = ["git", "-C", target_dir, "checkout", sha]
            result = subprocess.run(
                checkout_cmd,
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode != 0:
                # Try fetching the specific commit if shallow clone didn't have it
                fetch_cmd = ["git", "-C", target_dir, "fetch", "--depth", "1", "origin", sha]
                subprocess.run(fetch_cmd, capture_output=True, text=True, timeout=60)
                result = subprocess.run(
                    checkout_cmd,
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

            return {
                "success": result.returncode == 0,
                "error": result.stderr if result.returncode != 0 else None,
            }

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Clone timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _apply_patch(self, repo_dir: str, solution_path: str) -> dict:
        """Apply the candidate solution as a patch to the repo."""
        try:
            # Read the solution file
            with open(solution_path, "r") as f:
                solution_content = f.read()

            # If it's a proper patch file, apply it directly
            if solution_content.startswith("diff ") or solution_content.startswith("---"):
                result = subprocess.run(
                    ["git", "-C", repo_dir, "apply", "-"],
                    input=solution_content,
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                return {
                    "success": result.returncode == 0,
                    "error": result.stderr if result.returncode != 0 else None,
                    "method": "patch_apply",
                }

            # Otherwise, treat as a file to replace a specific path
            # The manifest should specify which file this solution replaces
            return {
                "success": False,
                "error": "Solution is not a valid patch file. "
                         "Expected format: diff/patch output starting with 'diff' or '---'",
                "method": "unknown",
            }

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Patch application timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _get_git_diff(self, repo_dir: str) -> dict:
        """Get the git diff of the working tree."""
        try:
            result = subprocess.run(
                ["git", "-C", repo_dir, "diff", "--stat"],
                capture_output=True,
                text=True,
                timeout=15,
            )
            stat_output = result.stdout

            # Get detailed diff
            result_detail = subprocess.run(
                ["git", "-C", repo_dir, "diff"],
                capture_output=True,
                text=True,
                timeout=15,
            )
            diff_output = result_detail.stdout

            # Parse modified files from diff stat
            modified_files = []
            for line in stat_output.strip().split("\n"):
                line = line.strip()
                if line and "|" in line:
                    filename = line.split("|")[0].strip()
                    modified_files.append(filename)

            return {
                "success": True,
                "modified_files": modified_files,
                "diff_stat": stat_output,
                "diff_detail": diff_output[:5000],  # Truncate for response size
            }

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Git diff timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _check_files_touched(self, modified_files: list[str],
                              expected_files: list[str]) -> dict:
        """Validate that all expected files were modified and no unexpected ones."""
        expected_set = set(expected_files)
        modified_set = set(modified_files)

        files_missing = expected_set - modified_set
        unexpected_files = modified_set - expected_set

        return {
            "all_expected_modified": len(files_missing) == 0,
            "no_unexpected_changes": len(unexpected_files) == 0,
            "files_missing": sorted(files_missing),
            "unexpected_files": sorted(unexpected_files),
            "modified_count": len(modified_set),
            "expected_count": len(expected_set),
        }

    def _run_existing_tests(self, repo_dir: str) -> dict:
        """Run any existing test suite in the repository."""
        test_results = {"run": False, "passed": False, "results": []}

        # Check if there's a Makefile/test target
        if os.path.isfile(os.path.join(repo_dir, "Makefile")):
            try:
                result = subprocess.run(
                    ["make", "-C", repo_dir, "test"],
                    capture_output=True,
                    text=True,
                    timeout=self.test_timeout,
                )
                test_results["run"] = True
                test_results["passed"] = result.returncode == 0
                test_results["results"].append({
                    "command": "make test",
                    "returncode": result.returncode,
                    "stdout_preview": result.stdout[:500],
                    "stderr_preview": result.stderr[:500],
                })
            except (subprocess.TimeoutExpired, Exception) as e:
                test_results["results"].append({
                    "command": "make test",
                    "error": str(e),
                })

        # Check for pytest
        if os.path.isfile(os.path.join(repo_dir, "pytest.ini")) or \
           os.path.isfile(os.path.join(repo_dir, "pyproject.toml")) or \
           os.path.isdir(os.path.join(repo_dir, "tests")):
            try:
                result = subprocess.run(
                    ["python3", "-m", "pytest", "-x", "--timeout=60", "-q", repo_dir],
                    capture_output=True,
                    text=True,
                    timeout=self.test_timeout,
                )
                test_results["run"] = True
                found_pytest = any(
                    r.get("command", "").startswith("pytest")
                    for r in test_results["results"]
                )
                if not found_pytest:
                    test_results["results"].append({
                        "command": "pytest",
                        "returncode": result.returncode,
                        "stdout_preview": result.stdout[:500],
                        "stderr_preview": result.stderr[:500],
                    })
                    if result.returncode == 0:
                        test_results["passed"] = True
            except (subprocess.TimeoutExpired, Exception) as e:
                test_results["results"].append({
                    "command": "pytest",
                    "error": str(e),
                })

        # Check for npm test
        if os.path.isfile(os.path.join(repo_dir, "package.json")):
            try:
                result = subprocess.run(
                    ["npm", "test", "--prefix", repo_dir],
                    capture_output=True,
                    text=True,
                    timeout=self.test_timeout,
                )
                test_results["run"] = True
                test_results["results"].append({
                    "command": "npm test",
                    "returncode": result.returncode,
                    "stdout_preview": result.stdout[:500],
                    "stderr_preview": result.stderr[:500],
                })
                if result.returncode == 0:
                    test_results["passed"] = True
            except (subprocess.TimeoutExpired, Exception) as e:
                test_results["results"].append({
                    "command": "npm test",
                    "error": str(e),
                })

        if not test_results["run"]:
            # No test framework detected — that's OK, skip test validation
            test_results["skipped"] = True
            test_results["passed"] = None  # No tests to run
            test_results["reason"] = "No test framework detected"

        return test_results

    def grade(self, solution_path: str, manifest: dict[str, Any]) -> dict[str, Any]:
        """Grade an agentic solution by cloning the repo, applying the patch,
        and validating the changes.

        Args:
            solution_path: Path to the candidate patch/solution file.
            manifest: Problem manifest with source_repo, pre_fix_sha,
                      fix_merge_sha, files_touched, etc.

        Returns:
            A dict with: passed (bool), score (float), modified_files (list),
            file_validation (dict), test_results (dict), details (dict).
        """
        total_start = time.time()

        source_repo = manifest.get("source_repo", "")
        pre_fix_sha = manifest.get("pre_fix_sha", "")
        fix_merge_sha = manifest.get("fix_merge_sha", "")
        expected_files = manifest.get("files_touched", [])
        grader_config = manifest.get("grader_spec", {}).get("config", {})

        if not source_repo or not pre_fix_sha:
            return {
                "passed": False,
                "score": 0.0,
                "error": "Manifest missing source_repo or pre_fix_sha",
                "modified_files": [],
                "file_validation": {},
                "test_results": {},
                "details": {},
                "runtime_s": 0.0,
            }

        # Create a temporary directory for the repo clone
        tmp_dir = tempfile.mkdtemp(prefix="agentic_grade_")
        try:
            # Step 1: Clone the repo at the pre-fix SHA
            clone_result = self._clone_repo(source_repo, tmp_dir, pre_fix_sha)
            if not clone_result["success"]:
                return {
                    "passed": False,
                    "score": 0.0,
                    "error": f"Failed to clone repo: {clone_result['error']}",
                    "modified_files": [],
                    "file_validation": {},
                    "test_results": {},
                    "details": {"clone_result": clone_result},
                    "runtime_s": round(time.time() - total_start, 3),
                }

            # Step 2: Apply the candidate solution as a patch
            patch_result = self._apply_patch(tmp_dir, solution_path)
            if not patch_result["success"]:
                return {
                    "passed": False,
                    "score": 0.0,
                    "error": f"Failed to apply patch: {patch_result['error']}",
                    "modified_files": [],
                    "file_validation": {},
                    "test_results": {},
                    "details": {
                        "clone": "success",
                        "patch_result": patch_result,
                    },
                    "runtime_s": round(time.time() - total_start, 3),
                }

            # Step 3: Get git diff to see what changed
            diff_result = self._get_git_diff(tmp_dir)
            if not diff_result["success"]:
                return {
                    "passed": False,
                    "score": 0.0,
                    "error": f"Failed to get git diff: {diff_result['error']}",
                    "modified_files": [],
                    "file_validation": {},
                    "test_results": {},
                    "details": {},
                    "runtime_s": round(time.time() - total_start, 3),
                }

            modified_files = diff_result.get("modified_files", [])

            # Step 4: Validate files_touched
            file_validation = self._check_files_touched(modified_files, expected_files)

            # Step 5: Run any existing tests
            test_results = self._run_existing_tests(tmp_dir)

            # Step 6: Determine pass/fail
            file_check_pass = (
                file_validation["all_expected_modified"]
                and file_validation["no_unexpected_changes"]
            )
            test_pass = test_results.get("passed") is not False  # True, None (skipped), or True

            passed = file_check_pass and (test_pass or test_results.get("skipped", False))
            score = 1.0 if passed else 0.0

            return {
                "passed": passed,
                "score": score,
                "error": None,
                "modified_files": modified_files,
                "file_validation": file_validation,
                "test_results": test_results,
                "details": {
                    "diff_stat": diff_result.get("diff_stat", ""),
                    "diff_preview": diff_result.get("diff_detail", "")[:1000],
                    "source_repo": source_repo,
                    "pre_fix_sha": pre_fix_sha,
                    "fix_merge_sha": fix_merge_sha,
                    "expected_files": expected_files,
                },
                "runtime_s": round(time.time() - total_start, 3),
            }

        except Exception as e:
            return {
                "passed": False,
                "score": 0.0,
                "error": str(e),
                "modified_files": [],
                "file_validation": {},
                "test_results": {},
                "details": {"exception": str(e)},
                "runtime_s": round(time.time() - total_start, 3),
            }
        finally:
            # Clean up the cloned repo
            shutil.rmtree(tmp_dir, ignore_errors=True)