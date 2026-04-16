#!/usr/bin/env python3
"""
Unit tests for tools/test_generator.py

MIT License
Copyright (c) 2024 Nrupal Akolkar
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tools.test_generator import TestGenerator, generate_test_content, parse_python_file


class TestParsePythonFile:
    def test_parse_simple_function(self):
        code = '''
def hello():
    """Say hello."""
    print("Hello")
'''
        result = parse_python_file(code)
        
        assert len(result["functions"]) == 1
        assert result["functions"][0]["name"] == "hello"
        assert result["functions"][0]["docstring"] == "Say hello."

    def test_parse_class_with_methods(self):
        code = '''
class Calculator:
    """A simple calculator."""
    
    def add(self, a, b):
        """Add two numbers."""
        return a + b
    
    def subtract(self, a, b):
        """Subtract two numbers."""
        return a - b
    
    def _private(self):
        """Private method - should be excluded."""
        pass
'''
        result = parse_python_file(code)
        
        assert len(result["classes"]) == 1
        assert result["classes"][0]["name"] == "Calculator"
        assert len(result["classes"][0]["methods"]) == 2

    def test_parse_empty_code(self):
        result = parse_python_file("")
        assert result["functions"] == []
        assert result["classes"] == []

    def test_parse_code_with_imports(self):
        code = '''
import os
from pathlib import Path
import json

def func():
    pass
'''
        result = parse_python_file(code)
        assert "os" in result["imports"]
        assert "pathlib" in result["imports"] or "Path" in result["imports"]


class TestGenerateTestContent:
    def test_generate_simple_function_test(self):
        functions = [
            {
                "name": "add",
                "docstring": "Add two numbers.",
                "params": ["a: int", "b: int"],
                "return_type": "int"
            }
        ]
        
        result = generate_test_content(functions, [])
        
        assert "def test_add" in result
        assert "add" in result

    def test_generate_class_test(self):
        classes = [
            {
                "name": "Calculator",
                "docstring": "A calculator class.",
                "methods": [
                    {
                        "name": "add",
                        "docstring": "Add numbers.",
                        "params": ["self", "a: int", "b: int"]
                    }
                ]
            }
        ]
        
        result = generate_test_content([], classes)
        
        assert "class TestCalculator" in result
        assert "test_add" in result

    def test_generate_mocks_imports(self):
        code = '''
import pytest
from unittest.mock import Mock, patch
'''
        result = generate_test_content([], [], code)
        
        assert "pytest" in result
        assert "Mock" in result


class TestTestGenerator:
    @pytest.fixture
    def temp_dir(self):
        tmpdir = tempfile.mkdtemp()
        yield Path(tmpdir)
        import shutil
        shutil.rmtree(tmpdir, ignore_errors=True)

    def test_generator_creation(self):
        generator = TestGenerator()
        assert generator.output_dir == Path("tests/generated")

    def test_generator_custom_output_dir(self, temp_dir):
        generator = TestGenerator(output_dir=temp_dir)
        assert generator.output_dir == temp_dir

    def test_generate_test_for_file(self, temp_dir):
        source_file = temp_dir / "calculator.py"
        source_file.write_text('''
def add(a, b):
    """Add two numbers."""
    return a + b

def subtract(a, b):
    """Subtract two numbers."""
    return a - b

class Calculator:
    """A calculator class."""
    
    def multiply(self, a, b):
        """Multiply two numbers."""
        return a * b
''')

        generator = TestGenerator(output_dir=temp_dir / "tests")
        result = generator.generate_test_for_file(source_file)

        assert result is not None
        assert "test_add" in result
        assert "test_subtract" in result
        assert "TestCalculator" in result

    def test_generate_all_tests(self, temp_dir):
        source_dir = temp_dir / "src"
        source_dir.mkdir()
        
        (source_dir / "module.py").write_text('''
def func():
    """A function."""
    pass
''')

        generator = TestGenerator(output_dir=temp_dir / "tests")
        results = generator.generate_all_tests(source_dir)

        assert len(results) > 0

    def test_run_generated_tests(self, temp_dir):
        test_file = temp_dir / "test_sample.py"
        test_file.write_text('''
import pytest

def test_placeholder():
    """A placeholder test."""
    assert True
''')

        generator = TestGenerator(output_dir=temp_dir)
        results = generator.run_tests(temp_dir)

        assert "test_sample.py" in results
        assert results["test_sample.py"]["passed"] >= 0

    def test_run_tests_with_failures(self, temp_dir):
        test_file = temp_dir / "test_failing.py"
        test_file.write_text('''
import pytest

def test_failure():
    """A failing test."""
    assert False, "This test should fail"
''')

        generator = TestGenerator(output_dir=temp_dir)
        results = generator.run_tests(temp_dir)

        assert "test_failing.py" in results
        assert results["test_failing.py"]["failed"] >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
