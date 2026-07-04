"""Java language adapter for compiling and running Java solutions."""

from typing import Optional


class JavaAdapter:
    """Adapter for compiling and executing Java candidate solutions."""

    def compile(self, source_path: str, output_path: str) -> dict:
        """Compile a Java source file into a .class file.

        Args:
            source_path: Path to the .java source file.
            output_path: Directory for compiled .class files.

        Returns:
            A dict with success status and compiler output.

        Raises:
            NotImplementedError: This method is not yet implemented.
        """
        raise NotImplementedError("JavaAdapter.compile is not yet implemented")

    def run(self, executable_path: str, stdin: Optional[str] = None) -> dict:
        """Run a compiled Java class.

        Args:
            executable_path: Path to the compiled .class file or class name.
            stdin: Optional stdin string.

        Returns:
            A dict with stdout, stderr, returncode, and runtime.

        Raises:
            NotImplementedError: This method is not yet implemented.
        """
        raise NotImplementedError("JavaAdapter.run is not yet implemented")