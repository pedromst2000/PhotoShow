"""
Unit tests for CommentService.

Text validation fires *before* any DB call, so the empty / too-long cases
need no mocking at all.
"""

from app.core.services.comment_service import CommentService


class TestAddCommentValidation:
    def test_empty_text_returns_error_tuple(self):
        success, msg, data = CommentService.add_comment(user_id=1, photo_id=1, text="")
        assert success is False
        assert "empty" in msg.lower()
        assert data is None

    def test_whitespace_only_returns_error_tuple(self):
        success, msg, data = CommentService.add_comment(
            user_id=1, photo_id=1, text="   "
        )
        assert success is False
        assert data is None

    def test_text_over_255_chars_returns_error_tuple(self):
        long_text = "A" * 256  # _MAX_LEN = 255
        success, msg, data = CommentService.add_comment(
            user_id=1, photo_id=1, text=long_text
        )
        assert success is False
        assert "255" in msg
        assert data is None

    def test_text_at_max_length_passes_validation(self, mocker):
        """255-char comment passes validation and proceeds to the DB layer."""
        max_text = "A" * 255

        mock_session = mocker.MagicMock()
        mock_cm = mocker.MagicMock()
        mock_cm.__enter__ = mocker.MagicMock(return_value=mock_session)
        mock_cm.__exit__ = mocker.MagicMock(return_value=False)
        mocker.patch(
            "app.core.services.comment_service.SessionLocal",
            return_value=mock_cm,
        )

        comment_row = {
            "id": 1,
            "authorId": 1,
            "comment": max_text,
            "photoId": 1,
            "publishedDate": None,
            "createdAt": None,
            "updatedAt": None,
        }
        mocker.patch(
            "app.core.services.comment_service.CommentModel.create",
            return_value=comment_row,
        )
        mocker.patch(
            "app.core.services.comment_service.UserModel.get_by_id",
            return_value={"id": 1, "username": "alice", "avatar": None},
        )
        mocker.patch(
            "app.core.services.comment_service.PhotoModel.get_by_id",
            return_value=None,
        )
        mocker.patch(
            "app.core.services.comment_service.NotificationService.send",
            return_value=None,
        )

        success, msg, data = CommentService.add_comment(
            user_id=1, photo_id=1, text=max_text
        )
        assert success is True
        assert data is not None
