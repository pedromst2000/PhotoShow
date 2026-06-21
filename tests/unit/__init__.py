"""Unit test layer: isolated service and utility functions with mocked databases.

Tests pure business logic and validation that do NOT require a real database.
Mocks are applied at the module level using pytest-mock so all service calls use
mocked `SessionLocal` instead of the real SQLite engine.

Sub-packages:
    services/    Service layer unit tests (auth, album, photo, etc.)
    utils/       Utility function tests (date formatting, hashing, ratings)

Run:
    pytest tests/unit/ -v
"""
