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


class PhotoImageModel(Base):
    """
    PhotoImageModel stores the Cloudinary asset data for a photo.
    """

    __tablename__ = "photo_image"

    __table_args__ = (
        UniqueConstraint("photoId", name="uq_photo_image_photoId"),
        CheckConstraint("id > 0 AND id < 10000000", name="ck_photo_image_id_range"),
        CheckConstraint(
            "photoId > 0 AND photoId < 10000000", name="ck_photo_image_photoId_range"
        ),
    )

    id: int = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    photoId: int = Column(
        Integer, ForeignKey("photos.id", ondelete="CASCADE"), nullable=False
    )
    provider_image_id: str = Column(String(512), nullable=True)
    provider_image_url: str = Column(String(1024), nullable=True)
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
            "photoId": self.photoId,
            "provider_image_id": self.provider_image_id,
            "provider_image_url": self.provider_image_url,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt,
        }

    @classmethod
    def create(
        cls,
        session: Session,
        photo_id: int,
        provider_image_id: str,
        provider_image_url: str,
    ) -> dict:
        """
        Create or update the Cloudinary image record for a photo.

        Args:
            session:           Active SQLAlchemy session.
            photo_id:          The photo this image belongs to.
            provider_image_id: Cloudinary public_id.
            provider_image_url: Cloudinary secure_url.

        Returns:
            dict representation of the created / updated record.
        """
        existing = (
            session.query(cls)
            .filter_by(photoId=photo_id)
            .order_by(desc(cls.createdAt))
            .first()
        )
        if existing:
            existing.provider_image_id = provider_image_id
            existing.provider_image_url = provider_image_url
            session.flush()
            return existing.to_dict()

        obj = cls(
            photoId=photo_id,
            provider_image_id=provider_image_id,
            provider_image_url=provider_image_url,
        )
        session.add(obj)
        session.flush()
        return obj.to_dict()

    @classmethod
    def get_for_photo(cls, session: Session, photo_id: int) -> dict | None:
        """
        Return the single image record for a photo as a dict, or None.

        Args:
            session:  Active SQLAlchemy session.
            photo_id: The ID of the photo for which to retrieve the image.

        Returns:
            dict | None: A dictionary representation of the image record, or None if not found.
        """
        row = (
            session.query(cls)
            .filter_by(photoId=photo_id)
            .order_by(desc(cls.createdAt))
            .first()
        )
        return row.to_dict() if row else None

    @classmethod
    def get_primary_for_photo(cls, session: Session, photo_id: int) -> str | None:
        """
        Return the Cloudinary secure_url for a photo, or None.

        Args:
            session:  Active SQLAlchemy session.
            photo_id: The ID of the photo.

        Returns:
            str | None: The Cloudinary URL of the primary image, or None if not found.
        """
        row = (
            session.query(cls)
            .filter_by(photoId=photo_id)
            .order_by(desc(cls.createdAt))
            .first()
        )
        if row:
            return row.provider_image_url
        return None
