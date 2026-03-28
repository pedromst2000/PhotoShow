from typing import Optional, Tuple

from services.auth_service import AuthService
from services.photo_service import PhotoService
from services.user_service import UserService
from state.session import session


class ProfileController:
    """
    Controller for profile operations.

    Coordinates between views and services for:
    - Viewing user profile
    - Updating avatar
    - Changing password
    - Refreshing session data after updates
    """

    @staticmethod
    def get_profile(user_id: int = None) -> Optional[dict]:
        """
        Get a user's profile information.

        Args:
            user_id: The user's ID. If None, returns the current user's profile from session.

        Returns:
            dict or None: The user's profile data.
        """
        if user_id is None:
            return session.user_data
        return UserService.get_user_by_id(user_id)

    @staticmethod
    def get_profile_stats(user_id: int) -> dict:
        """
        Get profile statistics (follower count, photo count) for a user.

        Args:
            user_id: The user's ID.

        Returns:
            dict with 'follower_count' and 'photo_count'.
        """
        return {
            "follower_count": UserService.count_followers(user_id),
            "photo_count": PhotoService.count_photos_by_user(user_id),
        }

    @staticmethod
    def update_avatar(avatar_filename: str) -> Tuple[bool, str]:
        """
        Update the current user's avatar.

        Args:
            avatar_filename: The new avatar filename.

        Returns:
            Tuple of (success, message)
        """
        if not session.is_authenticated:
            return False, "You must be logged in to change your avatar"

        if not avatar_filename:
            return False, "Please select an avatar"

        if UserService.update_avatar(session.user_id, avatar_filename):
            new_avatar_path = f"assets/images/profile_avatars/{avatar_filename}"
            session.update_user_data({"avatar": new_avatar_path})
            return True, "Avatar updated successfully"

        return False, "Failed to update avatar"

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
            Tuple of (success, message)
        """
        if not session.is_authenticated:
            return False, "You must be logged in to change your password"

        if not current_password or not new_password or not confirm_password:
            return False, "All password fields are required"

        if new_password != confirm_password:
            return False, "New passwords do not match"

        # Delegate verification and password change to AuthService (business logic)
        try:
            if AuthService.change_password(
                session.user_id, current_password, new_password
            ):
                return True, "Password changed successfully"
            return False, "Current password is incorrect"
        except ValueError as e:
            return False, str(e)

    @staticmethod
    def refresh_session_data() -> bool:
        """
        Refresh the current session with the latest user data from the database.
        Should be called after any profile update (avatar, password, etc.).

        Returns:
            bool: True if refreshed successfully.
        """
        if not session.is_authenticated:
            return False

        user = UserService.get_user_by_id(session.user_id)
        if user:
            session.login(user, is_new_user=session.is_new_user)
            return True
        return False

    @staticmethod
    def contact_admin(title: str, message: str) -> Tuple[bool, str]:
        """
        Send a contact message to the admin (used by blocked users).

        Args:
            title: Subject/title of the message.
            message: Body of the message.

        Returns:
            Tuple of (success, message)
        """
        if not session.is_authenticated:
            return False, "You must be logged in to contact the admin"
        if not title or not title.strip():
            return False, "Title is required"
        if not message or not message.strip():
            return False, "Message is required"
        try:
            UserService.create_contact(
                title=title.strip(), message=message.strip(), user_id=session.user_id
            )
            return True, "Your message has been sent to the admin"
        except ValueError as e:
            return False, str(e)
