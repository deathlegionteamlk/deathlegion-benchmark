"""Python language adapter for compiling and running Python solutions."""

import subprocess
import time
import os
from typing import Optional


class PythonAdapter:
    """Adapter for executing Python candidate solutions."""

    def compile(self, source_path: str, output_path: str) -> dict:
        """Prepare a Python solution for execution via syntax check.

        Runs python3 -m py_compile for syntax validation.

        Args:
            source_path: Path to the Python source file.
            output_path: Path where compiled artifacts would be placed.

        Returns:
            A dict with success status, compiler output, stderr, and returncode.
        """
        start = time.time()
        try:
            result = subprocess.run(
                ["python3", "-m", "py_compile", source_path],
                capture_output=True,
                text=True,
                timeout=30,
            )
            elapsed = time.time() - start
            if result.returncode == 0:
                # Copy .pyc to output_path
                pycache_dir = os.path.join(os.path.dirname(source_path), "__pycache__")
                if os.path.isdir(pycache_dir):
                    for f in os.listdir(pycache_dir):
                        if f.endswith(".pyc"):
                            dest = os.path.join(output_path, f) if output_path else source_path
                            break
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
                "stderr": "Compilation timed out after 30s",
                "returncode": -1,
                "runtime_s": 30.0,
            }

    def run(self, executable_path: str, stdin: Optional[str] = None) -> dict:
        """Run a Python solution.

        Args:
            executable_path: Path to the Python script.
            stdin: Optional stdin string.

        Returns:
            A dict with stdout, stderr, returncode, and runtime.
        """
        start = time.time()
        try:
            proc = subprocess.run(
                ["python3", executable_path],
                input=stdin,
                capture_output=True,
                text=True,
                timeout=60,
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
                "stderr": "Execution timed out after 60s",
                "returncode": -1,
                "timed_out": True,
                "runtime_s": 60.0,
            }