"""Rust language adapter for compiling and running Rust solutions."""

import subprocess
import time
import os
from typing import Optional


class RustAdapter:
    """Adapter for compiling and executing Rust candidate solutions."""

    def compile(self, source_path: str, output_path: str) -> dict:
        """Compile a Rust source file into an executable.

        Uses rustc -O for optimized compilation.

        Args:
            source_path: Path to the .rs source file.
            output_path: Path for the compiled binary.

        Returns:
            A dict with success status, compiler output, stderr, and returncode.
        """
        if not output_path:
            output_path = source_path.replace(".rs", "")
        start = time.time()
        try:
            result = subprocess.run(
                ["rustc", "-O", "-o", output_path, source_path],
                capture_output=True,
                text=True,
                timeout=120,
            )
            elapsed = time.time() - start
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "runtime_s": round(elapsed, 3),
                "binary_path": output_path if result.returncode == 0 else None,
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": "Compilation timed out after 120s",
                "returncode": -1,
                "runtime_s": 120.0,
                "binary_path": None,
            }

    def run(self, executable_path: str, stdin: Optional[str] = None) -> dict:
        """Run a compiled Rust executable.

        Args:
            executable_path: Path to the compiled binary.
            stdin: Optional stdin string.

        Returns:
            A dict with stdout, stderr, returncode, and runtime.
        """
        start = time.time()
        try:
            proc = subprocess.run(
                [executable_path],
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