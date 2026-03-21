from datetime import datetime, timezone

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
from sqlalchemy.orm import relationship

from db.engine import Base, SessionLocal


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
            "userId > 0 AND userId < 10000000", name="ck_notifications_userId_range"
        ),
        CheckConstraint(
            "(senderId IS NULL) OR (senderId > 0 AND senderId < 10000000)",
            name="ck_notifications_senderId_null_or_range",
        ),
        CheckConstraint(
            "length(trim(message)) > 0", name="ck_notifications_message_not_empty"
        ),
        # targetType and targetId must be provided together or not at all
        CheckConstraint(
            "(targetType IS NULL) = (targetId IS NULL)",
            name="ck_notifications_target_pair",
        ),
        # targetType must be one of the allowed discriminator values
        CheckConstraint(
            "targetType IS NULL OR targetType IN ('photo', 'comment', 'album')",
            name="ck_notifications_target_type_values",
        ),
        # performance indexes for common queries
        Index("ix_notifications_userid_createdat", "userId", "createdAt"),
        Index("ix_notifications_userid_isread", "userId", "isRead"),
    )

    id: int = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    typeId: int = Column(
        Integer,
        ForeignKey("notification_types.id", ondelete="CASCADE"),
        nullable=False,
    )
    userId: int = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )  # recipient
    senderId: int = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )  # who triggered it
    # polymorphic target — both must be set together or both null
    targetType: str = Column(String(20), nullable=True)  # 'photo' | 'comment' | 'album'
    targetId: int = Column(Integer, nullable=True)  # PK of the referenced resource
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

    # ORM many-to-one: many notifications belong to one notification type
    type_rel = relationship(
        "NotificationTypeModel",
        foreign_keys=[typeId],
        back_populates="notifications_rel",
    )
    # ORM many-to-one: many notifications are received by one user (recipient)
    recipient_rel = relationship(
        "UserModel", foreign_keys=[userId], back_populates="notifications_received_rel"
    )
    # ORM many-to-one: many notifications are triggered by one sender user (nullable)
    sender_rel = relationship(
        "UserModel", foreign_keys=[senderId], back_populates="notifications_sent_rel"
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
            "userId": self.userId,
            "senderId": self.senderId,
            "targetType": self.targetType,
            "targetId": self.targetId,
            "message": self.message,
            "isRead": self.isRead,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt,
        }

    @classmethod
    def get_all(cls) -> list:
        """
        Retrieve all notifications from the database and return them as a list of dictionaries.

        Returns:
            list: A list of dictionaries, each representing a notification.
        """
        with SessionLocal() as session:
            return [n.to_dict() for n in session.query(cls).all()]

    @classmethod
    def get_by_user(cls, user_id: int) -> list:
        """
        Retrieve all notifications for a specific user (newest first).

        Parameters:
            user_id (int): The recipient user ID.

        Returns:
            list: A list of notification dicts.
        """
        with SessionLocal() as session:
            return [
                n.to_dict()
                for n in session.query(cls)
                .filter_by(userId=user_id)
                .order_by(cls.createdAt.desc())
                .all()
            ]

    @classmethod
    def get_unread_count(cls, user_id: int) -> int:
        """
        Return the number of unread notifications for a user.

        Parameters:
            user_id (int): The recipient user ID.

        Returns:
            int: Count of unread notifications.
        """
        with SessionLocal() as session:
            return session.query(cls).filter_by(userId=user_id, isRead=False).count()

    @classmethod
    def mark_read(cls, notID: int) -> bool:
        """
        Mark a single notification as read.

        Parameters:
            notID (int): The notification ID.

        Returns:
            bool: True if updated successfully.
        """
        with SessionLocal() as session:
            with session.begin():
                n = session.query(cls).filter_by(id=notID).first()
                if n:
                    n.isRead = True
                    return True
        return False

    @classmethod
    def mark_all_read(cls, user_id: int) -> None:
        """
        Mark all notifications for a user as read.

        Parameters:
            user_id (int): The recipient user ID.
        """
        with SessionLocal() as session:
            with session.begin():
                session.query(cls).filter_by(userId=user_id, isRead=False).update(
                    {"isRead": True}
                )

    @classmethod
    def create(
        cls,
        type_id: int,
        message: str,
        user_id: int,
        sender_id: int = None,
        target_type: str = None,
        target_id: int = None,
    ) -> dict:
        """
        Create a new notification.

        Parameters:
            type_id (int): FK to notification_types.id.
            message (str): Human-readable notification message.
            user_id (int): The recipient user ID.
            sender_id (int, optional): Who triggered the notification.
            target_type (str, optional): Polymorphic discriminator — 'photo', 'comment', or 'album'.
            target_id (int, optional): PK of the referenced resource (must pair with target_type).

        Returns:
            dict: A dictionary representation of the newly created notification.
        """
        m = message.strip() if message is not None else ""
        if not m:
            raise ValueError("Notification message must not be empty")
        if len(m) > 255:
            raise ValueError("Notification message must be at most 255 characters")

        # target_type and target_id must both be provided or both omitted
        if (target_type is None) != (target_id is None):
            raise ValueError(
                "target_type and target_id must both be provided or both be None"
            )
        if target_type is not None and target_type not in ("photo", "comment", "album"):
            raise ValueError(
                f"target_type must be 'photo', 'comment', or 'album', got: {target_type!r}"
            )

        from db.models.notification_types import NotificationTypeModel

        if not NotificationTypeModel.get_by_id(type_id):
            raise ValueError(f"Unknown notification type id: {type_id}")

        with SessionLocal() as session:
            with session.begin():
                obj = cls(
                    typeId=type_id,
                    message=m,
                    userId=user_id,
                    senderId=sender_id,
                    targetType=target_type,
                    targetId=target_id,
                )
                session.add(obj)
                session.flush()
                return obj.to_dict()
