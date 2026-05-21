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
from sqlalchemy.orm import Session

from app.core.db.engine import Base


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
        Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
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
    def get_all(cls, session: Session) -> list:
        """
        Retrieve all albums from the database.

        Args:
            session: Active SQLAlchemy session.

        Returns:
            list: A list of dictionaries, each representing an album.
        """
        return [a.to_dict() for a in session.query(cls).all()]

    @classmethod
    def create(cls, session: Session, name: str, creatorId: int) -> dict:
        """
        Create a new album in the database.

        Args:
            session: Active SQLAlchemy session.
            name (str): The name of the album (pre-validated).
            creatorId (int): The ID of the user creating the album.

        Returns:
            dict: A dictionary representation of the newly created album.
        """
        obj: AlbumModel = cls(name=name, creatorId=creatorId)
        session.add(obj)
        session.flush()
        return obj.to_dict()

    @classmethod
    def update(cls, session: Session, updated: dict) -> dict:
        """
        Update an existing album in the database.

        Args:
            session: Active SQLAlchemy session.
            updated (dict): A dictionary containing the updated album information, including "id" and "name".

        Returns:
            dict: A dictionary representation of the updated album.
        """
        a: AlbumModel = session.query(cls).filter_by(id=updated["id"]).first()
        if a:
            a.name = updated["name"]
        return updated

    @classmethod
    def get_by_id(cls, session: Session, album_id: int) -> dict | None:
        """
        Retrieve an album by its ID.

        Args:
            session: Active SQLAlchemy session.
            album_id (int): The ID of the album to retrieve.

        Returns:
            dict | None: A dictionary representation of the album if found, otherwise None.
        """
        a = session.query(cls).filter_by(id=album_id).first()
        return a.to_dict() if a else None

    @classmethod
    def get_by_creator(cls, session: Session, creator_id: int) -> list:
        """
        Retrieve all albums created by a specific user.

        Args:
            session: Active SQLAlchemy session.
            creator_id (int): The ID of the user who created the albums.

        Returns:
            list: A list of dictionaries representing the user's albums.
        """
        return [
            a.to_dict()
            for a in session.query(cls).filter_by(creatorId=creator_id).all()
        ]

    @classmethod
    def delete(cls, session: Session, album_id: int) -> bool:
        """
        Delete an album from the database by its ID.

        Args:
            session: Active SQLAlchemy session.
            album_id (int): The ID of the album to delete.

        Returns:
            bool: True if deleted successfully, False otherwise.
        """
        a = session.query(cls).filter_by(id=album_id).first()
        if a:
            session.delete(a)
            return True
        return False
