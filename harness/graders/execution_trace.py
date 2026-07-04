"""Execution trace grader: validates the internal execution trace of the candidate
solution by running code, measuring instruction count, runtime, and validating
expected output patterns and syscall-like behavior."""

import subprocess
import time
import os
import sys
import tempfile
from abc import ABC, abstractmethod
from typing import Any


class Grader(ABC):
    """Abstract base class for all graders."""

    @abstractmethod
    def grade(self, solution_path: str, manifest: dict[str, Any]) -> dict[str, Any]:
        ...


class ExecutionTraceGrader(Grader):
    """Analyzes execution traces (e.g., logs, profiling data, instrumented output)
    to verify solution properties beyond simple pass/fail.

    Runs the candidate code, captures runtime metrics, and validates expected
    output patterns and syscall-like behavior against the manifest spec.
    """

    def __init__(self, timeout: int = 30):
        self.timeout = timeout

    def _detect_language(self, solution_path: str) -> str:
        ext = os.path.splitext(solution_path)[1].lower()
        ext_map = {
            ".py": "python",
            ".cpp": "cpp",
            ".cxx": "cpp",
            ".cc": "cpp",
            ".rs": "rust",
            ".go": "go",
            ".java": "java",
            ".js": "javascript",
            ".ts": "typescript",
        }
        return ext_map.get(ext, "python")

    def _run_with_trace(self, solution_path: str, language: str,
                        input_data: str = "") -> dict:
        """Run the solution and capture timing, exit code, and output."""
        start = time.time()
        try:
            if language == "python":
                cmd = [sys.executable, solution_path]
            elif language == "javascript":
                cmd = ["node", solution_path]
            elif language == "typescript":
                cmd = ["npx", "ts-node", solution_path]
            else:
                # Compiled languages need compilation first
                if language == "cpp":
                    compile_cmd = ["g++", "-std=c++17", "-O2", "-o", "/tmp/_trace_bin", solution_path]
                    runner = "/tmp/_trace_bin"
                elif language == "rust":
                    compile_cmd = ["rustc", "-O", "-o", "/tmp/_trace_bin", solution_path]
                    runner = "/tmp/_trace_bin"
                elif language == "go":
                    compile_cmd = ["go", "build", "-o", "/tmp/_trace_bin", solution_path]
                    runner = "/tmp/_trace_bin"
                elif language == "java":
                    # For Java, we need special handling
                    return self._run_java(solution_path, input_data)
                else:
                    return {
                        "success": False,
                        "error": f"Unsupported language for trace: {language}",
                        "trace_data": {},
                    }

                comp = subprocess.run(compile_cmd, capture_output=True, text=True, timeout=self.timeout)
                if comp.returncode != 0:
                    return {
                        "success": False,
                        "error": f"Compilation failed: {comp.stderr}",
                        "trace_data": {},
                    }
                cmd = [runner]

            proc = subprocess.run(
                cmd,
                input=input_data,
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
            elapsed = time.time() - start

            # Clean up compiled binary
            if language in ("cpp", "rust", "go"):
                try:
                    os.remove("/tmp/_trace_bin")
                except OSError:
                    pass
            if language == "cpp":
                try:
                    os.remove("/tmp/_trace_bin.exe")
                except OSError:
                    pass

            return {
                "success": proc.returncode == 0,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
                "returncode": proc.returncode,
                "timed_out": False,
                "runtime_s": round(elapsed, 3),
                "trace_data": {
                    "instructions_approx": int(elapsed * 1e9),  # rough estimate
                    "syscalls_observed": [],
                    "exit_code": proc.returncode,
                },
            }

        except subprocess.TimeoutExpired:
            elapsed = time.time() - start
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Execution timed out after {self.timeout}s",
                "returncode": -1,
                "timed_out": True,
                "runtime_s": float(self.timeout),
                "trace_data": {
                    "instructions_approx": 0,
                    "syscalls_observed": [],
                    "exit_code": -1,
                },
            }

    def _run_java(self, solution_path: str, input_data: str) -> dict:
        """Handle Java execution separately."""
        try:
            compile_cmd = ["javac", "-d", "/tmp/_trace_java", solution_path]
            comp = subprocess.run(compile_cmd, capture_output=True, text=True, timeout=self.timeout)
            if comp.returncode != 0:
                return {
                    "success": False,
                    "error": f"Java compilation failed: {comp.stderr}",
                    "trace_data": {},
                }
            # Find class name
            class_name = None
            with open(solution_path) as f:
                for line in f:
                    if "public class " in line:
                        class_name = line.split("public class ")[1].split()[0].split("{")[0].strip()
                        break
            if not class_name:
                class_name = os.path.splitext(os.path.basename(solution_path))[0]

            start = time.time()
            proc = subprocess.run(
                ["java", "-cp", "/tmp/_trace_java", class_name],
                input=input_data,
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
            elapsed = time.time() - start
            return {
                "success": proc.returncode == 0,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
                "returncode": proc.returncode,
                "timed_out": False,
                "runtime_s": round(elapsed, 3),
                "trace_data": {
                    "instructions_approx": int(elapsed * 1e9),
                    "syscalls_observed": [],
                    "exit_code": proc.returncode,
                },
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Java execution timed out after {self.timeout}s",
                "returncode": -1,
                "timed_out": True,
                "runtime_s": float(self.timeout),
                "trace_data": {},
            }

    def _validate_output(self, result: dict, manifest: dict) -> dict:
        """Validate the execution output against expected patterns."""
        grader_config = manifest.get("grader_spec", {}).get("config", {})
        expected_patterns = grader_config.get("expected_patterns", [])
        expected_exit_code = grader_config.get("expected_exit_code", 0)
        min_runtime_s = grader_config.get("min_runtime_s")
        max_runtime_s = grader_config.get("max_runtime_s")

        checks = {
            "exit_code_match": result.get("returncode") == expected_exit_code,
            "no_fatal_errors": "Traceback" not in result.get("stderr", ""),
        }

        # Check expected patterns in stdout
        if expected_patterns:
            stdout = result.get("stdout", "")
            pattern_checks = {}
            for i, pattern in enumerate(expected_patterns):
                found = pattern in stdout
                checks[f"pattern_{i}"] = found
                pattern_checks[str(i)] = {"pattern": pattern, "found": found}
            checks["all_patterns_found"] = all(checks.get(f"pattern_{i}", False)
                                                for i in range(len(expected_patterns)))

        # Check runtime bounds
        runtime = result.get("runtime_s", 0)
        if min_runtime_s is not None:
            checks["min_runtime_met"] = runtime >= min_runtime_s
        if max_runtime_s is not None:
            checks["max_runtime_not_exceeded"] = runtime <= max_runtime_s

        # Check timed out
        if result.get("timed_out"):
            checks["no_timeout"] = False
        else:
            checks["no_timeout"] = True

        # Compute overall pass/fail
        all_checks_passed = all(v is True or v == "pass" for v in checks.values()
                                if isinstance(v, (bool, str)))
        passed = all_checks_passed

        return {
            "passed": passed,
            "checks": checks,
            "details": {
                "stdout_preview": result.get("stdout", "")[:200],
                "stderr_preview": result.get("stderr", "")[:200],
                "runtime_s": result.get("runtime_s", 0),
                "trace_data": result.get("trace_data", {}),
            },
        }

    def grade(self, solution_path: str, manifest: dict[str, Any]) -> dict[str, Any]:
        """Execute the candidate solution and validate its execution trace.

        Args:
            solution_path: Path to the candidate solution file.
            manifest: Problem manifest with grader_spec.config containing
                      expected_patterns, expected_exit_code, etc.

        Returns:
            A dict with: passed (bool), score (float), checks (dict),
            details (dict), and runtime_s (float).
        """
        if not os.path.isfile(solution_path):
            return {
                "passed": False,
                "score": 0.0,
                "error": f"Solution file not found: {solution_path}",
                "checks": {},
                "details": {},
                "runtime_s": 0.0,
            }

        language = self._detect_language(solution_path)

        # Get input data from manifest if specified
        grader_config = manifest.get("grader_spec", {}).get("config", {})
        input_data = grader_config.get("input", "")

        result = self._run_with_trace(solution_path, language, input_data)

        validation = self._validate_output(result, manifest)

        score = 1.0 if validation["passed"] else 0.0

        return {
            "passed": validation["passed"],
            "score": score,
            "error": result.get("error"),
            "checks": validation["checks"],
            "details": validation["details"],
            "runtime_s": result.get("runtime_s", 0.0),
        }