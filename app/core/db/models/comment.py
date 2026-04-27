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
from sqlalchemy.orm import Session

from app.core.db.engine import Base


class CommentModel(Base):
    """
    CommentModel represents a plain comment in the database.
    """

    __tablename__: str = "comments"

    __table_args__ = (
        CheckConstraint("id > 0 AND id < 10000000", name="ck_comments_id_range"),
        CheckConstraint(
            "authorId > 0 AND authorId < 10000000", name="ck_comments_author_range"
        ),
        CheckConstraint(
            "photoId > 0 AND photoId < 10000000", name="ck_comments_photo_range"
        ),
        CheckConstraint(
            "length(trim(comment)) > 0", name="ck_comments_comment_not_empty"
        ),
        CheckConstraint("length(comment) <= 255", name="ck_comments_comment_maxlen"),
        Index("ix_comments_photoId_createdAt", "photoId", "createdAt"),
    )

    id: int = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    authorId: int = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    comment: str = Column(String(255), nullable=False)
    photoId: int = Column(
        Integer, ForeignKey("photos.id", ondelete="CASCADE"), nullable=False
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
        Convert the CommentModel instance to a dictionary.

        Returns:
            dict: A dictionary representation of the CommentModel instance.
        """
        return {
            "id": self.id,
            "authorId": self.authorId,
            "comment": self.comment,
            "photoId": self.photoId,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt,
        }

    @classmethod
    def get_by_id(cls, session: Session, comment_id: int) -> dict | None:
        """
        Retrieve a comment by its ID.

        Args:
            session: Active SQLAlchemy session.
            comment_id (int): The ID of the comment to retrieve.

        Returns:
            dict | None: A dictionary representation of the comment if found, otherwise None.
        """
        obj = session.query(cls).filter_by(id=comment_id).first()
        return obj.to_dict() if obj else None

    @classmethod
    def get_all(cls, session: Session) -> list:
        """
        Retrieve all comments from the database.

        Args:
            session: Active SQLAlchemy session.

        Returns:
            list: A list of dictionaries, each representing a comment.
        """
        return [c.to_dict() for c in session.query(cls).all()]

    @classmethod
    def get_by_photo(cls, session: Session, photo_id: int) -> list:
        """
        Retrieve all comments for a photo ordered by creation time (oldest first).

        Args:
            session: Active SQLAlchemy session.
            photo_id (int): The photo ID.

        Returns:
            list: A list of comment dicts.
        """
        return [
            c.to_dict()
            for c in session.query(cls)
            .filter_by(photoId=photo_id)
            .order_by(cls.createdAt)
            .all()
        ]

    @classmethod
    def create(
        cls,
        session: Session,
        authorId: int,
        comment: str,
        photoId: int,
    ) -> dict:
        """
        Create a new comment in the database.

        Args:
            session: Active SQLAlchemy session.
            authorId (int): The ID of the user who authored the comment.
            comment (str): The content of the comment (pre-validated).
            photoId (int): The ID of the photo the comment belongs to.

        Returns:
            dict: A dictionary representation of the newly created comment.
        """
        obj: CommentModel = cls(
            authorId=authorId,
            comment=comment,
            photoId=photoId,
        )
        session.add(obj)
        session.flush()
        return obj.to_dict()

    @classmethod
    def delete(cls, session: Session, comment_id: int) -> bool:
        """
        Delete a comment from the database.

        Args:
            session: Active SQLAlchemy session.
            comment_id (int): The ID of the comment to delete.
        Returns:
            bool: True if the comment was deleted, False if it was not found.
        """
        obj: CommentModel | None = session.query(cls).filter_by(id=comment_id).first()
        if obj is None:
            return False
        session.delete(obj)
        return True
