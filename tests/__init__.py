"""PhotoShow test suite — automated testing across unit, integration, smoke, and E2E layers.

Structure:
    tests/
    ├── unit/           Unit tests: pure functions and mocked DB (fast, no integration)
    ├── integration/    Integration tests: fresh in-memory SQLite per test
    ├── smoke/          Smoke tests: module imports and critical singletons
    └── e2e/            End-to-end tests: full controller→service→DB workflows

Run via:
    python run_tests.py         # All tests
    python run_tests.py --unit  # Unit + smoke only
    pytest tests/ -v            # Direct pytest
"""
