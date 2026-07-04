"""TypeScript language adapter for compiling and running TypeScript solutions."""

import subprocess
import time
import os
from typing import Optional


class TypeScriptAdapter:
    """Adapter for compiling and executing TypeScript candidate solutions."""

    def compile(self, source_path: str, output_path: str) -> dict:
        """Compile a TypeScript source file to JavaScript.

        Uses npx tsc --noEmit for type checking (no emit).

        Args:
            source_path: Path to the .ts source file.
            output_path: Path for the compiled .js output.

        Returns:
            A dict with success status and compiler output.
        """
        start = time.time()
        try:
            # Create a minimal tsconfig for the check
            tsconfig_dir = os.path.dirname(os.path.abspath(source_path))
            tsconfig_path = os.path.join(tsconfig_dir, "tsconfig.json")
            need_cleanup = False
            if not os.path.exists(tsconfig_path):
                with open(tsconfig_path, "w") as f:
                    f.write('{"compilerOptions":{"target":"ES2020","module":"commonjs","strict":true,"esModuleInterop":true}}')
                need_cleanup = True

            result = subprocess.run(
                ["npx", "tsc", "--noEmit", "--project", tsconfig_dir],
                capture_output=True,
                text=True,
                timeout=60,
            )
            elapsed = time.time() - start

            if need_cleanup:
                try:
                    os.remove(tsconfig_path)
                except OSError:
                    pass

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
                "stderr": "TypeScript compilation timed out after 60s",
                "returncode": -1,
                "runtime_s": 60.0,
            }

    def run(self, executable_path: str, stdin: Optional[str] = None) -> dict:
        """Run a TypeScript solution via ts-node.

        Args:
            executable_path: Path to the .ts source file.
            stdin: Optional stdin string.

        Returns:
            A dict with stdout, stderr, returncode, and runtime.
        """
        start = time.time()
        try:
            # Use --compiler-options to force CommonJS module output
            proc = subprocess.run(
                ["npx", "ts-node", "--compiler-options", '{"module":"commonjs"}', executable_path],
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