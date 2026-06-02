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
        """
        if NotificationService.mark_read(not_id):
            return True, "Notification marked as read"
        return False, "Notification not found"

    @staticmethod
    def mark_all_read() -> Tuple[bool, str]:
        """
        Mark all notifications as read for the currently logged-in user.

        Returns:
            Tuple[bool, str]: (success, message)
        """
        if session.user_id is None:
            return False, "Not authenticated"
        NotificationService.mark_all_read(session.user_id)
        return True, "All notifications marked as read"

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

    # ── Enriched / window helpers ─────────────────────────────────────────────

    @staticmethod
    def ensure_types_seeded() -> None:
        """Ensure all canonical notification types exist in the database."""
        NotificationService.ensure_types_seeded()

    @staticmethod
    def get_enriched(*, unread_only: bool = False) -> List[dict]:
        """Return enriched notifications (with sender info and type label).

        Args:
            unread_only: When True, only unread notifications are returned.

        Returns:
            List[dict]: Enriched notification dicts, newest first.
        """
        if session.user_id is None:
            return []
        return NotificationService.get_enriched_notifications(
            session.user_id, unread_only=unread_only
        )

    @staticmethod
    def delete_by_photo(photo_id: int) -> int:
        """Delete all notifications referencing *photo_id* from the database.

        Must be called **before** the photo is deleted so the FK is still set.

        Args:
            photo_id: ID of the photo whose notifications to remove.

        Returns:
            int: Number of notifications deleted.
        """
        return NotificationService.delete_by_photo_id(photo_id)

    @staticmethod
    def delete_by_like(user_id: int, photo_id: int) -> int:
        """Delete like_photo notification when a user unlikes a photo.

        Args:
            user_id: The user who unliked the photo.
            photo_id: The photo being unliked.

        Returns:
            int: Number of notifications deleted.
        """
        return NotificationService.delete_by_like(user_id, photo_id)

    @staticmethod
    def delete_by_comment(comment_id: int) -> int:
        """Delete comment_on_photo notification when a comment is deleted.

        Args:
            comment_id: The comment being deleted.

        Returns:
            int: Number of notifications deleted.
        """
        return NotificationService.delete_by_comment(comment_id)

    @staticmethod
    def delete_by_favorite(album_id: int, user_id: int) -> int:
        """Delete album_favorited notification when a user removes an album from favorites.

        Args:
            album_id: The album being unfavorited.
            user_id: The user removing from favorites.

        Returns:
            int: Number of notifications deleted.
        """
        return NotificationService.delete_by_favorite(album_id, user_id)

    @staticmethod
    def delete_by_follow(follower_id: int, followed_id: int) -> int:
        """Delete new_follower notification when a user unfollows.

        Args:
            follower_id: The user who unfollowed.
            followed_id: The user being unfollowed.

        Returns:
            int: Number of notifications deleted.
        """
        return NotificationService.delete_by_follow(follower_id, followed_id)
