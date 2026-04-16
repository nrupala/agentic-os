#!/usr/bin/env python3
"""
Unit tests for tools/security_scanner.py

MIT License
Copyright (c) 2024 Nrupal Akolkar
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tools.security_scanner import (
    SecurityScanner,
    SeverityLevel,
    ConfidenceLevel,
    Vulnerability,
    ScanResult
)


class TestSeverityLevel:
    def test_severity_values(self):
        assert SeverityLevel.CRITICAL.value == "CRITICAL"
        assert SeverityLevel.HIGH.value == "HIGH"
        assert SeverityLevel.MEDIUM.value == "MEDIUM"
        assert SeverityLevel.LOW.value == "LOW"


class TestConfidenceLevel:
    def test_confidence_values(self):
        assert ConfidenceLevel.HIGH.value == "HIGH"
        assert ConfidenceLevel.MEDIUM.value == "MEDIUM"
        assert ConfidenceLevel.LOW.value == "LOW"


class TestVulnerability:
    def test_vulnerability_creation(self):
        vuln = Vulnerability(
            severity=SeverityLevel.HIGH,
            confidence=ConfidenceLevel.HIGH,
            issue="B101",
            code="assert True",
            file="test.py",
            line=10,
            category="Security"
        )
        
        assert vuln.severity == SeverityLevel.HIGH
        assert vuln.issue == "B101"
        assert vuln.file == "test.py"

    def test_vulnerability_with_defaults(self):
        vuln = Vulnerability(
            severity=SeverityLevel.MEDIUM,
            confidence=ConfidenceLevel.LOW,
            issue="Test",
            code="code",
            file="test.py",
            line=1,
            category="Test"
        )
        
        assert vuln.description == ""
        assert vuln.cwe_id == ""
        assert vuln.remediation == ""


class TestScanResult:
    def test_scan_result_creation(self):
        result = ScanResult(
            file_path="test.py",
            vulnerabilities=[],
            scan_time=1.5
        )
        
        assert result.file_path == "test.py"
        assert result.scan_time == 1.5
        assert result.vulnerabilities == []
        assert result.is_safe is True

    def test_scan_result_with_vulnerabilities(self):
        vuln = Vulnerability(
            severity=SeverityLevel.HIGH,
            confidence=ConfidenceLevel.HIGH,
            issue="Test",
            code="code",
            file="test.py",
            line=1,
            category="Test"
        )
        
        result = ScanResult(
            file_path="test.py",
            vulnerabilities=[vuln],
            scan_time=1.0,
            lines_scanned=10
        )
        
        assert len(result.vulnerabilities) == 1
        result.is_safe = len(result.vulnerabilities) == 0
        assert result.is_safe is False

    def test_scan_result_severity_counts(self):
        vuln1 = Vulnerability(
            severity=SeverityLevel.HIGH,
            confidence=ConfidenceLevel.HIGH,
            issue="Test1",
            code="code",
            file="test.py",
            line=1,
            category="Test"
        )
        vuln2 = Vulnerability(
            severity=SeverityLevel.LOW,
            confidence=ConfidenceLevel.LOW,
            issue="Test2",
            code="code",
            file="test.py",
            line=2,
            category="Test"
        )
        
        result = ScanResult(
            file_path="test.py",
            vulnerabilities=[vuln1, vuln2],
            scan_time=1.0
        )
        
        counts = result.severity_counts
        assert counts["HIGH"] == 1
        assert counts["LOW"] == 1


class TestSecurityScanner:
    @pytest.fixture
    def temp_dir(self):
        tmpdir = tempfile.mkdtemp()
        yield Path(tmpdir)

    @pytest.fixture
    def scanner(self, temp_dir):
        return SecurityScanner(project_path=str(temp_dir))

    def test_scanner_creation(self, temp_dir):
        scanner = SecurityScanner(project_path=str(temp_dir))
        
        assert scanner.project_path == Path(temp_dir)

    def test_scan_file(self, scanner, temp_dir):
        test_file = temp_dir / "test.py"
        test_file.write_text("import os\nos.system('ls')")
        
        result = scanner.scan_file(test_file)
        
        assert result.file_path == str(test_file)

    def test_scan_project(self, scanner, temp_dir):
        (temp_dir / "file1.py").write_text("import os\nos.system('ls')")
        (temp_dir / "file2.py").write_text("print('hello')")
        
        result = scanner.scan_project()
        
        assert "summary" in result
        assert result["summary"]["files_scanned"] == 2

    def test_safe_file_no_vulnerabilities(self, scanner, temp_dir):
        test_file = temp_dir / "safe.py"
        test_file.write_text("print('hello world')\n x = 1")
        
        result = scanner.scan_file(test_file)
        
        assert result.is_safe is True