from typing import List, Optional, Tuple

from app.core.services.auth_service import AuthService
from app.core.services.user_service import UserService
from app.core.state.session import session
from app.utils.log_utils import log_exception, log_operation


class UserController:
    """
    Controller for user management operations.

    Coordinates between views and services for:
    - User listing and filtering
    - Role changes
    - Blocking/unblocking users
    - Profile viewing and editing
    - Session management
    - Follow/unfollow
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
    def change_user_role(username: str, new_role: str) -> Tuple[bool, str]:
        """
        Change a user's role.

        Args:
            username: The username of the user to modify.
            new_role: The new role to assign ('regular', 'unsigned', etc.)

        Returns:
            Tuple[bool, str]: (success, message)
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
            log_operation(
                "user.change_role",
                "validation_error",
                f"ValueError: {str(e)}",
                user_id=session.user_id,
            )
            return False, "Invalid role or user not found."
        except Exception as e:
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
            Tuple[bool, str]: (success, message)
        """
        if not username:
            log_operation(
                "user.block_user",
                "validation_error",
                "Username is required",
                user_id=session.user_id,
            )
            return False, "Username is required"

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
            Tuple[bool, str]: (success, message)
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
    def filter_users(
        username: str,
        email: str,
        role: str = "",
        status: str = "",
    ) -> List[dict]:
        """
        Filter users by username, email, role, and/or blocked status.

        Args:
            username: Username prefix to filter by (empty string to skip).
            email: Email prefix to filter by (empty string to skip).
            role: Role name to filter by (empty string to skip).
            status: ``"blocked"`` or ``"active"`` (empty string to skip).

        Returns:
            List[dict]: Filtered list of user dicts (admin users excluded).
        """
        try:
            log_operation(
                "user.filter_users",
                "success",
                f"Filtering by username={username!r}, email={email!r}, role={role!r}, status={status!r}",
                user_id=session.user_id,
            )
            return UserService.filter_users(username, email, role, status)
        except Exception as e:
            log_exception(
                "user.filter_users",
                e,
                user_id=session.user_id,
                context={
                    "username": username,
                    "email": email,
                    "role": role,
                    "status": status,
                },
            )
            return []

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
        if user_id is None:
            return session.user_data
        try:
            profile = UserService.get_profile(user_id)
            if profile:
                log_operation(
                    "profile.get_profile",
                    "success",
                    f"Retrieved profile for user_id={user_id}",
                )
            return profile
        except Exception as e:
            log_exception("profile.get_profile", e, context={"user_id": user_id})
            return None

    @staticmethod
    def get_profile_stats(user_id: int) -> dict:
        """
        Get profile statistics (follower count, photo count) for a user.

        Args:
            user_id: The user's ID.

        Returns:
            dict: Dictionary with 'follower_count' and 'photo_count'.
        """
        try:
            stats = UserService.get_profile_stats(user_id)
            log_operation(
                "profile.get_profile_stats",
                "success",
                f"Retrieved stats for user_id={user_id}",
            )
            return stats
        except Exception as e:
            log_exception("profile.get_profile_stats", e, context={"user_id": user_id})
            return {"follower_count": 0, "photo_count": 0}

    @staticmethod
    def update_avatar(avatar_filename: str) -> Tuple[bool, str]:
        """
        Update the current user's avatar.

        Args:
            avatar_filename: The new avatar filename.

        Returns:
            Tuple[bool, str]: (success, message)
        """
        if not avatar_filename:
            log_operation(
                "profile.update_avatar",
                "validation_error",
                "Avatar filename is required",
            )
            return False, "Please select an avatar"

        try:
            assert session.user_id is not None

            if UserService.update_avatar(session.user_id, avatar_filename):
                new_avatar_path = f"assets/images/local_cloud_media/latest/profile_avatars/{avatar_filename}"
                session.update_user_data({"avatar": new_avatar_path})
                log_operation(
                    "profile.update_avatar",
                    "success",
                    f"Avatar updated for user_id={session.user_id}",
                    user_id=session.user_id,
                )
                return True, "Avatar updated successfully"

            log_operation(
                "profile.update_avatar",
                "failed",
                f"Service returned False for user_id={session.user_id}",
                user_id=session.user_id,
            )
            return False, "Unable to update avatar. Please try again."
        except Exception as e:
            log_exception(
                "profile.update_avatar",
                e,
                user_id=session.user_id,
                context={"avatar_filename": avatar_filename},
            )
            return False, "Something went wrong. Please try again later."

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
        if not current_password or not new_password or not confirm_password:
            log_operation(
                "profile.change_password",
                "validation_error",
                "Missing password fields",
                user_id=session.user_id,
            )
            return False, "All password fields are required"

        if new_password != confirm_password:
            log_operation(
                "profile.change_password",
                "validation_error",
                "Passwords do not match",
                user_id=session.user_id,
            )
            return False, "New passwords do not match"

        password_valid, password_error = AuthService.validate_password_format(
            new_password
        )
        if not password_valid:
            error_msg = password_error or "Invalid password format"
            log_operation(
                "profile.change_password",
                "validation_error",
                f"Invalid password format: {error_msg}",
                user_id=session.user_id,
            )
            return False, error_msg

        try:
            if not session.user_id:
                log_operation(
                    "profile.change_password",
                    "validation_error",
                    "User ID is not available",
                )
                return False, "Unable to change password: User not authenticated"
            if AuthService.change_password(
                session.user_id, current_password, new_password
            ):
                log_operation(
                    "profile.change_password",
                    "success",
                    f"Password changed for user_id={session.user_id}",
                    user_id=session.user_id,
                )
                return True, "Password changed successfully"

            log_operation(
                "profile.change_password",
                "validation_error",
                "Incorrect current password",
                user_id=session.user_id,
            )
            return False, "Current password is incorrect"
        except ValueError as e:
            log_operation(
                "profile.change_password",
                "validation_error",
                f"ValueError: {str(e)}",
                user_id=session.user_id,
            )
            return False, str(e)
        except Exception as e:
            log_exception("profile.change_password", e, user_id=session.user_id)
            return False, "Something went wrong. Please try again later."

    @staticmethod
    def refresh_session_data() -> bool:
        """
        Refresh the current session with the latest user data from the database.
        Should be called after any profile update (avatar, password, etc.).

        Returns:
            bool: True if refreshed successfully.
        """
        try:
            if not session.user_id:
                log_operation(
                    "profile.refresh_session_data",
                    "validation_error",
                    "User ID is not available",
                )
                return False
            user = UserService.refresh_user_session(session.user_id)
            if user:
                session.login(user, is_new_user=session.is_new_user)
                log_operation(
                    "profile.refresh_session_data",
                    "success",
                    f"Session refreshed for user_id={session.user_id}",
                    user_id=session.user_id,
                )
                return True

            log_operation(
                "profile.refresh_session_data",
                "failed",
                f"User not found for user_id={session.user_id}",
                user_id=session.user_id,
            )
            return False
        except Exception as e:
            log_exception("profile.refresh_session_data", e, user_id=session.user_id)
            return False

    # ========== Follow Operations ==========

    @staticmethod
    def follow_user(followed_id: int) -> bool:
        """
        Follow a user. The current session user follows followed_id.

        Args:
            followed_id: The user ID to follow.
        Returns:
            bool: True if the follow was created, False if already following.
        """
        if session.user_id is None:
            return False
        return UserService.follow_user(session.user_id, followed_id)

    @staticmethod
    def unfollow_user(followed_id: int) -> bool:
        """
        Unfollow a user. The current session user unfollows followed_id.

        Args:
            followed_id: The user ID to unfollow.

        Returns:
            bool: True if the relationship was removed.
        """
        if session.user_id is None:
            return False
        return UserService.unfollow_user(session.user_id, followed_id)

    @staticmethod
    def is_following(followed_id: int) -> bool:
        """
        Check whether the current session user is following followed_id.

        Args:
            followed_id: The user ID to check.

        Returns:
            bool: True if currently following.
        """
        if session.user_id is None:
            return False
        return UserService.is_following(session.user_id, followed_id)
