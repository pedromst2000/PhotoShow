from typing import Optional, Tuple

from app.core.services.auth_service import AuthService
from app.core.services.user_service import UserService
from app.core.state.session import session
from app.utils.log_utils import log_exception, log_operation


class ProfileHelpers:
    """Helpers for profile operations."""

    @staticmethod
    def get_profile(user_id: Optional[int] = None) -> Optional[dict]:
        """
        Get a user's profile information.

        Args:
            user_id: The user's ID. If None, returns the current user's profile from session.

        Returns:
            Optional[dict]: The user's profile data.

        Raises:
            Exception: Any unexpected error during profile retrieval is caught and logged; None returned.
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

        Raises:
            Exception: Any unexpected error during stats retrieval is caught and logged; defaults returned.
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

        Raises:
            Exception: Any unexpected error during avatar update is caught and logged.
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

        Raises:
            ValueError: If the new password format is invalid.
            Exception: Any other unexpected error during password change is caught and logged.
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

        # Validate password format using AuthService (no redundancy)
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

        Raises:
            Exception: Any unexpected error during session refresh is caught and logged; False returned.
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
