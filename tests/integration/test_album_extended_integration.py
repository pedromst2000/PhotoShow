"""
Integration tests for AlbumService and UserService covering extended operations.

Focuses on album management, user profiles, and follow operations.
"""

import pytest

from app.core.db import engine as db_engine
from app.core.db.models.follow import FollowModel
from app.core.services.album_service import AlbumService
from app.core.services.auth_service import AuthService
from app.core.services.photo_service import PhotoService


class TestAlbumServiceOperations:
    """Test AlbumService methods for album management."""

    def test_get_albums_by_creator(self, integration_db):
        """Get all albums created by a user."""
        user = AuthService.register_user("alice", "alice@example.com", "password")

        # Create 3 albums
        for i in range(3):
            album = AlbumService.create_album(f"Album {i}", user["id"])
            assert album is not None

        # Get albums for user
        albums = AlbumService.get_user_albums(user["id"])

        assert len(albums) >= 3

    def test_get_album_details(self, integration_db):
        """Get album details."""
        user = AuthService.register_user("bob", "bob@example.com", "password")
        album = AlbumService.create_album("My Album", user["id"])

        retrieved = AlbumService.get_album_details(
            album_id=album["id"],
            user_id=user["id"],
        )

        assert retrieved is not None
        assert retrieved["album"]["id"] == album["id"]
        assert retrieved["album"]["name"] == "My Album"

    def test_delete_album(self, integration_db):
        """Delete an album."""
        user = AuthService.register_user("diana", "diana@example.com", "password")
        album = AlbumService.create_album("To Delete", user["id"])

        result = AlbumService.delete_album_for_user(user["id"], album["id"])

        assert result is True

    def test_delete_nonexistent_album(self, integration_db):
        """Delete nonexistent album raises ValueError."""
        user = AuthService.register_user("eve", "eve@example.com", "password")

        with pytest.raises(ValueError, match="Album not found"):
            AlbumService.delete_album_for_user(user["id"], 9999)


class TestUserFollowOperations:
    """Test user following functionality."""

    def test_follow_and_unfollow(self, integration_db):
        """Follow and unfollow operations."""
        user1 = AuthService.register_user("mary", "mary@example.com", "password")
        user2 = AuthService.register_user("nancy", "nancy@example.com", "password")

        # Follow user2
        with db_engine.SessionLocal() as session:
            FollowModel.follow(
                session, follower_id=user1["id"], followed_id=user2["id"]
            )
            session.commit()

        # Verify following
        with db_engine.SessionLocal() as session:
            is_following = FollowModel.is_following(session, user1["id"], user2["id"])

        assert is_following is True

        # Check follower count
        with db_engine.SessionLocal() as session:
            count = FollowModel.count_followers(session, user2["id"])

        assert count >= 1

        # Unfollow
        with db_engine.SessionLocal() as session:
            result = FollowModel.unfollow(session, user1["id"], user2["id"])
            session.commit()

        assert result is True

    def test_get_follower_count(self, integration_db):
        """Get follower count for a user."""
        user1 = AuthService.register_user("oscar", "oscar@example.com", "password")
        user2 = AuthService.register_user("paul", "paul@example.com", "password")
        user3 = AuthService.register_user("quinn", "quinn@example.com", "password")

        # Both follow user1
        with db_engine.SessionLocal() as session:
            FollowModel.follow(
                session, follower_id=user2["id"], followed_id=user1["id"]
            )
            FollowModel.follow(
                session, follower_id=user3["id"], followed_id=user1["id"]
            )
            session.commit()

        # Check count
        with db_engine.SessionLocal() as session:
            count = FollowModel.count_followers(session, user1["id"])

        assert count >= 2


class TestAlbumWithPhotos:
    """Test album operations with photos."""

    def test_album_contains_photos(self, integration_db):
        """Album correctly groups its photos."""
        user = AuthService.register_user("rachel", "rachel@example.com", "password")
        album = AlbumService.create_album("Album 1", user["id"])

        # Add 5 photos
        for i in range(5):
            PhotoService.create_photo_record(
                album_id=album["id"],
                category_id=1,
                description=f"Photo {i}",
            )

        # Get all photos (using models directly if needed)
        from app.core.db.engine import SessionLocal
        from app.core.db.models.photo import PhotoModel

        with SessionLocal() as session:
            photos = PhotoModel.get_by_album(session, album["id"])

        assert len(photos) >= 5

    def test_album_photo_count(self, integration_db):
        """Album tracks photo count correctly."""
        user = AuthService.register_user("steve", "steve@example.com", "password")
        album = AlbumService.create_album("Album 1", user["id"])

        from app.core.db.engine import SessionLocal
        from app.core.db.models.photo import PhotoModel

        # Initially no photos
        with SessionLocal() as session:
            photos1 = PhotoModel.get_by_album(session, album["id"])
        initial_count = len(photos1)

        # Add a photo
        PhotoService.create_photo_record(
            album_id=album["id"],
            category_id=1,
            description="Photo 1",
        )

        # Count should increase
        with SessionLocal() as session:
            photos2 = PhotoModel.get_by_album(session, album["id"])
        new_count = len(photos2)

        assert new_count > initial_count
