from datetime import datetime, timezone

from sqlalchemy import func  # import func for SQL functions like lower() and trim()
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


class ContactModel(Base):
    """
    ContactModel represents a contact message in the database, with methods to create and retrieve contacts.
    """

    __tablename__: str = "contacts"

    __table_args__ = (
        CheckConstraint("id > 0 AND id < 10000000", name="ck_contacts_id_range"),
        CheckConstraint(
            "userId > 0 AND userId < 10000000", name="ck_contacts_userId_range"
        ),
        CheckConstraint("length(trim(title)) > 0", name="ck_contacts_title_not_empty"),
        CheckConstraint(
            "length(trim(message)) > 0", name="ck_contacts_message_not_empty"
        ),
        CheckConstraint("length(title) <= 75", name="ck_contacts_title_maxlen"),
        CheckConstraint("length(message) <= 255", name="ck_contacts_message_maxlen"),
        Index("ix_contacts_userId", "userId"),
    )

    id: int = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    title: str = Column(String(75), nullable=False)
    message: str = Column(String(255), nullable=False)
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
        Convert the ContactModel instance to a dictionary.

        Returns:
            dict: A dictionary representation of the ContactModel instance.
        """
        return {
            "id": self.id,
            "title": self.title,
            "message": self.message,
            "userId": self.userId,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt,
        }

    @classmethod
    def get_all(cls, session: Session) -> list:
        """
        Retrieve all contact messages from the database.

        Args:
            session: Active SQLAlchemy session.

        Returns:
            list: A list of dictionaries, each representing a contact message.
        """
        return [c.to_dict() for c in session.query(cls).all()]

    @classmethod
    def create(cls, session: Session, title: str, message: str, userId: int) -> dict:
        """
        Create a new contact message in the database.

        Args:
            session: Active SQLAlchemy session.
            title (str): The title of the contact message (pre-validated).
            message (str): The content of the contact message (pre-validated).
            userId (int): The ID of the user who submitted the contact message.

        Returns:
            dict: A dictionary representation of the newly created contact message.
        """
        obj: ContactModel = cls(title=title, message=message, userId=userId)
        session.add(obj)
        session.flush()
        return obj.to_dict()

    @classmethod
    def title_exists(cls, session: Session, title: str) -> bool:
        """
        Check whether a contact with this title already exists (case-insensitive, exact match).
        Expects pre-normalized title from the service layer.

        Args:
            session: Active SQLAlchemy session.
            title (str): The title to check (should be already validated/normalized by service).

        Returns:
            bool: True if a matching title exists.
        """
        return session.query(
            session.query(cls)
            .filter(func.lower(func.trim(cls.title)) == title.lower())
            .exists()
        ).scalar()
