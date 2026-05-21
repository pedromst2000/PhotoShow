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
    def get_all(cls, session: Session) -> list:
        """
        Retrieve all notifications from the database.

        Args:
            session: Active SQLAlchemy session.

        Returns:
            list: A list of dictionaries, each representing a notification.
        """
        return [n.to_dict() for n in session.query(cls).all()]

    @classmethod
    def get_by_user(cls, session: Session, user_id: int) -> list:
        """
        Retrieve all notifications for a specific user (newest first).

        Args:
            session: Active SQLAlchemy session.
            user_id (int): The recipient user ID.

        Returns:
            list: A list of notification dicts.
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
