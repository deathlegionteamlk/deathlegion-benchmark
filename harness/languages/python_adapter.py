"""Python language adapter for compiling and running Python solutions."""

from typing import Optional


class PythonAdapter:
    """Adapter for executing Python candidate solutions."""

    def compile(self, source_path: str, output_path: str) -> dict:
        """Prepare a Python solution for execution.

        For Python, compilation is typically a syntax check or bytecode
        compilation. Most solutions run directly without a separate compile step.

        Args:
            source_path: Path to the Python source file.
            output_path: Path where compiled artifacts would be placed.

        Returns:
            A dict with success status and any compilation output.

        Raises:
            NotImplementedError: This method is not yet implemented.
        """
        raise NotImplementedError("PythonAdapter.compile is not yet implemented")

    def run(self, executable_path: str, stdin: Optional[str] = None) -> dict:
        """Run a Python solution.

        Args:
            executable_path: Path to the Python script or compiled artifact.
            stdin: Optional stdin string.

        Returns:
            A dict with stdout, stderr, returncode, and runtime.

        Raises:
            NotImplementedError: This method is not yet implemented.
        """
        raise NotImplementedError("PythonAdapter.run is not yet implemented")