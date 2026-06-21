#!/usr/bin/env python
"""
Test runner script for PhotoShow project.

Executes tests in the tests/ directory using pytest with verbose output
and short traceback format for readability.

Usage:
    python run_tests.py              # Run all tests
    python run_tests.py --unit       # Run only unit tests
    python run_tests.py --functional # Run only functional tests
    python run_tests.py --integration # Run only integration tests
    python run_tests.py --acceptance # Run only acceptance tests
    python run_tests.py --smoke      # Run only smoke tests
"""

import argparse
import subprocess
import sys


def main():
    """Run tests with pytest, optionally filtered by test type."""
    parser = argparse.ArgumentParser(
        description="Run PhotoShow tests, optionally filtered by type"
    )
    parser.add_argument(
        "--unit",
        action="store_true",  # Run only unit tests
        help="Run only unit tests",
    )
    parser.add_argument(
        "--functional",
        action="store_true",
        help="Run only functional tests",
    )
    parser.add_argument(
        "--integration",
        action="store_true",
        help="Run only integration tests",
    )
    parser.add_argument(
        "--acceptance",
        action="store_true",
        help="Run only acceptance tests",
    )
    parser.add_argument(
        "--smoke",
        action="store_true",
        help="Run only smoke tests",
    )

    args = parser.parse_args()

    # Determine which tests to run
    test_path = "tests/"

    if args.unit:
        test_path = "tests/unit"
        print("[Info] Running unit tests...")
    elif args.functional:
        test_path = "tests/functional"
        print("[Info] Running functional tests...")
    elif args.integration:
        test_path = "tests/integration"
        print("[Info] Running integration tests...")
    elif args.acceptance:
        test_path = "tests/acceptance"
        print("[Info] Running acceptance tests...")
    elif args.smoke:
        test_path = "tests/smoke"
        print("[Info] Running smoke tests...")
    else:
        print("[Info] Running all tests...")

    cmd = [
        sys.executable,
        "-m",
        "pytest",
        test_path,
        "-v",
        "--tb=short",
    ]

    print(f"[Info] Command: {' '.join(cmd)}")
    print()

    result = subprocess.run(cmd)

    if result.returncode == 0:
        print()
        print("[Info] ✅ All tests passed successfully!")
    else:
        print()
        print("[Info] ❌ Some tests failed. See output above for details.")

    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
