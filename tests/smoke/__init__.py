"""Smoke tests: quick sanity checks that modules import and core singletons work.

Smoke tests run in seconds and serve as the FIRST GATE in CI/CD:
  1. Verify all service and utility modules can be imported (no syntax/import errors)
  2. Verify UserSession singleton behaves correctly (same instance, login/logout)

These tests catch structural issues (missing imports, broken configs) before
heavier unit, integration, and E2E test suites run.

Run:
    pytest tests/smoke/ -v
"""
