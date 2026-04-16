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
import hashlib

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tools.file_ops import (
    FileOperations,
    OperationType,
    OperationResult,
    FileSearchResult,
    DiffResult
)


class TestOperationType:
    def test_operation_type_values(self):
        assert OperationType.READ.value == "read"
        assert OperationType.WRITE.value == "write"
        assert OperationType.EDIT.value == "edit"
        assert OperationType.DELETE.value == "delete"
        assert OperationType.SEARCH.value == "search"
        assert OperationType.GLOB.value == "glob"


class TestOperationResult:
    def test_operation_result_success(self):
        result = OperationResult(
            success=True,
            operation=OperationType.READ,
            path="/test/file.py"
        )
        
        assert result.success is True
        assert result.operation == OperationType.READ

    def test_operation_result_failure(self):
        result = OperationResult(
            success=False,
            operation=OperationType.READ,
            path="/test/file.py",
            error="File not found"
        )
        
        assert result.success is False
        assert result.error == "File not found"

    def test_operation_result_with_content(self):
        result = OperationResult(
            success=True,
            operation=OperationType.READ,
            path="/test/file.py",
            content="file content"
        )
        
        assert result.content == "file content"

    def test_operation_result_to_dict(self):
        result = OperationResult(
            success=True,
            operation=OperationType.WRITE,
            path="/test/file.py",
            bytes_written=100
        )
        
        data = result.to_dict()
        assert data["success"] is True
        assert data["operation"] == "write"
        assert data["bytes_written"] == 100


class TestFileSearchResult:
    def test_file_search_result_creation(self):
        result = FileSearchResult(
            file_path="/test/file.py",
            line_number=10,
            line_content="def test():",
            match_context=["line 1", "def test():", "line 3"]
        )
        
        assert result.file_path == "/test/file.py"
        assert result.line_number == 10

    def test_file_search_result_to_dict(self):
        result = FileSearchResult(
            file_path="/test/file.py",
            line_number=5,
            line_content="test",
            match_context=[]
        )
        
        data = result.to_dict()
        assert data["file_path"] == "/test/file.py"
        assert data["line_number"] == 5


class TestDiffResult:
    def test_diff_result_creation(self):
        diff = DiffResult(
            file_path="/test/file.py",
            original_hash="abc123",
            new_hash="def456",
            lines_added=10,
            lines_removed=5
        )
        
        assert diff.file_path == "/test/file.py"
        assert diff.lines_added == 10
        assert diff.lines_removed == 5

    def test_diff_result_to_dict(self):
        diff = DiffResult(
            file_path="/test/file.py",
            original_hash="abc",
            new_hash="def"
        )
        
        data = diff.to_dict()
        assert data["file_path"] == "/test/file.py"


class TestFileOperations:
    @pytest.fixture
    def temp_dir(self):
        tmpdir = tempfile.mkdtemp()
        yield Path(tmpdir)
        shutil.rmtree(tmpdir, ignore_errors=True)

    @pytest.fixture
    def file_ops(self, temp_dir):
        return FileOperations(base_path=temp_dir, enable_logging=True)

    def test_read_file(self, file_ops, temp_dir):
        test_file = temp_dir / "test.txt"
        test_file.write_text("Hello, World!")
        
        result = file_ops.read_file(test_file)
        
        assert result.success is True
        assert result.content == "Hello, World!"

    def test_read_nonexistent_file(self, file_ops, temp_dir):
        result = file_ops.read_file(temp_dir / "nonexistent.txt")
        
        assert result.success is False
        assert "not found" in result.error.lower()

    def test_write_file(self, file_ops, temp_dir):
        result = file_ops.write_file(
            temp_dir / "new_file.txt",
            "New content"
        )
        
        assert result.success is True
        assert (temp_dir / "new_file.txt").read_text() == "New content"

    def test_write_file_creates_directory(self, file_ops, temp_dir):
        result = file_ops.write_file(
            temp_dir / "subdir" / "new_file.txt",
            "Content"
        )
        
        assert result.success is True
        assert (temp_dir / "subdir" / "new_file.txt").exists()

    def test_edit_file(self, file_ops, temp_dir):
        test_file = temp_dir / "test.txt"
        test_file.write_text("line 1\nline 2\nline 3\n")
        
        result = file_ops.edit_file(
            test_file,
            new_content="modified line 2",
            line_start=2,
            line_end=2
        )
        
        assert result.success is True
        content = test_file.read_text()
        assert "modified line 2" in content
        assert "line 1" in content
        assert "line 3" in content

    def test_edit_file_creates_backup(self, file_ops, temp_dir):
        test_file = temp_dir / "test.txt"
        test_file.write_text("original content")
        
        file_ops.edit_file(test_file, new_content="new content")
        
        backup_file = temp_dir / "test.txt.bak"
        assert backup_file.exists()
        assert backup_file.read_text() == "original content"

    def test_delete_file(self, file_ops, temp_dir):
        test_file = temp_dir / "test.txt"
        test_file.write_text("content")
        
        result = file_ops.delete_file(test_file)
        
        assert result.success is True
        assert not test_file.exists()

    def test_delete_nonexistent_file(self, file_ops, temp_dir):
        result = file_ops.delete_file(temp_dir / "nonexistent.txt")
        
        assert result.success is False

    def test_search_in_file(self, file_ops, temp_dir):
        test_file = temp_dir / "test.py"
        test_file.write_text("def hello():\n    print('hello')\n    return True\n")
        
        results = file_ops.search_in_file(test_file, "return")
        
        assert len(results) == 1
        assert results[0].line_content.strip() == "return True"

    def test_search_in_file_no_match(self, file_ops, temp_dir):
        test_file = temp_dir / "test.py"
        test_file.write_text("def hello():\n    pass\n")
        
        results = file_ops.search_in_file(test_file, "nonexistent")
        
        assert len(results) == 0

    def test_glob_files(self, file_ops, temp_dir):
        (temp_dir / "file1.py").write_text("")
        (temp_dir / "file2.py").write_text("")
        (temp_dir / "file3.txt").write_text("")
        
        results = file_ops.glob_files(temp_dir, "*.py")
        
        assert len(results) == 2
        assert all(str(r).endswith(".py") for r in results)

    def test_glob_recursive(self, file_ops, temp_dir):
        (temp_dir / "root.py").write_text("")
        (temp_dir / "subdir").mkdir()
        (temp_dir / "subdir" / "nested.py").write_text("")
        
        results = file_ops.glob_files(temp_dir, "**/*.py")
        
        assert len(results) >= 2

    def test_get_file_hash(self, file_ops, temp_dir):
        test_file = temp_dir / "test.txt"
        test_file.write_text("content")
        
        file_hash = file_ops.get_file_hash(test_file)
        
        assert file_hash is not None
        assert len(file_hash) == 64

    def test_get_file_info(self, file_ops, temp_dir):
        test_file = temp_dir / "test.txt"
        test_file.write_text("Hello")
        
        info = file_ops.get_file_info(test_file)
        
        assert info["exists"] is True
        assert info["size"] == 5
        assert info["extension"] == ".txt"

    def test_copy_file(self, file_ops, temp_dir):
        source = temp_dir / "source.txt"
        source.write_text("content")
        dest = temp_dir / "dest.txt"
        
        result = file_ops.copy_file(source, dest)
        
        assert result.success is True
        assert dest.exists()
        assert dest.read_text() == "content"

    def test_copy_file_to_directory(self, file_ops, temp_dir):
        source = temp_dir / "source.txt"
        source.write_text("content")
        dest_dir = temp_dir / "subdir"
        dest_dir.mkdir()
        
        result = file_ops.copy_file(source, dest_dir)
        
        assert result.success is True
        assert (dest_dir / "source.txt").exists()

    def test_move_file(self, file_ops, temp_dir):
        source = temp_dir / "source.txt"
        source.write_text("content")
        dest = temp_dir / "dest.txt"
        
        result = file_ops.move_file(source, dest)
        
        assert result.success is True
        assert not source.exists()
        assert dest.exists()

    def test_batch_write(self, file_ops, temp_dir):
        files = {
            "file1.txt": "content 1",
            "file2.txt": "content 2",
            "file3.txt": "content 3"
        }
        
        results = file_ops.batch_write(files)
        
        assert all(r.success for r in results.values())
        assert all((temp_dir / f).exists() for f in files.keys())

    def test_ensure_directory(self, file_ops, temp_dir):
        new_dir = temp_dir / "new" / "nested" / "dir"
        
        result = file_ops.ensure_directory(new_dir)
        
        assert result.success is True
        assert new_dir.exists()
        assert new_dir.is_dir()


class TestFileOperationsLogging:
    @pytest.fixture
    def temp_dir(self):
        tmpdir = tempfile.mkdtemp()
        yield Path(tmpdir)
        shutil.rmtree(tmpdir, ignore_errors=True)

    def test_logging_enabled(self, temp_dir):
        file_ops = FileOperations(base_path=temp_dir, enable_logging=True)
        
        test_file = temp_dir / "test.txt"
        test_file.write_text("content")
        
        file_ops.read_file(test_file)
        
        assert len(file_ops.operation_log) > 0

    def test_logging_disabled(self, temp_dir):
        file_ops = FileOperations(base_path=temp_dir, enable_logging=False)
        
        test_file = temp_dir / "test.txt"
        test_file.write_text("content")
        
        file_ops.read_file(test_file)
        
        assert len(file_ops.operation_log) == 0

    def test_operation_log_structure(self, temp_dir):
        file_ops = FileOperations(base_path=temp_dir, enable_logging=True)
        
        test_file = temp_dir / "test.txt"
        test_file.write_text("content")
        
        file_ops.read_file(test_file)
        
        log_entry = file_ops.operation_log[0]
        assert "timestamp" in log_entry
        assert "operation" in log_entry
        assert "path" in log_entry


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
