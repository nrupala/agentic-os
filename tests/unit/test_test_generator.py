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

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tools.test_generator import TestGenerator, FunctionSignature, ClassInfo


class TestFunctionSignature:
    def test_function_signature_creation(self):
        sig = FunctionSignature(
            name="test_func",
            args=["a", "b"],
            arg_types=["int", "str"],
            returns="bool",
            decorators=["@staticmethod"],
            docstring="Test function"
        )
        
        assert sig.name == "test_func"
        assert len(sig.args) == 2
        assert sig.returns == "bool"

    def test_function_signature_defaults(self):
        sig = FunctionSignature(
            name="test_func",
            args=[],
            arg_types=[],
            returns="None"
        )
        
        assert sig.decorators == []
        assert sig.docstring is None


class TestClassInfo:
    def test_class_info_creation(self):
        func = FunctionSignature(name="method", args=["self"], arg_types=[], returns="None")
        cls = ClassInfo(
            name="TestClass",
            bases=["object"],
            methods=[func],
            docstring="Test class"
        )
        
        assert cls.name == "TestClass"
        assert len(cls.methods) == 1
        assert cls.docstring == "Test class"

    def test_class_info_empty_methods(self):
        cls = ClassInfo(name="Test", bases=[], methods=[])
        
        assert len(cls.methods) == 0


class TestTestGenerator:
    @pytest.fixture
    def temp_dir(self):
        tmpdir = tempfile.mkdtemp()
        yield Path(tmpdir)
    
    @pytest.fixture
    def sample_file(self, temp_dir):
        file_path = temp_dir / "sample.py"
        file_path.write_text('''
"""Sample module for testing."""

def hello():
    """Say hello."""
    print("Hello")

class Calculator:
    """A simple calculator."""
    
    def add(self, a, b):
        """Add two numbers."""
        return a + b
    
    def subtract(self, a, b):
        return a - b
''')
        return file_path

    def test_test_generator_creation(self, sample_file):
        generator = TestGenerator(str(sample_file))
        
        assert generator.source_path == sample_file
        assert generator.module_name == "sample"

    def test_analyze_extraction(self, sample_file):
        generator = TestGenerator(str(sample_file))
        generator.analyze()
        
        assert "Calculator" in generator.classes
        assert len(generator.functions) >= 1

    def test_extract_classes(self, sample_file):
        generator = TestGenerator(str(sample_file))
        generator.analyze()
        
        calc = generator.classes.get("Calculator")
        assert calc is not None
        assert calc.docstring == "A simple calculator."
        assert len(calc.methods) == 2

    def test_extract_functions(self, sample_file):
        generator = TestGenerator(str(sample_file))
        generator.analyze()
        
        func_names = [f.name for f in generator.functions]
        assert "hello" in func_names

    def test_extract_imports(self, temp_dir):
        test_file = temp_dir / "imports.py"
        test_file.write_text('''
import os
import sys
from pathlib import Path
''')
        
        generator = TestGenerator(str(test_file))
        generator.analyze()
        
        assert "os" in generator.imports
        assert "sys" in generator.imports
        assert "pathlib" in generator.imports

    def test_generate_tests_output(self, sample_file):
        generator = TestGenerator(str(sample_file))
        generator.analyze()
        
        output = generator.generate()
        
        assert len(output) > 0
        assert "Calculator" in output

    def test_generate_test_methods(self, sample_file):
        generator = TestGenerator(str(sample_file))
        generator.analyze()
        
        output = generator.generate()
        
        assert len(output) > 0