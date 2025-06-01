"""
Test runner script for the sentence parser tests.

Usage:
    python run_tests.py              # Run all tests
    python run_tests.py -v          # Run with verbose output
    python run_tests.py -k 401k     # Run tests matching '401k'
    python run_tests.py test/test_edge_cases.py  # Run specific test file
"""

import sys
import subprocess
import os


def main():
    """Run pytest with appropriate configuration."""
    # Build pytest command
    cmd = [sys.executable, "-m", "pytest"]
    
    # Add coverage if available
    try:
        import pytest_cov
        cmd.extend(["--cov=src/services", "--cov-report=term-missing"])
    except ImportError:
        print("Note: Install pytest-cov for coverage reports")
    
    # Add default options
    cmd.extend([
        "-v",  # Verbose
        "--tb=short",  # Short traceback format
        "--strict-markers",  # Strict marker checking
    ])
    
    # Add any command line arguments
    if len(sys.argv) > 1:
        cmd.extend(sys.argv[1:])
    else:
        # Default to running all tests
        cmd.append("test/")
    
    # Set PYTHONPATH to include src
    env = os.environ.copy()
    src_path = os.path.join(os.path.dirname(__file__), "src")
    if "PYTHONPATH" in env:
        env["PYTHONPATH"] = f"{src_path}{os.pathsep}{env['PYTHONPATH']}"
    else:
        env["PYTHONPATH"] = src_path
    
    # Run tests
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, env=env)
    
    return result.returncode


if __name__ == "__main__":
    sys.exit(main()) 