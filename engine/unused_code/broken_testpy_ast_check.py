# SPDX-License-Identifier: MIT OR Apache-2.0
# Copyright 2026 agentic-OS Contributors

# BROKEN: test.py AST parse verification check
#
# This was in _phase_verify method (omega_codex.py line 365)
# Issue: Tries to read 'test.py' that doesn't exist -> FileNotFoundError
#
# BROKEN CODE:
#     lint_tools = ["ruff check .", "python -m py_compile", "python -c \"import ast; ast.parse(open('test.py').read())\""]
#     lint_result = self.shell.run("python -c \"import ast; ast.parse(open('test.py').read())\"", timeout=30)
#     # Error: FileNotFoundError: [Errno 2] No such file or directory: 'test.py'
#
# The generated code is in memory, never written to test.py
# The fix would need either:
#     1. Write the generated code to test.py first, OR
#     2. Use ast.parse(code) directly in Python (not file-based)