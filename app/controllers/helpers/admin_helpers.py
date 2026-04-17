from typing import List, Tuple

from app.core.services.user_service import UserService
from app.core.state.session import session
from app.utils.log_utils import log_exception, log_operation


class AdminHelpers:
    """Helpers for admin user management operations."""

    @staticmethod
    def change_user_role(username: str, new_role: str) -> Tuple[bool, str]:
        """
        Change a user's role.

        Args:
            username: The username of the user to modify.
            new_role: The new role to assign ('regular', 'unsigned', etc.)

        Returns:
            Tuple of (success, message)

        Raises:
            ValueError: If the role is invalid or user is not found.
            Exception: Any other unexpected error during role change is caught and logged.
        """
        if not username or not new_role:
            log_operation(
                "user.change_role", "validation_error", "Missing username or role"
            )
            return False, "Username and role are required"

        try:
            if UserService.change_role(username, new_role):
                log_operation(
                    "user.change_role",
                    "success",
                    f"Changed {username} role to {new_role}",
                    user_id=session.user_id,
                )
                return True, f"User {username} role changed to {new_role}"
            log_operation(
                "user.change_role",
                "failed",
                f"Service returned False for {username}",
                user_id=session.user_id,
            )
            return False, "Unable to change user role. Please try again."
        except ValueError as e:
            # Validation error from service - log with context
            log_operation(
                "user.change_role",
                "validation_error",
                f"ValueError: {str(e)}",
                user_id=session.user_id,
            )
            return False, "Invalid role or user not found."
        except Exception as e:
            # Unexpected error - log full details, show generic message
            log_exception(
                "user.change_role",
                e,
                user_id=session.user_id,
                context={"username": username, "new_role": new_role},
            )
            return False, "Something went wrong. Please try again later."

    @staticmethod
    def block_user(username: str) -> Tuple[bool, str]:
        """
        Block a user by username.

        Args:
            username: The username of the user to block.

        Returns:
            Tuple of (success, message)

        Raises:
            ValueError: If the user is not found.
            Exception: Any other unexpected error during block operation is caught and logged.
        """
        if not username:
            log_operation(
                "user.block_user",
                "validation_error",
                "Username is required",
                user_id=session.user_id,
            )
            return False, "Username is required"

        # Prevent admin from blocking themselves
        if username == session.username:
            log_operation(
                "user.block_user",
                "validation_error",
                "Admin attempted to block themselves",
                user_id=session.user_id,
            )
            return False, "You cannot block yourself"

        try:
            if UserService.block_user(username):
                log_operation(
                    "user.block_user",
                    "success",
                    f"Blocked user {username}",
                    user_id=session.user_id,
                )
                return True, f"User {username} has been blocked"
            log_operation(
                "user.block_user",
                "failed",
                f"Service returned False for {username}",
                user_id=session.user_id,
            )
            return False, "Unable to block user. Please try again."
        except ValueError as e:
            log_operation(
                "user.block_user",
                "validation_error",
                f"ValueError: {str(e)}",
                user_id=session.user_id,
            )
            return False, "User not found."
        except Exception as e:
            log_exception(
                "user.block_user",
                e,
                user_id=session.user_id,
                context={"username": username},
            )
            return False, "Something went wrong. Please try again later."

    @staticmethod
    def unblock_user(username: str) -> Tuple[bool, str]:
        """
        Unblock a user by username.

        Args:
            username: The username of the user to unblock.

        Returns:
            Tuple of (success, message)

        Raises:
            ValueError: If the user is not found.
            Exception: Any other unexpected error during unblock operation is caught and logged.
        """
        if not username:
            log_operation(
                "user.unblock_user",
                "validation_error",
                "Username is required",
                user_id=session.user_id,
            )
            return False, "Username is required"

        try:
            if UserService.unblock_user(username):
                log_operation(
                    "user.unblock_user",
                    "success",
                    f"Unblocked user {username}",
                    user_id=session.user_id,
                )
                return True, f"User {username} has been unblocked"
            log_operation(
                "user.unblock_user",
                "failed",
                f"Service returned False for {username}",
                user_id=session.user_id,
            )
            return False, "Unable to unblock user. Please try again."
        except ValueError as e:
            log_operation(
                "user.unblock_user",
                "validation_error",
                f"ValueError: {str(e)}",
                user_id=session.user_id,
            )
            return False, "User not found."
        except Exception as e:
            log_exception(
                "user.unblock_user",
                e,
                user_id=session.user_id,
                context={"username": username},
            )
            return False, "Something went wrong. Please try again later."

    @staticmethod
    def filter_users(username: str, email: str) -> List[dict]:
        """
        Filter users by username and/or email prefix.

        Args:
            username: Username prefix to filter by (empty string to skip).
            email: Email prefix to filter by (empty string to skip).

        Returns:
            list: Filtered list of user dicts (admin users excluded).

        Raises:
            Exception: Any unexpected error during filtering is caught and logged; empty list returned.
        """
        try:
            log_operation(
                "user.filter_users",
                "success",
                f"Filtering by username={username}, email={email}",
                user_id=session.user_id,
            )
            return UserService.filter_users(username, email)
        except Exception as e:
            log_exception(
                "user.filter_users",
                e,
                user_id=session.user_id,
                context={"username": username, "email": email},
            )
            return []  # Return empty list on error instead of propagating
