from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
)
from sqlalchemy.orm import Session

from app.core.db.engine import Base


class NotificationModel(Base):
    """
    NotificationModel represents a notification in the database.

    Polymorphic target: targetType indicates what the notification refers to
    ('photo', 'comment', or 'album') and targetId holds the PK of that resource.
    """

    __tablename__: str = "notifications"

    __table_args__ = (
        CheckConstraint("id > 0 AND id < 10000000", name="ck_notifications_id_range"),
        CheckConstraint(
            "recipientId > 0 AND recipientId < 10000000",
            name="ck_notifications_recipientId_range",
        ),
        CheckConstraint(
            "senderId > 0 AND senderId < 10000000",
            name="ck_notifications_senderId_range",
        ),
        CheckConstraint(
            "length(trim(message)) > 0", name="ck_notifications_message_not_empty"
        ),
        CheckConstraint(
            "photoId IS NULL OR (photoId > 0 AND photoId < 10000000)",
            name="ck_notifications_photoId_null_or_range",
        ),
        CheckConstraint(
            "albumId IS NULL OR (albumId > 0 AND albumId < 10000000)",
            name="ck_notifications_albumId_null_or_range",
        ),
        CheckConstraint(
            "commentId IS NULL OR (commentId > 0 AND commentId < 10000000)",
            name="ck_notifications_commentId_null_or_range",
        ),
        # performance indexes for common queries
        Index("ix_notifications_recipientid_createdat", "recipientId", "createdAt"),
        Index("ix_notifications_recipientid_isread", "recipientId", "isRead"),
    )

    id: int = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    typeId: int = Column(
        Integer,
        ForeignKey("notification_types.id", ondelete="RESTRICT"),
        nullable=False,
    )
    recipientId: int = Column(
        Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )  # recipient
    senderId: int = Column(
        Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )  # who triggered it
    photoId: int = Column(
        Integer, ForeignKey("photos.id", ondelete="SET NULL"), nullable=True
    )
    albumId: int = Column(
        Integer, ForeignKey("albuns.id", ondelete="SET NULL"), nullable=True
    )
    commentId: int = Column(
        Integer, ForeignKey("comments.id", ondelete="SET NULL"), nullable=True
    )
    message: str = Column(String(255), nullable=False)
    isRead: bool = Column(Boolean, default=False, nullable=False)
    createdAt: DateTime = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updatedAt: DateTime = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self) -> dict:
        """
        Convert the NotificationModel instance to a dictionary.

        Returns:
            dict: A dictionary representation of the NotificationModel instance.
        """
        return {
            "id": self.id,
            "typeId": self.typeId,
            "recipientId": self.recipientId,
            "senderId": self.senderId,
            "photoId": self.photoId,
            "albumId": self.albumId,
            "commentId": self.commentId,
            "message": self.message,
            "isRead": self.isRead,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt,
        }

    @classmethod
    def get_by_user(cls, session: Session, user_id: int) -> list[dict]:
        """
        Retrieve all notifications for a specific user (newest first).

        Args:
            session: Active SQLAlchemy session.
            user_id (int): The recipient user ID.

        Returns:
            list[dict]: A list of notification dicts.
        """
        return [
            n.to_dict()
            for n in session.query(cls)
            .filter_by(recipientId=user_id)
            .order_by(cls.createdAt.desc())
            .all()
        ]

    @classmethod
    def get_unread_count(cls, session: Session, user_id: int) -> int:
        """
        Return the number of unread notifications for a user.

        Args:
            session: Active SQLAlchemy session.
            user_id (int): The recipient user ID.

        Returns:
            int: Count of unread notifications.
        """
        return session.query(cls).filter_by(recipientId=user_id, isRead=False).count()

    @classmethod
    def mark_read(cls, session: Session, notID: int) -> bool:
        """
        Mark a single notification as read.

        Args:
            session: Active SQLAlchemy session.
            notID (int): The notification ID.

        Returns:
            bool: True if updated successfully.
        """
        n = session.query(cls).filter_by(id=notID).first()
        if n:
            n.isRead = True
            return True
        return False

    @classmethod
    def mark_all_read(cls, session: Session, user_id: int) -> None:
        """
        Mark all notifications for a user as read.

        Args:
            session: Active SQLAlchemy session.
            user_id (int): The recipient user ID.
        """
        session.query(cls).filter_by(recipientId=user_id, isRead=False).update(
            {"isRead": True}
        )

    @classmethod
    def create(
        cls,
        session: Session,
        type_id: int,
        message: str,
        user_id: int,
        sender_id: int,
        photo_id: Optional[int] = None,
        album_id: Optional[int] = None,
        comment_id: Optional[int] = None,
    ) -> dict:
        """
        Create a new notification.

        Args:
            session: Active SQLAlchemy session.
            type_id (int): FK to notification_types.id.
            message (str): Human-readable notification message (pre-validated).
            user_id (int): The recipient user ID.
            sender_id (int): Who triggered the notification.
            photo_id (int, optional): FK to photos.id.
            album_id (int, optional): FK to albuns.id.
            comment_id (int, optional): FK to comments.id.

        Returns:
            dict: A dictionary representation of the newly created notification.
        """
        obj = cls(
            typeId=type_id,
            message=message,
            recipientId=user_id,
            senderId=sender_id,
            photoId=photo_id,
            albumId=album_id,
            commentId=comment_id,
        )
        session.add(obj)
        session.flush()
        return obj.to_dict()

    @classmethod
    def delete(cls, session: Session, not_id: int) -> bool:
        """
        Delete a notification by ID.

        Args:
            session: Active SQLAlchemy session.
            not_id: The ID of the notification to delete.

        Returns:
            bool: True if the notification was found and deleted, False otherwise.
        """
        n = session.query(cls).filter_by(id=not_id).first()
        if n:
            session.delete(n)
            return True
        return False

    @classmethod
    def delete_by_photo_id(cls, session: Session, photo_id: int) -> int:
        """Delete all notifications that reference *photo_id*.

        Must be called **before** the photo row is deleted so the FK
        ``photoId`` is still set on the notification rows.

        Args:
            session: Active SQLAlchemy session.
            photo_id: ID of the photo whose notifications to remove.

        Returns:
            int: Number of rows deleted.
        """
        rows = session.query(cls).filter_by(photoId=photo_id).all()
        for row in rows:
            session.delete(row)
        return len(rows)

    @classmethod
    def delete_by_album_id(cls, session: Session, album_id: int) -> int:
        """Delete all notifications that reference *album_id*.

        Used when an album is deleted to clean up album_favorited notifications.
        Must be called **before** the album row is deleted so the FK
        ``albumId`` is still set on the notification rows.

        Args:
            session: Active SQLAlchemy session.
            album_id: ID of the album whose notifications to remove.

        Returns:
            int: Number of rows deleted.
        """
        rows = session.query(cls).filter_by(albumId=album_id).all()
        for row in rows:
            session.delete(row)
        return len(rows)

    @classmethod
    def delete_by_like(cls, session: Session, user_id: int, photo_id: int) -> int:
        """Delete like_photo notifications for a specific user unliking a photo.

        When a user unlikes a photo, remove the corresponding like_photo notification
        sent to the photo owner.

        Args:
            session: Active SQLAlchemy session.
            user_id: The user who unliked the photo (senderId).
            photo_id: The photo being unliked (photoId).

        Returns:
            int: Number of rows deleted.
        """
        from app.core.db.models.notification_types import NotificationTypeModel

        type_obj = (
            session.query(NotificationTypeModel).filter_by(type="like_photo").first()
        )
        if not type_obj:
            return 0
        type_id = type_obj.id

        rows = (
            session.query(cls)
            .filter(
                cls.photoId == photo_id, cls.senderId == user_id, cls.typeId == type_id
            )
            .all()
        )
        for row in rows:
            session.delete(row)
        return len(rows)

    @classmethod
    def delete_by_comment(cls, session: Session, comment_id: int) -> int:
        """Delete comment_on_photo notifications for a specific comment.

        When a comment is deleted, remove the corresponding comment_on_photo
        notification sent to the photo owner.

        Args:
            session: Active SQLAlchemy session.
            comment_id: The comment being deleted (commentId).

        Returns:
            int: Number of rows deleted.
        """
        from app.core.db.models.notification_types import NotificationTypeModel

        type_obj = (
            session.query(NotificationTypeModel)
            .filter_by(type="comment_on_photo")
            .first()
        )
        if not type_obj:
            return 0
        type_id = type_obj.id

        rows = (
            session.query(cls)
            .filter(cls.commentId == comment_id, cls.typeId == type_id)
            .all()
        )
        for row in rows:
            session.delete(row)
        return len(rows)

    @classmethod
    def delete_by_favorite(cls, session: Session, album_id: int, user_id: int) -> int:
        """Delete album_favorited notifications when a user removes an album from favorites.

        When a user unfavorites an album, remove the album_favorited notification
        that was sent to the album owner.

        Args:
            session: Active SQLAlchemy session.
            album_id: The album being unfavorited (albumId).
            user_id: The user removing from favorites (senderId).

        Returns:
            int: Number of rows deleted.
        """
        from app.core.db.models.notification_types import NotificationTypeModel

        type_obj = (
            session.query(NotificationTypeModel)
            .filter_by(type="album_favorited")
            .first()
        )
        if not type_obj:
            return 0
        type_id = type_obj.id

        rows = (
            session.query(cls)
            .filter(
                cls.albumId == album_id, cls.senderId == user_id, cls.typeId == type_id
            )
            .all()
        )
        for row in rows:
            session.delete(row)
        return len(rows)

    @classmethod
    def delete_by_follow(
        cls, session: Session, follower_id: int, followed_id: int
    ) -> int:
        """Delete new_follower notifications when a user unfollows.

        When a user unfollows another user, remove the new_follower notification
        that was sent to the followed user.

        Args:
            session: Active SQLAlchemy session.
            follower_id: The user who unfollowed (senderId).
            followed_id: The user being unfollowed (recipientId).

        Returns:
            int: Number of rows deleted.
        """
        from app.core.db.models.notification_types import NotificationTypeModel

        type_obj = (
            session.query(NotificationTypeModel).filter_by(type="new_follower").first()
        )
        if not type_obj:
            return 0
        type_id = type_obj.id

        rows = (
            session.query(cls)
            .filter(
                cls.senderId == follower_id,
                cls.recipientId == followed_id,
                cls.typeId == type_id,
            )
            .all()
        )
        for row in rows:
            session.delete(row)
        return len(rows)
