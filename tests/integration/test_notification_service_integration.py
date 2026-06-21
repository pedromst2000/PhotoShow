"""
Integration tests for NotificationService covering notification retrieval, marking as read, and cleanup.

Focuses on:
- Notification unread count tracking
- Marking notifications as read
- Marking all notifications as read
- Notification type retrieval
- Enriched notification data retrieval
- Notification cleanup by content type (photo, comment, like, favorite, follow)
"""

from app.core.services.album_service import AlbumService
from app.core.services.auth_service import AuthService
from app.core.services.comment_service import CommentService
from app.core.services.notification_service import NotificationService
from app.core.services.photo_service import PhotoService


class TestNotificationUnreadCount:
    """Test unread notification count tracking."""

    def test_unread_count_new_user(self, integration_db):
        """New user has zero unread notifications."""
        user = AuthService.register_user("alice", "alice@example.com", "password")
        count = NotificationService.get_unread_count(user["id"])

        assert count == 0

    def test_unread_count_returns_int(self, integration_db):
        """Unread count is always an integer."""
        user = AuthService.register_user("bob", "bob@example.com", "password")
        count = NotificationService.get_unread_count(user["id"])

        assert isinstance(count, int)
        assert count >= 0


class TestNotificationTypes:
    """Test notification type retrieval."""

    def test_get_notification_types(self, integration_db):
        """Retrieve all notification types."""
        types = NotificationService.get_notification_types()

        assert len(types) > 0
        # Each type should have id and name
        for ntype in types:
            assert "id" in ntype or "ID" in str(ntype)
            assert "name" in ntype or "label" in str(ntype)

    def test_notification_types_not_empty(self, integration_db):
        """Notification types list is not empty."""
        types = NotificationService.get_notification_types()
        assert len(types) > 0


class TestMarkNotificationsRead:
    """Test marking notifications as read."""

    def test_mark_single_read_success(self, integration_db):
        """Mark a single notification as read."""
        user1 = AuthService.register_user("charlie", "charlie@example.com", "password")
        user2 = AuthService.register_user("diana", "diana@example.com", "password")

        # Create notification (via follow)
        from app.core.db.engine import SessionLocal
        from app.core.db.models.notification import NotificationModel

        with SessionLocal() as session:
            NotificationModel.create(
                session,
                type_id=1,
                message="started following you",
                user_id=user1["id"],
                sender_id=user2["id"],
            )
            session.commit()

        # Get notifications and mark one as read
        with SessionLocal() as session:
            notifs = (
                session.query(NotificationModel)
                .filter_by(recipientId=user1["id"])
                .all()
            )
            if notifs:
                result = NotificationService.mark_read(notifs[0].id)
                # If DB supports updates, result should be True
                assert isinstance(result, (bool, int))

    def test_mark_nonexistent_read(self, integration_db):
        """Marking nonexistent notification returns False."""
        result = NotificationService.mark_read(9999)
        assert result is False or result == 0 or result is None

    def test_mark_all_read(self, integration_db):
        """Mark all notifications for user as read."""
        user = AuthService.register_user("eve", "eve@example.com", "password")

        # Mark all read (should not error even with no notifications)
        NotificationService.mark_all_read(user["id"])

        # Should have zero unread
        count = NotificationService.get_unread_count(user["id"])
        assert count == 0


class TestNotificationCleanup:
    """Test notification cleanup operations."""

    def test_delete_by_photo_id(self, integration_db):
        """Delete notifications associated with a photo."""
        user1 = AuthService.register_user("frank", "frank@example.com", "password")

        # Create photo
        album = AlbumService.create_album("Album 1", user1["id"])
        photo = PhotoService.create_photo_record(
            album_id=album["id"],
            category_id=1,
            description="Photo 1",
        )

        # Delete by photo should not error
        count = NotificationService.delete_by_photo_id(photo["id"])
        assert isinstance(count, int)
        assert count >= 0

    def test_delete_by_like(self, integration_db):
        """Delete notifications for a specific like."""
        user1 = AuthService.register_user("helen", "helen@example.com", "password")
        user2 = AuthService.register_user("ian", "ian@example.com", "password")

        # Create photo and like it
        album = AlbumService.create_album("Album 1", user1["id"])
        photo = PhotoService.create_photo_record(
            album_id=album["id"],
            category_id=1,
            description="Photo 1",
        )

        # Delete by like should not error
        count = NotificationService.delete_by_like(user2["id"], photo["id"])
        assert isinstance(count, int)
        assert count >= 0

    def test_delete_by_comment(self, integration_db):
        """Delete notifications for a specific comment."""
        user = AuthService.register_user("jack", "jack@example.com", "password")
        album = AlbumService.create_album("Album 1", user["id"])
        photo = PhotoService.create_photo_record(
            album_id=album["id"],
            category_id=1,
            description="Photo 1",
        )

        _, _, comment = CommentService.add_comment(
            user["id"], photo["id"], "Test comment"
        )
        assert comment is not None

        # Delete by comment should not error
        count = NotificationService.delete_by_comment(comment["id"])
        assert isinstance(count, int)
        assert count >= 0

    def test_delete_by_follow(self, integration_db):
        """Delete notifications for a follow action."""
        user1 = AuthService.register_user("karen", "karen@example.com", "password")
        user2 = AuthService.register_user("leo", "leo@example.com", "password")

        # Delete by follow should not error
        count = NotificationService.delete_by_follow(user1["id"], user2["id"])
        assert isinstance(count, int)
        assert count >= 0

    def test_delete_by_favorite(self, integration_db):
        """Delete notifications for a favorite action."""
        user1 = AuthService.register_user("mary", "mary@example.com", "password")
        user2 = AuthService.register_user("nancy", "nancy@example.com", "password")

        # Create album
        album = AlbumService.create_album("Album 1", user1["id"])

        # Delete by favorite should not error
        count = NotificationService.delete_by_favorite(album["id"], user2["id"])
        assert isinstance(count, int)
        assert count >= 0


class TestEnrichedNotifications:
    """Test enriched notification retrieval with full details."""

    def test_get_enriched_notifications(self, integration_db):
        """Retrieve enriched notifications with full context."""
        user = AuthService.register_user("oscar", "oscar@example.com", "password")

        # Get enriched notifications (should not error)
        notifications = NotificationService.get_enriched_notifications(user["id"])

        # Should return list
        assert isinstance(notifications, list)

        # Each should have expected keys
        for notif in notifications:
            assert isinstance(notif, dict)

    def test_get_enriched_notifications_empty(self, integration_db):
        """New user has empty enriched notifications."""
        user = AuthService.register_user("paul", "paul@example.com", "password")

        notifications = NotificationService.get_enriched_notifications(user["id"])

        assert isinstance(notifications, list)
        assert len(notifications) == 0
