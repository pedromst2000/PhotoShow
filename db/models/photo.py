from datetime import datetime, timezone

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
)

from db.engine import Base, SessionLocal

from .photo_image import PhotoImageModel


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
        Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False
    )
    albumId: int = Column(
        Integer, ForeignKey("albuns.id", ondelete="SET NULL"), nullable=True
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
    def get_all(cls) -> list:
        """
        Retrieve all photos from the database and return them as a list of dictionaries.

        Returns:
            list: A list of dictionaries, each representing a photo.
        """
        with SessionLocal() as session:
            return [p.to_dict() for p in session.query(cls).all()]

    @classmethod
    def create(
        cls,
        description: str,
        publishedDate,
        categoryId: int,
        albumId: int,
    ) -> dict:
        """
        Create a new photo in the database.

        Args:
            description (str): The description of the photo.
            publishedDate (datetime): The date and time when the photo was published.
            categoryId (int): The ID of the category the photo belongs to.
            albumId (int, optional): The ID of the album the photo belongs to. Defaults to None.
            Note: image data is stored in `photo_images` table; ratings are stored in `ratings`.
        Returns:
            dict: A dictionary representation of the newly created photo.
        """
        with SessionLocal() as session:
            with session.begin():
                obj: PhotoModel = cls(
                    description=description,
                    publishedDate=publishedDate,
                    categoryId=categoryId,
                    albumId=albumId,
                )
                session.add(obj)
                session.flush()
                # ensure the photo has a PhotoImage row (DER: 1:1 mandatory)
                try:

                    default_image = "assets/images/photos_gallery/default_photo.jpg"
                    img_obj = PhotoImageModel(photoId=obj.id, image=default_image)
                    session.add(img_obj)
                    session.flush()
                except Exception:
                    # do not fail photo creation if image insertion fails
                    pass
                return obj.to_dict()

    @classmethod
    def delete(cls, photoID: int) -> None:
        """
        Delete a photo from the database by its ID.

        Args:
            photoID (int): The ID of the photo to delete.
        """
        with SessionLocal() as session:
            with session.begin():
                p = session.query(cls).filter_by(id=photoID).first()
                if p:
                    session.delete(p)

    @classmethod
    def delete_many(cls, *photoIDs: int) -> None:
        """
        Delete multiple photos from the database by their IDs.

        Args:
            *photoIDs (int): A variable number of photo IDs to delete.
        """
        with SessionLocal() as session:
            with session.begin():
                for pid in photoIDs:
                    p = session.query(cls).filter_by(id=int(pid)).first()
                    if p:
                        session.delete(p)

    @classmethod
    def get_by_id(cls, photo_id: int) -> dict | None:
        """
        Retrieve a photo by its ID.

        Args:
            photo_id (int): The ID of the photo to retrieve.

        Returns:
            dict | None: A dictionary representation of the photo if found, otherwise None.
        """
        with SessionLocal() as session:
            p = session.query(cls).filter_by(id=photo_id).first()
            if not p:
                return None
            data = p.to_dict()
            # lazy import to avoid circular imports (use package-relative imports)
            try:
                from .photo_image import PhotoImageModel
                from .rating import RatingModel

                img = PhotoImageModel.get_primary_for_photo(p.id)
                data["image"] = img or ""
                data["rating"] = RatingModel.get_average_for_photo(p.id) or 0.0
            except Exception:
                # if enrichment fails, provide sensible defaults
                data["image"] = ""
                data["rating"] = 0.0
            return data

    @classmethod
    def get_by_album(cls, album_id: int) -> list:
        """
        Retrieve all photos in a specific album.

        Args:
            album_id (int): The ID of the album.

        Returns:
            list: A list of dictionaries representing photos in the album.
        """
        with SessionLocal() as session:
            return [
                p.to_dict()
                for p in session.query(cls).filter_by(albumId=album_id).all()
            ]

    @classmethod
    def get_by_category(cls, category_id: int) -> list:
        """
        Retrieve all photos in a specific category.

        Args:
            category_id (int): The ID of the category.

        Returns:
            list: A list of dictionaries representing photos in the category.
        """
        with SessionLocal() as session:
            return [
                p.to_dict()
                for p in session.query(cls).filter_by(categoryId=category_id).all()
            ]

    @classmethod
    def update(cls, updated: dict) -> bool:
        """
        Update an existing photo in the database.

        Args:
            updated (dict): A dictionary containing the updated photo information.

        Returns:
            bool: True if updated successfully, False otherwise.
        """
        allowed = {"description", "publishedDate", "categoryID", "albumID"}
        with SessionLocal() as session:
            with session.begin():
                p = session.query(cls).filter_by(id=updated["id"]).first()
                if p:
                    for key, value in updated.items():
                        if key == "id":
                            continue
                        if key not in allowed:
                            continue
                        if key == "description":
                            val = str(value).strip()
                            if not val:
                                return False
                            setattr(p, key, val)
                        else:
                            setattr(p, key, value)
                    return True
        return False
