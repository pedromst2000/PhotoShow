"""
Unit tests for NotificationModel.

Covers to_dict, get_by_user, get_unread_count, mark_read, mark_all_read,
create, delete, and delete_by_* class methods.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.db.engine import Base
from app.core.db.models.notification import NotificationModel
from app.core.db.models.notification_types import NotificationTypeModel
from app.core.db.models.role import RoleModel
from app.core.db.models.user import UserModel


@pytest.fixture
def test_db():
    """Create an isolated in-memory SQLite DB with all tables and seed data."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Seed roles
    session.add_all(
        [
            RoleModel(id=1, role="admin"),
            RoleModel(id=2, role="regular"),
            RoleModel(id=3, role="unsigned"),
        ]
    )
    # Seed a notification type
    session.add(
        NotificationTypeModel(
            id=1, type="like_photo", label="liked your photo", isEnabled=True
        )
    )
    session.add(
        NotificationTypeModel(
            id=2, type="comment_on_photo", label="commented", isEnabled=True
        )
    )
    session.add(
        NotificationTypeModel(
            id=3, type="new_follower", label="new follower", isEnabled=True
        )
    )
    session.add(
        NotificationTypeModel(
            id=4, type="album_favorited", label="favorited", isEnabled=True
        )
    )
    # Seed two users
    session.add(
        UserModel(
            id=1, username="sender", email="sender@example.com", password="pw", roleId=2
        )
    )
    session.add(
        UserModel(
            id=2,
            username="recipient",
            email="recipient@example.com",
            password="pw",
            roleId=2,
        )
    )
    session.commit()

    yield session
    session.close()
    engine.dispose()


def _create_notification(
    session, recipient_id=2, sender_id=1, type_id=1, message="test", **kwargs
):
    """Helper to create a NotificationModel and flush to get an ID."""
    n = NotificationModel(
        typeId=type_id,
        recipientId=recipient_id,
        senderId=sender_id,
        message=message,
        **kwargs,
    )
    session.add(n)
    session.flush()
    return n


class TestNotificationModelToDict:
    """Tests for NotificationModel.to_dict()."""

    def test_to_dict_has_required_fields(self, test_db):
        n = _create_notification(test_db)
        result = n.to_dict()
        assert "id" in result
        assert "typeId" in result
        assert "recipientId" in result
        assert "senderId" in result
        assert "message" in result
        assert "isRead" in result

    def test_to_dict_is_unread_by_default(self, test_db):
        n = _create_notification(test_db, message="hello")
        result = n.to_dict()
        assert result["isRead"] is False

    def test_to_dict_message_matches(self, test_db):
        n = _create_notification(test_db, message="you got a like")
        result = n.to_dict()
        assert result["message"] == "you got a like"

    def test_to_dict_optional_ids_default_none(self, test_db):
        n = _create_notification(test_db)
        result = n.to_dict()
        assert result["photoId"] is None
        assert result["albumId"] is None
        assert result["commentId"] is None


class TestNotificationModelGetByUser:
    """Tests for NotificationModel.get_by_user()."""

    def test_get_by_user_returns_list(self, test_db):
        _create_notification(test_db, recipient_id=2, message="first")
        _create_notification(test_db, recipient_id=2, message="second")
        test_db.commit()

        results = NotificationModel.get_by_user(test_db, user_id=2)
        assert isinstance(results, list)
        assert len(results) >= 2

    def test_get_by_user_empty_for_unknown(self, test_db):
        results = NotificationModel.get_by_user(test_db, user_id=999)
        assert results == []

    def test_get_by_user_ordered_newest_first(self, test_db):
        _create_notification(test_db, recipient_id=2, message="older")
        test_db.commit()
        _create_notification(test_db, recipient_id=2, message="newer")
        test_db.commit()

        results = NotificationModel.get_by_user(test_db, user_id=2)
        # newest first: second notification's id > first
        assert results[0]["id"] >= results[-1]["id"]


class TestNotificationModelGetUnreadCount:
    """Tests for NotificationModel.get_unread_count()."""

    def test_unread_count_initially_correct(self, test_db):
        _create_notification(test_db, recipient_id=2)
        _create_notification(test_db, recipient_id=2)
        test_db.commit()

        count = NotificationModel.get_unread_count(test_db, user_id=2)
        assert count >= 2

    def test_unread_count_zero_for_no_notifications(self, test_db):
        count = NotificationModel.get_unread_count(test_db, user_id=999)
        assert count == 0

    def test_unread_count_excludes_read(self, test_db):
        n = _create_notification(test_db, recipient_id=2)
        n.isRead = True
        test_db.commit()

        count = NotificationModel.get_unread_count(test_db, user_id=2)
        assert count == 0


class TestNotificationModelMarkRead:
    """Tests for NotificationModel.mark_read()."""

    def test_mark_read_returns_true_when_found(self, test_db):
        n = _create_notification(test_db)
        test_db.commit()

        result = NotificationModel.mark_read(test_db, notID=n.id)
        assert result is True
        assert n.isRead is True

    def test_mark_read_returns_false_when_not_found(self, test_db):
        result = NotificationModel.mark_read(test_db, notID=99999)
        assert result is False


class TestNotificationModelMarkAllRead:
    """Tests for NotificationModel.mark_all_read()."""

    def test_mark_all_read_sets_all_unread_to_read(self, test_db):
        _create_notification(test_db, recipient_id=2)
        _create_notification(test_db, recipient_id=2)
        test_db.commit()

        NotificationModel.mark_all_read(test_db, user_id=2)
        test_db.commit()

        count = NotificationModel.get_unread_count(test_db, user_id=2)
        assert count == 0

    def test_mark_all_read_no_error_when_none(self, test_db):
        # Should not raise even if no notifications exist
        NotificationModel.mark_all_read(test_db, user_id=999)


class TestNotificationModelCreate:
    """Tests for NotificationModel.create()."""

    def test_create_returns_dict(self, test_db):
        result = NotificationModel.create(
            test_db,
            type_id=1,
            message="liked your photo",
            user_id=2,
            sender_id=1,
        )
        assert isinstance(result, dict)
        assert result["message"] == "liked your photo"
        assert result["recipientId"] == 2

    def test_create_with_optional_photo_id(self, test_db):
        result = NotificationModel.create(
            test_db,
            type_id=1,
            message="liked",
            user_id=2,
            sender_id=1,
            photo_id=None,
        )
        assert result["photoId"] is None

    def test_create_increments_count(self, test_db):
        before = NotificationModel.get_unread_count(test_db, user_id=2)
        NotificationModel.create(
            test_db, type_id=1, message="msg", user_id=2, sender_id=1
        )
        test_db.commit()
        after = NotificationModel.get_unread_count(test_db, user_id=2)
        assert after == before + 1


class TestNotificationModelDelete:
    """Tests for NotificationModel.delete()."""

    def test_delete_returns_true_when_found(self, test_db):
        n = _create_notification(test_db)
        test_db.commit()

        result = NotificationModel.delete(test_db, not_id=n.id)
        assert result is True

    def test_delete_returns_false_when_not_found(self, test_db):
        result = NotificationModel.delete(test_db, not_id=99999)
        assert result is False

    def test_delete_removes_from_db(self, test_db):
        n = _create_notification(test_db)
        test_db.commit()
        nid = n.id

        NotificationModel.delete(test_db, not_id=nid)
        test_db.commit()

        found = test_db.query(NotificationModel).filter_by(id=nid).first()
        assert found is None


class TestNotificationModelDeleteByPhoto:
    """Tests for NotificationModel.delete_by_photo_id()."""

    def test_delete_by_photo_id_returns_count(self, test_db):
        # Add photo FK manually
        n = NotificationModel(
            typeId=1, recipientId=2, senderId=1, message="x", photoId=42
        )
        test_db.add(n)
        test_db.commit()

        count = NotificationModel.delete_by_photo_id(test_db, photo_id=42)
        assert count >= 1

    def test_delete_by_photo_id_zero_if_none(self, test_db):
        count = NotificationModel.delete_by_photo_id(test_db, photo_id=9999)
        assert count == 0


class TestNotificationModelDeleteByAlbum:
    """Tests for NotificationModel.delete_by_album_id()."""

    def test_delete_by_album_id_returns_count(self, test_db):
        n = NotificationModel(
            typeId=1, recipientId=2, senderId=1, message="fav", albumId=10
        )
        test_db.add(n)
        test_db.commit()

        count = NotificationModel.delete_by_album_id(test_db, album_id=10)
        assert count >= 1

    def test_delete_by_album_id_zero_if_none(self, test_db):
        count = NotificationModel.delete_by_album_id(test_db, album_id=9999)
        assert count == 0


class TestNotificationModelDeleteByLike:
    """Tests for NotificationModel.delete_by_like()."""

    def test_delete_by_like_returns_zero_if_type_missing(self, test_db):
        # Remove the like_photo type
        t = test_db.query(NotificationTypeModel).filter_by(type="like_photo").first()
        test_db.delete(t)
        test_db.commit()

        count = NotificationModel.delete_by_like(test_db, user_id=1, photo_id=5)
        assert count == 0

    def test_delete_by_like_deletes_matching(self, test_db):
        type_obj = (
            test_db.query(NotificationTypeModel).filter_by(type="like_photo").first()
        )
        n = NotificationModel(
            typeId=type_obj.id, recipientId=2, senderId=1, message="like", photoId=7
        )
        test_db.add(n)
        test_db.commit()

        count = NotificationModel.delete_by_like(test_db, user_id=1, photo_id=7)
        assert count >= 1


class TestNotificationModelDeleteByComment:
    """Tests for NotificationModel.delete_by_comment()."""

    def test_delete_by_comment_zero_if_type_missing(self, test_db):
        t = (
            test_db.query(NotificationTypeModel)
            .filter_by(type="comment_on_photo")
            .first()
        )
        test_db.delete(t)
        test_db.commit()

        count = NotificationModel.delete_by_comment(test_db, comment_id=5)
        assert count == 0

    def test_delete_by_comment_deletes_matching(self, test_db):
        type_obj = (
            test_db.query(NotificationTypeModel)
            .filter_by(type="comment_on_photo")
            .first()
        )
        n = NotificationModel(
            typeId=type_obj.id,
            recipientId=2,
            senderId=1,
            message="comment",
            commentId=3,
        )
        test_db.add(n)
        test_db.commit()

        count = NotificationModel.delete_by_comment(test_db, comment_id=3)
        assert count >= 1


class TestNotificationModelDeleteByFavorite:
    """Tests for NotificationModel.delete_by_favorite()."""

    def test_delete_by_favorite_zero_if_type_missing(self, test_db):
        t = (
            test_db.query(NotificationTypeModel)
            .filter_by(type="album_favorited")
            .first()
        )
        test_db.delete(t)
        test_db.commit()

        count = NotificationModel.delete_by_favorite(test_db, album_id=5, user_id=1)
        assert count == 0

    def test_delete_by_favorite_deletes_matching(self, test_db):
        type_obj = (
            test_db.query(NotificationTypeModel)
            .filter_by(type="album_favorited")
            .first()
        )
        n = NotificationModel(
            typeId=type_obj.id, recipientId=2, senderId=1, message="fav", albumId=5
        )
        test_db.add(n)
        test_db.commit()

        count = NotificationModel.delete_by_favorite(test_db, album_id=5, user_id=1)
        assert count >= 1


class TestNotificationModelDeleteByFollow:
    """Tests for NotificationModel.delete_by_follow()."""

    def test_delete_by_follow_zero_if_type_missing(self, test_db):
        t = test_db.query(NotificationTypeModel).filter_by(type="new_follower").first()
        test_db.delete(t)
        test_db.commit()

        count = NotificationModel.delete_by_follow(
            test_db, follower_id=1, followed_id=2
        )
        assert count == 0

    def test_delete_by_follow_deletes_matching(self, test_db):
        type_obj = (
            test_db.query(NotificationTypeModel).filter_by(type="new_follower").first()
        )
        n = NotificationModel(
            typeId=type_obj.id, recipientId=2, senderId=1, message="follow"
        )
        test_db.add(n)
        test_db.commit()

        count = NotificationModel.delete_by_follow(
            test_db, follower_id=1, followed_id=2
        )
        assert count >= 1
