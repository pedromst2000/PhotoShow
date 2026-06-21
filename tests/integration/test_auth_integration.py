"""
Integration tests for the authentication workflow.

Each test receives a fresh in-memory SQLite database via ``integration_db``
(defined in tests/integration/conftest.py).  All service calls use that
isolated database — no real DB file is touched.
"""

import pytest

from app.core.services.auth_service import AuthService

# ── Shared test credentials ───────────────────────────────────────

_USER = {
    "username": "integ_alice",
    "email": "integ_alice@gmail.com",
    "password": "Test1_abc",
}


# ═══════════════════════════════════════════════════════════════════
# User registration
# ═══════════════════════════════════════════════════════════════════


class TestRegistration:
    def test_register_returns_user_dict(self, integration_db):
        user = AuthService.register_user(**_USER)
        assert user["username"] == _USER["username"]
        assert user["email"] == _USER["email"]

    def test_password_is_stored_hashed(self, integration_db):
        user = AuthService.register_user(**_USER)
        assert user["password"] != _USER["password"]
        assert user["password"].startswith(("$2b$", "$2a$"))

    def test_new_user_gets_unsigned_role(self, integration_db):
        user = AuthService.register_user(**_USER)
        assert user["role"] == "unsigned"

    def test_duplicate_username_raises(self, integration_db):
        AuthService.register_user(**_USER)
        with pytest.raises(Exception):
            AuthService.register_user(
                username=_USER["username"],
                email="other@gmail.com",
                password="Test2_abc",
            )

    def test_duplicate_email_raises(self, integration_db):
        AuthService.register_user(**_USER)
        with pytest.raises(Exception):
            AuthService.register_user(
                username="other_user",
                email=_USER["email"],
                password="Test2_abc",
            )


# ═══════════════════════════════════════════════════════════════════
# Authentication
# ═══════════════════════════════════════════════════════════════════


class TestAuthentication:
    def test_valid_credentials_return_user_dict(self, integration_db):
        AuthService.register_user(**_USER)
        result = AuthService.authenticate(_USER["email"], _USER["password"])
        assert result is not None
        assert result["username"] == _USER["username"]

    def test_wrong_password_returns_none(self, integration_db):
        AuthService.register_user(**_USER)
        result = AuthService.authenticate(_USER["email"], "WrongPass1.")
        assert result is None

    def test_unknown_email_returns_none(self, integration_db):
        result = AuthService.authenticate("nobody@gmail.com", "Test1_abc")
        assert result is None


# ═══════════════════════════════════════════════════════════════════
# Availability checks
# ═══════════════════════════════════════════════════════════════════


class TestAvailability:
    def test_email_available_before_registration(self, integration_db):
        assert AuthService.is_email_available("fresh@gmail.com") is True

    def test_email_unavailable_after_registration(self, integration_db):
        AuthService.register_user(**_USER)
        assert AuthService.is_email_available(_USER["email"]) is False

    def test_username_available_before_registration(self, integration_db):
        assert AuthService.is_username_available("brand_new_user") is True

    def test_username_unavailable_after_registration(self, integration_db):
        AuthService.register_user(**_USER)
        assert AuthService.is_username_available(_USER["username"]) is False
