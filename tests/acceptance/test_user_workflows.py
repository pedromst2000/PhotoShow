"""
Acceptance tests: Critical user workflows.

Tests that core user journeys work end-to-end through the service layer —
registration, login, and album management — verifying the happy path while
also checking that the system correctly rejects conflicting data.
"""

import pytest

from app.core.services.album_service import AlbumService
from app.core.services.auth_service import AuthService
from app.core.services.user_service import UserService

# ═══════════════════════════════════════════════════════════════════
# Registration workflow
# ═══════════════════════════════════════════════════════════════════


class TestRegistrationWorkflow:
    def test_new_user_can_register(self, integration_db):
        user = AuthService.register_user("newuser", "newuser@gmail.com", "Test1_abc")
        assert user is not None
        assert user["username"] == "newuser"
        assert user["email"] == "newuser@gmail.com"

    def test_registered_user_can_authenticate(self, integration_db):
        AuthService.register_user("loginuser", "loginuser@gmail.com", "Test1_abc")
        result = AuthService.authenticate("loginuser@gmail.com", "Test1_abc")
        assert result is not None
        assert result["username"] == "loginuser"

    def test_duplicate_username_raises_error(self, integration_db):
        AuthService.register_user("dupname", "first@gmail.com", "Test1_abc")
        with pytest.raises(Exception):
            AuthService.register_user("dupname", "second@gmail.com", "Test2_abc")

    def test_duplicate_email_raises_error(self, integration_db):
        AuthService.register_user("user_one", "same@gmail.com", "Test1_abc")
        with pytest.raises(Exception):
            AuthService.register_user("user_two", "same@gmail.com", "Test2_abc")

    def test_wrong_password_prevents_login(self, integration_db):
        AuthService.register_user("wrongpass", "wrongpass@gmail.com", "Correct.1")
        result = AuthService.authenticate("wrongpass@gmail.com", "Wrong.999")
        assert result is None

    def test_newly_registered_user_has_empty_profile_stats(self, integration_db):
        user = AuthService.register_user("newstats", "newstats@gmail.com", "Test1_abc")
        stats = UserService.get_profile_stats(user["id"])
        assert stats["follower_count"] == 0
        assert stats["photo_count"] == 0

    def test_registered_user_has_default_role(self, integration_db):
        user = AuthService.register_user("roleuser", "roleuser@gmail.com", "Test1_abc")
        # New users start with the "unsigned" role
        assert user["role"] == "unsigned"


# ═══════════════════════════════════════════════════════════════════
# Album management workflow
# ═══════════════════════════════════════════════════════════════════


class TestAlbumWorkflow:
    def test_user_can_create_album(self, integration_db):
        user = AuthService.register_user(
            "albumcreator", "albumcreator@gmail.com", "Test1_abc"
        )
        album = AlbumService.create_album("Vacation 2025", creator_id=user["id"])
        assert album is not None
        assert album["name"] == "Vacation 2025"

    def test_created_album_appears_in_user_albums(self, integration_db):
        user = AuthService.register_user(
            "albumlister", "albumlister@gmail.com", "Test1_abc"
        )
        AlbumService.create_album("Portfolio", creator_id=user["id"])
        albums = AlbumService.get_user_albums(user["id"])
        assert len(albums) == 1
        assert albums[0]["name"] == "Portfolio"

    def test_user_starts_with_no_albums(self, integration_db):
        user = AuthService.register_user(
            "emptyuser", "emptyuser@gmail.com", "Test1_abc"
        )
        albums = AlbumService.get_user_albums(user["id"])
        assert albums == []

    def test_user_can_create_multiple_albums(self, integration_db):
        user = AuthService.register_user(
            "multialbum", "multialbum@gmail.com", "Test1_abc"
        )
        AlbumService.create_album("Nature", creator_id=user["id"])
        AlbumService.create_album("Travel", creator_id=user["id"])
        AlbumService.create_album("Food", creator_id=user["id"])
        albums = AlbumService.get_user_albums(user["id"])
        assert len(albums) == 3
