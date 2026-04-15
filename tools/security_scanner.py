import subprocess
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class SeverityLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ConfidenceLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


@dataclass
class Vulnerability:
    severity: SeverityLevel
    confidence: ConfidenceLevel
    issue: str
    code: str
    file: str
    line: int
    category: str
    description: str = ""
    cwe_id: str = ""
    remediation: str = ""


@dataclass
class ScanResult:
    file_path: str
    vulnerabilities: List[Vulnerability] = field(default_factory=list)
    scan_time: float = 0.0
    lines_scanned: int = 0
    is_safe: bool = True

    @property
    def severity_counts(self) -> Dict[str, int]:
        counts = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
        for v in self.vulnerabilities:
            counts[v.severity.value] += 1
        return counts


class SecurityScanner:
    """SAST Security Scanner using Bandit patterns."""

    BUILTINS_TO_CHECK = [
        "eval", "exec", "compile", "__import__", "open", "input",
        "compile", "reload", "vars", "globals", "locals", "dir"
    ]

    DANGEROUS_PATTERNS = [
        (r"eval\s*\(", "Use of eval()", SeverityLevel.HIGH, ConfidenceLevel.HIGH),
        (r"exec\s*\(", "Use of exec()", SeverityLevel.HIGH, ConfidenceLevel.HIGH),
        (r"os\.system\s*\(", "Use of os.system()", SeverityLevel.MEDIUM, ConfidenceLevel.HIGH),
        (r"os\.popen\s*\(", "Use of os.popen()", SeverityLevel.MEDIUM, ConfidenceLevel.HIGH),
        (r"subprocess\.call\s*\(.*shell\s*=\s*True", "Shell injection via subprocess", SeverityLevel.HIGH, ConfidenceLevel.HIGH),
        (r"subprocess\.Popen\s*\(.*shell\s*=\s*True", "Shell injection via subprocess", SeverityLevel.HIGH, ConfidenceLevel.HIGH),
        (r"pickle\.loads?\s*\(", "Insecure pickle deserialization", SeverityLevel.HIGH, ConfidenceLevel.HIGH),
        (r"yaml\.load\s*\(", "Insecure YAML load", SeverityLevel.HIGH, ConfidenceLevel.HIGH),
        (r"yaml\.unsafe_load\s*\(", "Insecure YAML load", SeverityLevel.HIGH, ConfidenceLevel.HIGH),
        (r"\.format\s*\(.*\{.*\}", "String format with user input", SeverityLevel.LOW, ConfidenceLevel.MEDIUM),
        (r"%\s*\(.*\)", "String interpolation with user input", SeverityLevel.LOW, ConfidenceLevel.MEDIUM),
        (r"f['\"].*\{.*\}", "F-string with potential injection", SeverityLevel.LOW, ConfidenceLevel.MEDIUM),
        (r"random\.random\s*\(", "Predictable random numbers", SeverityLevel.LOW, ConfidenceLevel.LOW),
        (r"hashlib\.md5\s*\(", "Weak hash MD5", SeverityLevel.LOW, ConfidenceLevel.HIGH),
        (r"hashlib\.sha1\s*\(", "Weak hash SHA1", SeverityLevel.LOW, ConfidenceLevel.HIGH),
        (r"crypt\.crypt\s*\(", "Insecure crypt", SeverityLevel.MEDIUM, ConfidenceLevel.HIGH),
        (r"telnetlib\s*\.Telnet", "Telnet usage", SeverityLevel.HIGH, ConfidenceLevel.HIGH),
        (r"ftplib\s*\.FTP", "FTP usage", SeverityLevel.LOW, ConfidenceLevel.MEDIUM),
        (r"requests\.get\s*\(.*verify\s*=\s*False", "Disabled SSL verification", SeverityLevel.MEDIUM, ConfidenceLevel.HIGH),
        (r"ssl.*context\s*=\s*ssl\.create_default_context\s*\(\)\s*.*check_hostname\s*=\s*False", "Disabled SSL hostname check", SeverityLevel.MEDIUM, ConfidenceLevel.HIGH),
        (r"tempfile\.mktemp\s*\(", "Insecure temp file", SeverityLevel.LOW, ConfidenceLevel.MEDIUM),
        (r"hardcoded_password", "Hardcoded password", SeverityLevel.MEDIUM, ConfidenceLevel.HIGH),
        (r"hardcoded_secret", "Hardcoded secret", SeverityLevel.MEDIUM, ConfidenceLevel.HIGH),
        (r"api[_-]?key", "Potential API key", SeverityLevel.LOW, ConfidenceLevel.LOW),
        (r"password\s*=\s*['\"][^'\"]+['\"]", "Hardcoded password", SeverityLevel.MEDIUM, ConfidenceLevel.MEDIUM),
        (r"secret\s*=\s*['\"][^'\"]+['\"]", "Hardcoded secret", SeverityLevel.MEDIUM, ConfidenceLevel.MEDIUM),
        (r"jwt\.decode\s*\(.*verify\s*=\s*False", "Disabled JWT verification", SeverityLevel.HIGH, ConfidenceLevel.HIGH),
        (r"\.sqlite3\.connect\s*\(.*check_same_thread\s*=\s*False", "SQLite thread safety", SeverityLevel.LOW, ConfidenceLevel.LOW),
        (r"debug\s*=\s*True", "Debug mode enabled", SeverityLevel.LOW, ConfidenceLevel.MEDIUM),
    ]

    REMEDIATION_GUIDE = {
        "eval": "Avoid using eval(). Use safer alternatives like ast.literal_eval() for parsing.",
        "exec": "Avoid using exec(). Consider redesigning the code to not need dynamic execution.",
        "os.system": "Use subprocess module with a list of arguments instead of shell commands.",
        "os.popen": "Use subprocess.Popen() with proper argument handling instead.",
        "shell=True": "Avoid shell=True in subprocess calls. Use shell=False with argument lists.",
        "pickle": "Never unpickle untrusted data. Use JSON or other safe serialization formats.",
        "yaml.load": "Use yaml.safe_load() instead of yaml.load().",
        "hardcoded_password": "Use environment variables or a secure secrets manager.",
        "hardcoded_secret": "Use environment variables or a secure secrets manager.",
        "MD5": "Use a stronger hash algorithm like SHA-256 from hashlib.",
        "SHA1": "Use a stronger hash algorithm like SHA-256 from hashlib.",
        "SSL verification": "Always verify SSL certificates. Remove verify=False from requests.",
        "JWT verification": "Always verify JWT signatures and claims.",
    }

    CWE_MAPPING = {
        "eval": "CWE-95",
        "exec": "CWE-95",
        "os.system": "CWE-78",
        "shell=True": "CWE-78",
        "pickle": "CWE-502",
        "yaml.load": "CWE-20",
        "hardcoded_password": "CWE-259",
        "hardcoded_secret": "CWE-798",
    }

    def __init__(self, project_path: Optional[str] = None):
        self.project_path = Path(project_path) if project_path else Path.cwd()
        self.results: List[ScanResult] = []
        self.total_vulnerabilities: int = 0
        self.files_scanned: int = 0

    def scan_file(self, file_path: Path) -> ScanResult:
        """Scan a single Python file for vulnerabilities."""
        import time
        start_time = time.time()

        result = ScanResult(file_path=str(file_path))

        try:
            content = file_path.read_text(encoding='utf-8')
        except (UnicodeDecodeError, FileNotFoundError):
            return result

        result.lines_scanned = len(content.splitlines())

        for line_num, line in enumerate(content.splitlines(), 1):
            for pattern, issue, severity, confidence in self.DANGEROUS_PATTERNS:
                if re.search(pattern, line, re.IGNORECASE):
                    vuln = self._create_vulnerability(
                        severity, confidence, issue, line.strip(),
                        str(file_path), line_num, pattern
                    )
                    result.vulnerabilities.append(vuln)

        result.is_safe = len(result.vulnerabilities) == 0
        result.scan_time = time.time() - start_time
        self.files_scanned += 1

        return result

    def _create_vulnerability(
        self, severity: SeverityLevel, confidence: ConfidenceLevel,
        issue: str, code: str, file: str, line: int, pattern: str
    ) -> Vulnerability:
        """Create a vulnerability object with remediation info."""
        category = self._get_category(issue)
        description = self._get_description(issue)
        remediation = self._get_remediation(pattern)
        cwe_id = self._get_cwe_id(pattern)

        return Vulnerability(
            severity=severity,
            confidence=confidence,
            issue=issue,
            code=code,
            file=file,
            line=line,
            category=category,
            description=description,
            cwe_id=cwe_id,
            remediation=remediation
        )

    def _get_category(self, issue: str) -> str:
        """Categorize the vulnerability."""
        issue_lower = issue.lower()
        if any(x in issue_lower for x in ["injection", "command", "shell"]):
            return "Injection"
        elif any(x in issue_lower for x in ["deserializ", "pickle", "yaml"]):
            return "Deserialization"
        elif any(x in issue_lower for x in ["password", "secret", "key", "hardcoded"]):
            return "Cryptography"
        elif any(x in issue_lower for x in ["ssl", "verify", "certificate"]):
            return "Cryptography"
        elif any(x in issue_lower for x in ["hash", "md5", "sha"]):
            return "Cryptography"
        else:
            return "Code Quality"

    def _get_description(self, issue: str) -> str:
        """Get a description of the vulnerability."""
        descriptions = {
            "Use of eval()": "The eval() function executes code dynamically, which can lead to code injection vulnerabilities.",
            "Use of exec()": "The exec() function executes code dynamically, which can lead to code injection vulnerabilities.",
            "Use of os.system()": "os.system() executes shell commands, which can lead to command injection.",
            "Use of os.popen()": "os.popen() executes shell commands, which can lead to command injection.",
            "Shell injection via subprocess": "Using shell=True in subprocess can lead to command injection attacks.",
            "Insecure pickle deserialization": "Unpickling untrusted data can lead to arbitrary code execution.",
            "Insecure YAML load": "Using yaml.load() without a safe loader can lead to arbitrary code execution.",
            "Hardcoded password": "Hardcoded credentials are a security risk and should be externalized.",
            "Hardcoded secret": "Hardcoded secrets can be exposed in source code and should use secure storage.",
            "Weak hash MD5": "MD5 is cryptographically broken and should not be used for security purposes.",
            "Weak hash SHA1": "SHA1 is cryptographically weak and should not be used for security purposes.",
            "Disabled SSL verification": "Disabling SSL verification removes protection against man-in-the-middle attacks.",
            "Disabled JWT verification": "Disabling JWT verification allows forged tokens to be accepted.",
        }
        return descriptions.get(issue, f"Potential security issue: {issue}")

    def _get_remediation(self, pattern: str) -> str:
        """Get remediation guidance for the pattern."""
        for key, guidance in self.REMEDIATION_GUIDE.items():
            if key in pattern:
                return guidance
        return "Review and refactor the code to follow security best practices."

    def _get_cwe_id(self, pattern: str) -> str:
        """Get CWE ID for the vulnerability."""
        for key, cwe in self.CWE_MAPPING.items():
            if key in pattern:
                return cwe
        return ""

    def scan_project(self, extensions: List[str] = None) -> Dict:
        """Scan entire project for vulnerabilities."""
        if extensions is None:
            extensions = ['.py']

        self.results = []
        python_files = []
        for ext in extensions:
            python_files.extend(self.project_path.rglob(f'*{ext}'))

        python_files = [f for f in python_files if not self._should_skip(f)]

        for file_path in python_files:
            result = self.scan_file(file_path)
            self.results.append(result)
            self.total_vulnerabilities += len(result.vulnerabilities)

        return self._generate_report()

    def _should_skip(self, file_path: Path) -> bool:
        """Check if file should be skipped from scanning."""
        skip_patterns = [
            '__pycache__', '.git', '.venv', 'venv', 'env',
            '.tox', 'node_modules', 'build', 'dist', '.egg-info',
            '.pytest_cache', '.mypy_cache', '.coverage', 'htmlcov'
        ]
        path_str = str(file_path)
        return any(pattern in path_str for pattern in skip_patterns)

    def _generate_report(self) -> Dict:
        """Generate comprehensive scan report."""
        total_high = 0
        total_medium = 0
        total_low = 0
        total_critical = 0

        for result in self.results:
            counts = result.severity_counts
            total_critical += counts.get("CRITICAL", 0)
            total_high += counts.get("HIGH", 0)
            total_medium += counts.get("MEDIUM", 0)
            total_low += counts.get("LOW", 0)

        return {
            "summary": {
                "files_scanned": self.files_scanned,
                "total_vulnerabilities": self.total_vulnerabilities,
                "critical": total_critical,
                "high": total_high,
                "medium": total_medium,
                "low": total_low,
                "is_safe": self.total_vulnerabilities == 0
            },
            "results": [
                {
                    "file": r.file_path,
                    "vulnerabilities": [
                        {
                            "severity": v.severity.value,
                            "confidence": v.confidence.value,
                            "issue": v.issue,
                            "code": v.code,
                            "line": v.line,
                            "category": v.category,
                            "description": v.description,
                            "cwe_id": v.cwe_id,
                            "remediation": v.remediation
                        }
                        for v in r.vulnerabilities
                    ]
                }
                for r in self.results if r.vulnerabilities
            ]
        }

    def print_report(self, report: Dict = None):
        """Print a human-readable report."""
        if report is None:
            report = self._generate_report()

        summary = report["summary"]

        print("\n" + "=" * 70)
        print("                    SECURITY SCAN REPORT")
        print("=" * 70)

        if summary["total_vulnerabilities"] == 0:
            print("\n  [OK] No vulnerabilities found!")
            print(f"  Scanned {summary['files_scanned']} files.")
            return

        print(f"\n  Files Scanned: {summary['files_scanned']}")
        print(f"  Total Issues:  {summary['total_vulnerabilities']}")
        print("\n  Severity Breakdown:")
        print(f"    CRITICAL:  {summary['critical']}")
        print(f"    HIGH:      {summary['high']}")
        print(f"    MEDIUM:    {summary['medium']}")
        print(f"    LOW:       {summary['low']}")

        if summary["is_safe"]:
            print("\n  [OK] No high or critical vulnerabilities found.")
        else:
            print("\n  [!] High or critical vulnerabilities detected!")

        for file_result in report.get("results", []):
            print(f"\n  File: {file_result['file']}")
            print("  " + "-" * 60)
            for vuln in file_result["vulnerabilities"]:
                severity_icon = {
                    "CRITICAL": "[!]",
                    "HIGH": "[!]",
                    "MEDIUM": "[*]",
                    "LOW": "[i]"
                }.get(vuln["severity"], "[?]")

                print(f"    {severity_icon} {vuln['severity']}: {vuln['issue']}")
                code_snippet = vuln['code'][:60].encode('ascii', 'replace').decode('ascii')
                print(f"        Line {vuln['line']}: {code_snippet}...")
                if vuln['cwe_id']:
                    print(f"        {vuln['cwe_id']}")
                if vuln['remediation']:
                    print(f"        Fix: {vuln['remediation'][:80]}...")

        print("\n" + "=" * 70)


def run_bandit(file_path: str) -> Optional[Dict]:
    """Run Bandit security scanner if available."""
    try:
        result = subprocess.run(
            ['bandit', '-r', file_path, '-f', 'json'],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode in [0, 1]:
            return json.loads(result.stdout)
        return None
    except (subprocess.SubprocessError, FileNotFoundError, json.JSONDecodeError):
        return None


def scan_security(file_or_dir: str) -> Dict:
    """Main entry point for security scanning."""
    scanner = SecurityScanner()
    path = Path(file_or_dir)

    if path.is_file():
        result = scanner.scan_file(path)
        scanner.results.append(result)
        scanner.files_scanned = 1
        scanner.total_vulnerabilities = len(result.vulnerabilities)
        return scanner._generate_report()
    else:
        return scanner.scan_project()


if __name__ == "__main__":
    import sys
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    if len(sys.argv) < 2:
        print("Usage: python security_scanner.py <file_or_directory>")
        print("Example: python security_scanner.py engine/")
        print("Example: python security_scanner.py engine/omega_forge.py")
        sys.exit(1)

    target = sys.argv[1]
    report = scan_security(target)

    scanner = SecurityScanner()
    scanner.print_report(report)

    summary = report["summary"]
    sys.exit(0 if summary["high"] == 0 and summary["critical"] == 0 else 1)
