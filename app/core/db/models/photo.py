from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
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


class PhotoModel(Base):
    """
    PhotoModel represents a photo in the database, with methods to create, retrieve, and delete photos.
    """

    __tablename__: str = "photos"

    __table_args__ = (
        CheckConstraint("id > 0 AND id < 10000000", name="ck_photos_id_range"),
        CheckConstraint(
            "categoryId > 0 AND categoryId < 10000000",
            name="ck_photos_categoryId_range",
        ),
        CheckConstraint(
            "albumId IS NULL OR (albumId > 0 AND albumId < 10000000)",
            name="ck_photos_albumId_range",
        ),
        CheckConstraint(
            "length(trim(description)) > 0", name="ck_photos_description_not_empty"
        ),
        CheckConstraint(
            "length(description) <= 255", name="ck_photos_description_maxlen"
        ),
        Index("ix_photos_albumId", "albumId"),
        Index("ix_photos_categoryId", "categoryId"),
    )

    id: int = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    description: str = Column(String(255), nullable=False)
    publishedDate: DateTime = Column(DateTime(timezone=True), nullable=False)
    categoryId: int = Column(
        Integer, ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False
    )
    albumId: int = Column(
        Integer, ForeignKey("albuns.id", ondelete="CASCADE"), nullable=True
    )
    createdAt: DateTime = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updatedAt: DateTime = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    @property
    def image(self):
        return self.image_rel

    @property
    def ratings(self):
        return self.ratings_rel

    @property
    def comments(self):
        return self.comments_rel

    @property
    def likes(self):
        return self.likes_rel

    def to_dict(self) -> dict:
        """
        Convert the PhotoModel instance to a dictionary.

        Returns:
            dict: A dictionary representation of the PhotoModel instance.
        """
        return {
            "id": self.id,
            "description": self.description,
            "publishedDate": self.publishedDate,
            "rating": 0.0,
            "categoryId": self.categoryId,
            "albumId": self.albumId,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt,
        }

    @classmethod
    def get_all(cls, session: Session) -> list[dict]:
        """
        Retrieve all photos from the database.

        Args:
            session: Active SQLAlchemy session.

        Returns:
            list[dict]: A list of dictionaries, each representing a photo.
        """
        return [photo.to_dict() for photo in session.query(cls).all()]

    @classmethod
    def create(
        cls,
        session: Session,
        description: str,
        publishedDate,
        categoryId: Optional[int],
        albumId: Optional[int],
    ) -> dict:
        """
        Create a new photo in the database.

        Args:
            session: Active SQLAlchemy session.
            description (str): The description of the photo (pre-validated).
            publishedDate (datetime): The date and time when the photo was published.
            categoryId (int): The ID of the category the photo belongs to.
            albumId (int, optional): The ID of the album the photo belongs to.

        Returns:
            dict: A dictionary representation of the newly created photo.
        """
        obj: PhotoModel = cls(
            description=description,
            publishedDate=publishedDate,
            categoryId=categoryId,
            albumId=albumId,
        )
        session.add(obj)
        session.flush()
        return obj.to_dict()

    @classmethod
    def delete(cls, session: Session, photoID: int) -> bool:
        """
        Delete a photo from the database by its ID.

        Args:
            session: Active SQLAlchemy session.
            photoID (int): The ID of the photo to delete.

        Returns:
            bool: True if a photo was deleted, False if photo was not found.
        """
        p = session.query(cls).filter_by(id=photoID).first()
        if p:
            session.delete(p)
            return True
        return False

    @classmethod
    def delete_many(cls, session: Session, *photoIDs: int) -> None:
        """
        Delete multiple photos from the database by their IDs.

        Args:
            session: Active SQLAlchemy session.
            *photoIDs (int): A variable number of photo IDs to delete.
        """
        for pid in photoIDs:
            p = session.query(cls).filter_by(id=int(pid)).first()
            if p:
                session.delete(p)

    @classmethod
    def get_by_id(cls, session: Session, photo_id: int) -> dict | None:
        """
        Retrieve a photo by its ID.

        Args:
            session: Active SQLAlchemy session.
            photo_id (int): The ID of the photo to retrieve.

        Returns:
            dict | None: A dictionary representation of the photo if found, otherwise None.
        """
        p = session.query(cls).filter_by(id=photo_id).first()
        if not p:
            return None
        return p.to_dict()

    @classmethod
    def get_by_album(cls, session: Session, album_id: int) -> list[dict]:
        """
        Retrieve all photos in a specific album.

        Args:
            session: Active SQLAlchemy session.
            album_id (int): The ID of the album.

        Returns:
            list[dict]: A list of dictionaries representing photos in the album.
        """
        return [
            photo.to_dict()
            for photo in session.query(cls).filter_by(albumId=album_id).all()
        ]

    @classmethod
    def get_by_category(cls, session: Session, category_id: int) -> list[dict]:
        """
        Retrieve all photos in a specific category.

        Args:
            session: Active SQLAlchemy session.
            category_id (int): The ID of the category.

        Returns:
            list[dict]: A list of dictionaries representing photos in the category.
        """
        return [
            photo.to_dict()
            for photo in session.query(cls).filter_by(categoryId=category_id).all()
        ]

    @classmethod
    def update(cls, session: Session, updated: dict) -> bool:
        """
        Update an existing photo in the database.

        Args:
            session: Active SQLAlchemy session.
            updated (dict): A dictionary containing the updated photo information.

        Returns:
            bool: True if updated successfully, False otherwise.
        """
        allowed = {"description", "publishedDate", "categoryID", "albumID"}
        photo = session.query(cls).filter_by(id=updated["id"]).first()
        if photo:
            for key, value in updated.items():
                if key == "id":
                    continue
                if key not in allowed:
                    continue
                setattr(photo, key, value)
            return True
        return False
