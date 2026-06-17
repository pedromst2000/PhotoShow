from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Session

from app.core.db.engine import Base


class NotificationTypeModel(Base):
    """
    Stores one row per notification type (renamed from notification_settings).
    The admin can toggle isEnabled to control which notification types are auto-sent.
    """

    __tablename__: str = "notification_types"

    __table_args__ = (
        UniqueConstraint("type", name="uq_notification_types_type"),
        CheckConstraint(
            "id > 0 AND id < 10000000", name="ck_notification_types_id_range"
        ),
        CheckConstraint(
            "length(trim(type)) > 0", name="ck_notification_types_type_not_empty"
        ),
        CheckConstraint(
            "length(trim(label)) > 0", name="ck_notification_types_label_not_empty"
        ),
    )

    id: int = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    type: str = Column(String(50), unique=True, nullable=False)
    label: str = Column(String(255), nullable=False)
    isEnabled: bool = Column(Boolean, default=True, nullable=False)
    createdAt: DateTime = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updatedAt: DateTime = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.type,
            "label": self.label,
            "isEnabled": self.isEnabled,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt,
        }

    @classmethod
    def get_all(cls, session: Session) -> list[dict]:
        """
        Retrieve all notification types from the database and return them as a list of dictionaries.

        Args:
            session: Active SQLAlchemy session.
        Returns:
            list[dict]: A list of dictionaries, each representing a notification type.
        """

        return [s.to_dict() for s in session.query(cls).order_by(cls.id).all()]

    @classmethod
    def get_by_type(cls, session: Session, type_key: str) -> dict | None:
        """
        Retrieve a notification type by its type from the database.

        Args:
            session: Active SQLAlchemy session.
            type_key: The type of the notification to retrieve.
        Returns:
            dict | None: A dictionary representing the notification type if found, otherwise None.
        """

        s = session.query(cls).filter_by(type=type_key).first()
        return s.to_dict() if s else None

    @classmethod
    def get_by_id(cls, session: Session, id_key: int) -> dict | None:
        """
        Retrieve a notification type by its ID from the database.

        Args:
            session: Active SQLAlchemy session.
            id_key: The ID of the notification type to retrieve.
        Returns:
            dict | None: A dictionary representing the notification type if found, otherwise None.
        """

        s = session.query(cls).filter_by(id=id_key).first()
        return s.to_dict() if s else None

    @classmethod
    def is_enabled(cls, session: Session, type_key: str) -> bool:
        """
        Check if a notification type is enabled.

        A notification type is considered enabled if it exists in the database and its isEnabled field is True.

        Args:
            session: Active SQLAlchemy session.
            type_key: The type of the notification to check.
        Returns:
            bool: True if the notification type is enabled, False otherwise.
        """

        s = session.query(cls).filter_by(type=type_key).first()
        return s.isEnabled if s else False

    @classmethod
    def set_enabled(cls, session: Session, type_key: str, enabled: bool) -> bool:
        """
        Set the enabled status of a notification type.

        Args:
            session: Active SQLAlchemy session.
            type_key: The type of the notification to update.
            enabled: The new enabled status.
        Returns:
            bool: True if the notification type was found and updated, False otherwise.
        """
        s = session.query(cls).filter_by(type=type_key).first()
        if s:
            s.isEnabled = enabled
            return True
        return False

    @classmethod
    def ensure_types_seeded(
        cls,
        session: Session,
        canonical: list,
    ) -> None:
        """
        Insert any canonical notification types that do not yet exist in the
        database, matching rows by their *type key* string (not by ID).

        This allows the service layer to keep IDs out of the canonical list
        and avoids ID drift between fresh installs (seeded via CSV with
        explicit IDs) and upgraded installs (seeded here with auto-increment).

        Args:
            session: Active SQLAlchemy session.
            canonical: List of ``(type_key, label)`` tuples to ensure exist.
        """
        for type_key, label in canonical:
            if not session.query(cls).filter_by(type=type_key).first():
                session.add(cls(type=type_key, label=label, isEnabled=True))
