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


class ReportModel(Base):
    """
    ReportModel represents a user-submitted content report against a photo or comment.
    """

    __tablename__: str = "reports"

    __table_args__ = (
        CheckConstraint("id > 0 AND id < 10000000", name="ck_reports_id_range"),
        CheckConstraint(
            "reporterId > 0 AND reporterId < 10000000",
            name="ck_reports_reporterId_range",
        ),
        CheckConstraint(
            "reasonId > 0 AND reasonId < 10000",
            name="ck_reports_reasonId_range",
        ),
        CheckConstraint(
            "(photoId IS NULL) != (commentId IS NULL)",
            name="ck_reports_target_exclusive",
        ),
        CheckConstraint(
            "description IS NULL OR length(description) <= 255",
            name="ck_reports_description_maxlen",
        ),
        Index("ix_reports_reporterId", "reporterId"),
        Index("ix_reports_reasonId", "reasonId"),
        Index("ix_reports_photoId", "photoId"),
        Index("ix_reports_commentId", "commentId"),
    )

    id: int = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    reporterId: int = Column(
        Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    reasonId: int = Column(
        Integer, ForeignKey("report_reasons.id", ondelete="RESTRICT"), nullable=False
    )
    photoId: int = Column(
        Integer, ForeignKey("photos.id", ondelete="CASCADE"), nullable=True
    )
    commentId: int = Column(
        Integer, ForeignKey("comments.id", ondelete="CASCADE"), nullable=True
    )
    description: str = Column(String(255), nullable=True)
    createdAt: DateTime = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updatedAt: DateTime = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self) -> dict:
        """Return the report as a dict."""
        return {
            "id": self.id,
            "reporterId": self.reporterId,
            "reasonId": self.reasonId,
            "photoId": self.photoId,
            "commentId": self.commentId,
            "description": self.description,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt,
        }

    @classmethod
    def get_all(cls, session: Session) -> list[dict]:
        """
        Return all reports as a list of dicts.

        Args:
            session: Active SQLAlchemy session.
        Returns:
            list[dict]: List of report dicts.
        """
        return [r.to_dict() for r in session.query(cls).order_by(cls.id).all()]

    @classmethod
    def create(
        cls,
        session: Session,
        reporter_id: int,
        reason_id: int,
        photo_id: int | None = None,
        comment_id: int | None = None,
        description: str | None = None,
    ) -> dict:
        """
        Create a new report against a photo or comment.

        Args:
            session: Active SQLAlchemy session (caller manages the transaction).
            reporter_id: The ID of the user submitting the report.
            reason_id: The ID of the report reason (foreign key to report_reasons).
            photo_id: The ID of the photo being reported (if applicable).
            comment_id: The ID of the comment being reported (if applicable).
            description: Optional extra detail (required when reason is "Other").
        Returns:
            dict: The created report as a dict.
        """
        obj = cls(
            reporterId=reporter_id,
            reasonId=reason_id,
            photoId=photo_id,
            commentId=comment_id,
            description=description or None,
        )
        session.add(obj)
        session.flush()
        return obj.to_dict()

    @classmethod
    def get_by_id(cls, session: Session, report_id: int) -> dict | None:
        """
        Get a single report by its ID.

        Args:
            session: Active SQLAlchemy session.
            report_id: The ID of the report to retrieve.
        Returns:
            dict | None: The report as a dict if found, or None if not found.
        """
        obj = session.query(cls).filter(cls.id == report_id).first()
        return obj.to_dict() if obj else None

    @classmethod
    def delete(cls, session: Session, report_id: int) -> bool:
        """
        Delete a report by its ID.

        Args:
            session: Active SQLAlchemy session (caller manages the transaction).
            report_id: The ID of the report to delete.
        Returns:
            bool: True if the report was successfully deleted, False if not found.
        """
        obj = session.query(cls).filter(cls.id == report_id).first()
        if obj is None:
            return False
        session.delete(obj)
        return True

    @classmethod
    def has_user_reported(
        cls,
        session: Session,
        reporter_id: int,
        photo_id: int | None = None,
        comment_id: int | None = None,
    ) -> bool:
        """
        Check if a user has already reported a specific photo or comment.

        Args:
            session: Active SQLAlchemy session.
            reporter_id: The ID of the user (reporter).
            photo_id: The ID of the photo (mutually exclusive with comment_id).
            comment_id: The ID of the comment (mutually exclusive with photo_id).
        Returns:
            bool: True if the user has already reported this photo/comment, False otherwise.
        """
        query = session.query(cls).filter(cls.reporterId == reporter_id)

        if photo_id is not None:
            query = query.filter(cls.photoId == photo_id)
        elif comment_id is not None:
            query = query.filter(cls.commentId == comment_id)

        return query.first() is not None
