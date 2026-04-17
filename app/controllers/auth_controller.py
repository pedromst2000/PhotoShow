from typing import Optional, Tuple

from app.core.services.auth_service import AuthService
from app.core.state.session import session
from app.utils.file_utils import resolve_avatar_path
from app.utils.log_utils import log_exception, log_operation


class AuthController:
    """
    Controller for authentication operations.

    Coordinates between views and services for:
    - User login
    - User registration
    - User logout
    - Input validation
    """

    # Validate inputs
    # NOTE: All failure returns provide `None` as the third tuple element
    # (`user_data`) so callers can always unpack three values safely.

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

        Raises:
            Exception: Any unexpected error during authentication is caught and logged.
        """
        # Validate inputs
        if not email or not password:
            log_operation("auth.login", "validation_error", "Missing email or password")
            return False, "Email and password are required", None

        if not AuthService.validate_email_format(email):
            log_operation(
                "auth.login", "validation_error", f"Invalid email format: {email}"
            )
            return False, "Invalid email format", None

        # Attempt authentication
        try:
            user = AuthService.authenticate(email, password)

            if user is None:
                # Return a consistent 3-tuple: (success, message, user_data).
                # `user_data` is `None` on failures to avoid leaking which part failed.
                log_operation("auth.login", "validation_error", "Invalid credentials")
                return False, "Invalid credentials", None

            # Normalize avatar path so presentation code can open it reliably
            user["avatar"] = resolve_avatar_path(user.get("avatar"))

            # Check if user is blocked
            if user.get("isBlocked", False):
                # Still login but flag as blocked
                session.login(user, is_new_user=False)
                log_operation(
                    "auth.login",
                    "success",
                    "User logged in (account restricted)",
                    user_id=user["id"],
                )
                return (
                    True,
                    f"Welcome back {user['username']} (Account restricted)",
                    user,
                )

            # Successful login - update session
            session.login(user, is_new_user=False)
            log_operation("auth.login", "success", "User logged in", user_id=user["id"])
            return True, f"Welcome back {user['username']}", user
        except Exception as e:
            log_exception("auth.login", e, context={"email": email})
            return False, "Something went wrong. Please try again later.", None

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
            Tuple[bool, str, Optional[dict]]: Tuple of (success, message, user_data)
            - success (bool): Whether registration was successful
            - message (str): Status message for display
            - user_data (Optional[dict]): New user data if successful

        Raises:
            Exception: Any unexpected error during registration is caught and logged.
        """

        if not username or not email or not password:
            log_operation(
                "auth.register", "validation_error", "Missing required fields"
            )
            return False, "All fields are required", None

        if not AuthService.validate_username_format(username):
            log_operation(
                "auth.register",
                "validation_error",
                f"Invalid username format: {username}",
            )
            return (
                False,
                "Invalid username. Use only letters (A-Z, a-z), digits (0-9), underscore (_), dot (.), and hyphen (-). No spaces or other characters. Username must include at least one letter.",
                None,
            )

        if not AuthService.validate_email_format(email):
            log_operation(
                "auth.register", "validation_error", f"Invalid email format: {email}"
            )
            return False, "Invalid email format", None

        # Validate password format with strong security rules
        password_valid, password_error = AuthService.validate_password_format(password)
        if not password_valid:
            log_operation(
                "auth.register", "validation_error", "Invalid password format"
            )
            return False, (password_error or "Invalid password"), None

        # Check availability
        if not AuthService.is_username_available(username):
            log_operation(
                "auth.register",
                "validation_error",
                f"Username already taken: {username}",
            )
            return False, "Username is already taken", None

        if not AuthService.is_email_available(email):
            log_operation(
                "auth.register",
                "validation_error",
                f"Email already registered: {email}",
            )
            return False, "Email is already registered", None

        if not AuthService.is_password_available(password):
            log_operation("auth.register", "validation_error", "Password is too common")
            return (
                False,
                "Password is too common. Please choose a stronger password.",
                None,
            )

        # Register user
        try:
            user = AuthService.register_user(username, email, password)
            # Normalize avatar path so presentation code can open it reliably
            user["avatar"] = resolve_avatar_path(user.get("avatar"))
            # Auto-login after registration
            session.login(user, is_new_user=True)
            log_operation(
                "auth.register",
                "success",
                "User registered and logged in",
                user_id=user["id"],
            )
            return True, f"Welcome {username}! Your account has been created.", user
        except Exception as e:
            log_exception(
                "auth.register", e, context={"username": username, "email": email}
            )
            return (
                False,
                "Registration failed: Something went wrong! Try again later.",
                None,
            )
            # return False, f"Registration failed: {str(e)}", None # Uncomment for detailed error messages during development!

    @staticmethod
    def logout() -> Tuple[bool, str]:
        """
        Process user logout request.

        Returns:
            Tuple[bool, str]: Tuple of (success, message)
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
