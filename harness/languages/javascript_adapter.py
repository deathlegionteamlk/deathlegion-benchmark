"""JavaScript language adapter for running JavaScript solutions (Node.js)."""

from typing import Optional


class JavaScriptAdapter:
    """Adapter for executing JavaScript candidate solutions via Node.js."""

    def compile(self, source_path: str, output_path: str) -> dict:
        """Prepare a JavaScript solution for execution.

        For JavaScript, this may involve syntax checking or transpilation.

        Args:
            source_path: Path to the .js source file.
            output_path: Path for compiled/transpiled output.

        Returns:
            A dict with success status and any compilation output.

        Raises:
            NotImplementedError: This method is not yet implemented.
        """
        raise NotImplementedError("JavaScriptAdapter.compile is not yet implemented")

    def run(self, executable_path: str, stdin: Optional[str] = None) -> dict:
        """Run a JavaScript solution via Node.js.

        Args:
            executable_path: Path to the .js script.
            stdin: Optional stdin string.

        Returns:
            A dict with stdout, stderr, returncode, and runtime.

        Raises:
            NotImplementedError: This method is not yet implemented.
        """
        raise NotImplementedError("JavaScriptAdapter.run is not yet implemented")