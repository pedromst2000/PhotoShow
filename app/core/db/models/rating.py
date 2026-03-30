from datetime import datetime, timezone

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    UniqueConstraint,
    func,
)

from app.core.db.engine import Base, SessionLocal


class RatingModel(Base):
    """
    RatingModel represents a rating given by a user to a photo.
    """

    __tablename__ = "ratings"

    __table_args__ = (
        CheckConstraint("id > 0 AND id < 10000000", name="ck_ratings_id_range"),
        CheckConstraint("rating >= 1 AND rating <= 5", name="ck_ratings_range"),
        CheckConstraint(
            "userId > 0 AND userId < 10000000", name="ck_ratings_user_range"
        ),
        CheckConstraint(
            "photoId > 0 AND photoId < 10000000", name="ck_ratings_photo_range"
        ),
        UniqueConstraint("userId", "photoId", name="uq_ratings_user_photo"),
        Index("ix_ratings_photoId", "photoId"),
        Index("ix_ratings_userId", "userId"),
    )

    id: int = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    userId: int = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    photoId: int = Column(
        Integer, ForeignKey("photos.id", ondelete="CASCADE"), nullable=False
    )
    rating: int = Column(Integer, nullable=False)
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
        Convert the RatingModel instance to a dictionary.

        Returns:
            dict: A dictionary representation of the RatingModel instance.
        """

        return {
            "id": self.id,
            "userId": self.userId,
            "photoId": self.photoId,
            "rating": self.rating,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt,
        }

    @classmethod
    def create(cls, user_id: int, photo_id: int, rating_value: int) -> dict:
        """
        Create or update a rating for a photo by a user.

        Args:
            user_id (int): The ID of the user giving the rating.
            photo_id (int): The ID of the photo being rated.
            rating_value (int): The rating value (1-5).
        Returns:
            dict: The created or updated rating entry as a dictionary.
        """

        # clamp rating
        r = max(1, min(5, int(rating_value)))
        with SessionLocal() as session:
            with session.begin():
                existing = (
                    session.query(cls)
                    .filter_by(userId=user_id, photoId=photo_id)
                    .first()
                )
                if existing:
                    existing.rating = r
                    session.flush()
                    return existing.to_dict()
                obj = cls(userId=user_id, photoId=photo_id, rating=r)
                session.add(obj)
                session.flush()
                return obj.to_dict()

    @classmethod
    def get_for_photo(cls, photo_id: int) -> list:
        """
        Retrieve all ratings for a given photo.

        Args:
            photo_id (int): The ID of the photo for which to retrieve ratings.

        Returns:
            list: A list of dictionaries, each representing a rating for the photo.
        """

        with SessionLocal() as session:
            return [
                r.to_dict()
                for r in session.query(cls).filter_by(photoId=photo_id).all()
            ]

    @classmethod
    def get_average_for_photo(cls, photo_id: int) -> float:
        """
        Calculate the average rating for a given photo.

        Args:
            photo_id (int): The ID of the photo for which to calculate the average rating.
        Returns:
            float: The average rating for the photo, rounded to one decimal place. Returns 0.0 if there are no ratings.
        """

        with SessionLocal() as session:
            avg = (
                session.query(func.avg(cls.rating)).filter_by(photoId=photo_id).scalar()
            )
            if avg is None:
                return 0.0
            return round(float(avg), 1)
