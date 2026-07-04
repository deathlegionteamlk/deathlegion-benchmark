"""Java language adapter for compiling and running Java solutions."""

import subprocess
import time
import os
from typing import Optional


class JavaAdapter:
    """Adapter for compiling and executing Java candidate solutions."""

    def _get_class_name(self, source_path: str) -> str:
        """Extract the public class name from a Java source file."""
        with open(source_path, "r") as f:
            for line in f:
                if line.strip().startswith("public class "):
                    return line.strip().split("public class ")[1].split()[0].split("{")[0].strip()
        # Fallback: use filename without .java
        return os.path.splitext(os.path.basename(source_path))[0]

    def compile(self, source_path: str, output_path: str) -> dict:
        """Compile a Java source file into a .class file.

        Uses javac -d for compilation.

        Args:
            source_path: Path to the .java source file.
            output_path: Directory for compiled .class files.

        Returns:
            A dict with success status, compiler output, stderr, and returncode.
        """
        if not output_path:
            output_path = os.path.dirname(source_path)
        os.makedirs(output_path, exist_ok=True)
        start = time.time()
        try:
            result = subprocess.run(
                ["javac", "-d", output_path, source_path],
                capture_output=True,
                text=True,
                timeout=60,
            )
            elapsed = time.time() - start
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "runtime_s": round(elapsed, 3),
                "class_dir": output_path if result.returncode == 0 else None,
                "class_name": self._get_class_name(source_path) if result.returncode == 0 else None,
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": "Compilation timed out after 60s",
                "returncode": -1,
                "runtime_s": 60.0,
                "class_dir": None,
                "class_name": None,
            }

    def run(self, executable_path: str, stdin: Optional[str] = None) -> dict:
        """Run a compiled Java class.

        executable_path should be the directory containing .class files.
        The class name is derived from the executable_path basename or the
        compilation result.

        Args:
            executable_path: Path to the directory with .class files, or
                             a colon-separated "class_dir:class_name" string.
            stdin: Optional stdin string.

        Returns:
            A dict with stdout, stderr, returncode, and runtime.
        """
        class_dir = executable_path
        class_name = None

        if ":" in executable_path:
            parts = executable_path.split(":", 1)
            class_dir = parts[0]
            class_name = parts[1]

        if not class_name:
            # Try to find a .class file in the directory
            if os.path.isdir(class_dir):
                for f in os.listdir(class_dir):
                    if f.endswith(".class") and not f.endswith("$1.class"):
                        class_name = f.replace(".class", "")
                        break

        if not class_name:
            return {
                "stdout": "",
                "stderr": "Could not determine class name from path",
                "returncode": -1,
                "timed_out": False,
                "runtime_s": 0.0,
            }

        start = time.time()
        try:
            proc = subprocess.run(
                ["java", "-cp", class_dir, class_name],
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