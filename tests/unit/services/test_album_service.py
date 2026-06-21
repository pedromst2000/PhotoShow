"""
Unit tests for AlbumService.

Validation that fires *before* any DB access needs no mocking.
Tests that reach the DB mock SessionLocal + model methods.
"""

import pytest

from app.core.services.album_service import AlbumService


def _mock_session(mocker, *, return_value=None):
    """Helper: patch SessionLocal to return a no-op context manager."""
    mock_session = mocker.MagicMock()
    mock_cm = mocker.MagicMock()
    mock_cm.__enter__ = mocker.MagicMock(return_value=mock_session)
    mock_cm.__exit__ = mocker.MagicMock(return_value=False)
    mocker.patch(
        "app.core.services.album_service.SessionLocal",
        return_value=mock_cm,
    )
    return mock_session


# ═══════════════════════════════════════════════════════════════════
# create_album — validation (no DB needed)
# ═══════════════════════════════════════════════════════════════════


class TestCreateAlbumValidation:
    def test_empty_name_raises(self):
        with pytest.raises(ValueError, match="Album name is required"):
            AlbumService.create_album("", creator_id=1)

    def test_whitespace_only_name_raises(self):
        with pytest.raises(ValueError, match="Album name is required"):
            AlbumService.create_album("   ", creator_id=1)

    def test_name_over_50_chars_raises(self):
        with pytest.raises(ValueError, match="too long"):
            AlbumService.create_album("A" * 51, creator_id=1)

    def test_name_exactly_50_chars_is_accepted(self, mocker):
        """50-character name passes validation — DB call is attempted."""
        mocker.patch(
            "app.core.services.album_service.AlbumModel.get_by_creator",
            return_value=[],
        )
        expected = {"id": 1, "name": "A" * 50, "creatorId": 1}
        mocker.patch(
            "app.core.services.album_service.AlbumModel.create",
            return_value=expected,
        )
        result = AlbumService.create_album("A" * 50, creator_id=1)
        assert result is not None
        assert result["name"] == "A" * 50


# ═══════════════════════════════════════════════════════════════════
# rename_album — validation (no DB needed for empty / too-long)
# ═══════════════════════════════════════════════════════════════════


class TestRenameAlbumValidation:
    def test_empty_name_raises(self):
        with pytest.raises(ValueError, match="Album name is required"):
            AlbumService.rename_album(user_id=1, album_id=1, new_name="")

    def test_whitespace_only_name_raises(self):
        with pytest.raises(ValueError, match="Album name is required"):
            AlbumService.rename_album(user_id=1, album_id=1, new_name="  ")

    def test_name_over_50_chars_raises(self):
        with pytest.raises(ValueError, match="too long"):
            AlbumService.rename_album(user_id=1, album_id=1, new_name="A" * 51)

    def test_non_owner_without_admin_raises(self, mocker):
        """User who doesn't own the album cannot rename it."""
        album = {"id": 1, "name": "Original", "creatorId": 99}
        _mock_session(mocker)
        mocker.patch(
            "app.core.services.album_service.AlbumModel.get_by_id",
            return_value=album,
        )
        with pytest.raises(ValueError, match="own albums"):
            AlbumService.rename_album(user_id=1, album_id=1, new_name="Hijack")

    def test_admin_bypasses_ownership_check(self, mocker):
        """is_admin=True allows renaming any album."""
        album = {"id": 1, "name": "Old", "creatorId": 99}
        _mock_session(mocker)
        mocker.patch(
            "app.core.services.album_service.AlbumModel.get_by_id",
            return_value=album,
        )
        mocker.patch(
            "app.core.services.album_service.AlbumModel.get_by_creator",
            return_value=[],
        )
        mocker.patch(
            "app.core.services.album_service.AlbumModel.update",
            return_value=None,
        )
        result = AlbumService.rename_album(
            user_id=1, album_id=1, new_name="Admin Rename", is_admin=True
        )
        assert result is True

    def test_album_not_found_raises(self, mocker):
        _mock_session(mocker)
        mocker.patch(
            "app.core.services.album_service.AlbumModel.get_by_id",
            return_value=None,
        )
        with pytest.raises(ValueError, match="not found"):
            AlbumService.rename_album(user_id=1, album_id=999, new_name="NewName")
