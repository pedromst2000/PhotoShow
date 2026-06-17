from datetime import datetime, timezone

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    UniqueConstraint,
)
from sqlalchemy.orm import Session

from app.core.db.engine import Base


class FavoriteModel(Base):
    """
    FavoriteModel represents a favorite album entry in the database, with methods to create and retrieve favorites.
    """

    __tablename__: str = "favorites"

    __table_args__ = (
        CheckConstraint("id > 0 AND id < 10000000", name="ck_favorites_id_range"),
        CheckConstraint(
            "albumId > 0 AND albumId < 10000000",
            name="ck_favorites_albumId_range",
        ),
        CheckConstraint(
            "userId > 0 AND userId < 10000000", name="ck_favorites_userId_range"
        ),
        UniqueConstraint("userId", "albumId", name="uq_favorites_user_album"),
        Index("ix_favorites_albumId", "albumId"),
        Index("ix_favorites_userId", "userId"),
    )

    id: int = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    albumId: int = Column(
        Integer, ForeignKey("albuns.id", ondelete="CASCADE"), nullable=False
    )
    userId: int = Column(
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

    def to_dict(self) -> dict:
        """
        Convert the FavoriteModel instance to a dictionary.

        Returns:
            dict: A dictionary representation of the FavoriteModel instance.
        """
        return {
            "id": self.id,
            "albumId": self.albumId,
            "userId": self.userId,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt,
        }

    @classmethod
    def get_all(cls, session: Session) -> list[dict]:
        """
        Retrieve all favorite album entries from the database.

        Args:
            session: Active SQLAlchemy session.

        Returns:
            list[dict]: A list of dictionaries, each representing a favorite album entry.
        """
        return [f.to_dict() for f in session.query(cls).all()]

    @classmethod
    def create(cls, session: Session, albumId: int, userId: int) -> dict:
        """
        Create a new favorite album entry in the database.

        Args:
            session: Active SQLAlchemy session.
            albumId (int): The ID of the album being favorited.
            userId (int): The ID of the user who is favoriting the album.

        Returns:
            dict: A dictionary representation of the newly created favorite album entry.
        """
        existing = session.query(cls).filter_by(albumId=albumId, userId=userId).first()
        if existing:
            return existing.to_dict()
        obj: FavoriteModel = cls(albumId=albumId, userId=userId)
        session.add(obj)
        session.flush()
        return obj.to_dict()

    @classmethod
    def get_users_by_album(cls, session: Session, albumId: int) -> list[int]:
        """
        Return the IDs of all users who have favorited a given album.

        Args:
            session: Active SQLAlchemy session.
            albumId (int): The album ID to query favorites for.

        Returns:
            list[int]: A list of userId values.
        """
        rows = session.query(cls).filter(cls.albumId == albumId).all()
        return [row.userId for row in rows]

    @classmethod
    def get_by_user(cls, session: Session, userId: int) -> list[dict]:
        """Return favorite rows for a user as dicts.

        Args:
            session: Active SQLAlchemy session.
            userId (int): The user ID to query favorites for.

        Returns:
            list[dict]: A list of favorite entries as dictionaries.
        """
        rows = session.query(cls).filter(cls.userId == userId).all()
        return [r.to_dict() for r in rows]

    @classmethod
    def delete_for_user(cls, session: Session, albumId: int, userId: int) -> bool:
        """
        Delete a favorite for a user.

        Args:
            session: Active SQLAlchemy session.
            albumId (int): The ID of the album to remove from favorites.
            userId (int): The ID of the user whose favorite is being removed.

        Returns:
            bool: True if the favorite was deleted, False otherwise.
        """
        q = session.query(cls).filter_by(albumId=albumId, userId=userId)
        count = q.delete()
        return count > 0

    @classmethod
    def delete_all_for_album(cls, session: Session, album_id: int) -> int:
        """
        Delete all favorite entries for a specific album.

        Used when an album is deleted to clean up all favorite references.

        Args:
            session: Active SQLAlchemy session.
            album_id (int): The ID of the album to remove from all users' favorites.

        Returns:
            int: Number of favorite entries deleted.
        """
        count = (
            session.query(cls)
            .filter_by(albumId=album_id)
            .delete(synchronize_session=False)
        )
        return count
