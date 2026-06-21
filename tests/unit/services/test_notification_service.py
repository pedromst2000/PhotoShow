"""
Unit tests for NotificationService.
"""

from app.core.services.notification_service import NotificationService


def _mock_session(mocker):
    mock_session = mocker.MagicMock()
    mock_cm = mocker.MagicMock()
    mock_cm.__enter__ = mocker.MagicMock(return_value=mock_session)
    mock_cm.__exit__ = mocker.MagicMock(return_value=False)
    mocker.patch(
        "app.core.services.notification_service.SessionLocal",
        return_value=mock_cm,
    )
    return mock_session


class TestGetUnreadCount:
    def test_returns_zero_on_db_exception(self, mocker):
        """Any DB error is swallowed and 0 is returned safely."""
        mocker.patch(
            "app.core.services.notification_service.SessionLocal",
            side_effect=Exception("DB unavailable"),
        )
        result = NotificationService.get_unread_count(user_id=1)
        assert result == 0

    def test_delegates_to_model(self, mocker):
        _mock_session(mocker)
        mocker.patch(
            "app.core.services.notification_service.NotificationModel.get_unread_count",
            return_value=7,
        )
        result = NotificationService.get_unread_count(user_id=1)
        assert result == 7


class TestSend:
    def test_disabled_type_returns_none(self, mocker):
        """Notification is not created when its type is disabled."""
        _mock_session(mocker)
        mocker.patch(
            "app.core.services.notification_service.NotificationTypeModel.get_by_type",
            return_value={"type": "like_photo", "isEnabled": False},
        )
        result = NotificationService.send(
            type_key="like_photo",
            message="liked your photo",
            user_id=2,
            sender_id=1,
        )
        assert result is None

    def test_unknown_type_returns_none(self, mocker):
        """Unknown type key causes send() to return None."""
        _mock_session(mocker)
        mocker.patch(
            "app.core.services.notification_service.NotificationTypeModel.get_by_type",
            return_value=None,
        )
        result = NotificationService.send(
            type_key="nonexistent_event",
            message="test",
            user_id=2,
            sender_id=1,
        )
        assert result is None

    def test_enabled_type_creates_notification(self, mocker):
        """Enabled type triggers NotificationModel.create."""
        _mock_session(mocker)
        mocker.patch(
            "app.core.services.notification_service.NotificationTypeModel.get_by_type",
            return_value={"id": 1, "type": "like_photo", "isEnabled": True},
        )
        created = {
            "id": 1,
            "typeId": 1,
            "message": "liked your photo",
            "userId": 2,
            "senderId": 1,
        }
        mocker.patch(
            "app.core.services.notification_service.NotificationModel.create",
            return_value=created,
        )
        result = NotificationService.send(
            type_key="like_photo",
            message="liked your photo",
            user_id=2,
            sender_id=1,
        )
        assert result is not None
        assert result["id"] == 1
