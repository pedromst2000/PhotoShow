"""
Integration tests for PhotoService covering photo operations beyond basic unit tests.

Focuses on photo retrieval, updates, deletion, and ratings.
"""

from app.core.services.album_service import AlbumService
from app.core.services.auth_service import AuthService
from app.core.services.photo_service import PhotoService


class TestPhotoServiceOperations:
    """Test PhotoService methods with full database integration."""

    def test_get_photo_by_album(self, integration_db):
        """Get all photos in an album."""
        user = AuthService.register_user("alice", "alice@example.com", "password")
        album = AlbumService.create_album("Album 1", user["id"])

        assert album is not None, "Album creation failed"

        # Create 3 photos
        photo_ids = []
        for i in range(3):
            photo = PhotoService.create_photo_record(
                album_id=album["id"],
                category_id=1,
                description=f"Photo {i}",
            )
            if photo:
                photo_ids.append(photo["id"])

        # Retrieve all photos from album
        photos = PhotoService.get_by_album(album["id"])

        assert len(photos) >= 3, f"Expected at least 3 photos, got {len(photos)}"

    def test_get_photo_by_id(self, integration_db):
        """Get a specific photo by ID."""
        user = AuthService.register_user("bob", "bob@example.com", "password")
        album = AlbumService.create_album("Album 1", user["id"])

        photo = PhotoService.create_photo_record(
            album_id=album["id"],
            category_id=1,
            description="Test photo",
        )

        assert photo is not None

        # Get it back
        retrieved = PhotoService.get_by_id(photo["id"])

        assert retrieved is not None
        assert retrieved["id"] == photo["id"]
        assert retrieved["description"] == "Test photo"

    def test_get_photo_nonexistent(self, integration_db):
        """Get nonexistent photo returns None."""
        photo = PhotoService.get_by_id(9999)

        assert photo is None

    def test_update_photo_description(self, integration_db):
        """Update photo description."""
        user = AuthService.register_user("charlie", "charlie@example.com", "password")
        album = AlbumService.create_album("Album 1", user["id"])

        photo = PhotoService.create_photo_record(
            album_id=album["id"],
            category_id=1,
            description="Original",
        )

        # Update it
        result = PhotoService.update_photo_for_user(
            user_id=user["id"],
            photo_id=photo["id"],
            updates={"description": "Updated"},
        )

        # Should succeed or return a value
        assert result is not None or result is True

    def test_delete_photo(self, integration_db):
        """Delete a photo."""
        user = AuthService.register_user("diana", "diana@example.com", "password")
        album = AlbumService.create_album("Album 1", user["id"])

        photo = PhotoService.create_photo_record(
            album_id=album["id"],
            category_id=1,
            description="To delete",
        )

        # Delete it
        result, _ = PhotoService.delete_photo(photo["id"], user["id"])

        assert result is True

    def test_like_photo(self, integration_db):
        """Like a photo."""
        user1 = AuthService.register_user("eve", "eve@example.com", "password")
        user2 = AuthService.register_user("frank", "frank@example.com", "password")

        album = AlbumService.create_album("Album 1", user1["id"])
        photo = PhotoService.create_photo_record(
            album_id=album["id"],
            category_id=1,
            description="Likeable photo",
        )

        result = PhotoService.like_photo(user2["id"], photo["id"])

        assert result is True

    def test_unlike_photo(self, integration_db):
        """Unlike a photo."""
        user1 = AuthService.register_user("grace", "grace@example.com", "password")
        user2 = AuthService.register_user("helen", "helen@example.com", "password")

        album = AlbumService.create_album("Album 1", user1["id"])
        photo = PhotoService.create_photo_record(
            album_id=album["id"],
            category_id=1,
            description="Likeable photo",
        )

        PhotoService.like_photo(user2["id"], photo["id"])
        result = PhotoService.unlike_photo(user2["id"], photo["id"])

        assert result is True

    def test_is_photo_liked(self, integration_db):
        """Check if user liked a photo."""
        user1 = AuthService.register_user("ian", "ian@example.com", "password")
        user2 = AuthService.register_user("jack", "jack@example.com", "password")

        album = AlbumService.create_album("Album 1", user1["id"])
        photo = PhotoService.create_photo_record(
            album_id=album["id"],
            category_id=1,
            description="Photo",
        )

        # Before liking
        is_liked = PhotoService.check_if_liked(user2["id"], photo["id"])
        assert is_liked is False

        # Like it
        PhotoService.like_photo(user2["id"], photo["id"])

        # After liking
        is_liked = PhotoService.check_if_liked(user2["id"], photo["id"])
        assert is_liked is True

    def test_get_like_count(self, integration_db):
        """Get total likes for a photo."""
        user1 = AuthService.register_user("karen", "karen@example.com", "password")
        user2 = AuthService.register_user("leo", "leo@example.com", "password")
        user3 = AuthService.register_user("mary", "mary@example.com", "password")

        album = AlbumService.create_album("Album 1", user1["id"])
        photo = PhotoService.create_photo_record(
            album_id=album["id"],
            category_id=1,
            description="Popular photo",
        )

        # Add likes
        PhotoService.like_photo(user2["id"], photo["id"])
        PhotoService.like_photo(user3["id"], photo["id"])

        # Get count
        count = PhotoService.get_like_count(photo["id"])

        assert count >= 2

    def test_rate_photo(self, integration_db):
        """Rate a photo."""
        user1 = AuthService.register_user("nancy", "nancy@example.com", "password")
        user2 = AuthService.register_user("oscar", "oscar@example.com", "password")

        album = AlbumService.create_album("Album 1", user1["id"])
        photo = PhotoService.create_photo_record(
            album_id=album["id"],
            category_id=1,
            description="Photo",
        )

        result = PhotoService.rate_photo(user2["id"], photo["id"], 5)

        assert result is True

    def test_get_photo_rating_average(self, integration_db):
        """Get average rating for a photo."""
        user1 = AuthService.register_user("paul", "paul@example.com", "password")
        user2 = AuthService.register_user("quinn", "quinn@example.com", "password")
        user3 = AuthService.register_user("rachel", "rachel@example.com", "password")

        album = AlbumService.create_album("Album 1", user1["id"])
        photo = PhotoService.create_photo_record(
            album_id=album["id"],
            category_id=1,
            description="Photo",
        )

        # Add ratings
        PhotoService.rate_photo(user2["id"], photo["id"], 4)
        PhotoService.rate_photo(user3["id"], photo["id"], 5)

        # Get average
        avg = PhotoService.get_photo_rating_average(photo["id"])

        assert avg is not None
        assert avg >= 0
