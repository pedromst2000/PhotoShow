"""
User session state management.

This module provides a singleton session object that maintains
the current user's authentication state across the application.
"""

from typing import Optional


class UserSession:
    """
    Singleton class to manage user authentication state.

    Maintains the current user's session data including:
    - Authentication status
    - User profile information
    - Session flags (is_new_user, etc.)

    Attributes:
        _instance: Class-level singleton instance
        _user_data: Dictionary containing current user's data
        _is_authenticated: Boolean flag for login status
        _is_new_user: Boolean flag for newly registered users
    """

    _instance: Optional["UserSession"] = None

    def __new__(cls) -> "UserSession":
        """Ensure only one instance exists (Singleton pattern)."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        """Initialize session with default values."""
        self._user_data: Optional[dict] = None
        self._is_authenticated: bool = False
        self._is_new_user: bool = False

    def login(self, user_data: dict, is_new_user: bool = False) -> None:
        """
        Authenticate user and store session data.

        Parameters:
            user_data: Dictionary containing user information from database.
            is_new_user: Whether this is a newly registered user.
        Returns:
            None
        """
        self._user_data = user_data.copy()
        self._is_authenticated = True
        self._is_new_user = is_new_user

    def logout(self) -> None:
        """Clear session data and reset authentication state.

        Returns:
            None
        """
        self._user_data = None
        self._is_authenticated = False
        self._is_new_user = False

    def update_user_data(self, updates: dict) -> None:
        """
        Update specific fields in the current user's session data.

        Parameters:
            updates: Dictionary of fields to update.
        Returns:
            None
        """
        if self._user_data:
            self._user_data.update(updates)

    @property
    def is_authenticated(self) -> bool:
        """Check if a user is currently logged in.

        Returns:
            bool: True if authenticated, False otherwise.

        """
        return self._is_authenticated

    @property
    def is_new_user(self) -> bool:
        """Check if the current user is newly registered.

        Returns:
            bool: True if newly registered, False otherwise.
        """
        return self._is_new_user

    @property
    def user_data(self) -> Optional[dict]:
        """Get the current user's full data dictionary.

        Returns:
            dict or None: The user's data if logged in, None otherwise.
        """
        return self._user_data.copy() if self._user_data else None

    @property
    def user_id(self) -> Optional[int]:
        """Get the current user's ID.

        Returns:
            int or None: The user's ID if logged in, None otherwise.
        """
        return self._user_data.get("id") if self._user_data else None

    @property
    def username(self) -> Optional[str]:
        """Get the current user's username.

        Returns:
            str or None: The user's username if logged in, None otherwise.
        """
        return self._user_data.get("username") if self._user_data else None

    @property
    def email(self) -> Optional[str]:
        """Get the current user's email.

        Returns:
            str or None: The user's email if logged in, None otherwise.
        """
        return self._user_data.get("email") if self._user_data else None

    @property
    def avatar(self) -> Optional[str]:
        """Get the current user's avatar path.

        Returns:
            str or None: The user's avatar path if logged in, None otherwise.
        """
        return self._user_data.get("avatar") if self._user_data else None

    @property
    def role(self) -> Optional[str]:
        """Get the current user's role.

        Returns:
            str or None: The user's role if logged in, None otherwise.
        """
        return self._user_data.get("role") if self._user_data else None

    @property
    def is_blocked(self) -> bool:
        """Check if the current user is blocked.

        Returns:
            bool: True if the user is blocked, False otherwise.
        """
        return self._user_data.get("isBlocked", False) if self._user_data else False

    @property
    def is_admin(self) -> bool:
        """Check if the current user has admin role.

        Returns:
            bool: True if the user is an admin, False otherwise.
        """
        return self.role == "admin" if self._user_data else False


# Global singleton instance - import this to use session management
session: UserSession = UserSession()
