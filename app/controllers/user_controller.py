from typing import List, Optional, Tuple

from app.controllers.helpers.admin_helpers import AdminHelpers
from app.controllers.helpers.profile_helpers import ProfileHelpers
from app.core.services.user_service import UserService


class UserController:
    """
    Controller for user management operations.

    Coordinates between views and services for:
    - User listing and filtering
    - Role changes
    - Blocking/unblocking users
    - Contact management
    """

    @staticmethod
    def get_manageable_users() -> List[dict]:
        """
        Get list of users that can be managed by admin.
        Excludes admin users.

        Returns:
            List[dict]: List of user dictionaries with essential fields.
        """
        return UserService.get_user_list_for_admin()

    @staticmethod
    def get_all_users() -> List[dict]:
        """
        Get all users in the system.

        Returns:
            List[dict]: List of all user dictionaries.
        """
        return UserService.get_all_users()

    @staticmethod
    def change_user_role(username: str, new_role: str) -> Tuple[bool, str]:
        """
        Change a user's role.

        Args:
            username: The username of the user to modify.
            new_role: The new role to assign ('regular', 'unsigned', etc.)

        Returns:
            Tuple[bool, str]: (success, message)
        """
        return AdminHelpers.change_user_role(username, new_role)

    @staticmethod
    def block_user(username: str) -> Tuple[bool, str]:
        """
        Block a user by username.

        Args:
            username: The username of the user to block.

        Returns:
            Tuple[bool, str]: (success, message)
        """
        return AdminHelpers.block_user(username)

    @staticmethod
    def unblock_user(username: str) -> Tuple[bool, str]:
        """
        Unblock a user by username.

        Args:
            username: The username of the user to unblock.

        Returns:
            Tuple[bool, str]: (success, message)
        """
        return AdminHelpers.unblock_user(username)

    @staticmethod
    def get_users_by_role(role: str) -> List[dict]:
        """
        Get all users with a specific role.

        Args:
            role: The role to filter by.

        Returns:
            List[dict]: List of user dictionaries with the specified role.
        """
        return UserService.get_users_by_role(role)

    @staticmethod
    def filter_users(username: str, email: str) -> List[dict]:
        """
        Filter users by username and/or email prefix.

        Args:
            username: Username prefix to filter by (empty string to skip).
            email: Email prefix to filter by (empty string to skip).

        Returns:
            List[dict]: Filtered list of user dicts (admin users excluded).
        """
        return AdminHelpers.filter_users(username, email)

    @staticmethod
    def get_contacts() -> List[dict]:
        """
        Get all contacts with associated usernames.

        Returns:
            List[dict]: List of dicts with contactID, title, message, username.
        """
        return UserService.get_contacts_with_usernames()

    # ========== Profile Operations ==========

    @staticmethod
    def get_profile(user_id: Optional[int] = None) -> Optional[dict]:
        """
        Get a user's profile information.

        Args:
            user_id: The user's ID. If None, returns the current user's profile from session.

        Returns:
            Optional[dict]: The user's profile data.
        """
        return ProfileHelpers.get_profile(user_id)

    @staticmethod
    def get_profile_stats(user_id: int) -> dict:
        """
        Get profile statistics (follower count, photo count) for a user.

        Args:
            user_id: The user's ID.

        Returns:
            dict: Dictionary with 'follower_count' and 'photo_count'.
        """
        return ProfileHelpers.get_profile_stats(user_id)

    @staticmethod
    def update_avatar(avatar_filename: str) -> Tuple[bool, str]:
        """
        Update the current user's avatar.

        Args:
            avatar_filename: The new avatar filename.

        Returns:
            Tuple[bool, str]: (success, message)
        """
        return ProfileHelpers.update_avatar(avatar_filename)

    @staticmethod
    def change_password(
        current_password: str, new_password: str, confirm_password: str
    ) -> Tuple[bool, str]:
        """
        Change the current user's password.

        Args:
            current_password: The user's current password.
            new_password: The desired new password.
            confirm_password: Confirmation of the new password.

        Returns:
            Tuple[bool, str]: (success, message)
        """
        return ProfileHelpers.change_password(
            current_password, new_password, confirm_password
        )

    @staticmethod
    def refresh_session_data() -> bool:
        """
        Refresh the current session with the latest user data from the database.
        Should be called after any profile update (avatar, password, etc.).

        Returns:
            bool: True if refreshed successfully.
        """
        return ProfileHelpers.refresh_session_data()

    @staticmethod
    def contact_admin(
        title: str, message: str, user_id: Optional[int] = None
    ) -> Tuple[bool, str]:
        """
        Send a contact message to the admin (used by blocked users).
        Controller handles input validation and user-facing error messages.

        Args:
            title: Subject/title of the message.
            message: Body of the message.
            user_id: Optional user ID; falls back to session if not provided.

        Returns:
            Tuple[bool, str]: (success, message) tuple.
        """
        return ProfileHelpers.contact_admin(title, message, user_id)
