from datetime import datetime, timezone

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)

from db.engine import Base, SessionLocal


class AlbumModel(Base):
    """
    AlbumModel represents an album in the database, with methods to create, retrieve, and update albums.
    """

    __tablename__: str = "albuns"

    __table_args__ = (
        UniqueConstraint("creatorId", "name", name="uq_albums_creatorId_name"),
        CheckConstraint("id > 0 AND id < 10000000", name="ck_albums_id_range"),
        CheckConstraint(
            "creatorId > 0 AND creatorId < 10000000", name="ck_albums_creatorId_range"
        ),
        CheckConstraint("length(trim(name)) > 0", name="ck_albums_name_not_empty"),
        Index("ix_albums_creatorId", "creatorId"),
    )

    id: int = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name: str = Column(String(50), nullable=False)
    creatorId: int = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
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
    def photos(self):
        return self.photos_rel

    @property
    def favorites(self):
        return self.favorites_rel

    def to_dict(self) -> dict:
        """Convert the AlbumModel instance to a dictionary.

        Returns:
            dict: A dictionary representation of the AlbumModel instance.
        """

        return {
            "id": self.id,
            "name": self.name,
            "creatorId": self.creatorId,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt,
        }

    @classmethod
    def get_all(cls) -> list:
        """
        Retrieve all albums from the database and return them as a list of dictionaries.
        Returns:
            list: A list of dictionaries, each representing an album.
        """

        with SessionLocal() as session:
            return [a.to_dict() for a in session.query(cls).all()]

    @classmethod
    def create(cls, name: str, creatorId: int) -> dict:
        """
        Create a new album in the database.

        Parameters:
            name (str): The name of the album.
            creatorId (int): The ID of the user creating the album.

        Returns:
            dict: A dictionary representation of the newly created album.
        """
        # model-level defensive trim/validation (service should already validate)
        trimmed = name.strip() if name is not None else ""
        if not trimmed:
            raise ValueError("Album name must not be empty")
        if len(trimmed) > 50:
            raise ValueError("Album name must be at most 50 characters")

        with SessionLocal() as session:
            with session.begin():
                obj: AlbumModel = cls(name=trimmed, creatorId=creatorId)
                session.add(obj)
                session.flush()
                return obj.to_dict()

    @classmethod
    def update(cls, updated: dict) -> dict:
        """
        Update an existing album in the database.

        Parameters:
            updated (dict): A dictionary containing the updated album information, including "albumID" and "name".
        Returns:
            dict: A dictionary representation of the updated album.
        """
        with SessionLocal() as session:
            with session.begin():
                a: AlbumModel = session.query(cls).filter_by(id=updated["id"]).first()
                if a:
                    a.name = updated["name"]
        return updated

    @classmethod
    def get_by_id(cls, album_id: int) -> dict | None:
        """
        Retrieve an album by its ID.

        Parameters:
            album_id (int): The ID of the album to retrieve.

        Returns:
            dict | None: A dictionary representation of the album if found, otherwise None.
        """
        with SessionLocal() as session:
            a = session.query(cls).filter_by(id=album_id).first()
            return a.to_dict() if a else None

    @classmethod
    def get_by_creator(cls, creator_id: int) -> list:
        """
        Retrieve all albums created by a specific user.

        Parameters:
            creator_id (int): The ID of the user who created the albums.

        Returns:
            list: A list of dictionaries representing the user's albums.
        """
        with SessionLocal() as session:
            return [
                a.to_dict()
                for a in session.query(cls).filter_by(creatorId=creator_id).all()
            ]

    @classmethod
    def delete(cls, album_id: int) -> bool:
        """
        Delete an album from the database by its ID.

        Parameters:
            album_id (int): The ID of the album to delete.

        Returns:
            bool: True if deleted successfully, False otherwise.
        """
        with SessionLocal() as session:
            with session.begin():
                a = session.query(cls).filter_by(id=album_id).first()
                if a:
                    session.delete(a)
                    return True
        return False
