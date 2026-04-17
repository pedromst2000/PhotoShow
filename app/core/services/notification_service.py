from typing import Optional

from app.core.db.engine import SessionLocal
from app.core.db.models.notification import NotificationModel
from app.core.db.models.notification_types import NotificationTypeModel
from app.utils.log_utils import log_exception, log_operation


class NotificationService:
    """
    Service class for notification business logic.

    Business rules enforced:
    - Notifications are only created if their type is enabled in notification_types.
    - The service method abstracts away the need for controllers to check notification type status.
    """

    # ========== Read Operations ==========

    @staticmethod
    def get_my_notifications(user_id: int) -> list[dict]:
        """
        Retrieve notifications for a specific user.

        Args:
            user_id: The ID of the user.

        Returns:
            List[dict]: List of notification dictionaries for the user.

        Raises:
            Exception: Any database error is caught and logged; empty list returned.
        """
        try:
            with SessionLocal() as session:
                notifications = NotificationModel.get_by_user(session, user_id)
            log_operation(
                "notification.get_my_notifications",
                "success",
                f"Retrieved {len(notifications)} notifications",
                user_id=user_id,
            )
            return notifications
        except Exception as e:
            log_exception("notification.get_my_notifications", e, user_id=user_id)
            return []

    @staticmethod
    def get_unread_count(user_id: int) -> int:
        """
        Get the count of unread notifications for a user.

        Args:
            user_id: The ID of the user.

        Returns:
            int: Number of unread notifications.

        Raises:
            Exception: Any database error is caught and logged; 0 returned.
        """
        try:
            with SessionLocal() as session:
                count = NotificationModel.get_unread_count(session, user_id)
            return count
        except Exception as e:
            log_exception("notification.get_unread_count", e, user_id=user_id)
            return 0

    @staticmethod
    def get_notification_types() -> list[dict]:
        """
        Retrieve all notification types.

        Returns:
            List[dict]: List of notification type dictionaries.

        Raises:
            Exception: Any database error is caught and logged; empty list returned.
        """
        try:
            with SessionLocal() as session:
                types = NotificationTypeModel.get_all(session)
            log_operation(
                "notification.get_notification_types",
                "success",
                f"Retrieved {len(types)} notification types",
            )
            return types
        except Exception as e:
            log_exception("notification.get_notification_types", e)
            return []

    # ========== Write Operations ==========

    @staticmethod
    def mark_read(not_id: int) -> bool:
        """
        Mark a notification as read.

        Args:
            not_id: The ID of the notification to mark as read.

        Returns:
            bool: True if successful, False otherwise.

        Raises:
            Exception: Any database error is caught and logged; False returned.
        """
        try:
            with SessionLocal() as session:
                result = NotificationModel.mark_read(session, not_id)
                session.commit()
            if result:
                log_operation(
                    "notification.mark_read",
                    "success",
                    f"Marked notification {not_id} as read",
                )
            return result
        except Exception as e:
            log_exception(
                "notification.mark_read", e, context={"notification_id": not_id}
            )
            return False

    @staticmethod
    def mark_all_read(user_id: int) -> None:
        """
        Mark all notifications as read for a user.

        Args:
            user_id: The ID of the user.

        Raises:
            Exception: Any database error is caught and logged (does not raise).
        """
        try:
            with SessionLocal() as session:
                NotificationModel.mark_all_read(session, user_id)
                session.commit()
            log_operation(
                "notification.mark_all_read",
                "success",
                "Marked all notifications as read",
                user_id=user_id,
            )
        except Exception as e:
            log_exception("notification.mark_all_read", e, user_id=user_id)

    @staticmethod
    def toggle_type(type_key: str, enabled: bool) -> bool:
        """
        Enable or disable a notification type.

        Returns:
            bool: True if the type was found and updated, False otherwise.
        """
        with SessionLocal() as session:
            result = NotificationTypeModel.set_enabled(session, type_key, enabled)
            session.commit()
            return result

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
            Optional[dict]: The created notification as a dict, or None if the type is disabled or unknown.

        Raises:
            Exception: Any database error is caught and logged; None returned.
        """
        try:
            with SessionLocal() as session:
                nt = NotificationTypeModel.get_by_type(session, type_key)
                if not nt or not nt["isEnabled"]:
                    log_operation(
                        "notification.send",
                        "validation_error",
                        f"Notification type '{type_key}' is disabled or not found",
                        user_id=user_id,
                    )
                    return None

                result = NotificationModel.create(
                    session,
                    type_id=nt["id"],
                    message=message,
                    user_id=user_id,
                    sender_id=sender_id,
                    photo_id=photo_id,
                    album_id=album_id,
                    comment_id=comment_id,
                )
                session.commit()
            log_operation(
                "notification.send",
                "success",
                f"Sent notification type '{type_key}' to user {user_id}",
                user_id=user_id,
            )
            return result
        except Exception as e:
            log_exception(
                "notification.send", e, user_id=user_id, context={"type_key": type_key}
            )
            return None
