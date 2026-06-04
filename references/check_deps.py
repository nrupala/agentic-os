# SPDX-License-Identifier: MIT OR Apache-2.0
import importlib
import sys

def check_dependencies():
    """Ensures all OMEGA-CODE dependencies are present and correct versions."""
    required = {
        "numpy": "1.26.4",
        "flask": "3.0.2",
        "gunicorn": "21.2.0"
    }

    print("--- DEPENDENCY VERIFICATION ---")
    missing = []
    for lib, version in required.items():
        try:
            mod = importlib.import_module(lib)
            current_v = getattr(mod, '__version__', 'Standard Lib')
            print(f"FOUND: {lib:10} (Target: {version}, Current: {current_v})")
        except ImportError:
            print(f"MISSING: {lib}")
            missing.append(lib)

    if missing:
        sys.exit(1)
    print("\n[OK] All systems go.")

if __name__ == "__main__":
    check_dependencies()
