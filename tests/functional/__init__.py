"""Functional test layer: business logic and rule enforcement.

Functional tests verify that the system enforces BUSINESS RULES and prevents
unauthorized operations. These tests focus on business outcomes and logic,
NOT input format validation (which belongs in unit tests).

KEY DISTINCTION:
  ❌ NOT: "Does validate_email_format() reject empty string?" (unit test)
  ✓  YES: "Can user register with duplicate email?" (business rule)

  ❌ NOT: "Does album name validation reject names > 50 chars?" (unit test)
  ✓  YES: "Does system prevent duplicate album names per-user?" (business rule)

SCOPE:
  ✓ Business rule enforcement (duplicate prevention)
  ✓ Authorization failures (wrong credentials, permission denied)
  ✓ Ownership constraints (users can't modify others' data)
  ✓ Role-based access control enforcement
  ✓ System behavior when violations occur

OUT OF SCOPE:
  ✗ Input format validation (use unit tests - already tested)
  ✗ Service interactions (use integration tests)
  ✗ Complete workflows (use acceptance tests)

Test files:
    test_album_rules.py    Business rules: Album name uniqueness per-user
    test_security.py       Security rules: Auth, roles, photo ownership

NOTE: test_auth_validation.py (pure input validation) was DELETED in refactoring
and moved to unit layer (tests/unit/services/test_auth_service.py).

Each test uses a real in-memory SQLite database to verify business logic.

Run:
    pytest tests/functional/ -v
    pytest tests/functional/ -v -k "prevent"  # Business rule prevention
"""
