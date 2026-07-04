"""Go language adapter for compiling and running Go solutions."""

from typing import Optional


class GoAdapter:
    """Adapter for compiling and executing Go candidate solutions."""

    def compile(self, source_path: str, output_path: str) -> dict:
        """Compile a Go source file into an executable.

        Args:
            source_path: Path to the .go source file.
            output_path: Path for the compiled binary.

        Returns:
            A dict with success status and compiler output.

        Raises:
            NotImplementedError: This method is not yet implemented.
        """
        raise NotImplementedError("GoAdapter.compile is not yet implemented")

    def run(self, executable_path: str, stdin: Optional[str] = None) -> dict:
        """Run a compiled Go executable.

        Args:
            executable_path: Path to the compiled binary.
            stdin: Optional stdin string.

        Returns:
            A dict with stdout, stderr, returncode, and runtime.

        Raises:
            NotImplementedError: This method is not yet implemented.
        """
        raise NotImplementedError("GoAdapter.run is not yet implemented")