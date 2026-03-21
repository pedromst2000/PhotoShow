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
from sqlalchemy.orm import relationship

from db.engine import Base, SessionLocal


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

    # ORM back-reference: one notification_type has many notifications
    notifications_rel = relationship(
        "NotificationModel",
        cascade="all, delete-orphan",
        passive_deletes=True,
        back_populates="type_rel",
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
    def get_all(cls) -> list:
        with SessionLocal() as session:
            return [s.to_dict() for s in session.query(cls).order_by(cls.id).all()]

    @classmethod
    def get_by_type(cls, type_key: str) -> dict | None:
        with SessionLocal() as session:
            s = session.query(cls).filter_by(type=type_key).first()
            return s.to_dict() if s else None

    @classmethod
    def get_by_id(cls, id_key: int) -> dict | None:
        with SessionLocal() as session:
            s = session.query(cls).filter_by(id=id_key).first()
            return s.to_dict() if s else None

    @classmethod
    def is_enabled(cls, type_key: str) -> bool:
        with SessionLocal() as session:
            s = session.query(cls).filter_by(type=type_key).first()
            return s.isEnabled if s else False

    @classmethod
    def set_enabled(cls, type_key: str, enabled: bool) -> bool:
        with SessionLocal() as session:
            with session.begin():
                s = session.query(cls).filter_by(type=type_key).first()
                if s:
                    s.isEnabled = enabled
                    return True
        return False
