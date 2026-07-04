"""TypeScript language adapter for compiling and running TypeScript solutions."""

from typing import Optional


class TypeScriptAdapter:
    """Adapter for compiling and executing TypeScript candidate solutions."""

    def compile(self, source_path: str, output_path: str) -> dict:
        """Compile a TypeScript source file to JavaScript.

        Args:
            source_path: Path to the .ts source file.
            output_path: Path for the compiled .js output.

        Returns:
            A dict with success status and compiler output.

        Raises:
            NotImplementedError: This method is not yet implemented.
        """
        raise NotImplementedError("TypeScriptAdapter.compile is not yet implemented")

    def run(self, executable_path: str, stdin: Optional[str] = None) -> dict:
        """Run a compiled TypeScript (JavaScript) solution via Node.js.

        Args:
            executable_path: Path to the compiled .js script.
            stdin: Optional stdin string.

        Returns:
            A dict with stdout, stderr, returncode, and runtime.

        Raises:
            NotImplementedError: This method is not yet implemented.
        """
        raise NotImplementedError("TypeScriptAdapter.run is not yet implemented")