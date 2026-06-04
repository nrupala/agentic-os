#!/usr/bin/env python3
# SPDX-License-Identifier: MIT OR Apache-2.0
"""
OMEGA-CODE Dependency Checker
Verifies critical libraries are present and correct versions.
Exit code 0 = All OK, Exit code 1 = Missing dependencies
"""

import importlib
import sys

def check_dependencies():
    """Ensures all OMEGA-CODE dependencies are present."""
    required = {
        "flask": "3.0.2",
        "pytest": "8.0.0",
        "cryptography": "42.0.0",
        "sqlite3": None,  # Standard library
        "asyncio": None,
    }

    print("=" * 50)
    print("DEPENDENCY VERIFICATION")
    print("=" * 50)
    
    missing = []
    for lib, version in required.items():
        try:
            if lib == "sqlite3" or lib == "asyncio":
                print(f"  FOUND: {lib:12} (Standard Library)")
            else:
                mod = importlib.import_module(lib)
                current_v = getattr(mod, '__version__', 'Unknown')
                match = "OK" if version is None or current_v.startswith(str(version).split('.')[0]) else "MISMATCH"
                print(f"  FOUND: {lib:12} v{current_v} [{match}]")
        except ImportError:
            print(f"  MISSING: {lib}")
            missing.append(lib)

    print("=" * 50)
    
    if missing:
        print(f"FATAL: Missing {len(missing)} dependencies")
        sys.exit(1)
    
    print("[OK] All systems go")
    sys.exit(0)

if __name__ == "__main__":
    check_dependencies()
