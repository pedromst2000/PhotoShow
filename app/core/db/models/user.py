from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    Boolean,
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


class UserModel(Base):
    """
    UserModel represents a user in the database, with methods to create, retrieve, and update users.
    """

    __tablename__: str = "users"

    __table_args__ = (
        CheckConstraint("id > 0 AND id < 10000000", name="ck_users_id_range"),
        CheckConstraint(
            "roleId > 0 AND roleId < 10000000",
            name="ck_users_roleId_range",
        ),
        CheckConstraint(
            "length(trim(username)) > 0", name="ck_users_username_not_empty"
        ),
        CheckConstraint("length(username) <= 125", name="ck_users_username_maxlen"),
        CheckConstraint("length(trim(email)) > 0", name="ck_users_email_not_empty"),
        CheckConstraint("length(email) <= 125", name="ck_users_email_maxlen"),
        Index("ix_users_roleId", "roleId"),
    )

    id: int = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    username: str = Column(String(125), unique=True, nullable=False)
    email: str = Column(String(125), unique=True, nullable=False)
    password: str = Column(String(125), nullable=False)

    roleId: int = Column(
        Integer, ForeignKey("roles.id", ondelete="RESTRICT"), nullable=False, default=3
    )  # roleId defaults to 3 (unsigned) and is required
    isBlocked: bool = Column(Boolean, default=False)
    createdAt: DateTime = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updatedAt: DateTime = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    @property
    def following(self):
        return self.following_rel

    @property
    def followers(self):
        return self.followers_rel

    @property
    def role(self) -> str:
        """
        Get the user's role as a string via ORM relationship.

        Returns:
            str: The user's role ('admin', 'regular', 'unsigned').
        """
        if self.roleId is None:
            return "unsigned"
        try:
            if getattr(self, "role_rel", None) is not None:
                return getattr(self.role_rel, "role", "unsigned") or "unsigned"
        except Exception:
            pass
        return "unsigned"

    def to_dict(self) -> dict:
        """
        Convert the UserModel instance to a dictionary.
        Uses ORM relationships for avatar and role (requires active session).

        Returns:
            dict: A dictionary representation of the UserModel instance.
        """
        avatar_path = None
        try:
            if getattr(self, "avatar_rel", None) is not None:
                from app.utils.file_utils import resolve_avatar_path

                avatar_path = resolve_avatar_path(self.avatar_rel.avatar)
        except Exception:
            pass
        if avatar_path is None:
            from app.utils.file_utils import _DEFAULT_AVATAR

            avatar_path = _DEFAULT_AVATAR

        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "password": self.password,
            "avatar": avatar_path,
            "role": self.role,
            "roleId": self.roleId,
            "isBlocked": self.isBlocked,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt,
        }

    @classmethod
    def get_all(cls, session: Session) -> list:
        """
        Retrieve all users from the database.

        Args:
            session: Active SQLAlchemy session.

        Returns:
            list: A list of dictionaries, each representing a user.
        """
        return [u.to_dict() for u in session.query(cls).all()]

    @classmethod
    def get_password_hashes(cls, session: Session) -> list:
        """
        Retrieve only the password column for all users.

        Args:
            session: Active SQLAlchemy session.

        Returns:
            list: A list of password strings.
        """
        rows = session.query(cls.password).all()  # type: ignore[call-overload]
        return [r[0] for r in rows if r and r[0] is not None]

    @classmethod
    def get_by_id(cls, session: Session, userID: int) -> dict | None:
        """
        Retrieve a user by their ID.

        Args:
            session: Active SQLAlchemy session.
            userID (int): The ID of the user to retrieve.

        Returns:
            dict | None: A dictionary representation of the user if found, otherwise None.
        """
        u = session.query(cls).filter_by(id=userID).first()
        return u.to_dict() if u else None

    @classmethod
    def get_by_ids(cls, session: Session, user_ids: list[int]) -> dict[int, dict]:
        """
        Retrieve multiple users by a list of IDs in a single query.

        Args:
            session: Active SQLAlchemy session.
            user_ids (list[int]): The list of user IDs to retrieve.

        Returns:
            dict[int, dict]: A mapping of user ID -> user dict for all found users.
        """
        rows = session.query(cls).filter(cls.id.in_(user_ids)).all()
        return {u.id: u.to_dict() for u in rows}

    @classmethod
    def create(
        cls,
        session: Session,
        username: str,
        email: str,
        password: str,
        roleId: Optional[int] = None,
        isBlocked: bool = False,
    ) -> dict:
        """
        Create a new user in the database.

        Args:
            session: Active SQLAlchemy session.
            username (str): The username of the user.
            email (str): The email address of the user.
            password (str): The hashed password of the user.
            roleId (int, optional): The ID of the user's role.
            isBlocked (bool, optional): Whether the user is blocked.

        Returns:
            dict: A dictionary representation of the newly created user.
        """
        user: UserModel = cls(
            username=username,
            email=email,
            password=password,
            roleId=roleId,
            isBlocked=isBlocked,
        )
        session.add(user)
        session.flush()
        return user.to_dict()

    @classmethod
    def update(cls, session: Session, updated: dict) -> dict:
        """
        Update an existing user in the database.

        Args:
            session: Active SQLAlchemy session.
            updated (dict): A dictionary containing the updated user information.

        Returns:
            dict: A dictionary representation of the updated user.
        """
        u: UserModel = session.query(cls).filter_by(id=updated["id"]).first()
        if u:
            ALLOWED = {"username", "email", "password", "roleId", "isBlocked"}
            for key, value in updated.items():
                if key in ALLOWED:
                    setattr(u, key, value)
        return updated

    @classmethod
    def get_by_email(cls, session: Session, email: str) -> dict | None:
        """
        Retrieve a user by their email address.

        Args:
            session: Active SQLAlchemy session.
            email (str): The email address to search for.

        Returns:
            dict | None: A dictionary representation of the user if found, otherwise None.
        """
        u = session.query(cls).filter(cls.email.ilike(email)).first()
        return u.to_dict() if u else None

    @classmethod
    def get_by_username(cls, session: Session, username: str) -> dict | None:
        """
        Retrieve a user by their username (case-insensitive).

        Args:
            session: Active SQLAlchemy session.
            username (str): The username to search for.

        Returns:
            dict | None: A dictionary representation of the user if found, otherwise None.
        """
        u = session.query(cls).filter(cls.username.ilike(username)).first()
        return u.to_dict() if u else None

    @classmethod
    def email_exists(cls, session: Session, email: str) -> bool:
        """
        Check if an email already exists in the database.

        Args:
            session: Active SQLAlchemy session.
            email (str): The email address to check.

        Returns:
            bool: True if the email exists, False otherwise.
        """
        return session.query(cls).filter(cls.email.ilike(email)).count() > 0

    @classmethod
    def username_exists(cls, session: Session, username: str) -> bool:
        """
        Check if a username already exists in the database (case-insensitive).

        Args:
            session: Active SQLAlchemy session.
            username (str): The username to check.

        Returns:
            bool: True if the username exists, False otherwise.
        """
        return session.query(cls).filter(cls.username.ilike(username)).count() > 0

    @classmethod
    def get_blocked_users(cls, session: Session) -> list:
        """
        Retrieve all blocked users.

        Args:
            session: Active SQLAlchemy session.

        Returns:
            list: A list of dictionaries representing blocked users.
        """
        return [u.to_dict() for u in session.query(cls).filter_by(isBlocked=True).all()]

    @classmethod
    def update_password(
        cls, session: Session, user_id: int, hashed_password: str
    ) -> bool:
        """
        Update a user's password.

        Args:
            session: Active SQLAlchemy session.
            user_id (int): The user's ID.
            hashed_password (str): The new hashed password.

        Returns:
            bool: True if updated successfully, False otherwise.
        """
        u = session.query(cls).filter_by(id=user_id).first()
        if u:
            u.password = hashed_password
            return True
        return False

    @classmethod
    def set_blocked(cls, session: Session, user_id: int, is_blocked: bool) -> bool:
        """
        Set a user's blocked status.

        Args:
            session: Active SQLAlchemy session.
            user_id (int): The user's ID.
            is_blocked (bool): The blocked status.

        Returns:
            bool: True if updated successfully, False otherwise.
        """
        u = session.query(cls).filter_by(id=user_id).first()
        if u:
            u.isBlocked = is_blocked
            return True
        return False

    @classmethod
    def delete(cls, session: Session, user_id: int) -> bool:
        """
        Delete a user from the database.

        Args:
            session: Active SQLAlchemy session.
            user_id (int): The user's ID.

        Returns:
            bool: True if deleted successfully, False otherwise.
        """
        u = session.query(cls).filter_by(id=user_id).first()
        if u:
            session.delete(u)
            return True
        return False
