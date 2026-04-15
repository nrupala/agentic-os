import ast
import re
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field


@dataclass
class FunctionSignature:
    name: str
    args: List[str]
    arg_types: List[str]
    returns: str
    decorators: List[str] = field(default_factory=list)
    docstring: Optional[str] = None


@dataclass
class ClassInfo:
    name: str
    bases: List[str]
    methods: List[FunctionSignature]
    docstring: Optional[str] = None


class TestGenerator:
    """Auto-generate pytest tests from Python source code."""

    def __init__(self, source_path: str):
        self.source_path = Path(source_path)
        self.source_code = self.source_path.read_text(encoding='utf-8')
        self.tree = ast.parse(self.source_code)
        self.module_name = self.source_path.stem
        self.imports: Set[str] = set()
        self.classes: Dict[str, ClassInfo] = {}
        self.functions: List[FunctionSignature] = []

    def analyze(self) -> 'TestGenerator':
        """Analyze source code and extract metadata."""
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.imports.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    self.imports.add(node.module)
            elif isinstance(node, ast.ClassDef):
                class_info = self._extract_class(node)
                self.classes[node.name] = class_info
            elif isinstance(node, ast.FunctionDef) and not isinstance(node, ast.AsyncFunctionDef):
                if not self._is_method(node):
                    func_sig = self._extract_function(node)
                    self.functions.append(func_sig)
        return self

    def _is_method(self, node: ast.FunctionDef) -> bool:
        """Check if function is a class method."""
        return hasattr(node, 'parent') and isinstance(node.parent, (ast.ClassDef, ast.AsyncFunctionDef))

    def _extract_function(self, node: ast.FunctionDef) -> FunctionSignature:
        """Extract function signature details."""
        args = []
        arg_types = []
        for arg in node.args.args:
            args.append(arg.arg)
            annotation = self._get_annotation(arg)
            arg_types.append(annotation if annotation else 'Any')
        returns = self._get_annotation(node.returns) or 'None'
        decorators = [d.id if isinstance(d, ast.Name) else self._unparse(d) 
                      for d in node.decorator_list]
        docstring = ast.get_docstring(node)
        return FunctionSignature(
            name=node.name,
            args=args,
            arg_types=arg_types,
            returns=returns,
            decorators=decorators,
            docstring=docstring
        )

    def _extract_class(self, node: ast.ClassDef) -> ClassInfo:
        """Extract class details."""
        bases = [self._unparse(base) for base in node.bases]
        methods = []
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                methods.append(self._extract_function(item))
        docstring = ast.get_docstring(node)
        return ClassInfo(name=node.name, bases=bases, methods=methods, docstring=docstring)

    def _get_annotation(self, node: Optional[ast.AST]) -> str:
        """Get type annotation as string."""
        if node is None:
            return 'Any'
        return self._unparse(node)

    def _unparse(self, node: ast.AST) -> str:
        """Unparse AST node to string."""
        return ast.unparse(node)

    def generate_imports(self) -> str:
        """Generate test file imports."""
        lines = [
            "import pytest",
            "from unittest.mock import Mock, patch, MagicMock",
            "from unittest.mock import AsyncMock",
            f"from {self.source_path.stem} import *",
            "",
            "",
        ]
        return '\n'.join(lines)

    def generate_class_fixture(self, class_name: str, class_info: ClassInfo) -> str:
        """Generate pytest fixture for a class."""
        fixture = f"""
@pytest.fixture
def {class_name.lower()}_instance():
    \"\"\"Fixture for {class_name} instance.\"\"\"
    return {class_name}()
"""
        return fixture

    def generate_function_test(self, func: FunctionSignature) -> str:
        """Generate test for a standalone function."""
        test_name = f"test_{func.name}"
        if func.args:
            param_str = ', '.join(func.args)
            params = {arg: self._mock_value(typ) for arg, typ in zip(func.args, func.arg_types)}
            param_lines = '\n        '.join(f"{k}={v}" for k, v in params.items())
            
            if func.docstring:
                docstring = f'    """Test {func.name}: {func.docstring.split(chr(10))[0]}"""'
            else:
                docstring = f'    """Test {func.name}."""'
            
            body = f"""
def {test_name}():
{docstring}
    # Arrange
    {param_lines}
    
    # Act
    result = {func.name}({param_str})
    
    # Assert
    assert result is not None
"""
        else:
            body = f"""
def {test_name}():
    \"\"\"Test {func.name} with no arguments.\"\"\"
    # Act
    result = {func.name}()
    
    # Assert
    assert result is not None
"""
        return body

    def generate_class_test(self, class_name: str, class_info: ClassInfo) -> List[str]:
        """Generate tests for a class and its methods."""
        tests = []
        
        class_test = f"""
class Test{class_name}:
    \"\"\"Test suite for {class_name}.\"\"\"
    
    def setup_method(self):
        \"\"\"Setup test fixtures.\"\"\"
        self.instance = {class_name}()
"""
        tests.append(class_test)
        
        for method in class_info.methods:
            method_name = method.name
            if method_name.startswith('_') and not method_name.startswith('__'):
                continue
            
            if method.args:
                self_arg = 'self, ' if method.args[0] == 'self' else ''
                remaining_args = method.args[1:] if method.args[0] == 'self' else method.args
                remaining_types = method.arg_types[1:] if method.args[0] == 'self' else method.arg_types
                param_str = ', '.join(remaining_args)
                params = {arg: self._mock_value(typ) for arg, typ in zip(remaining_args, remaining_types)}
                param_lines = '\n        '.join(f"{k}={v}" for k, v in params.items())
                
                test_method = f"""
    def test_{method_name}(self):
        \"\"\"Test {method_name} method.\"\"\"
        # Arrange
        {param_lines}
        
        # Act
        result = self.instance.{method_name}({param_str})
        
        # Assert
        assert result is not None
"""
            else:
                test_method = f"""
    def test_{method_name}(self):
        \"\"\"Test {method_name} method.\"\"\"
        # Act
        result = self.instance.{method_name}()
        
        # Assert
        assert result is not None
"""
            tests.append(test_method)
        
        return tests

    def _mock_value(self, type_hint: str) -> str:
        """Generate mock value based on type hint."""
        type_lower = type_hint.lower().replace("'", "")
        
        if 'str' in type_lower or 'name' in type_lower or 'path' in type_lower:
            return '"test_value"'
        elif 'int' in type_lower or 'count' in type_lower or 'id' in type_lower or 'num' in type_lower:
            return '42'
        elif 'float' in type_lower or 'rate' in type_lower or 'price' in type_lower:
            return '3.14'
        elif 'bool' in type_lower:
            return 'True'
        elif 'list' in type_lower or 'array' in type_lower:
            return '[]'
        elif 'dict' in type_lower or 'map' in type_lower:
            return '{}'
        elif 'optional' in type_lower:
            return 'None'
        elif 'any' in type_lower:
            return 'None'
        else:
            return 'Mock()'

    def generate(self) -> str:
        """Generate complete test file."""
        lines = [
            f'"""Tests for {self.source_path.stem} module."""',
            '',
            'import pytest',
            'from unittest.mock import Mock, patch, MagicMock, AsyncMock',
            f'import {self.source_path.stem}',
            '',
        ]
        
        for class_name, class_info in self.classes.items():
            fixture = self.generate_class_fixture(class_name, class_info)
            lines.append(fixture)
        
        for func in self.functions:
            test = self.generate_function_test(func)
            lines.append(test)
        
        for class_name, class_info in self.classes.items():
            class_tests = self.generate_class_test(class_name, class_info)
            lines.extend(class_tests)
        
        return '\n'.join(lines)

    def write_tests(self, output_path: Optional[str] = None) -> Path:
        """Write generated tests to file."""
        if output_path is None:
            output_path = self.source_path.parent / f"test_{self.source_path.name}"
        else:
            output_path = Path(output_path)
        
        output_path.write_text(self.generate(), encoding='utf-8')
        return output_path


def generate_tests(source_path: str, output_path: Optional[str] = None) -> str:
    """Convenience function to generate tests."""
    generator = TestGenerator(source_path)
    generator.analyze()
    test_content = generator.generate()
    
    if output_path:
        Path(output_path).write_text(test_content, encoding='utf-8')
    
    return test_content


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python test_generator.py <source_file.py> [output_file.py]")
        sys.exit(1)
    
    source = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 else None
    
    content = generate_tests(source, output)
    print(content)
