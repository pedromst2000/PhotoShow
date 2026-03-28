import re as regex
from typing import Optional

import bcrypt

from db.models import UserModel


class AuthService:
    """
    Service class for authentication business logic.

    Handles user authentication, registration, and credential validation.
    All password hashing/verification is done here.
    """

    @staticmethod
    def authenticate(email: str, password: str) -> Optional[dict]:
        """
        Authenticate a user by email and password.

        Args:
            email: The user's email address.
            password: The user's plaintext password.

        Returns:
            dict: The user data if authentication is successful, None otherwise.
        """
        user = UserModel.get_by_email(email)
        if user is None:
            return None

        # Verify password using bcrypt
        if bcrypt.checkpw(password.encode("utf-8"), user["password"].encode("utf-8")):
            return user
        return None

    @staticmethod
    def register_user(username: str, email: str, password: str) -> dict:
        """
        Register a new user with hashed password.

        Args:
            username: The username for the new user.
            email: The email address for the new user.
            password: The plaintext password to be hashed.

        Returns:
            dict: The newly created user data.

        Raises:
            ValueError: If username or email already exists.
        """
        # Hash the password
        hashed_password: str = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

        from db.models import RoleModel

        unsigned_role = RoleModel.get_by_name("unsigned")
        # Create user in database (avatar is stored in avatars table)
        user = UserModel.create(
            username=username,
            email=email,
            password=hashed_password,
            roleId=unsigned_role["id"] if unsigned_role else None,
            isBlocked=False,
        )
        return user

    @staticmethod
    def validate_email_format(email: str) -> bool:
        """
        Validate email format using regex.

        Regex explanation:
            [^@]+   - one or more characters except '@'
            @       - the '@' symbol
            [^@]+   - one or more characters except '@'
            \\.      - a literal dot '.'
            [^@]+   - one or more characters except '@'

        Args:
            email: The email address to validate.

        Returns:
            bool: True if the email format is valid, False otherwise.
        """
        if not regex.match(r"[^@]+@[^@]+\.[^@]+", email):
            return False
        return True

    @staticmethod
    def validate_username_format(username: str) -> bool:
        """
        Validate username format using regex.

        Rules:
            - Only letters, digits, underscore, dot, hyphen allowed
            - Cannot be only digits

        Args:
            username: The username to validate.

        Returns:
            bool: True if the username format is valid, False otherwise.
        """
        if not regex.match(r"^[a-zA-Z0-9_.-]+$", username):
            return False
        if regex.match(r"^[0-9]+$", username):
            return False
        return True

    @staticmethod
    def is_email_available(email: str) -> bool:
        """
        Check if an email address is available for registration.

        Args:
            email: The email address to check.

        Returns:
            bool: True if email is available, False if already taken.
        """
        return not UserModel.email_exists(email)

    @staticmethod
    def is_username_available(username: str) -> bool:
        """
        Check if a username is available for registration (case-insensitive).

        Args:
            username: The username to check.

        Returns:
            bool: True if username is available, False if already taken.
        """
        return not UserModel.username_exists(username)

    @staticmethod
    def change_password(user_id: int, current_password: str, new_password: str) -> bool:
        """
        Change a user's password after verifying the current password.

        Args:
            user_id: The ID of the user.
            current_password: The user's current plaintext password to verify.
            new_password: The new plaintext password to be hashed.

        Returns:
            bool: True if password was changed successfully, False otherwise.

        Raises:
            ValueError: If new_password does not meet policy requirements.
        """
        # business-rule: password policy
        if len(new_password) < 6:
            raise ValueError("Password must be at least 6 characters")

        # verify current password
        if not AuthService.verify_password(user_id, current_password):
            return False

        hashed: str = bcrypt.hashpw(
            new_password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")
        return UserModel.update_password(user_id, hashed)

    @staticmethod
    def verify_password(user_id: int, password: str) -> bool:
        """
        Verify if a password matches the user's stored password.

        Args:
            user_id: The ID of the user.
            password: The plaintext password to verify.

        Returns:
            bool: True if password matches, False otherwise.
        """
        user = UserModel.get_by_id(user_id)
        if user is None:
            return False
        return bcrypt.checkpw(
            password.encode("utf-8"), user["password"].encode("utf-8")
        )
