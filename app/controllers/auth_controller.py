from typing import Optional, Tuple

from app.core.services.auth_service import AuthService
from app.core.state.session import session
from app.utils.file_utils import resolve_avatar_path


class AuthController:
    """
    Controller for authentication operations.

    Coordinates between views and services for:
    - User login
    - User registration
    - User logout
    - Input validation
    """

    @staticmethod
    def login(email: str, password: str) -> Tuple[bool, str, Optional[dict]]:
        """
        Process user login request.

        Args:
            email: The user's email address.
            password: The user's password.

        Returns:
            Tuple of (success, message, user_data):
            - success (bool): Whether login was successful
            - message (str): Status message for display
            - user_data (dict|None): User data if successful
        """
        # Validate inputs
        if not email or not password:
            return False, "Email and password are required", None

        if not AuthService.validate_email_format(email):
            return False, "Invalid email format", None

        # Attempt authentication
        user = AuthService.authenticate(email, password)

        if user is None:
            return False, "Invalid credentials", None

        # Normalize avatar path so presentation code can open it reliably
        user["avatar"] = resolve_avatar_path(user.get("avatar"))

        # Check if user is blocked
        if user.get("isBlocked", False):
            # Still login but flag as blocked
            session.login(user, is_new_user=False)
            return True, f"Welcome back {user['username']} (Account restricted)", user

        # Successful login - update session
        session.login(user, is_new_user=False)
        return True, f"Welcome back {user['username']}", user

    @staticmethod
    def get_post_login_destination() -> str:
        """
        Helper to determine the view destination after a successful login.

        Returns:
            str: 'home_banned' when the user is blocked, otherwise 'home'.

        This keeps the routing decision in the controller layer while leaving
        the actual view navigation to the presentation layer, avoiding
        circular imports.
        """
        return "home_banned" if AuthController.is_current_user_blocked() else "home"

    @staticmethod
    def register(
        username: str, email: str, password: str
    ) -> Tuple[bool, str, Optional[dict]]:
        """
        Process user registration request.

        Args:
            username: The desired username.
            email: The user's email address.
            password: The user's password.

        Returns:
            Tuple of (success, message, user_data):
            - success (bool): Whether registration was successful
            - message (str): Status message for display
            - user_data (dict|None): New user data if successful
        """
        # Validate inputs
        if not username or not email or not password:
            return False, "All fields are required", None

        if not AuthService.validate_username_format(username):
            return (
                False,
                "Invalid username format. Use only letters, numbers, underscore, dot, or hyphen",
                None,
            )

        if not AuthService.validate_email_format(email):
            return False, "Invalid email format", None

        # Check availability
        if not AuthService.is_username_available(username):
            return False, "Username is already taken", None

        if not AuthService.is_email_available(email):
            return False, "Email is already registered", None

        # Register user
        try:
            user = AuthService.register_user(username, email, password)
            # Normalize avatar path so presentation code can open it reliably
            user["avatar"] = resolve_avatar_path(user.get("avatar"))
            # Auto-login after registration
            session.login(user, is_new_user=True)
            return True, f"Welcome {username}! Your account has been created.", user
        except Exception as e:
            return False, f"Registration failed: {str(e)}", None

    @staticmethod
    def logout() -> Tuple[bool, str]:
        """
        Process user logout request.

        Returns:
            Tuple of (success, message)
        """
        session.logout()
        return True, "You have been logged out"

    @staticmethod
    def is_authenticated() -> bool:
        """Check if a user is currently logged in.

        Returns:
            bool: True if a user is authenticated, False otherwise.
        """
        return session.is_authenticated

    @staticmethod
    def get_current_user() -> Optional[dict]:
        """Get the currently logged-in user's data.

        Returns:
            dict or None: The current user's data if logged in, None otherwise.
        """
        return session.user_data

    @staticmethod
    def is_current_user_blocked() -> bool:
        """Check if the current user is blocked.

        Returns:
            bool: True if the current user is blocked, False otherwise.
        """
        return session.is_blocked

    @staticmethod
    def is_current_user_new() -> bool:
        """Check if the current user is newly registered.

        Returns:
            bool: True if the current user is newly registered, False otherwise.
        """
        return session.is_new_user
