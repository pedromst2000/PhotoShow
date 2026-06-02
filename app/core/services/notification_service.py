from typing import List, Optional

from app.core.db.engine import SessionLocal
from app.core.db.models.avatar import AvatarModel
from app.core.db.models.notification import NotificationModel
from app.core.db.models.notification_types import NotificationTypeModel
from app.core.db.models.user import UserModel
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
    def send(
        type_key: str,
        message: str,
        user_id: int,
        sender_id: int,
        photo_id: Optional[int] = None,
        album_id: Optional[int] = None,
        comment_id: Optional[int] = None,
    ) -> Optional[dict]:
        """Create a notification only if the type is enabled in notification_types.

        Args:
            type_key: The type key (e.g. 'like_photo').
            message: Human-readable message body.
            user_id: The recipient user ID.
            sender_id: The user who triggered the notification.
            photo_id: FK to photos.id (optional).
            album_id: FK to albuns.id (optional).
            comment_id: FK to comments.id (optional).

        Returns:
            Optional[dict]: The created notification dict, or None if type disabled/error.
        """
        try:
            with SessionLocal() as session:
                nt = NotificationTypeModel.get_by_type(session, type_key)
                if not nt or not nt["isEnabled"]:
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
            return result
        except Exception as e:
            log_exception(
                "notification.send", e, user_id=user_id, context={"type_key": type_key}
            )
            return None

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

    # ========== Enriched Read ==========

    # Canonical notification types: only the triggers defined in the requirements.
    # Format: (type_key, label)  — IDs are NOT stored here; the CSV/migration
    # handles IDs for fresh installs and ensure_types_seeded inserts by type key.
    _CANONICAL_TYPES: List[tuple] = [
        ("comment_on_photo", "commented on your photo"),
        ("like_photo", "liked your photo"),
        ("album_favorited", "added your album to favorites"),
        ("new_follower", "started following you"),
        ("admin_delete_comment", "Your comment was deleted by an admin"),
        ("admin_delete_photo", "Your photo was deleted by an admin"),
    ]

    @staticmethod
    def ensure_types_seeded() -> None:
        """Sync the database notification types with the canonical list.

        - Deletes any DB rows whose type key is NOT in the canonical list
          (removes stale types from previous schema versions).
        - Inserts any canonical type that does not yet exist (by type key).

        Safe to call at any time — all operations are idempotent.
        """
        try:
            with SessionLocal() as session:
                canonical_keys = {t[0] for t in NotificationService._CANONICAL_TYPES}
                # Remove orphaned types not in the canonical list.
                # These are types that existed in older versions and are now
                # retired (e.g. daily_content, comment_photos, favorite_album).
                session.query(NotificationTypeModel).filter(
                    NotificationTypeModel.type.notin_(canonical_keys)  # type: ignore
                ).delete(synchronize_session=False)
                # Insert any missing canonical types.
                NotificationTypeModel.ensure_types_seeded(
                    session, NotificationService._CANONICAL_TYPES
                )
                session.commit()
        except Exception as e:
            log_exception("notification.ensure_types_seeded", e)

    @staticmethod
    def get_enriched_notifications(
        user_id: int, *, unread_only: bool = False
    ) -> List[dict]:
        """Return notifications enriched with sender username/avatar and type info.

        All sender users and their avatars are fetched in a single batch query
        each (no N+1 queries).

        Args:
            user_id: The recipient user ID.
            unread_only: When True, only unread notifications are returned.

        Returns:
            List[dict]: Enriched notification dicts, newest first.
        """
        try:
            with SessionLocal() as session:
                raw = NotificationModel.get_by_user(session, user_id)
                if unread_only:
                    raw = [n for n in raw if not n["isRead"]]

                if not raw:
                    return []

                # ── Build lookup maps in one query each (no N+1) ──────────────
                types_map = {t["id"]: t for t in NotificationTypeModel.get_all(session)}
                sender_ids = list({n["senderId"] for n in raw if n.get("senderId")})
                users_map = {
                    u.id: u
                    for u in session.query(UserModel)
                    .filter(UserModel.id.in_(sender_ids))  # type: ignore
                    .all()
                }
                avatars_map = {
                    a.userId: a.avatar
                    for a in session.query(AvatarModel)
                    .filter(AvatarModel.userId.in_(sender_ids))  # type: ignore
                    .all()
                }

                # ── Enrich each notification dict ──────────────────────────────
                enriched: List[dict] = []
                for n in raw:
                    item = dict(n)
                    type_info = types_map.get(n["typeId"], {})
                    item["type_key"] = type_info.get("type", "")
                    item["type_label"] = type_info.get("label", "Notification")
                    sender = users_map.get(n.get("senderId"))
                    if sender:
                        item["sender_username"] = sender.username
                        item["sender_avatar"] = avatars_map.get(sender.id)
                    else:
                        item["sender_username"] = "Unknown"
                        item["sender_avatar"] = None
                    enriched.append(item)
            return enriched
        except Exception as e:
            log_exception("notification.get_enriched", e, user_id=user_id)
            return []

    @staticmethod
    def delete_by_photo_id(photo_id: int) -> int:
        """Delete all notifications that reference *photo_id*.

        Call this **before** deleting the photo so FK values are still intact.

        Args:
            photo_id: ID of the photo whose notifications to remove.

        Returns:
            int: Number of notifications deleted (0 on error).
        """
        try:
            with SessionLocal() as session:
                count = NotificationModel.delete_by_photo_id(session, photo_id)
                session.commit()
            log_operation(
                "notification.delete_by_photo_id",
                "success",
                f"Deleted {count} notification(s) for photo {photo_id}",
            )
            return count
        except Exception as e:
            log_exception(
                "notification.delete_by_photo_id",
                e,
                context={"photo_id": photo_id},
            )
            return 0

    @staticmethod
    def delete_by_like(user_id: int, photo_id: int) -> int:
        """Delete like_photo notification when a user unlikes a photo.

        Args:
            user_id: The user who unliked the photo.
            photo_id: The photo being unliked.

        Returns:
            int: Number of notifications deleted (0 on error).
        """
        try:
            with SessionLocal() as session:
                count = NotificationModel.delete_by_like(session, user_id, photo_id)
                session.commit()
            log_operation(
                "notification.delete_by_like",
                "success",
                f"Deleted like notification for photo {photo_id} by user {user_id}",
            )
            return count
        except Exception as e:
            log_exception(
                "notification.delete_by_like",
                e,
                context={"user_id": user_id, "photo_id": photo_id},
            )
            return 0

    @staticmethod
    def delete_by_comment(comment_id: int) -> int:
        """Delete comment_on_photo notification when a comment is deleted.

        Args:
            comment_id: The comment being deleted.

        Returns:
            int: Number of notifications deleted (0 on error).
        """
        try:
            with SessionLocal() as session:
                count = NotificationModel.delete_by_comment(session, comment_id)
                session.commit()
            log_operation(
                "notification.delete_by_comment",
                "success",
                f"Deleted comment notification for comment {comment_id}",
            )
            return count
        except Exception as e:
            log_exception(
                "notification.delete_by_comment",
                e,
                context={"comment_id": comment_id},
            )
            return 0

    @staticmethod
    def delete_by_favorite(album_id: int, user_id: int) -> int:
        """Delete album_favorited notification when a user removes an album from favorites.

        Args:
            album_id: The album being unfavorited.
            user_id: The user removing from favorites.

        Returns:
            int: Number of notifications deleted (0 on error).
        """
        try:
            with SessionLocal() as session:
                count = NotificationModel.delete_by_favorite(session, album_id, user_id)
                session.commit()
            log_operation(
                "notification.delete_by_favorite",
                "success",
                f"Deleted favorite notification for album {album_id} by user {user_id}",
            )
            return count
        except Exception as e:
            log_exception(
                "notification.delete_by_favorite",
                e,
                context={"album_id": album_id, "user_id": user_id},
            )
            return 0

    @staticmethod
    def delete_by_follow(follower_id: int, followed_id: int) -> int:
        """Delete new_follower notification when a user unfollows.

        Args:
            follower_id: The user who unfollowed.
            followed_id: The user being unfollowed.

        Returns:
            int: Number of notifications deleted (0 on error).
        """
        try:
            with SessionLocal() as session:
                count = NotificationModel.delete_by_follow(
                    session, follower_id, followed_id
                )
                session.commit()
            log_operation(
                "notification.delete_by_follow",
                "success",
                f"Deleted follow notification for user {follower_id} unfollowing {followed_id}",
            )
            return count
        except Exception as e:
            log_exception(
                "notification.delete_by_follow",
                e,
                context={"follower_id": follower_id, "followed_id": followed_id},
            )
            return 0
