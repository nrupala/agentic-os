#!/usr/bin/env python3
"""
Unit tests for tools/file_ops.py

MIT License
Copyright (c) 2024 Nrupal Akolkar
"""

import pytest
import tempfile
import os
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tools.file_ops import FileOperations, FileOperationResult


class TestFileOperationResult:
    def test_file_operation_result_success(self):
        result = FileOperationResult(
            success=True,
            operation="read",
            path="/test/file.py",
            content="file content"
        )
        
        assert result.success is True
        assert result.operation == "read"
        assert result.content == "file content"

    def test_file_operation_result_failure(self):
        result = FileOperationResult(
            success=False,
            operation="read",
            path="/test/file.py",
            error="File not found"
        )
        
        assert result.success is False
        assert result.error == "File not found"


class TestFileOperations:
    @pytest.fixture
    def temp_dir(self):
        tmpdir = tempfile.mkdtemp()
        yield Path(tmpdir)
        shutil.rmtree(tmpdir, ignore_errors=True)

    @pytest.fixture
    def file_ops(self, temp_dir):
        return FileOperations(project_root=str(temp_dir))

    def test_read_file(self, file_ops, temp_dir):
        test_file = temp_dir / "test.txt"
        test_file.write_text("Hello, World!")
        
        result = file_ops.read("test.txt")
        
        assert result.success is True
        assert result.content == "Hello, World!"

    def test_read_nonexistent_file(self, file_ops, temp_dir):
        result = file_ops.read("nonexistent.txt")
        
        assert result.success is False
        assert "not found" in result.error.lower()

    def test_write_file(self, file_ops, temp_dir):
        result = file_ops.write("new_file.txt", "New content")
        
        assert result.success is True
        assert (temp_dir / "new_file.txt").read_text() == "New content"

    def test_write_file_creates_directory(self, file_ops, temp_dir):
        result = file_ops.write("subdir/new_file.txt", "Content")
        
        assert result.success is True
        assert (temp_dir / "subdir" / "new_file.txt").exists()

    def test_edit_file(self, file_ops, temp_dir):
        test_file = temp_dir / "test.txt"
        test_file.write_text("line 1\nline 2\nline 3\n")
        
        result = file_ops.edit(
            "test.txt",
            old_content="line 2",
            new_content="modified line 2"
        )
        
        assert result.success is True
        content = test_file.read_text()
        assert "modified line 2" in content

    def test_delete_file(self, file_ops, temp_dir):
        test_file = temp_dir / "test.txt"
        test_file.write_text("content")
        
        result = file_ops.delete("test.txt")
        
        assert result.success is True
        assert not test_file.exists()

    def test_delete_nonexistent_file(self, file_ops, temp_dir):
        result = file_ops.delete("nonexistent.txt")
        
        assert result.success is False

    def test_glob_files(self, file_ops, temp_dir):
        (temp_dir / "file1.py").write_text("")
        (temp_dir / "file2.py").write_text("")
        (temp_dir / "file3.txt").write_text("")
        
        result = file_ops.glob("*.py")
        
        assert result.success is True
        assert result.lines == 2

    def test_grep_search(self, file_ops, temp_dir):
        test_file = temp_dir / "test.py"
        test_file.write_text("def hello():\n    print('hello')\n    return True\n")
        
        result = file_ops.grep("test.py", "return")
        
        assert result.success is True
        assert result.lines == 1

    def test_grep_no_match(self, file_ops, temp_dir):
        test_file = temp_dir / "test.py"
        test_file.write_text("def hello():\n    pass\n")
        
        result = file_ops.grep("test.py", "nonexistent")
        
        assert result.success is True
        assert result.lines == 0

    def test_bash_command(self, file_ops, temp_dir):
        result = file_ops.bash("echo hello")
        
        assert result.success is True
        assert "hello" in result.content.lower()

    def test_operation_log(self, file_ops, temp_dir):
        file_ops.write("test.txt", "content")
        file_ops.read("test.txt")
        
        assert len(file_ops.operation_log) >= 2
        assert any(op["operation"] == "write" for op in file_ops.operation_log)
        assert any(op["operation"] == "read" for op in file_ops.operation_log)