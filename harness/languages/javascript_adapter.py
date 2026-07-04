"""JavaScript language adapter for running JavaScript solutions (Node.js)."""

import subprocess
import time
from typing import Optional


class JavaScriptAdapter:
    """Adapter for executing JavaScript candidate solutions via Node.js."""

    def compile(self, source_path: str, output_path: str) -> dict:
        """Prepare a JavaScript solution for execution via syntax check.

        Uses node --check for syntax validation.

        Args:
            source_path: Path to the .js source file.
            output_path: Path for compiled/transpiled output (unused for JS).

        Returns:
            A dict with success status and any compilation output.
        """
        start = time.time()
        try:
            result = subprocess.run(
                ["node", "--check", source_path],
                capture_output=True,
                text=True,
                timeout=30,
            )
            elapsed = time.time() - start
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "runtime_s": round(elapsed, 3),
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": "Syntax check timed out after 30s",
                "returncode": -1,
                "runtime_s": 30.0,
            }

    def run(self, executable_path: str, stdin: Optional[str] = None) -> dict:
        """Run a JavaScript solution via Node.js.

        Args:
            executable_path: Path to the .js script.
            stdin: Optional stdin string.

        Returns:
            A dict with stdout, stderr, returncode, and runtime.
        """
        start = time.time()
        try:
            proc = subprocess.run(
                ["node", executable_path],
                input=stdin,
                capture_output=True,
                text=True,
                timeout=30,
            )
            elapsed = time.time() - start
            return {
                "stdout": proc.stdout,
                "stderr": proc.stderr,
                "returncode": proc.returncode,
                "timed_out": False,
                "runtime_s": round(elapsed, 3),
            }
        except subprocess.TimeoutExpired:
            return {
                "stdout": "",
                "stderr": "Execution timed out after 30s",
                "returncode": -1,
                "timed_out": True,
                "runtime_s": 30.0,
            }