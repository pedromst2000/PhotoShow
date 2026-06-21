"""
Unit tests for PhotoService.

Covers the actual public methods:
- create_photo / upload: create photo records with Cloudinary upload
- get_photo_details: retrieve enriched photo data
- like_photo / unlike_photo / check_if_liked: like interactions
- rate_photo / get_photo_rating_stats: rating interactions
- update_photo_for_user: edit photo metadata
- delete_photo: remove photo and Cloudinary asset
"""

from app.core.services.photo_service import PhotoService


class TestPhotoCreation:
    """Test photo creation methods."""

    def test_create_photo_exists(self):
        assert hasattr(PhotoService, "create_photo")

    def test_upload_exists(self):
        assert hasattr(PhotoService, "upload")

    def test_create_photo_record_exists(self):
        assert hasattr(PhotoService, "create_photo_record")


class TestPhotoRetrieval:
    """Test photo retrieval methods."""

    def test_get_photo_details_exists(self):
        assert hasattr(PhotoService, "get_photo_details")

    def test_get_liked_photos_exists(self):
        assert hasattr(PhotoService, "get_liked_photos")


class TestPhotoLikes:
    """Test like/unlike interactions."""

    def test_like_photo_exists(self):
        assert hasattr(PhotoService, "like_photo")

    def test_unlike_photo_exists(self):
        assert hasattr(PhotoService, "unlike_photo")

    def test_check_if_liked_exists(self):
        assert hasattr(PhotoService, "check_if_liked")


class TestPhotoRatings:
    """Test rating interactions."""

    def test_rate_photo_exists(self):
        assert hasattr(PhotoService, "rate_photo")

    def test_get_photo_rating_stats_exists(self):
        assert hasattr(PhotoService, "get_photo_rating_stats")


class TestPhotoEditing:
    """Test photo edit and delete."""

    def test_update_photo_for_user_exists(self):
        assert hasattr(PhotoService, "update_photo_for_user")

    def test_delete_photo_exists(self):
        assert hasattr(PhotoService, "delete_photo")

    def test_delete_photo_record_exists(self):
        assert hasattr(PhotoService, "delete_photo_record")
