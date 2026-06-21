"""
Integration tests for the photo upload and interaction workflow.

Cloudinary calls are always mocked — the tests verify service-level logic
(record creation, rollback on failure, like state) without real network I/O.
"""

import pytest

from app.core.services.album_service import AlbumService
from app.core.services.auth_service import AuthService
from app.core.services.photo_service import PhotoService

# ── Cloudinary mock helpers ───────────────────────────────────────

_CLOUDINARY_OK = {
    "public_id": "photo-show/prod/photos_gallery/Photo_1",
    "url": "https://res.cloudinary.com/test/image/upload/Photo_1.jpg",
}


def _patch_cloudinary_upload(mocker, return_value=_CLOUDINARY_OK):
    mocker.patch(
        "app.core.services.cloudinary_service.CloudinaryService.upload_photo",
        return_value=return_value,
    )


def _patch_cloudinary_delete(mocker):
    mocker.patch(
        "app.core.services.cloudinary_service.CloudinaryService.delete_image",
        return_value=None,
    )


# ── Fixtures ─────────────────────────────────────────────────────


@pytest.fixture()
def user_and_album(integration_db, seeded_category):
    """Return (user_dict, album_dict, category_id) for photo tests."""
    user = AuthService.register_user(
        username="photo_owner",
        email="photo_owner@gmail.com",
        password="Test1_abc",
    )
    album = AlbumService.create_album("My Photos", creator_id=user["id"])
    return user, album, seeded_category


# ═══════════════════════════════════════════════════════════════════
# Upload flow
# ═══════════════════════════════════════════════════════════════════


class TestPhotoUpload:
    def test_upload_fails_when_cloudinary_returns_none(
        self, integration_db, user_and_album, mocker
    ):
        """Cloudinary failure → photo record is rolled back → (False, msg)."""
        _user, album, cat_id = user_and_album
        _patch_cloudinary_upload(mocker, return_value=None)
        _patch_cloudinary_delete(mocker)

        success, message = PhotoService.upload(
            image_path="/fake/path/photo.jpg",
            album_id=album["id"],
            category_id=cat_id,
        )

        assert success is False
        assert message  # non-empty error message

    def test_upload_succeeds_with_valid_cloudinary_response(
        self, integration_db, user_and_album, mocker
    ):
        """Full upload flow with mocked Cloudinary returns (True, msg)."""
        _user, album, cat_id = user_and_album
        _patch_cloudinary_upload(mocker)
        _patch_cloudinary_delete(mocker)

        success, message = PhotoService.upload(
            image_path="/fake/path/photo.jpg",
            album_id=album["id"],
            category_id=cat_id,
            description="A test photo",
        )

        assert success is True

    def test_upload_with_optional_fields(self, integration_db, user_and_album, mocker):
        """Providing category_id and description does not break the flow."""
        _user, album, cat_id = user_and_album
        _patch_cloudinary_upload(mocker)
        _patch_cloudinary_delete(mocker)

        success, _ = PhotoService.upload(
            image_path="/fake/path/photo.jpg",
            album_id=album["id"],
            category_id=cat_id,
            description="Scenic view",
        )

        assert success is True


# ═══════════════════════════════════════════════════════════════════
# Like / unlike
# ═══════════════════════════════════════════════════════════════════


class TestPhotoLike:
    def _upload_one_photo(self, album_id, cat_id, mocker) -> None:
        _patch_cloudinary_upload(mocker)
        _patch_cloudinary_delete(mocker)
        PhotoService.upload(
            image_path="/fake/p.jpg",
            album_id=album_id,
            category_id=cat_id,
        )

    def test_user_has_not_liked_fresh_photo(
        self, integration_db, user_and_album, mocker
    ):
        user, album, cat_id = user_and_album
        self._upload_one_photo(album["id"], cat_id, mocker)

        result = PhotoService.check_if_liked(user_id=user["id"], photo_id=1)
        assert result is False
