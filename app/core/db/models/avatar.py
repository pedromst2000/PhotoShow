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
from sqlalchemy.exc import IntegrityError

from app.core.db.engine import Base, SessionLocal


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
    def create(cls, user_id: int, avatar_path: str) -> dict:
        """
        Create or update the avatar for a user. If an avatar exists it is updated in-place.

        Args:
            user_id (int): ID of the user owning the avatar.
            avatar_path (str): File path or URL of the avatar image.

        Returns:
            dict: The created or updated avatar row as a dictionary.
        """

        # validate avatar path
        trimmed = avatar_path.strip() if avatar_path is not None else ""
        if not trimmed:
            raise ValueError("Avatar path must not be empty")
        if len(trimmed) > 255:
            raise ValueError("Avatar path must be at most 255 characters")

        # upsert-like behavior with basic race handling
        with SessionLocal() as session:
            try:
                with session.begin():
                    existing = (
                        session.query(cls)
                        .filter_by(userId=user_id)
                        .order_by(desc(cls.createdAt))
                        .first()
                    )
                    if existing:
                        existing.avatar = trimmed
                        session.flush()
                        return existing.to_dict()

                    obj = cls(userId=user_id, avatar=trimmed)
                    session.add(obj)
                    session.flush()
                    return obj.to_dict()
            except IntegrityError:
                # concurrent insert may cause unique constraint violation; try update path
                session.rollback()
                with session.begin():
                    existing = (
                        session.query(cls)
                        .filter_by(userId=user_id)
                        .order_by(desc(cls.createdAt))
                        .first()
                    )
                    if existing:
                        existing.avatar = trimmed
                        session.flush()
                        return existing.to_dict()
                    # If still not found, re-raise
                    raise

    @classmethod
    def get_for_user(cls, user_id: int) -> dict | None:
        """
        Return the user's active avatar as a dict, or None if not found.

        Args:
            user_id (int): The ID of the user whose avatar is to be retrieved.

        Returns:
            dict or None: The primary avatar as returned by `to_dict()`, or None.
        """
        with SessionLocal() as session:
            row = (
                session.query(cls)
                .filter_by(userId=user_id)
                .order_by(desc(cls.createdAt))
                .first()
            )
            if row:
                return row.to_dict()
            return None
