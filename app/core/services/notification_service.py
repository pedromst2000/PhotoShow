from typing import Optional

from app.core.db.models import NotificationModel
from app.core.db.models.notification_types import NotificationTypeModel


class NotificationService:

    # ── Notification instances ────────────────────────────────────────────────

    @staticmethod
    def get_for_user(user_id: int) -> list:
        """
        Get all notifications for a user, ordered by most recent first.

        Args:
            user_id (int): The ID of the user to get notifications for.
        Returns:
            list: A list of notification dicts for the user.
        """

        return NotificationModel.get_by_user(user_id)

    @staticmethod
    def get_unread_count(user_id: int) -> int:
        """
        Get the count of unread notifications for a user.

        Args:
            user_id (int): The ID of the user to get unread notifications for.
        Returns:
            int: The count of unread notifications for the user.
        """

        return NotificationModel.get_unread_count(user_id)

    @staticmethod
    def mark_read(not_id: int) -> bool:
        """
        Mark a notification as read.

        Args:
            not_id (int): The ID of the notification to mark as read.
        Returns:
            bool: True if the notification was successfully marked as read, False otherwise.
        """

        return NotificationModel.mark_read(not_id)

    @staticmethod
    def mark_all_read(user_id: int) -> None:
        """
        Mark all notifications for a user as read.
        Args:
            user_id (int): The ID of the user to mark all notifications as read.
        """

        NotificationModel.mark_all_read(user_id)

    @staticmethod
    def send(
        type_key: str,
        message: str,
        user_id: int,
        sender_id: int,
        photo_id: Optional[int] = None,
        album_id: Optional[int] = None,
        comment_id: Optional[int] = None,
    ) -> Optional[dict]:
        """
        Create a notification only if the type is enabled in notification_types.

        Args:
            type_key (str): The type string of the notification (e.g. 'daily_content').
            message (str): The message content of the notification.
            user_id (int): The ID of the user to receive the notification.
            sender_id (int): The ID of the user who triggered the notification (required).
            photo_id (int, optional): FK to photos.id — set when the notification targets a photo.
            album_id (int, optional): FK to albuns.id — set when the notification targets an album.
            comment_id (int, optional): FK to comments.id — set when the notification targets a comment.

        Returns:
            dict: The created notification as a dict, or None if the type is disabled or unknown.
        """
        nt = NotificationTypeModel.get_by_type(type_key)
        if not nt or not nt["isEnabled"]:
            return None

        return NotificationModel.create(
            type_id=nt["id"],
            message=message,
            user_id=user_id,
            sender_id=sender_id,
            photo_id=photo_id,
            album_id=album_id,
            comment_id=comment_id,
        )

    # ── Notification types (admin) ─────────────────────────────────────────────

    @staticmethod
    def get_all_types() -> list:
        """
        Get all notification types.

        Returns:
            list: A list of all notification types as dicts.
        """

        return NotificationTypeModel.get_all()

    @staticmethod
    def toggle_type(type_key: str, enabled: bool) -> bool:
        """
        Enable or disable a notification type.

        Args:
            type_key (str): The key of the notification type to toggle (e.g. 'daily_content').
            enabled (bool): True to enable the notification type, False to disable it.

        Returns:
            bool: True if the setting was successfully updated, False otherwise.
        """

        return NotificationTypeModel.set_enabled(type_key, enabled)

    @staticmethod
    def is_type_enabled(type_key: str) -> bool:
        """
        Check if a notification type is enabled.

        Args:
            type_key (str): The key of the notification type to check (e.g. 'daily_content').
        Returns:
            bool: True if the notification type is enabled, False otherwise.
        """

        return NotificationTypeModel.is_enabled(type_key)
