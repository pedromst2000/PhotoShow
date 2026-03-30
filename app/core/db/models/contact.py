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

from app.core.db.engine import Base, SessionLocal


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
    def get_all(cls) -> list:
        """
        Retrieve all contact messages from the database and return them as a list of dictionaries.

        Returns:
            list: A list of dictionaries, each representing a contact message.
        """
        with SessionLocal() as session:
            return [c.to_dict() for c in session.query(cls).all()]

    @classmethod
    def create(cls, title: str, message: str, userId: int) -> dict:
        """
        Create a new contact message in the database.

        Args:
            title (str): The title of the contact message.
            message (str): The content of the contact message.
            userId (int): The ID of the user who submitted the contact message.

        Returns:
            dict: A dictionary representation of the newly created contact message.
        """
        # application-level validation: trim and ensure non-empty within limits
        trimmed_title = title.strip() if title is not None else ""
        trimmed_message = message.strip() if message is not None else ""
        if not trimmed_title:
            raise ValueError("Title is required")
        if not trimmed_message:
            raise ValueError("Message is required")
        if len(trimmed_title) > 75:
            raise ValueError("Title must be at most 75 characters")
        if len(trimmed_message) > 255:
            raise ValueError("Message must be at most 255 characters")

        with SessionLocal() as session:
            with session.begin():
                obj: ContactModel = cls(
                    title=trimmed_title, message=trimmed_message, userId=userId
                )
                session.add(obj)
                session.flush()
                return obj.to_dict()
