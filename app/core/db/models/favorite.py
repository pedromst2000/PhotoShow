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

from app.core.db.engine import Base, SessionLocal


class FavoriteModel(Base):
    """
    FavoriteModel represents a favorite album entry in the database, with methods to create and retrieve favorites.
    """

    __tablename__: str = "favorites"

    __table_args__ = (
        CheckConstraint("id > 0 AND id < 10000000", name="ck_favorites_id_range"),
        CheckConstraint(
            "albumId > 0 AND albumId < 10000000", name="ck_favorites_albumId_range"
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
    def get_all(cls) -> list:
        """
        Retrieve all favorite album entries from the database and return them as a list of dictionaries.

        Returns:
            list: A list of dictionaries, each representing a favorite album entry.
        """
        with SessionLocal() as session:
            return [f.to_dict() for f in session.query(cls).all()]

    @classmethod
    def create(cls, albumId: int, userId: int) -> dict:
        """
        Create a new favorite album entry in the database.

        Args:
            albumId (int): The ID of the album being favorited.
            userId (int): The ID of the user who is favoriting the album.

        Returns:
            dict: A dictionary representation of the newly created favorite album entry.
        """
        with SessionLocal() as session:
            with session.begin():
                # idempotent create: return existing if already favorited
                existing = (
                    session.query(cls).filter_by(albumId=albumId, userId=userId).first()
                )
                if existing:
                    return existing.to_dict()
                obj: FavoriteModel = cls(albumId=albumId, userId=userId)
                session.add(obj)
                session.flush()
                return obj.to_dict()

    @classmethod
    def get_users_by_album(cls, albumId: int) -> list:
        """
        Return the IDs of all users who have favorited a given album.

        Args:
            albumId (int): The album ID to query favorites for.

        Returns:
            list[int]: A list of userId values.
        """
        with SessionLocal() as session:
            rows = session.query(cls).filter(cls.albumId == albumId).all()
            return [row.userId for row in rows]

    @classmethod
    def get_by_user(cls, userId: int) -> list:
        """Return favorite rows for a user as dicts.

        Args:
            userId (int): The user ID to query favorites for.

        Returns:
            list[dict]: A list of favorite entries as dictionaries.
        """
        with SessionLocal() as session:
            rows = session.query(cls).filter(cls.userId == userId).all()
            return [r.to_dict() for r in rows]

    @classmethod
    def delete_for_user(cls, albumId: int, userId: int) -> bool:
        """
        Delete a favorite for a user.

        Args:
            albumId (int): The ID of the album to remove from favorites.
            userId (int): The ID of the user whose favorite is being removed.

        Returns:
            bool: True if the favorite was deleted, False otherwise.
        """
        with SessionLocal() as session:
            with session.begin():
                q = session.query(cls).filter_by(albumId=albumId, userId=userId)
                count = q.delete()
                return count > 0
