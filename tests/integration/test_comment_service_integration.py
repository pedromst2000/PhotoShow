"""
Integration tests for CommentService covering comment submission and management.

Focuses on:
- Comment creation and validation
- Comment retrieval by photo
- Comment deletion
- Comment enrichment with author info
"""

from app.core.services.album_service import AlbumService
from app.core.services.auth_service import AuthService
from app.core.services.comment_service import CommentService
from app.core.services.photo_service import PhotoService


class TestCommentCreation:
    """Test comment creation and validation."""

    def test_create_comment_success(self, integration_db):
        """Create a valid comment."""
        user = AuthService.register_user("mary", "mary@example.com", "password")
        album = AlbumService.create_album("Album 1", user["id"])
        photo = PhotoService.create_photo_record(
            album_id=album["id"],
            category_id=1,
            description="Photo 1",
        )

        success, msg, comment = CommentService.add_comment(
            user["id"], photo["id"], "Nice photo!"
        )

        assert success is True
        assert comment is not None
        assert comment["comment"] == "Nice photo!"

    def test_create_comment_empty(self, integration_db):
        """Empty comment is rejected."""
        user = AuthService.register_user("nancy", "nancy@example.com", "password")
        album = AlbumService.create_album("Album 1", user["id"])
        photo = PhotoService.create_photo_record(
            album_id=album["id"],
            category_id=1,
            description="Photo 1",
        )

        success, msg, _ = CommentService.add_comment(user["id"], photo["id"], "")
        assert success is False
        assert "empty" in msg.lower() or "cannot" in msg.lower()

    def test_create_comment_too_long(self, integration_db):
        """Comment exceeding max length is rejected."""
        user = AuthService.register_user("oscar", "oscar@example.com", "password")
        album = AlbumService.create_album("Album 1", user["id"])
        photo = PhotoService.create_photo_record(
            album_id=album["id"],
            category_id=1,
            description="Photo 1",
        )

        long_comment = "x" * 500
        success, msg, _ = CommentService.add_comment(
            user["id"], photo["id"], long_comment
        )
        assert success is False
        assert "255" in msg or "most" in msg.lower()


class TestCommentRetrieval:
    """Test comment retrieval."""

    def test_get_comments_by_photo(self, integration_db):
        """Get all comments for a photo."""
        user = AuthService.register_user("paul", "paul@example.com", "password")
        album = AlbumService.create_album("Album 1", user["id"])
        photo = PhotoService.create_photo_record(
            album_id=album["id"],
            category_id=1,
            description="Photo 1",
        )

        # Create 3 comments
        for i in range(3):
            CommentService.add_comment(user["id"], photo["id"], f"Comment {i}")

        comments = CommentService.get_comments_for_photo(photo["id"])

        assert len(comments) >= 3

    def test_get_comments_nonexistent_photo(self, integration_db):
        """Get comments for nonexistent photo returns empty list."""
        comments = CommentService.get_comments_for_photo(9999)

        assert isinstance(comments, list)
        assert len(comments) == 0

    def test_delete_comment(self, integration_db):
        """Delete a comment."""
        user = AuthService.register_user("quinn", "quinn@example.com", "password")
        album = AlbumService.create_album("Album 1", user["id"])
        photo = PhotoService.create_photo_record(
            album_id=album["id"],
            category_id=1,
            description="Photo 1",
        )

        _, _, comment = CommentService.add_comment(user["id"], photo["id"], "Test")
        assert comment is not None

        success, msg = CommentService.delete_comment(
            user["id"], comment["id"], is_admin=False
        )

        assert success is True

    def test_delete_nonexistent_comment(self, integration_db):
        """Delete nonexistent comment returns False."""
        user = AuthService.register_user("sam", "sam@example.com", "password")
        success, msg = CommentService.delete_comment(user["id"], 9999, is_admin=True)

        assert success is False


class TestCommentEnrichment:
    """Test comment data enrichment with author info."""

    def test_get_enriched_comments(self, integration_db):
        """Get comments with author information."""
        user = AuthService.register_user("rachel", "rachel@example.com", "password")
        album = AlbumService.create_album("Album 1", user["id"])
        photo = PhotoService.create_photo_record(
            album_id=album["id"],
            category_id=1,
            description="Photo 1",
        )

        CommentService.add_comment(user["id"], photo["id"], "Awesome!")

        # get_comments_for_photo returns enriched comments with author info
        enriched = CommentService.get_comments_for_photo(photo["id"])

        assert len(enriched) >= 1
        for c in enriched:
            assert "comment" in c
            assert "author_username" in c
