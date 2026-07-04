"""Unit tests for all 7 language adapters.

Tests that each adapter can compile and run a simple "hello world" program
and a stdin echo program, verifying exit code 0 and correct output.
"""

import os
import sys
import tempfile
import unittest

# Ensure the project root is on sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


class TestPythonAdapter(unittest.TestCase):
    """Tests for the Python language adapter."""

    def setUp(self):
        from harness.languages.python_adapter import PythonAdapter
        self.adapter = PythonAdapter()

    def test_compile_hello_world(self):
        """Test Python syntax check with a hello world program."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write('print("Hello, World!")\n')
            f.flush()
            source_path = f.name

        try:
            result = self.adapter.compile(source_path, "/tmp")
            self.assertTrue(result["success"], f"Compilation failed: {result.get('stderr')}")
            self.assertEqual(result["returncode"], 0)
        finally:
            os.unlink(source_path)

    def test_run_hello_world(self):
        """Test running a hello world Python program."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write('print("Hello, World!")\n')
            f.flush()
            source_path = f.name

        try:
            result = self.adapter.run(source_path)
            self.assertEqual(result["returncode"], 0, f"Run failed: {result.get('stderr')}")
            self.assertIn("Hello, World!", result["stdout"])
        finally:
            os.unlink(source_path)

    def test_run_with_stdin(self):
        """Test running a Python program that reads stdin."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write('import sys\nname = sys.stdin.read().strip()\nprint(f"Hello, {name}!")\n')
            f.flush()
            source_path = f.name

        try:
            result = self.adapter.run(source_path, stdin="Deathlegion")
            self.assertEqual(result["returncode"], 0, f"Run failed: {result.get('stderr')}")
            self.assertIn("Hello, Deathlegion!", result["stdout"])
        finally:
            os.unlink(source_path)


class TestCppAdapter(unittest.TestCase):
    """Tests for the C++ language adapter."""

    def setUp(self):
        from harness.languages.cpp_adapter import CppAdapter
        self.adapter = CppAdapter()

    def test_compile_and_run_hello_world(self):
        """Test compiling and running a hello world C++ program."""
        with tempfile.TemporaryDirectory() as tmpdir:
            source_path = os.path.join(tmpdir, "hello.cpp")
            binary_path = os.path.join(tmpdir, "hello")
            with open(source_path, "w") as f:
                f.write('#include <iostream>\nint main() { std::cout << "Hello, World!" << std::endl; return 0; }\n')

            # Compile
            comp_result = self.adapter.compile(source_path, binary_path)
            self.assertTrue(comp_result["success"], f"Compilation failed: {comp_result.get('stderr')}")
            self.assertTrue(os.path.exists(binary_path) or os.path.exists(binary_path + ".exe"))

            # Run
            run_path = binary_path if os.path.exists(binary_path) else binary_path + ".exe"
            if not os.path.exists(run_path):
                run_path = comp_result.get("binary_path", binary_path)
            run_result = self.adapter.run(run_path)
            self.assertEqual(run_result["returncode"], 0, f"Run failed: {run_result.get('stderr')}")
            self.assertIn("Hello, World!", run_result["stdout"])

    def test_compile_and_run_stdin_echo(self):
        """Test a C++ program that reads stdin."""
        with tempfile.TemporaryDirectory() as tmpdir:
            source_path = os.path.join(tmpdir, "echo.cpp")
            binary_path = os.path.join(tmpdir, "echo")
            with open(source_path, "w") as f:
                f.write('#include <iostream>\n#include <string>\nint main() { std::string name; std::getline(std::cin, name); std::cout << "Hello, " << name << "!" << std::endl; return 0; }\n')

            comp_result = self.adapter.compile(source_path, binary_path)
            self.assertTrue(comp_result["success"], f"Compilation failed: {comp_result.get('stderr')}")

            run_path = binary_path if os.path.exists(binary_path) else binary_path + ".exe"
            if not os.path.exists(run_path):
                run_path = comp_result.get("binary_path", binary_path)
            run_result = self.adapter.run(run_path, stdin="Deathlegion")
            self.assertEqual(run_result["returncode"], 0, f"Run failed: {run_result.get('stderr')}")
            self.assertIn("Hello, Deathlegion!", run_result["stdout"])


class TestRustAdapter(unittest.TestCase):
    """Tests for the Rust language adapter."""

    def setUp(self):
        from harness.languages.rust_adapter import RustAdapter
        self.adapter = RustAdapter()

    def test_compile_and_run_hello_world(self):
        """Test compiling and running a hello world Rust program."""
        with tempfile.TemporaryDirectory() as tmpdir:
            source_path = os.path.join(tmpdir, "hello.rs")
            binary_path = os.path.join(tmpdir, "hello_rust")
            with open(source_path, "w") as f:
                f.write('fn main() { println!("Hello, World!"); }\n')

            comp_result = self.adapter.compile(source_path, binary_path)
            self.assertTrue(comp_result["success"], f"Compilation failed: {comp_result.get('stderr')}")

            run_result = self.adapter.run(binary_path)
            self.assertEqual(run_result["returncode"], 0, f"Run failed: {run_result.get('stderr')}")
            self.assertIn("Hello, World!", run_result["stdout"])


class TestGoAdapter(unittest.TestCase):
    """Tests for the Go language adapter."""

    def setUp(self):
        from harness.languages.go_adapter import GoAdapter
        self.adapter = GoAdapter()

    def test_compile_and_run_hello_world(self):
        """Test compiling and running a hello world Go program."""
        with tempfile.TemporaryDirectory() as tmpdir:
            source_path = os.path.join(tmpdir, "hello.go")
            binary_path = os.path.join(tmpdir, "hello_go")
            with open(source_path, "w") as f:
                f.write('package main\nimport "fmt"\nfunc main() { fmt.Println("Hello, World!") }\n')

            comp_result = self.adapter.compile(source_path, binary_path)
            self.assertTrue(comp_result["success"], f"Compilation failed: {comp_result.get('stderr')}")

            run_result = self.adapter.run(binary_path)
            self.assertEqual(run_result["returncode"], 0, f"Run failed: {run_result.get('stderr')}")
            self.assertIn("Hello, World!", run_result["stdout"])


class TestJavaAdapter(unittest.TestCase):
    """Tests for the Java language adapter."""

    def setUp(self):
        from harness.languages.java_adapter import JavaAdapter
        self.adapter = JavaAdapter()

    def test_compile_and_run_hello_world(self):
        """Test compiling and running a hello world Java program."""
        with tempfile.TemporaryDirectory() as tmpdir:
            source_path = os.path.join(tmpdir, "HelloWorld.java")
            with open(source_path, "w") as f:
                f.write('public class HelloWorld {\n    public static void main(String[] args) {\n        System.out.println("Hello, World!");\n    }\n}\n')

            comp_result = self.adapter.compile(source_path, tmpdir)
            self.assertTrue(comp_result["success"], f"Compilation failed: {comp_result.get('stderr')}")

            # Run using class_dir:class_name format
            run_result = self.adapter.run(f"{tmpdir}:HelloWorld")
            self.assertEqual(run_result["returncode"], 0, f"Run failed: {run_result.get('stderr')}")
            self.assertIn("Hello, World!", run_result["stdout"])


class TestJavaScriptAdapter(unittest.TestCase):
    """Tests for the JavaScript language adapter."""

    def setUp(self):
        from harness.languages.javascript_adapter import JavaScriptAdapter
        self.adapter = JavaScriptAdapter()

    def test_compile_hello_world(self):
        """Test JavaScript syntax check."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False) as f:
            f.write('console.log("Hello, World!");\n')
            f.flush()
            source_path = f.name

        try:
            result = self.adapter.compile(source_path, "/tmp")
            self.assertTrue(result["success"], f"Syntax check failed: {result.get('stderr')}")
        finally:
            os.unlink(source_path)

    def test_run_hello_world(self):
        """Test running a hello world JavaScript program."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False) as f:
            f.write('console.log("Hello, World!");\n')
            f.flush()
            source_path = f.name

        try:
            result = self.adapter.run(source_path)
            self.assertEqual(result["returncode"], 0, f"Run failed: {result.get('stderr')}")
            self.assertIn("Hello, World!", result["stdout"])
        finally:
            os.unlink(source_path)

    def test_run_with_stdin(self):
        """Test running a JavaScript program that reads stdin."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False) as f:
            f.write('const fs = require("fs");\nconst input = fs.readFileSync("/dev/stdin", "utf8").trim();\nconsole.log(`Hello, ${input}!`);\n')
            f.flush()
            source_path = f.name

        try:
            result = self.adapter.run(source_path, stdin="Deathlegion")
            self.assertEqual(result["returncode"], 0, f"Run failed: {result.get('stderr')}")
            self.assertIn("Hello, Deathlegion!", result["stdout"])
        finally:
            os.unlink(source_path)


class TestTypeScriptAdapter(unittest.TestCase):
    """Tests for the TypeScript language adapter."""

    def setUp(self):
        from harness.languages.typescript_adapter import TypeScriptAdapter
        self.adapter = TypeScriptAdapter()

    def test_compile_and_run_hello_world(self):
        """Test TypeScript compilation and execution via ts-node."""
        with tempfile.TemporaryDirectory() as tmpdir:
            source_path = os.path.join(tmpdir, "hello.ts")
            with open(source_path, "w") as f:
                f.write('console.log("Hello, World!");\n')

            # Compile (type check)
            comp_result = self.adapter.compile(source_path, tmpdir)
            self.assertTrue(comp_result["success"], f"Type check failed: {comp_result.get('stderr')}")

            # Run via ts-node
            run_result = self.adapter.run(source_path)
            self.assertEqual(run_result["returncode"], 0, f"Run failed: {run_result.get('stderr')}")
            self.assertIn("Hello, World!", run_result["stdout"])


if __name__ == "__main__":
    unittest.main()