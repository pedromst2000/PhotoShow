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

from db.engine import Base, SessionLocal


class FollowModel(Base):
    """
    FollowModel represents a follow relationship between two users.
    """

    __tablename__: str = "follows"

    __table_args__ = (
        UniqueConstraint("followerId", "followedId", name="uq_follow_pair"),
        CheckConstraint("followerId != followedId", name="ck_follows_no_self_follow"),
        CheckConstraint("id > 0 AND id < 10000000", name="ck_follows_id_range"),
        CheckConstraint(
            "followerId > 0 AND followerId < 10000000", name="ck_follows_follower_range"
        ),
        CheckConstraint(
            "followedId > 0 AND followedId < 10000000", name="ck_follows_followed_range"
        ),
        Index("ix_follows_followedId", "followedId"),
        Index("ix_follows_followerId", "followerId"),
    )

    id: int = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    followerId: int = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    followedId: int = Column(
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
        Convert the FollowModel instance to a dictionary.

        Returns:
            dict: A dictionary representation of the FollowModel instance.
        """

        return {
            "id": self.id,
            "followerId": self.followerId,
            "followedId": self.followedId,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt,
        }

    @classmethod
    def follow(cls, follower_id: int, followed_id: int) -> dict | None:
        """
        Create a follow relationship.

        Args:
            follower_id (int): The ID of the user doing the following.
            followed_id (int): The ID of the user being followed.

        Returns:
            dict | None: The new follow entry, or None if already following.
        """
        with SessionLocal() as session:
            with session.begin():
                existing = (
                    session.query(cls)
                    .filter_by(followerId=follower_id, followedId=followed_id)
                    .first()
                )
                if existing:
                    return None
                obj = cls(followerId=follower_id, followedId=followed_id)
                session.add(obj)
                session.flush()
                return obj.to_dict()

    @classmethod
    def unfollow(cls, follower_id: int, followed_id: int) -> bool:
        """
        Remove a follow relationship.

        Args:
            follower_id (int): The ID of the user doing the unfollowing.
            followed_id (int): The ID of the user being unfollowed.

        Returns:
            bool: True if the relationship was removed, False if it didn't exist.
        """
        with SessionLocal() as session:
            with session.begin():
                deleted = (
                    session.query(cls)
                    .filter_by(followerId=follower_id, followedId=followed_id)
                    .delete()
                )
                return deleted > 0

    @classmethod
    def is_following(cls, follower_id: int, followed_id: int) -> bool:
        """
        Check whether follower_id is following followed_id.

        Returns:
            bool: True if the follow relationship exists.
        """
        with SessionLocal() as session:
            return (
                session.query(cls)
                .filter_by(followerId=follower_id, followedId=followed_id)
                .first()
            ) is not None

    @classmethod
    def get_followers(cls, user_id: int) -> list:
        """
        Return all follow entries where followed_id == user_id (people who follow this user).

        Returns:
            list[dict]: FollowModel dicts with followerID field.
        """
        with SessionLocal() as session:
            return [
                f.to_dict()
                for f in session.query(cls).filter_by(followedId=user_id).all()
            ]

    @classmethod
    def get_following(cls, user_id: int) -> list:
        """
        Return all follow entries where follower_id == user_id (users this user follows).

        Returns:
            list[dict]: FollowModel dicts with followedID field.
        """
        with SessionLocal() as session:
            return [
                f.to_dict()
                for f in session.query(cls).filter_by(followerId=user_id).all()
            ]

    @classmethod
    def count_followers(cls, user_id: int) -> int:
        """
        Return the number of users following user_id.

        Args:
            user_id (int): The ID of the user whose followers to count.

        Returns:
            int: The number of followers.
        """
        with SessionLocal() as session:
            return session.query(cls).filter_by(followedId=user_id).count()

    @classmethod
    def count_following(cls, user_id: int) -> int:
        """
        Return the number of users that user_id follows.

        Args:
            user_id (int): The ID of the user whose following to count.

        Returns:
            int: The number of users that user_id follows.
        """
        with SessionLocal() as session:
            return session.query(cls).filter_by(followerId=user_id).count()
