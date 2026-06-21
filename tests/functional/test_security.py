"""
Functional tests: Security and authorization enforcement.

Tests that the system refuses unauthorized operations and invalid credentials.
Covers three attack surfaces:
  1. Wrong / missing credentials at login
  2. Invalid role escalation attempts
  3. Cross-user data modification (photo ownership)
"""

import pytest

from app.core.services.album_service import AlbumService
from app.core.services.auth_service import AuthService
from app.core.services.photo_service import PhotoService
from app.core.services.user_service import UserService


@pytest.fixture()
def two_users(integration_db):
    """Return (owner, intruder) — two separate registered users."""
    owner = AuthService.register_user("owner", "owner@gmail.com", "Test1_abc")
    intruder = AuthService.register_user("intruder", "intruder@gmail.com", "Test2_abc")
    return owner, intruder


# ═══════════════════════════════════════════════════════════════════
# Authentication failures
# ═══════════════════════════════════════════════════════════════════


class TestAuthenticationFailures:
    def test_wrong_password_returns_none(self, integration_db):
        AuthService.register_user("secuser", "secuser@gmail.com", "Correct.1")
        result = AuthService.authenticate("secuser@gmail.com", "WrongPassword.1")
        assert result is None

    def test_nonexistent_email_returns_none(self, integration_db):
        result = AuthService.authenticate("nobody@gmail.com", "SomePass.1")
        assert result is None

    def test_empty_password_returns_none(self, integration_db):
        AuthService.register_user("empuser", "empuser@gmail.com", "Correct.1")
        result = AuthService.authenticate("empuser@gmail.com", "")
        assert result is None

    def test_correct_credentials_authenticate_successfully(self, integration_db):
        AuthService.register_user("okuser", "okuser@gmail.com", "Correct.1")
        result = AuthService.authenticate("okuser@gmail.com", "Correct.1")
        assert result is not None
        assert result["email"] == "okuser@gmail.com"


# ═══════════════════════════════════════════════════════════════════
# Role escalation prevention
# ═══════════════════════════════════════════════════════════════════


class TestRoleEnforcement:
    def test_assigning_admin_role_raises_value_error(self, integration_db, two_users):
        owner, _ = two_users
        with pytest.raises(ValueError):
            UserService.change_role(owner["username"], "admin")

    def test_assigning_unknown_role_raises_value_error(self, integration_db, two_users):
        owner, _ = two_users
        with pytest.raises(ValueError):
            UserService.change_role(owner["username"], "superuser")

    def test_valid_role_change_succeeds(self, integration_db, two_users):
        owner, _ = two_users
        result = UserService.change_role(owner["username"], "regular")
        assert result is True


# ═══════════════════════════════════════════════════════════════════
# Photo ownership enforcement
# ═══════════════════════════════════════════════════════════════════


class TestPhotoOwnership:
    def _make_photo(self, owner, cat_id):
        album = AlbumService.create_album("Owner Album", creator_id=owner["id"])
        return PhotoService.create_photo_record(
            album_id=album["id"],
            category_id=cat_id,
            description="A test photo",
        )

    def test_non_owner_cannot_update_photo(
        self, integration_db, two_users, seeded_category
    ):
        owner, intruder = two_users
        photo = self._make_photo(owner, seeded_category)

        result = PhotoService.update_photo_for_user(
            user_id=intruder["id"],
            photo_id=photo["id"],
            updates={"description": "hacked"},
        )
        assert result is False

    def test_owner_can_update_their_own_photo(
        self, integration_db, two_users, seeded_category
    ):
        owner, _ = two_users
        photo = self._make_photo(owner, seeded_category)

        result = PhotoService.update_photo_for_user(
            user_id=owner["id"],
            photo_id=photo["id"],
            updates={"description": "updated by owner"},
        )
        assert result is True

    def test_update_nonexistent_photo_returns_false(self, integration_db):
        result = PhotoService.update_photo_for_user(
            user_id=1, photo_id=9999, updates={"description": "ghost edit"}
        )
        assert result is False
