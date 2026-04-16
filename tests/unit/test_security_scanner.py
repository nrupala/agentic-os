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
    Vulnerability,
    VulnerabilitySeverity,
    scan_file,
    scan_directory
)


class TestVulnerabilitySeverity:
    def test_severity_values(self):
        assert VulnerabilitySeverity.CRITICAL.value == "critical"
        assert VulnerabilitySeverity.HIGH.value == "high"
        assert VulnerabilitySeverity.MEDIUM.value == "medium"
        assert VulnerabilitySeverity.LOW.value == "low"
        assert VulnerabilitySeverity.INFO.value == "info"


class TestVulnerability:
    def test_vulnerability_creation(self):
        vuln = Vulnerability(
            severity=VulnerabilitySeverity.HIGH,
            rule_id="B101",
            message="Assert usage",
            file_path="test.py",
            line_number=10,
            code_snippet="assert x == y"
        )
        
        assert vuln.severity == VulnerabilitySeverity.HIGH
        assert vuln.rule_id == "B101"
        assert vuln.file_path == "test.py"
        assert vuln.line_number == 10

    def test_vulnerability_to_dict(self):
        vuln = Vulnerability(
            severity=VulnerabilitySeverity.MEDIUM,
            rule_id="B102",
            message="exec usage",
            file_path="test.py",
            line_number=5
        )
        
        result = vuln.to_dict()
        
        assert result["severity"] == "medium"
        assert result["rule_id"] == "B102"
        assert result["line_number"] == 5

    def test_vulnerability_cwe_mapping(self):
        vuln = Vulnerability(
            severity=VulnerabilitySeverity.CRITICAL,
            rule_id="B301",
            message="Pickle deserialization",
            file_path="test.py",
            line_number=1
        )
        
        assert "CWE" in vuln.cwe_id or vuln.cwe_id.startswith("CWE-")


class TestSecurityScanner:
    @pytest.fixture
    def temp_dir(self):
        import shutil
        tmpdir = tempfile.mkdtemp()
        yield Path(tmpdir)
        shutil.rmtree(tmpdir, ignore_errors=True)

    def test_scanner_creation(self):
        scanner = SecurityScanner()
        assert scanner.excluded_paths is not None

    def test_scanner_with_custom_rules(self):
        custom_rules = [
            {"pattern": r"dangerous_pattern", "severity": "critical", "message": "Dangerous!"}
        ]
        scanner = SecurityScanner(custom_rules=custom_rules)
        assert len(scanner.custom_rules) == 1

    def test_scan_python_file_eval(self, temp_dir):
        test_file = temp_dir / "test_eval.py"
        test_file.write_text('result = eval("2 + 2")')
        
        scanner = SecurityScanner()
        results = scanner.scan_file(test_file)
        
        vulnerabilities = results.get("vulnerabilities", [])
        assert any(v.rule_id == "B102" for v in vulnerabilities)

    def test_scan_python_file_exec(self, temp_dir):
        test_file = temp_dir / "test_exec.py"
        test_file.write_text('exec("print(1)")')
        
        scanner = SecurityScanner()
        results = scanner.scan_file(test_file)
        
        vulnerabilities = results.get("vulnerabilities", [])
        assert any(v.rule_id == "B102" for v in vulnerabilities)

    def test_scan_python_file_hardcoded_password(self, temp_dir):
        test_file = temp_dir / "test_password.py"
        test_file.write_text('password = "secret123"')
        
        scanner = SecurityScanner()
        results = scanner.scan_file(test_file)
        
        vulnerabilities = results.get("vulnerabilities", [])
        assert any(v.severity == VulnerabilitySeverity.HIGH for v in vulnerabilities)

    def test_scan_python_file_sql_injection(self, temp_dir):
        test_file = temp_dir / "test_sql.py"
        test_file.write_text('''
query = "SELECT * FROM users WHERE id = " + user_input
''')
        
        scanner = SecurityScanner()
        results = scanner.scan_file(test_file)
        
        vulnerabilities = results.get("vulnerabilities", [])
        assert any("SQL" in v.message or "injection" in v.message.lower() for v in vulnerabilities)

    def test_scan_python_file_shell_injection(self, temp_dir):
        test_file = temp_dir / "test_shell.py"
        test_file.write_text('''
import os
os.system("ls " + user_input)
''')
        
        scanner = SecurityScanner()
        results = scanner.scan_file(test_file)
        
        vulnerabilities = results.get("vulnerabilities", [])
        assert any("shell" in v.message.lower() or "command" in v.message.lower() for v in vulnerabilities)

    def test_scan_safe_code(self, temp_dir):
        test_file = temp_dir / "test_safe.py"
        test_file.write_text('''
def add(a, b):
    """Add two numbers."""
    return a + b

result = add(1, 2)
''')
        
        scanner = SecurityScanner()
        results = scanner.scan_file(test_file)
        
        vulnerabilities = results.get("vulnerabilities", [])
        critical_high = [v for v in vulnerabilities if v.severity in [VulnerabilitySeverity.CRITICAL, VulnerabilitySeverity.HIGH]]
        assert len(critical_high) == 0

    def test_scan_with_skipped_patterns(self, temp_dir):
        test_file = temp_dir / "test_skip.py"
        test_file.write_text('password = "test123"')
        
        scanner = SecurityScanner(skip_patterns=["test_skip.py"])
        results = scanner.scan_file(test_file)
        
        assert results["skipped"] is True

    def test_scan_directory(self, temp_dir):
        (temp_dir / "file1.py").write_text('eval("1")')
        (temp_dir / "file2.py").write_text('exec("1")')
        
        scanner = SecurityScanner()
        results = scanner.scan_directory(temp_dir)
        
        assert results["files_scanned"] == 2
        assert results["total_vulnerabilities"] > 0

    def test_scan_directory_with_exclusions(self, temp_dir):
        (temp_dir / "file1.py").write_text('eval("1")')
        
        venv_dir = temp_dir / "venv"
        venv_dir.mkdir()
        (venv_dir / "file2.py").write_text('eval("1")')
        
        scanner = SecurityScanner()
        results = scanner.scan_directory(temp_dir)
        
        assert results["files_skipped"] >= 1

    def test_generate_report(self, temp_dir):
        test_file = temp_dir / "test.py"
        test_file.write_text('password = "secret"')
        
        scanner = SecurityScanner()
        scanner.scan_file(test_file)
        report = scanner.generate_report()
        
        assert "summary" in report
        assert "vulnerabilities" in report

    def test_scan_unicode_file(self, temp_dir):
        test_file = temp_dir / "test_unicode.py"
        test_file.write_text('# -*- coding: utf-8 -*-\npassword = "密码"')
        
        scanner = SecurityScanner()
        results = scanner.scan_file(test_file)
        
        assert results is not None


class TestScanFileFunction:
    def test_scan_file_function(self, tmp_path):
        test_file = tmp_path / "test.py"
        test_file.write_text('eval("1")')
        
        results = scan_file(test_file)
        
        assert "vulnerabilities" in results
        assert results["file"] == str(test_file)


class TestScanDirectoryFunction:
    def test_scan_directory_function(self, tmp_path):
        (tmp_path / "test1.py").write_text('eval("1")')
        (tmp_path / "test2.py").write_text('exec("1")')
        
        results = scan_directory(tmp_path)
        
        assert results["files_scanned"] == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
