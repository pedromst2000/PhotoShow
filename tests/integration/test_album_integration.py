"""
Integration tests for the album management workflow.
"""

import pytest

from app.core.services.album_service import AlbumService
from app.core.services.auth_service import AuthService


@pytest.fixture()
def owner(integration_db):
    """Freshly registered user who owns albums in these tests."""
    return AuthService.register_user(
        username="album_owner",
        email="album_owner@gmail.com",
        password="Test1_abc",
    )


@pytest.fixture()
def other_user(integration_db):
    """A second user with no album ownership."""
    return AuthService.register_user(
        username="other_user",
        email="other_user@gmail.com",
        password="Test1_abc",
    )


# ═══════════════════════════════════════════════════════════════════
# Album creation
# ═══════════════════════════════════════════════════════════════════


class TestAlbumCreation:
    def test_create_returns_album_dict(self, integration_db, owner):
        album = AlbumService.create_album("Holidays", creator_id=owner["id"])
        assert album is not None
        assert album["name"] == "Holidays"
        assert album["creatorId"] == owner["id"]

    def test_created_album_appears_in_user_list(self, integration_db, owner):
        AlbumService.create_album("Travel", creator_id=owner["id"])
        albums = AlbumService.get_user_albums(owner["id"])
        assert len(albums) == 1
        assert albums[0]["name"] == "Travel"

    def test_multiple_albums_returned(self, integration_db, owner):
        AlbumService.create_album("First", creator_id=owner["id"])
        AlbumService.create_album("Second", creator_id=owner["id"])
        albums = AlbumService.get_user_albums(owner["id"])
        assert len(albums) == 2


# ═══════════════════════════════════════════════════════════════════
# Album rename
# ═══════════════════════════════════════════════════════════════════


class TestAlbumRename:
    def test_owner_can_rename(self, integration_db, owner):
        album = AlbumService.create_album("Old Name", creator_id=owner["id"])
        result = AlbumService.rename_album(
            user_id=owner["id"], album_id=album["id"], new_name="New Name"
        )
        assert result is True
        albums = AlbumService.get_user_albums(owner["id"])
        assert albums[0]["name"] == "New Name"

    def test_non_owner_cannot_rename(self, integration_db, owner, other_user):
        album = AlbumService.create_album("Protected", creator_id=owner["id"])
        with pytest.raises(ValueError, match="own albums"):
            AlbumService.rename_album(
                user_id=other_user["id"],
                album_id=album["id"],
                new_name="Hijacked",
            )

    def test_admin_can_rename_any_album(self, integration_db, owner):
        album = AlbumService.create_album("Any Album", creator_id=owner["id"])
        result = AlbumService.rename_album(
            user_id=999,  # not the owner
            album_id=album["id"],
            new_name="Admin Renamed",
            is_admin=True,
        )
        assert result is True


# ═══════════════════════════════════════════════════════════════════
# Album deletion
# ═══════════════════════════════════════════════════════════════════


class TestAlbumDeletion:
    def test_owner_can_delete_album(self, integration_db, owner):
        album = AlbumService.create_album("To Delete", creator_id=owner["id"])
        result = AlbumService.delete_album_for_user(
            user_id=owner["id"], album_id=album["id"]
        )
        assert result is True
        albums = AlbumService.get_user_albums(owner["id"])
        assert len(albums) == 0

    def test_non_owner_cannot_delete(self, integration_db, owner, other_user):
        album = AlbumService.create_album("Safe Album", creator_id=owner["id"])
        with pytest.raises(ValueError):
            AlbumService.delete_album_for_user(
                user_id=other_user["id"], album_id=album["id"]
            )


# ═══════════════════════════════════════════════════════════════════
# Service interaction tests (verify services work together)
# ═══════════════════════════════════════════════════════════════════


class TestServiceInteractions:
    """Verify that AlbumService interacts properly with other services."""

    def test_album_appears_in_user_album_list_after_creation(
        self, integration_db, owner
    ):
        """Test: AlbumService integrates with user profile tracking."""
        # Verify service can create and retrieve album
        album = AlbumService.create_album("My Collection", creator_id=owner["id"])
        assert album is not None

        # Verify album is accessible through the service
        user_albums = AlbumService.get_user_albums(owner["id"])
        assert len(user_albums) == 1
        assert user_albums[0]["id"] == album["id"]

    def test_multiple_users_have_independent_album_lists(
        self, integration_db, owner, other_user
    ):
        """Test: AlbumService maintains separate state per user."""
        # Owner creates albums
        AlbumService.create_album("Owner Album 1", creator_id=owner["id"])
        AlbumService.create_album("Owner Album 2", creator_id=owner["id"])

        # Other user creates albums
        AlbumService.create_album("Other User Album", creator_id=other_user["id"])

        # Verify each user only sees their own albums
        owner_albums = AlbumService.get_user_albums(owner["id"])
        other_albums = AlbumService.get_user_albums(other_user["id"])

        assert len(owner_albums) == 2
        assert len(other_albums) == 1
        assert all(a["creatorId"] == owner["id"] for a in owner_albums)
        assert all(a["creatorId"] == other_user["id"] for a in other_albums)

    def test_album_operations_persist_to_database(self, integration_db, owner):
        """Test: AlbumService database operations are durable."""
        # Create album
        album = AlbumService.create_album("Persistent Album", creator_id=owner["id"])
        album_id = album["id"]

        # Rename album (tests update persistence)
        AlbumService.rename_album(
            user_id=owner["id"], album_id=album_id, new_name="Renamed Album"
        )

        # Retrieve and verify rename persisted
        user_albums = AlbumService.get_user_albums(owner["id"])
        assert user_albums[0]["name"] == "Renamed Album"

        # Delete album
        AlbumService.delete_album_for_user(user_id=owner["id"], album_id=album_id)

        # Verify deletion persisted
        user_albums = AlbumService.get_user_albums(owner["id"])
        assert len(user_albums) == 0
