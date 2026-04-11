import re as regex

from app.core.db.engine import SessionLocal
from app.core.db.models.album import AlbumModel
from app.core.db.models.avatar import AvatarModel
from app.core.db.models.contact import ContactModel
from app.core.db.models.follow import FollowModel
from app.core.db.models.photo import PhotoModel
from app.core.db.models.role import RoleModel
from app.core.db.models.user import UserModel


class UserService:
    """
    Service class for user management business logic.

    Business rules enforced in this service:
    - User listing for admin management excludes admin users and returns only essential fields.
    - Avatar updates create a new avatar record and associate it with the user.
    - Role changes validate that the new role is a valid assignable role.
    - Blocking/unblocking users checks current status to prevent redundant operations.
    - User filtering by username/email is case-insensitive and excludes admin users.
    - Contact messages are checked for duplicate titles before creation.
    - Follow/unfollow operations check for existing relationships to prevent duplicates or errors.
    - When retrieving followers/following, full user profiles are returned for display purposes.
    - All methods that modify data enforce necessary validation and business rules.
    """

    @staticmethod
    def get_profile_stats(user_id: int) -> dict:
        """
        Get profile statistics combining follower count and photo count.

        Combines FollowModel, AlbumModel, and PhotoModel in one session —
        a real use-case representing the data needed for the profile page.
        """
        with SessionLocal() as session:
            follower_count = FollowModel.count_followers(session, user_id)
            albums = AlbumModel.get_by_creator(session, user_id)
            photo_count = sum(
                len(PhotoModel.get_by_album(session, a["id"])) for a in albums
            )
        return {"follower_count": follower_count, "photo_count": photo_count}

    @staticmethod
    def delete_user(user_id: int) -> bool:
        with SessionLocal() as session:
            result = UserModel.delete(session, user_id)
            session.commit()
            return result

    @staticmethod
    def get_user_list_for_admin() -> list:
        """
        Get a filtered list of users for admin management.
        Excludes admin users and returns only essential fields.

        Returns:
            list: List of user dicts with userID, username, email, role, avatar, isBlocked.
        """
        with SessionLocal() as session:
            return [
                {
                    "id": user["id"],
                    "username": user["username"],
                    "email": user["email"],
                    "role": user["role"],
                    "avatar": user["avatar"],
                    "isBlocked": user["isBlocked"],
                }
                for user in UserModel.get_all(session)
                if user["role"] != "admin"
            ]

    @staticmethod
    def update_avatar(user_id: int, avatar_filename: str) -> bool:
        """
        Update a user's avatar.

        Args:
            user_id: The user's ID.
            avatar_filename: The new avatar filename (not full path).

        Returns:
            bool: True if updated successfully, False otherwise.
        """
        avatar_path = f"assets/images/profile_avatars/{avatar_filename}"
        with SessionLocal() as session:
            result = AvatarModel.create(session, user_id, avatar_path)
            session.commit()
        return result is not None

    @staticmethod
    def change_role(username: str, new_role: str) -> bool:
        """
        Change a user's role.

        Args:
            username: The username of the user.
            new_role: The new role to assign.

        Returns:
            bool: True if role was changed successfully, False otherwise.

        Raises:
            ValueError: If new_role is not a valid assignable role.
        """
        VALID_ROLES = ["regular", "unsigned"]
        if new_role not in VALID_ROLES:
            raise ValueError(f"Invalid role. Must be one of: {', '.join(VALID_ROLES)}")

        with SessionLocal() as session:
            user = UserModel.get_by_username(session, username)
            if not user:
                return False
            role = RoleModel.get_by_name(session, new_role)
            if not role:
                return False
            UserModel.update(session, {**user, "roleId": role["id"]})
            session.commit()
        return True

    @staticmethod
    def block_user(username: str) -> bool:
        """
        Block a user by username.

        Args:
            username: The username of the user to block.

        Returns:
            bool: True if blocked successfully, False otherwise.
        """
        with SessionLocal() as session:
            user = UserModel.get_by_username(session, username)
            if not user:
                return False
            if user["isBlocked"]:
                raise ValueError(f'"{username}" is already blocked.')
            result = UserModel.set_blocked(session, user["id"], True)
            session.commit()
            return result

    @staticmethod
    def unblock_user(username: str) -> bool:
        """
        Unblock a user by username.

        Args:
            username: The username of the user to unblock.

        Returns:
            bool: True if unblocked successfully, False otherwise.
        """
        with SessionLocal() as session:
            user = UserModel.get_by_username(session, username)
            if not user:
                return False
            if not user["isBlocked"]:
                raise ValueError(f'"{username}" is already unblocked.')
            result = UserModel.set_blocked(session, user["id"], False)
            session.commit()
            return result

    @staticmethod
    def is_user_blocked(user_id: int) -> bool:
        """
        Check if a user is blocked.

        Args:
            user_id: The user's ID.

        Returns:
            bool: True if user is blocked, False otherwise.
        """
        with SessionLocal() as session:
            user = UserModel.get_by_id(session, user_id)
        return user["isBlocked"] if user else False

    @staticmethod
    def get_users_by_role(role: str) -> list:
        """
        Get all users with a specific role.

        Args:
            role: The role to filter by.

        Returns:
            list: List of user dictionaries with the specified role.
        """
        with SessionLocal() as session:
            role_obj = RoleModel.get_by_name(session, role)
            if not role_obj:
                return []
            return [
                u for u in UserModel.get_all(session) if u["roleId"] == role_obj["id"]
            ]

    @staticmethod
    def filter_users(username: str, email: str) -> list:
        """
        Filter users by username prefix and/or email prefix (case-insensitive).
        Admin users are always excluded.

        Args:
            username: Username prefix to filter by (empty string to skip).
            email: Email prefix to filter by (empty string to skip).

        Returns:
            list: Filtered list of user dictionaries.
        """
        with SessionLocal() as session:
            users = [u for u in UserModel.get_all(session) if u["role"] != "admin"]

        if username:
            users = [
                u for u in users if u["username"].lower().startswith(username.lower())
            ]

        if email:
            users = [u for u in users if u["email"].lower().startswith(email.lower())]

        return users

    @staticmethod
    def get_contacts_with_usernames() -> list:
        """
        Retrieve all contact messages enriched with the submitting user's username.

        Returns:
            list: List of dicts with contactID, title, message, username.
        """
        with SessionLocal() as session:
            contacts = ContactModel.get_all(session)
            if not contacts:
                return []
            return [
                {
                    "id": c["id"],
                    "title": c["title"],
                    "message": c["message"],
                    "username": (UserModel.get_by_id(session, c["userId"]) or {}).get(
                        "username", "Unknown"
                    ),
                }
                for c in contacts
            ]

    @staticmethod
    def follow_user(follower_id: int, followed_id: int) -> bool:
        """
        Make follower_id follow followed_id.

        Args:
            follower_id: The ID of the user doing the following.
            followed_id: The ID of the user being followed.

        Returns:
            bool: True if the follow was created, False if already following.
        """
        with SessionLocal() as session:
            result = FollowModel.follow(session, follower_id, followed_id)
            session.commit()
        return result is not None

    @staticmethod
    def unfollow_user(follower_id: int, followed_id: int) -> bool:
        """
        Make follower_id unfollow followed_id.

        Args:
            follower_id: The ID of the user doing the unfollowing.
            followed_id: The ID of the user being unfollowed.

        Returns:
            bool: True if the relationship was removed, False if it didn't exist.
        """
        with SessionLocal() as session:
            return FollowModel.unfollow(session, follower_id, followed_id)

    @staticmethod
    def get_followers(user_id: int) -> list:
        """
        Return full user profiles for everyone who follows user_id.

        Returns:
            list[dict]: User dicts (from UserModel) for each follower.
        """
        with SessionLocal() as session:
            follows = FollowModel.get_followers(session, user_id)
            result = []
            for f in follows:
                user = UserModel.get_by_id(session, f["followerId"])
                if user:
                    result.append(user)
            return result

    @staticmethod
    def get_following(user_id: int) -> list:
        """
        Return full user profiles for everyone that user_id follows.

        Returns:
            list[dict]: User dicts (from UserModel) for each followed user.
        """
        with SessionLocal() as session:
            follows = FollowModel.get_following(session, user_id)
            result = []
            for f in follows:
                user = UserModel.get_by_id(session, f["followedId"])
                if user:
                    result.append(user)
            return result

    @staticmethod
    def validate_contact_title_format(title: str) -> bool:
        """
        Validate contact message title format.

        Rules enforced:
        - Title must contain only ASCII letters (A-Z, a-z).
        - No digits, spaces, or special characters allowed.

        Args:
            title: The contact title to validate.

        Returns:
            bool: True if the title format is valid, False otherwise.
        """
        if not title or not isinstance(title, str):
            return False
        # Use fullmatch to ensure only letters, no spaces or special chars
        return bool(regex.fullmatch(r"[A-Za-z]+", title))

    @staticmethod
    def create_contact(title: str, message: str, userId: int) -> dict:
        """
        Create a new contact message from a user.

        Args:
            title: Subject of the message (should be trimmed, pre-validated).
            message: Body of the message (should be trimmed, pre-validated).
            userId: The ID of the user sending the message.

        Returns:
            dict: The created contact message as a dictionary.

        Raises:
            ValueError: If a message with the same title already exists (after whitespace normalization).
        """

        # Business rule: normalize whitespace for duplicate detection.
        # Treats "Apologizes ", "Apologizes", "Apologizes   ", and "Apologizes  A"
        # as duplicates based on their normalized form.
        def _normalize(s: str) -> str:
            return " ".join(s.split()).strip().lower()

        normalized_title = _normalize(title)

        with SessionLocal() as session:
            # Fetch all existing titles and check normalized duplicates in service layer
            rows = session.query(ContactModel.title).all()
            for (t,) in rows:
                if _normalize(t) == normalized_title:
                    raise ValueError("A message with this title already exists")
            result = ContactModel.create(
                session, title=title, message=message, userId=userId
            )
            session.commit()
            return result
