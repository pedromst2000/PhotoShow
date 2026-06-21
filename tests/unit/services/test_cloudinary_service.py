"""
Unit tests for CloudinaryService.

Covers the actual public methods:
- upload_avatar: upload user avatar to Cloudinary
- upload_photo: upload photo to Cloudinary
- delete_image: remove image from Cloudinary by public_id
"""

from unittest.mock import patch

from app.core.services.cloudinary_service import CloudinaryService


class TestUploadAvatar:
    """Test CloudinaryService.upload_avatar."""

    def test_method_exists(self):
        assert hasattr(CloudinaryService, "upload_avatar")

    def test_returns_none_on_cloudinary_failure(self):
        with patch(
            "app.core.services.cloudinary_service.cloudinary.uploader.upload",
            side_effect=Exception("Network error"),
        ):
            result = CloudinaryService.upload_avatar(
                file_path="fake.jpg", username="user1"
            )
            assert result is None


class TestUploadPhoto:
    """Test CloudinaryService.upload_photo."""

    def test_method_exists(self):
        assert hasattr(CloudinaryService, "upload_photo")

    def test_returns_none_on_cloudinary_failure(self):
        with patch(
            "app.core.services.cloudinary_service.cloudinary.uploader.upload",
            side_effect=Exception("Network error"),
        ):
            result = CloudinaryService.upload_photo(file_path="fake.jpg", photo_id=1)
            assert result is None


class TestDeleteImage:
    """Test CloudinaryService.delete_image."""

    def test_method_exists(self):
        assert hasattr(CloudinaryService, "delete_image")

    def test_returns_false_on_cloudinary_failure(self):
        with patch(
            "app.core.services.cloudinary_service.cloudinary.uploader.destroy",
            side_effect=Exception("Network error"),
        ):
            result = CloudinaryService.delete_image(public_id="photo-show/photo_1")
            assert result is False
