from typing import List, Tuple

from app.core.services.notification_service import NotificationService
from app.core.state.session import session
from app.utils.log_utils import log_exception, log_operation


class NotificationController:
    """
    Controller for user notifications and admin notification settings.

    Coordinates between views and models/services for:
    - Retrieving user notifications
    - Marking notifications as read
    - Toggling notification types (admin)
    """

    # ── User notifications ────────────────────────────────────────────────────

    @staticmethod
    def get_my_notifications() -> List[dict]:
        """
        Retrieve notifications for the currently logged-in user.

        Returns:
            List[dict]: List of notification dictionaries, or empty list if not authenticated.
        """
        if session.user_id is None:
            return []
        return NotificationService.get_my_notifications(session.user_id)

    @staticmethod
    def get_unread_count() -> int:
        """
        Get the count of unread notifications for the currently logged-in user.

        Returns:
            int: Number of unread notifications, or 0 if not authenticated.
        """
        if session.user_id is None:
            return 0
        return NotificationService.get_unread_count(session.user_id)

    @staticmethod
    def mark_read(not_id: int) -> Tuple[bool, str]:
        """
        Mark a specific notification as read.

        Args:
            not_id (int): The ID of the notification to mark as read.

        Returns:
            Tuple[bool, str]: (success, message)

        Raises:
            Exception: Any unexpected error during marking is caught and logged.
        """
        try:
            if NotificationService.mark_read(not_id):
                log_operation(
                    "notification.mark_read",
                    "success",
                    f"Notification {not_id} marked as read",
                )
                return True, "Notification marked as read"
            log_operation(
                "notification.mark_read",
                "validation_error",
                f"Notification {not_id} not found",
            )
            return False, "Notification not found"
        except Exception as e:
            log_exception(
                "notification.mark_read", e, context={"notification_id": not_id}
            )
            return False, "Something went wrong. Please try again later."

    @staticmethod
    def mark_all_read() -> Tuple[bool, str]:
        """
        Mark all notifications as read for the currently logged-in user.

        Returns:
            Tuple[bool, str]: (success, message)

        Raises:
            Exception: Any unexpected error during marking is caught and logged.
        """
        assert session.user_id is not None
        try:
            NotificationService.mark_all_read(session.user_id)
            log_operation(
                "notification.mark_all_read",
                "success",
                "All notifications marked as read",
                user_id=session.user_id,
            )
            return True, "All notifications marked as read"
        except Exception as e:
            log_exception("notification.mark_all_read", e, user_id=session.user_id)
            return False, "Something went wrong. Please try again later."

    # ── Admin: notification settings ──────────────────────────────────────────

    @staticmethod
    def get_types() -> List[dict]:
        """
        Retrieve all notification types (admin only).

        Returns:
            List[dict]: List of notification type dictionaries, or empty list if not admin.
        """
        return NotificationService.get_notification_types()

    @staticmethod
    def toggle_notification_type(type_key: str, enabled: bool) -> Tuple[bool, str]:
        """
        Toggle a specific notification type on or off (admin only).

        Args:
            type_key (str): The key of the notification type to toggle.
            enabled (bool): True to enable, False to disable.

        Returns:
            Tuple[bool, str]: (success, message)

        Raises:
            Exception: Any unexpected error during toggle operation is caught and logged.
        """
        if not type_key:
            log_operation(
                "notification.toggle_notification_type",
                "validation_error",
                "Notification type is required",
            )
            return False, "Notification type is required"
        try:
            if NotificationService.toggle_type(type_key, enabled):
                state = "enabled" if enabled else "disabled"
                log_operation(
                    "notification.toggle_notification_type",
                    "success",
                    f"Notification type '{type_key}' {state}",
                )
                return True, f"Notifications for '{type_key}' are now {state}"
            log_operation(
                "notification.toggle_notification_type",
                "validation_error",
                f"Notification type '{type_key}' not found",
            )
            return False, f"Notification type '{type_key}' not found"
        except Exception as e:
            log_exception(
                "notification.toggle_notification_type",
                e,
                context={"type_key": type_key, "enabled": enabled},
            )
            return False, "Something went wrong. Please try again later."
