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
from sqlalchemy.orm import relationship

from db.engine import Base, SessionLocal


class PhotoImageModel(Base):
    """
    PhotoImageModel represents an image associated with a photo in the database
    """

    __tablename__ = "photo_image"

    __table_args__ = (
        UniqueConstraint("photoId", name="uq_photo_image_photoId"),
        CheckConstraint("id > 0 AND id < 10000000", name="ck_photo_image_id_range"),
        CheckConstraint(
            "photoId > 0 AND photoId < 10000000", name="ck_photo_image_photoId_range"
        ),
        CheckConstraint(
            "length(trim(image)) > 0", name="ck_photo_image_image_not_empty"
        ),
    )

    id: int = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    photoId: int = Column(
        Integer, ForeignKey("photos.id", ondelete="CASCADE"), nullable=False
    )
    image: str = Column(String(255), nullable=False)
    createdAt: DateTime = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updatedAt: DateTime = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # ORM one-to-one: image for the photo (unique constraint enforces one image per photo)
    photo_rel = relationship(
        "PhotoModel", foreign_keys=[photoId], back_populates="image_rel", uselist=False
    )

    def to_dict(self) -> dict:
        """
        Convert the PhotoImageModel instance to a dictionary.

        Returns:
            dict: A dictionary representation of the PhotoImageModel instance.
        """

        return {
            "id": self.id,
            "photoId": self.photoId,
            "image": self.image,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt,
        }

    @classmethod
    def create(cls, photo_id: int, image: str) -> dict:
        """
        Create a new PhotoImageModel record in the database.

        Parameters:
            photo_id (int): The ID of the photo to which this image belongs.
            image (str): The file path or URL of the image.
        Returns:
            dict: A dictionary representation of the created PhotoImageModel instance.
        """

        # validate image path
        trimmed = image.strip() if image is not None else ""
        if not trimmed:
            raise ValueError("Image path must not be empty")
        if len(trimmed) > 255:
            raise ValueError("Image path must be at most 255 characters")

        with SessionLocal() as session:
            try:
                with session.begin():
                    # If an image row already exists for this photo, update it in-place
                    existing = (
                        session.query(cls)
                        .filter_by(photoId=photo_id)
                        .order_by(desc(cls.createdAt))
                        .first()
                    )
                    if existing:
                        existing.image = trimmed
                        session.flush()
                        return existing.to_dict()

                    obj = cls(photoId=photo_id, image=trimmed)
                    session.add(obj)
                    session.flush()
                    return obj.to_dict()
            except IntegrityError:
                # concurrent insert may cause unique constraint violation; try update path
                session.rollback()
                with session.begin():
                    existing = (
                        session.query(cls)
                        .filter_by(photoId=photo_id)
                        .order_by(desc(cls.createdAt))
                        .first()
                    )
                    if existing:
                        existing.image = trimmed
                        session.flush()
                        return existing.to_dict()
                    raise

    @classmethod
    def get_for_photo(cls, photo_id: int) -> dict | None:
        """
        Return the single image record for a photo as a dict, or None.
        Photos in this app have only one image; this returns that image row.

        Parameters:
            photo_id (int): The ID of the photo for which to retrieve the image.

        Returns:
            dict | None: A dictionary representation of the image record, or None if not found.
        """
        with SessionLocal() as session:
            row = (
                session.query(cls)
                .filter_by(photoId=photo_id)
                .order_by(desc(cls.createdAt))
                .first()
            )
            return row.to_dict() if row else None

    @classmethod
    def get_primary_for_photo(cls, photo_id: int) -> str | None:
        """
        Return the primary image for a photo as a string, or None.
        Photos in this app have only one image; this returns that image row.

        Parameters:
            photo_id (int): The ID of the photo for which to retrieve the primary image.

        Returns:
            str | None: The file path or URL of the primary image, or None if not found.
        """
        with SessionLocal() as session:
            row = (
                session.query(cls)
                .filter_by(photoId=photo_id)
                .order_by(desc(cls.createdAt))
                .first()
            )
            if row:
                return row.image
            return None
