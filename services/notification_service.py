from typing import Optional

from db.models import NotificationModel
from db.models.notification_settings import NotificationSettingsModel


class NotificationService:

    # ── Notification instances ────────────────────────────────────────────────

    @staticmethod
    def get_for_user(user_id: int) -> list:
        """
        Get all notifications for a user, ordered by most recent first.

        Parameters:
            user_id (int): The ID of the user to get notifications for.
        Returns:
            list: A list of notification dicts for the user.
        """

        return NotificationModel.get_by_user(user_id)

    @staticmethod
    def get_unread_count(user_id: int) -> int:
        """
        Get the count of unread notifications for a user.

        Parameters:
            user_id (int): The ID of the user to get unread notifications for.
        Returns:
            int: The count of unread notifications for the user.
        """

        return NotificationModel.get_unread_count(user_id)

    @staticmethod
    def mark_read(not_id: int) -> bool:
        """
        Mark a notification as read.

        Parameters:
            not_id (int): The ID of the notification to mark as read.
        Returns:
            bool: True if the notification was successfully marked as read, False otherwise.
        """

        return NotificationModel.mark_read(not_id)

    @staticmethod
    def mark_all_read(user_id: int) -> None:
        """
        Mark all notifications for a user as read.
        Parameters:
            user_id (int): The ID of the user to mark all notifications as read.
        Returns:
            None
        """

        NotificationModel.mark_all_read(user_id)

    @staticmethod
    def send(
        type_key: str,
        message: str,
        user_id: int,
        sender_id: int = None,
        reference_id: int = None,
        reference_type: str = None,
    ) -> Optional[dict]:
        """
        Create a notification only if the type is enabled in notification_settings.

        Parameters:
            type_key (str): The type of the notification (e.g. "new_comment", "photo_liked").
            message (str): The message content of the notification.
            user_id (int): The ID of the user to receive the notification.
            sender_id (int, optional): The ID of the user who triggered the notification (e.g. the commenter or liker). Defaults to None.
            reference_id (int, optional): An optional ID referencing the related object (e.g. comment ID, photo ID). Defaults to None.
            reference_type (str, optional): An optional string describing the type of the reference (e.g. "comment", "photo"). Defaults to None.

        Returns:
            dict: The created notification as a dict, or None if the notification type is disabled.
        """
        if not NotificationSettingsModel.is_enabled(type_key):
            return None
        return NotificationModel.create(
            type=type_key,
            message=message,
            user_id=user_id,
            sender_id=sender_id,
            reference_id=reference_id,
            reference_type=reference_type,
        )

    # ── Notification settings (admin) ─────────────────────────────────────────

    @staticmethod
    def get_all_settings() -> list:
        """
        Get all notification settings.

        Returns:
            list: A list of all notification settings as dicts.
        """

        return NotificationSettingsModel.get_all()

    @staticmethod
    def toggle_setting(type_key: str, enabled: bool) -> bool:
        """
        Enable or disable a notification type.

        Parameters:
            type_key (str): The key of the notification type to toggle (e.g. "new_comment", "photo_liked").
            enabled (bool): True to enable the notification type, False to disable it.

        Returns:
            bool: True if the setting was successfully updated, False otherwise.
        """

        return NotificationSettingsModel.set_enabled(type_key, enabled)

    @staticmethod
    def is_type_enabled(type_key: str) -> bool:
        """
        Check if a notification type is enabled.

        Parameters:
            type_key (str): The key of the notification type to check (e.g. "new_comment", "photo_liked").
        Returns:
            bool: True if the notification type is enabled, False otherwise.
        """

        return NotificationSettingsModel.is_enabled(type_key)
