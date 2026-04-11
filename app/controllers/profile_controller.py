from typing import Optional, Tuple

from app.core.db.engine import SessionLocal
from app.core.db.models.user import UserModel
from app.core.services.auth_service import AuthService
from app.core.services.user_service import UserService
from app.core.state.session import session
from app.utils.log_utils import log_issue


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
    def get_profile(user_id: Optional[int] = None) -> Optional[dict]:
        """
        Get a user's profile information.

        Args:
            user_id: The user's ID. If None, returns the current user's profile from session.

        Returns:
            dict or None: The user's profile data.
        """
        if user_id is None:
            return session.user_data
        with SessionLocal() as db:
            return UserModel.get_by_id(db, user_id)

    @staticmethod
    def get_profile_stats(user_id: int) -> dict:
        """
        Get profile statistics (follower count, photo count) for a user.

        Args:
            user_id: The user's ID.

        Returns:
            dict with 'follower_count' and 'photo_count'.
        """
        return UserService.get_profile_stats(user_id)

    @staticmethod
    def update_avatar(avatar_filename: str) -> Tuple[bool, str]:
        """
        Update the current user's avatar.

        Args:
            avatar_filename: The new avatar filename.

        Returns:
            Tuple of (success, message)
        """
        assert session.user_id is not None

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
        assert session.user_id is not None

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
        assert session.user_id is not None
        with SessionLocal() as db:
            user = UserModel.get_by_id(db, session.user_id)
        if user:
            session.login(user, is_new_user=session.is_new_user)
            return True
        return False

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
        # Resolve user ID from session if not provided
        if user_id is None:
            user_id = session.user_id
        if user_id is None:
            return False, "Unable to identify user"

        # Delegate to UserService for business logic and database interaction
        title_clean = title.strip() if title else ""
        message_clean = message.strip() if message else ""

        # Check required fields
        if not title_clean and not message_clean:
            return False, "Title and message are required"
        if not title_clean:
            return False, "Title is required"
        if not message_clean:
            return False, "Message is required"

        # Validate title format using the service layer
        if not UserService.validate_contact_title_format(title_clean):
            return (
                False,
                "Title must contain only letters (A-Z, a-z) with no spaces or special characters",
            )

        # Check length limits (UI prevents this but we validate for safety)
        if len(title_clean) > 75:
            return False, "Title too long (max 75 characters)"
        if len(message_clean) > 255:
            return False, "Message too long (max 255 characters)"

        try:
            UserService.create_contact(
                title=title_clean, message=message_clean, userId=user_id
            )
            return True, "Your message has been sent to the admin"
        except ValueError:
            return False, "A message with this title already exists"
        except Exception as e:
            # Log the real error for diagnostics; never expose internal details to the user.
            # from app.utils.log_utils import log_issue # import here to avoid circular import
            log_issue("ProfileController.contact_admin failed", exc=e)
            return False, "Something went wrong. Please try again later."
