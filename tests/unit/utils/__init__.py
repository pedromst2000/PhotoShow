"""Unit tests for utility functions: date formatting, password hashing, rating calculations.

Tests pure helper functions that operate on data without side effects.
No database or mocking needed — these functions are deterministic.

Modules tested:
    test_date_utils.py       → format_timestamp() (relative time: "2 days ago")
    test_hash_utils.py       → hash_password() (bcrypt hashing)
    test_weighted_rating.py  → calculate_weighted_rating() (Bayesian average)
"""
