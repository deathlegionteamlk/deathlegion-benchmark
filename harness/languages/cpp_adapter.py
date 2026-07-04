"""C++ language adapter for compiling and running C++ solutions."""

from typing import Optional


class CppAdapter:
    """Adapter for compiling and executing C++ candidate solutions."""

    def compile(self, source_path: str, output_path: str) -> dict:
        """Compile a C++ source file into an executable.

        Args:
            source_path: Path to the .cpp source file.
            output_path: Path for the compiled binary.

        Returns:
            A dict with success status and compiler output.

        Raises:
            NotImplementedError: This method is not yet implemented.
        """
        raise NotImplementedError("CppAdapter.compile is not yet implemented")

    def run(self, executable_path: str, stdin: Optional[str] = None) -> dict:
        """Run a compiled C++ executable.

        Args:
            executable_path: Path to the compiled binary.
            stdin: Optional stdin string.

        Returns:
            A dict with stdout, stderr, returncode, and runtime.

        Raises:
            NotImplementedError: This method is not yet implemented.
        """
        raise NotImplementedError("CppAdapter.run is not yet implemented")