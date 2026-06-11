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
    AvatarModel stores the Cloudinary asset data for a user's avatar.
    """

    __tablename__ = "avatars"

    __table_args__ = (
        UniqueConstraint("userId", name="uq_avatars_userId"),
        CheckConstraint("id > 0 AND id < 10000000", name="ck_avatars_id_range"),
        CheckConstraint(
            "userId > 0 AND userId < 10000000", name="ck_avatars_userId_range"
        ),
    )

    id: int = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    userId: int = Column(
        Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    provider_id: str = Column(String(512), nullable=True)
    provider_url_image: str = Column(String(1024), nullable=True)
    createdAt: DateTime = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updatedAt: DateTime = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "userId": self.userId,
            "provider_id": self.provider_id,
            "provider_url_image": self.provider_url_image,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt,
        }

    @classmethod
    def create(
        cls,
        session: Session,
        user_id: int,
        provider_id: str,
        provider_url_image: str,
    ) -> dict:
        """
        Create a new avatar record for a user.

        Args:
            session:            Active SQLAlchemy session.
            user_id:            ID of the user owning the avatar.
            provider_id:        Cloudinary public_id.
            provider_url_image: Cloudinary secure_url.

        Returns:
            dict: The created avatar row as a dictionary.
        """
        obj = cls(
            userId=user_id,
            provider_id=provider_id,
            provider_url_image=provider_url_image,
        )
        session.add(obj)
        session.flush()
        return obj.to_dict()

    @classmethod
    def update(
        cls,
        session: Session,
        user_id: int,
        provider_id: str,
        provider_url_image: str,
    ) -> dict | None:
        """
        Update the avatar for an existing user.

        Args:
            session:            Active SQLAlchemy session.
            user_id:            ID of the user whose avatar should be updated.
            provider_id:        New Cloudinary public_id.
            provider_url_image: New Cloudinary secure_url.

        Returns:
            dict | None: The updated avatar row as a dictionary, or None if not found.
        """
        existing = (
            session.query(cls)
            .filter_by(userId=user_id)
            .order_by(desc(cls.createdAt))
            .first()
        )
        if existing:
            existing.provider_id = provider_id
            existing.provider_url_image = provider_url_image
            session.flush()
            return existing.to_dict()
        return None

    @classmethod
    def get_for_user(cls, session: Session, user_id: int) -> dict | None:
        """
        Return the user's active avatar as a dict, or None if not found.

        Args:
            session: Active SQLAlchemy session.
            user_id: The ID of the user whose avatar is to be retrieved.

        Returns:
            dict or None: The primary avatar as returned by `to_dict()`, or None.
        """
        row = (
            session.query(cls)
            .filter_by(userId=user_id)
            .order_by(desc(cls.createdAt))
            .first()
        )
        if row:
            return row.to_dict()
        return None
