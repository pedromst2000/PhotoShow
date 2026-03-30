from typing import List, Tuple

from app.core.services.auth_service import AuthService
from app.core.services.photo_service import PhotoService
from app.core.services.user_service import UserService
from app.core.state.session import session


class AdminController:
    """
    Controller for administrative operations.

    Coordinates between views and services for:
    - User management
    - Role changes
    - Blocking/unblocking users
    - User listing
    - Category management
    - Contact viewing
    """

    @staticmethod
    def is_admin() -> bool:
        """
        Check if the current user has admin privileges.

        Returns:
            bool: True if the user is an admin, False otherwise.
        """
        return session.is_admin

    @staticmethod
    def is_valid_email_format(email: str) -> bool:
        """
        Validate an email address format.

        Args:
            email: The email address to validate.

        Returns:
            bool: True if the format is valid, False otherwise.
        """
        return AuthService.validate_email_format(email)

    @staticmethod
    def get_manageable_users() -> List[dict]:
        """
        Get list of users that can be managed by admin.
        Excludes admin users.

        Returns:
            list: List of user dictionaries with essential fields.
        """
        if not session.is_admin:
            return []
        return UserService.get_user_list_for_admin()

    @staticmethod
    def get_all_users() -> List[dict]:
        """
        Get all users in the system.

        Returns:
            list: List of all user dictionaries.
        """
        if not session.is_admin:
            return []
        return UserService.get_all_users()

    @staticmethod
    def change_user_role(username: str, new_role: str) -> Tuple[bool, str]:
        """
        Change a user's role.

        Args:
            username: The username of the user to modify.
            new_role: The new role to assign ('regular', 'unsigned', etc.)

        Returns:
            Tuple of (success, message)
        """
        if not session.is_admin:
            return False, "Admin privileges required"

        if not username or not new_role:
            return False, "Username and role are required"

        try:
            if UserService.change_role(username, new_role):
                return True, f"User {username} role changed to {new_role}"
            return False, f"Failed to change role for {username}"
        except ValueError as e:
            return False, str(e)

    @staticmethod
    def block_user(username: str) -> Tuple[bool, str]:
        """
        Block a user by username.

        Args:
            username: The username of the user to block.

        Returns:
            Tuple of (success, message)
        """
        if not session.is_admin:
            return False, "Admin privileges required"

        if not username:
            return False, "Username is required"

        # Prevent admin from blocking themselves
        if username == session.username:
            return False, "You cannot block yourself"

        try:
            if UserService.block_user(username):
                return True, f"User {username} has been blocked"
            return False, f"Failed to block user {username}"
        except ValueError as e:
            return False, str(e)

    @staticmethod
    def unblock_user(username: str) -> Tuple[bool, str]:
        """
        Unblock a user by username.

        Args:
            username: The username of the user to unblock.

        Returns:
            Tuple of (success, message)
        """
        if not session.is_admin:
            return False, "Admin privileges required"

        if not username:
            return False, "Username is required"

        try:
            if UserService.unblock_user(username):
                return True, f"User {username} has been unblocked"
            return False, f"Failed to unblock user {username}"
        except ValueError as e:
            return False, str(e)

    @staticmethod
    def delete_user(user_id: int) -> Tuple[bool, str]:
        """
        Delete a user from the system.

        Args:
            user_id: The ID of the user to delete.

        Returns:
            Tuple of (success, message)
        """
        if not session.is_admin:
            return False, "Admin privileges required"

        # Prevent admin from deleting themselves
        if user_id == session.user_id:
            return False, "You cannot delete yourself"

        if UserService.delete_user(user_id):
            return True, "User has been deleted"

        return False, "Failed to delete user"

    @staticmethod
    def get_users_by_role(role: str) -> List[dict]:
        """
        Get all users with a specific role.

        Args:
            role: The role to filter by.

        Returns:
            list: List of user dictionaries with the specified role.
        """
        if not session.is_admin:
            return []
        return UserService.get_users_by_role(role)

    @staticmethod
    def filter_users(username: str, email: str) -> List[dict]:
        """
        Filter users by username and/or email prefix (admin only).

        Args:
            username: Username prefix to filter by (empty string to skip).
            email: Email prefix to filter by (empty string to skip).

        Returns:
            list: Filtered list of user dicts (admin users excluded).
        """
        if not session.is_admin:
            return []
        return UserService.filter_users(username, email)

    @staticmethod
    def get_categories() -> List[str]:
        """
        Get all category names.

        Returns:
            list: List of category name strings.
        """
        return PhotoService.get_category_names()

    @staticmethod
    def add_category(category_name: str) -> Tuple[bool, str]:
        """
        Add a new category (admin only).

        Args:
            category_name: The name of the category to add.

        Returns:
            Tuple of (success, message)
        """
        if not session.is_admin:
            return False, "Admin privileges required"
        if not category_name or not category_name.strip():
            return False, "Category name is required"
        if PhotoService.category_exists(category_name.strip()):
            return False, "The category already exists, please try again!"
        PhotoService.create_category(category_name.strip())
        return True, "The category was added successfully!"

    @staticmethod
    def delete_category(category_name: str) -> Tuple[bool, str]:
        """
        Delete a category and cascade-delete its photos (admin only).

        Args:
            category_name: The name of the category to delete.

        Returns:
            Tuple of (success, message)
        """
        if not session.is_admin:
            return False, "Admin privileges required"
        return PhotoService.delete_category_with_photos(category_name)

    @staticmethod
    def get_contacts() -> List[dict]:
        """
        Get all contacts with associated usernames (admin only).

        Returns:
            list: List of dicts with contactID, title, message, username.
        """
        if not session.is_admin:
            return []
        return UserService.get_contacts_with_usernames()
