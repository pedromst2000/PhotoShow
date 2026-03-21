from typing import Optional

from db.models import ContactModel, FollowModel, UserModel


class UserService:
    """
    Service class for user management business logic.

    Handles user profile operations, avatar changes, and user administration.
    """

    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[dict]:
        """
        Get a user's complete information by their ID.

        Parameters:
            user_id: The ID of the user.

        Returns:
            dict or None: The user data if found, None otherwise.
        """
        return UserModel.get_by_id(user_id)

    @staticmethod
    def get_user_by_email(email: str) -> Optional[dict]:
        """
        Get a user's complete information by their email.

        Parameters:
            email: The email address to search for.

        Returns:
            dict or None: The user data if found, None otherwise.
        """
        return UserModel.get_by_email(email)

    @staticmethod
    def get_user_by_username(username: str) -> Optional[dict]:
        """
        Get a user's complete information by their username.

        Parameters:
            username: The username to search for.

        Returns:
            dict or None: The user data if found, None otherwise.
        """
        return UserModel.get_by_username(username)

    @staticmethod
    def get_user_id_by_email(email: str) -> Optional[int]:
        """
        Get only the user ID from an email address.

        Parameters:
            email: The email address to search for.

        Returns:
            int or None: The user ID if found, None otherwise.
        """
        user = UserModel.get_by_email(email)
        return user["id"] if user else None

    @staticmethod
    def get_all_users() -> list:
        """
        Get all users (admin function).

        Returns:
            list: List of all user dictionaries.
        """
        return UserModel.get_all()

    @staticmethod
    def get_user_list_for_admin() -> list:
        """
        Get a filtered list of users for admin management.
        Excludes admin users and returns only essential fields.

        Returns:
            list: List of user dicts with userID, username, email, role, avatar, isBlocked.
        """
        return [
            {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "role": user["role"],
                "avatar": user["avatar"],
                "isBlocked": user["isBlocked"],
            }
            for user in UserModel.get_all()
            if user["role"] != "admin"
        ]

    @staticmethod
    def update_avatar(user_id: int, avatar_filename: str) -> bool:
        """
        Update a user's avatar.

        Parameters:
            user_id: The user's ID.
            avatar_filename: The new avatar filename (not full path).

        Returns:
            bool: True if updated successfully, False otherwise.
        """
        avatar_path = f"assets/images/profile_avatars/{avatar_filename}"
        return UserModel.update_avatar(user_id, avatar_path)

    @staticmethod
    def change_role(username: str, new_role: str) -> bool:
        """
        Change a user's role.

        Parameters:
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

        user = UserModel.get_by_username(username)
        if user:
            return UserModel.update_role(user["id"], new_role)
        return False

    @staticmethod
    def block_user(username: str) -> bool:
        """
        Block a user by username.

        Parameters:
            username: The username of the user to block.

        Returns:
            bool: True if blocked successfully, False otherwise.
        """
        user = UserModel.get_by_username(username)
        if not user:
            return False
        if user["isBlocked"]:
            raise ValueError(f'"{username}" is already blocked.')
        return UserModel.set_blocked(user["id"], True)

    @staticmethod
    def unblock_user(username: str) -> bool:
        """
        Unblock a user by username.

        Parameters:
            username: The username of the user to unblock.

        Returns:
            bool: True if unblocked successfully, False otherwise.
        """
        user = UserModel.get_by_username(username)
        if not user:
            return False
        if not user["isBlocked"]:
            raise ValueError(f'"{username}" is already unblocked.')
        return UserModel.set_blocked(user["id"], False)

    @staticmethod
    def is_user_blocked(user_id: int) -> bool:
        """
        Check if a user is blocked.

        Parameters:
            user_id: The user's ID.

        Returns:
            bool: True if user is blocked, False otherwise.
        """
        user = UserModel.get_by_id(user_id)
        return user["isBlocked"] if user else False

    @staticmethod
    def get_users_by_role(role: str) -> list:
        """
        Get all users with a specific role.

        Parameters:
            role: The role to filter by.

        Returns:
            list: List of user dictionaries with the specified role.
        """
        return UserModel.get_by_role(role)

    @staticmethod
    def delete_user(user_id: int) -> bool:
        """
        Delete a user from the database.

        Parameters:
            user_id: The user's ID.

        Returns:
            bool: True if deleted successfully, False otherwise.
        """
        return UserModel.delete(user_id)

    @staticmethod
    def filter_users(username: str, email: str) -> list:
        """
        Filter users by username prefix and/or email prefix (case-insensitive).
        Admin users are always excluded.

        Parameters:
            username: Username prefix to filter by (empty string to skip).
            email: Email prefix to filter by (empty string to skip).

        Returns:
            list: Filtered list of user dictionaries.
        """
        users = [u for u in UserModel.get_all() if u["role"] != "admin"]

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
        contacts = ContactModel.get_all()
        if not contacts:
            return []
        return [
            {
                "id": c["id"],
                "title": c["title"],
                "message": c["message"],
                "username": (UserModel.get_by_id(c["userId"]) or {}).get(
                    "username", "Unknown"
                ),
            }
            for c in contacts
        ]

    # ── Follow / Unfollow ────────────────────────────────────────────────────

    @staticmethod
    def follow_user(follower_id: int, followed_id: int) -> bool:
        """
        Make follower_id follow followed_id.
        Updates the followers counter on the followed user.

        Parameters:
            follower_id: The ID of the user doing the following.
            followed_id: The ID of the user being followed.

        Returns:
            bool: True if the follow was created, False if already following.
        """
        result = FollowModel.follow(follower_id, followed_id)
        if result is None:
            return False  # already following
        return True

    @staticmethod
    def unfollow_user(follower_id: int, followed_id: int) -> bool:
        """
        Make follower_id unfollow followed_id.
        Updates the followers counter on the followed user.

        Parameters:
            follower_id: The ID of the user doing the unfollowing.
            followed_id: The ID of the user being unfollowed.

        Returns:
            bool: True if the relationship was removed, False if it didn't exist.
        """
        return FollowModel.unfollow(follower_id, followed_id)

    @staticmethod
    def is_following(follower_id: int, followed_id: int) -> bool:
        """
        Check whether follower_id is currently following followed_id.

        Returns:
            bool: True if the follow relationship exists.
        """
        return FollowModel.is_following(follower_id, followed_id)

    @staticmethod
    def get_followers(user_id: int) -> list:
        """
        Return full user profiles for everyone who follows user_id.

        Returns:
            list[dict]: User dicts (from UserModel) for each follower.
        """
        follows = FollowModel.get_followers(user_id)
        result = []
        for f in follows:
            user = UserModel.get_by_id(f["followerId"])
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
        follows = FollowModel.get_following(user_id)
        result = []
        for f in follows:
            user = UserModel.get_by_id(f["followedId"])
            if user:
                result.append(user)
        return result

    @staticmethod
    def count_followers(user_id: int) -> int:
        """
        Return the number of users following user_id (live count from FollowModel).

        Returns:
            int: Follower count.
        """
        return FollowModel.count_followers(user_id)

    @staticmethod
    def count_following(user_id: int) -> int:
        """
        Return the number of users that user_id follows (live count from FollowModel).

        Returns:
            int: Following count.
        """
        return FollowModel.count_following(user_id)

    @staticmethod
    def create_contact(title: str, message: str, user_id: int) -> dict:
        """
        Create a contact message from a user to the admin.

        Parameters:
            title: Subject of the message.
            message: Body of the message.
            user_id: The ID of the user sending the message.

        Returns:
            dict: The created contact entry.
        """
        return ContactModel.create(title=title, message=message, userId=user_id)
