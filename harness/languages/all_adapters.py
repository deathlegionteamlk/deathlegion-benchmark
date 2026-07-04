"""Central adapter registry for all 7 supported languages.

Provides factory functions to compile and run candidate solutions
regardless of language, dispatching to the correct language-specific adapter.
"""

from typing import Optional

from .python_adapter import PythonAdapter
from .cpp_adapter import CppAdapter
from .rust_adapter import RustAdapter
from .go_adapter import GoAdapter
from .java_adapter import JavaAdapter
from .javascript_adapter import JavaScriptAdapter
from .typescript_adapter import TypeScriptAdapter


ADAPTER_MAP = {
    "python": PythonAdapter,
    "cpp": CppAdapter,
    "rust": RustAdapter,
    "go": GoAdapter,
    "java": JavaAdapter,
    "javascript": JavaScriptAdapter,
    "typescript": TypeScriptAdapter,
}


def get_adapter(language: str):
    """Get the language adapter instance for the given language.

    Args:
        language: One of 'python', 'cpp', 'rust', 'go', 'java',
                  'javascript', 'typescript'.

    Returns:
        An adapter instance with compile() and run() methods.

    Raises:
        ValueError: If the language is not supported.
    """
    if language not in ADAPTER_MAP:
        supported = ", ".join(sorted(ADAPTER_MAP.keys()))
        raise ValueError(f"Unsupported language '{language}'. Supported: {supported}")
    return ADAPTER_MAP[language]()


def compile_source(language: str, source_path: str, output_path: str = "") -> dict:
    """Compile a source file using the appropriate language adapter.

    Args:
        language: Programming language identifier.
        source_path: Path to the source file.
        output_path: Path for compiled output (optional, adapter may choose).

    Returns:
        Compilation result dict with success, stdout, stderr, returncode, runtime_s.
    """
    adapter = get_adapter(language)
    return adapter.compile(source_path, output_path)


def run_solution(
    language: str,
    executable_path: str,
    stdin: Optional[str] = None,
) -> dict:
    """Run a compiled solution using the appropriate language adapter.

    Args:
        language: Programming language identifier.
        executable_path: Path to the compiled binary or script.
        stdin: Optional stdin string.

    Returns:
        Execution result dict with stdout, stderr, returncode, timed_out, runtime_s.
    """
    adapter = get_adapter(language)
    return adapter.run(executable_path, stdin)