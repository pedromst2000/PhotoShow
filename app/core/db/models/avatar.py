from datetime import datetime, timezone

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    desc,
)
from sqlalchemy.orm import Session

from app.core.db.engine import Base


class AvatarModel(Base):
    """
    AvatarModel represents a user avatar in the database.
    """

    __tablename__ = "avatars"

    __table_args__ = (
        UniqueConstraint("userId", name="uq_avatars_userId"),
        CheckConstraint("id > 0 AND id < 10000000", name="ck_avatars_id_range"),
        CheckConstraint(
            "userId > 0 AND userId < 10000000", name="ck_avatars_userId_range"
        ),
        CheckConstraint("length(trim(avatar)) > 0", name="ck_avatars_avatar_not_empty"),
    )

    id: int = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    userId: int = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    avatar: str = Column(String(255), nullable=False)
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
        Convert the AvatarModel instance to a dictionary.

        Returns:
            dict: A dictionary representation of the AvatarModel instance.
        """

        return {
            "id": self.id,
            "userId": self.userId,
            "avatar": self.avatar,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt,
        }

    @classmethod
    def create(cls, session: Session, user_id: int, avatar_path: str) -> dict:
        """
        Create a new avatar for a user.

        Args:
            session: Active SQLAlchemy session.
            user_id (int): ID of the user owning the avatar.
            avatar_path (str): File path or URL of the avatar image (pre-validated).

        Returns:
            dict: The created avatar row as a dictionary.
        """
        obj = cls(userId=user_id, avatar=avatar_path)
        session.add(obj)
        session.flush()  # Flush to assign an ID before returning
        return obj.to_dict()

    @classmethod
    def update(cls, session: Session, user_id: int, avatar_path: str) -> dict | None:
        """
        Update the avatar for an existing user.

        Args:
            session: Active SQLAlchemy session.
            user_id (int): ID of the user whose avatar should be updated.
            avatar_path (str): File path or URL of the avatar image (pre-validated).

        Returns:
            dict | None: The updated avatar row as a dictionary, or None if not found.
        """
        existing = (
            session.query(cls)
            .filter_by(userId=user_id)
            .order_by(desc(cls.createdAt))
            .first()
        )
        if existing:  # Only update if an existing avatar is found for the user
            existing.avatar = avatar_path
            session.flush()  # Flush to apply the update before returning
            return existing.to_dict()
        return None

    @classmethod
    def get_for_user(cls, session: Session, user_id: int) -> dict | None:
        """
        Return the user's active avatar as a dict, or None if not found.

        Args:
            session: Active SQLAlchemy session.
            user_id (int): The ID of the user whose avatar is to be retrieved.

        Returns:
            dict or None: The primary avatar as returned by `to_dict()`, or None.
        """
        row = (
            session.query(cls)
            .filter_by(userId=user_id)
            .order_by(desc(cls.createdAt))
            .first()  # Get the most recently created avatar for the user, which is considered the active one
        )
        if row:
            return row.to_dict()
        return None
