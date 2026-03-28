from datetime import datetime, timezone

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

from db.engine import Base, SessionLocal

from .avatar import AvatarModel


class UserModel(Base):
    """
    UserModel represents a user in the database, with methods to create, retrieve, and update users.
    """

    __tablename__: str = "users"

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
        Get the user's role as a string.

        Returns:
            str: The user's role ('admin', 'regular', 'unsigned').
        """

        if self.roleId is None:
            return "unsigned"
        try:
            if getattr(self, "role_rel", None) is not None:
                return (
                    self.role_rel.role
                    if self.role_rel and getattr(self.role_rel, "role", None)
                    else "unsigned"
                )
        except Exception:
            # fall back to explicit query if relationship access fails
            pass

        from db.models.role import RoleModel

        with SessionLocal() as session:
            r = session.query(RoleModel).filter_by(id=self.roleId).first()
            return r.role if r else "unsigned"

    def to_dict(self) -> dict:
        """
        Convert the UserModel instance to a dictionary.

        Returns:
            dict: A dictionary representation of the UserModel instance.
        """
        # include avatar via related AvatarModel (lazy import to avoid circular deps)
        avatar_path = None
        try:
            from .avatar import AvatarModel

            avatar = AvatarModel.get_for_user(self.id)
            avatar_path = (
                avatar["avatar"]
                if avatar
                else "assets/images/profile_avatars/default_avatar.jpg"
            )
        except Exception:
            avatar_path = "assets/images/profile_avatars/default_avatar.jpg"
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
    def get_all(cls) -> list:
        """
        Retrieve all users from the database and return them as a list of dictionaries.

        Returns:
            list: A list of dictionaries, each representing a user.
        """
        with SessionLocal() as session:
            return [u.to_dict() for u in session.query(cls).all()]

    @classmethod
    def get_by_id(cls, userID: int) -> dict | None:
        """
        Retrieve a user by their ID.

        Args:
            userID (int): The ID of the user to retrieve.

        Returns:
            dict | None: A dictionary representation of the user if found, otherwise None.
        """
        with SessionLocal() as session:
            u = session.query(cls).filter_by(id=userID).first()
            return u.to_dict() if u else None

    @classmethod
    def create(
        cls,
        username: str,
        email: str,
        password: str,
        roleId: int = None,
        isBlocked: bool = False,
    ) -> dict:
        """
        Create a new user in the database.

        Args:
            username (str): The username of the user.
            email (str): The email address of the user.
            password (str): The password of the user.
            avatar (str, optional): The avatar image path.
            roleId (int, optional): The ID of the user's role.
            isBlocked (bool, optional): Whether the user is blocked.

        Returns:
            dict: A dictionary representation of the newly created user.
        """
        with SessionLocal() as session:
            with session.begin():
                user: UserModel = cls(
                    username=username,
                    email=email,
                    password=password,
                    roleId=roleId,
                    isBlocked=isBlocked,
                )
                session.add(user)
                session.flush()
                # ensure the user has an avatar row (DER: 1:1 mandatory)
                try:

                    default_avatar = "assets/images/profile_avatars/default_avatar.jpg"
                    # create avatar in the same transaction; if it already exists, ignore
                    avatar_obj = AvatarModel(userId=user.id, avatar=default_avatar)
                    session.add(avatar_obj)
                    session.flush()
                except Exception:
                    # do not fail user creation if avatar creation has issues
                    pass
                return user.to_dict()

    @classmethod
    def update(cls, updated: dict) -> dict:
        """
        Update an existing user in the database.

        Args:
            updated (dict): A dictionary containing the updated user information.

        Returns:
            dict: A dictionary representation of the updated user.
        """
        with SessionLocal() as session:
            with session.begin():
                u: UserModel = session.query(cls).filter_by(id=updated["id"]).first()
                if u:
                    ALLOWED = {"username", "email", "password", "roleId", "isBlocked"}
                    for key, value in updated.items():
                        if key in ALLOWED:
                            setattr(u, key, value)
        return updated

    @classmethod
    def get_by_email(cls, email: str) -> dict | None:
        """
        Retrieve a user by their email address.

        Args:
            email (str): The email address to search for.

        Returns:
            dict | None: A dictionary representation of the user if found, otherwise None.
        """
        with SessionLocal() as session:
            u = session.query(cls).filter(cls.email.ilike(email)).first()
            return u.to_dict() if u else None

    @classmethod
    def get_by_username(cls, username: str) -> dict | None:
        """
        Retrieve a user by their username (case-insensitive).

        Args:
            username (str): The username to search for.

        Returns:
            dict | None: A dictionary representation of the user if found, otherwise None.
        """
        with SessionLocal() as session:
            u = session.query(cls).filter(cls.username.ilike(username)).first()
            return u.to_dict() if u else None

    @classmethod
    def email_exists(cls, email: str) -> bool:
        """
        Check if an email already exists in the database.

        Args:
            email (str): The email address to check.

        Returns:
            bool: True if the email exists, False otherwise.
        """
        with SessionLocal() as session:
            return session.query(cls).filter(cls.email.ilike(email)).count() > 0

    @classmethod
    def username_exists(cls, username: str) -> bool:
        """
        Check if a username already exists in the database (case-insensitive).

        Args:
            username (str): The username to check.

        Returns:
            bool: True if the username exists, False otherwise.
        """
        with SessionLocal() as session:
            return session.query(cls).filter(cls.username.ilike(username)).count() > 0

    @classmethod
    def get_by_role(cls, role: str) -> list:
        """
        Retrieve all users with a specific role.

        Args:
            role (str): The role to filter by ('admin', 'regular', 'unsigned').

        Returns:
            list: A list of dictionaries representing users with that role.
        """
        from db.models.role import RoleModel

        with SessionLocal() as session:
            role_row = session.query(RoleModel).filter_by(role=role).first()
            if not role_row:
                return []
            return [
                u.to_dict()
                for u in session.query(cls).filter_by(roleId=role_row.id).all()
            ]

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

    @classmethod
    def get_blocked_users(cls) -> list:
        """
        Retrieve all blocked users.

        Returns:
            list: A list of dictionaries representing blocked users.
        """
        with SessionLocal() as session:
            return [
                u.to_dict() for u in session.query(cls).filter_by(isBlocked=True).all()
            ]

    @classmethod
    def update_avatar(cls, user_id: int, avatar_path: str) -> bool:
        """
        Update a user's avatar.

        Args:
            user_id (int): The user's ID.
            avatar_path (str): The new avatar path.

        Returns:
            bool: True if updated successfully, False otherwise.
        """
        # create a new AvatarModel row and mark it primary
        try:
            from .avatar import AvatarModel

            AvatarModel.create(
                user_id=user_id, avatar_path=avatar_path, is_primary=True
            )
            return True
        except Exception:
            return False

    @classmethod
    def update_password(cls, user_id: int, hashed_password: str) -> bool:
        """
        Update a user's password.

        Args:
            user_id (int): The user's ID.
            hashed_password (str): The new hashed password.

        Returns:
            bool: True if updated successfully, False otherwise.
        """
        with SessionLocal() as session:
            with session.begin():
                u = session.query(cls).filter_by(id=user_id).first()
                if u:
                    u.password = hashed_password
                    return True
        return False

    @classmethod
    def update_role(cls, user_id: int, role: str) -> bool:
        """
        Update a user's role by role name.

        Args:
            user_id (int): The user's ID.
            role (str): The new role name ('admin', 'regular', 'unsigned').

        Returns:
            bool: True if updated successfully, False otherwise.
        """
        from db.models.role import RoleModel

        with SessionLocal() as session:
            with session.begin():
                role_row = session.query(RoleModel).filter_by(role=role).first()
                if not role_row:
                    return False
                u = session.query(cls).filter_by(id=user_id).first()
                if u:
                    u.roleId = role_row.id
                    return True
        return False

    @classmethod
    def set_blocked(cls, user_id: int, is_blocked: bool) -> bool:
        """
        Set a user's blocked status.

        Args:
            user_id (int): The user's ID.
            is_blocked (bool): The blocked status.

        Returns:
            bool: True if updated successfully, False otherwise.
        """
        with SessionLocal() as session:
            with session.begin():
                u = session.query(cls).filter_by(id=user_id).first()
                if u:
                    u.isBlocked = is_blocked
                    return True
        return False

    @classmethod
    def delete(cls, user_id: int) -> bool:
        """
        Delete a user from the database.

        Args:
            user_id (int): The user's ID.

        Returns:
            bool: True if deleted successfully, False otherwise.
        """
        with SessionLocal() as session:
            with session.begin():
                u = session.query(cls).filter_by(id=user_id).first()
                if u:
                    session.delete(u)
                    return True
        return False
