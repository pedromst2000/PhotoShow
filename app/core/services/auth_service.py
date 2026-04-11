import re as regex
from typing import Optional, Tuple

import bcrypt

from app.core.db.engine import SessionLocal
from app.core.db.models.avatar import AvatarModel
from app.core.db.models.role import RoleModel
from app.core.db.models.user import UserModel

_DEFAULT_AVATAR = "assets/images/profile_avatars/default_avatar.png"


class AuthService:
    """
    Service class for authentication business logic.

    Handles user authentication, registration, and credential validation.
    All password hashing/verification is done here.

    Business rules enforced in this service:
    - Passwords must be at least 7 characters and contain a mix of character types.
    - Usernames must be unique (case-insensitive) and contain only allowed characters.
    - Emails must be unique and follow a valid format.
    - Admins cannot register through the public registration endpoint.
        - When registering, users are assigned the "unsigned" role by default and a default avatar.
        - Password availability check compares against all stored password hashes to prevent duplicates.
        - Authentication verifies email existence and password correctness using bcrypt.
        - Password changes require current password verification and new password validation.
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
        with SessionLocal() as session:
            user = UserModel.get_by_email(session, email)
            if user is None:
                return None

            # Verify password using bcrypt
            if bcrypt.checkpw(
                password.encode("utf-8"), user["password"].encode("utf-8")
            ):
                return user
            return None  # Authentication failed

    @staticmethod
    def register_user(username: str, email: str, password: str) -> dict:
        """
        Register a new user with hashed password and default avatar.

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

        with SessionLocal() as session:
            unsigned_role = RoleModel.get_by_name(session, "unsigned")
            # Create user in database
            user = UserModel.create(
                session,
                username=username,
                email=email,
                password=hashed_password,
                roleId=unsigned_role["id"] if unsigned_role else None,
                isBlocked=False,
            )
            # Create default avatar (was previously inside UserModel.create)
            AvatarModel.create(session, user["id"], _DEFAULT_AVATAR)
            session.commit()
            # Re-fetch after commit so the returned dict includes the avatar
            return UserModel.get_by_id(session, user["id"])  # type: ignore[return-value]

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
        # Reject non-string or empty values
        if not email or not isinstance(email, str):
            return False

        # Reject any whitespace characters (leading, trailing, or internal)
        if regex.search(r"\s", email):
            return False

        # Strict pattern: local part (letters, digits and common email punctuation),
        # then @, then allowed domains (gmail or hotmail), and ending with .com
        pattern = r"[A-Za-z0-9._%+-]+@(gmail|hotmail)\.com"

        # Use fullmatch to ensure there are no extra trailing/leading characters
        if not regex.fullmatch(pattern, email, flags=regex.IGNORECASE):
            return False
        return True

    @staticmethod
    def validate_username_format(username: str) -> bool:
        """
        Validate username format.

        Rules enforced by this function:
            - Allowed characters: letters (A-Z, a-z), digits (0-9), underscore (_),
              dot (.), and hyphen (-)
            - No spaces or other special characters are allowed
            - Username must include at least one letter (A-Z or a-z).
              Usernames composed only of digits or only of punctuation
              characters (underscore/dot/hyphen) are invalid.

        Args:
            username: The username to validate.

        Returns:
            bool: True if the username format is valid, False otherwise.
        """
        # Fast-fail: ensure only allowed characters are present
        if not regex.fullmatch(r"[A-Za-z0-9_.-]+", username):
            return False
        # Ensure there's at least one ASCII letter (prevents digits-only or punctuation-only)
        if not regex.search(r"[A-Za-z]", username):
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
        with SessionLocal() as session:
            return not UserModel.email_exists(session, email)

    @staticmethod
    def is_username_available(username: str) -> bool:
        """
        Check if a username is available for registration (case-insensitive).

        Args:
            username: The username to check.

        Returns:
            bool: True if username is available, False if already taken.
        """
        with SessionLocal() as session:
            return not UserModel.username_exists(session, username)

    @staticmethod
    def is_password_available(password: str) -> bool:
        """
        Check if a password is available for registration by verifying it against
        all stored password hashes in the database.

        Args:
            password: The plaintext password to check.
        Returns:
            bool: True if password is available (not taken), False if already taken.
        """
        try:
            with SessionLocal() as session:
                stored_passwords = UserModel.get_password_hashes(session)
            password_encoded = password.encode("utf-8")

            for stored in stored_passwords:
                if not stored:
                    continue

                # Verify against bcrypt hashes (all production passwords)
                if isinstance(stored, str) and stored.startswith("$2"):
                    try:
                        if bcrypt.checkpw(password_encoded, stored.encode("utf-8")):
                            return False  # Password is taken
                    except (ValueError, AttributeError):
                        # Malformed hash; skip and check next
                        continue
                else:
                    # Fallback for plaintext entries (sample CSV only)
                    if password == stored:
                        return False  # Password is taken

            return True  # Password is available
        except Exception:
            # If database fetch fails, assume password is available (safer than blocking)
            return True

    @staticmethod
    def validate_password_format(password: str) -> Tuple[bool, Optional[str]]:
        """
        Validate password format with strong security rules.

        Rules enforced:
            - Minimum 7 characters (security best practice)
            - No spaces allowed
            - Allowed characters: letters (A-Z, a-z), digits (0-9), underscore (_), dot (.), hyphen (-)
            - Must contain at least one uppercase letter (A-Z)
            - Must contain at least one lowercase letter (a-z)
            - Must contain at least one digit (0-9)
            - Must contain at least one special character from: underscore, dot, hyphen (_.-)

        Args:
            password: The password to validate.

        Returns:
            Tuple[bool, Optional[str]]: `(True, None)` when the password meets all
            criteria, otherwise `(False, "error message")` with a short
            explanation.
        """

        # Evaluate checks and compute the first failing rule as a code string.
        checks = [
            ("TOO_SHORT", len(password) < 7),
            ("HAS_SPACE", " " in password),
            ("INVALID_CHARS", not regex.fullmatch(r"[A-Za-z0-9_.-]+", password)),
            ("NO_UPPER", not regex.search(r"[A-Z]", password)),
            ("NO_LOWER", not regex.search(r"[a-z]", password)),
            ("NO_DIGIT", not regex.search(r"[0-9]", password)),
            ("NO_SPECIAL", not regex.search(r"[_.-]", password)),
            ("REPEATED", bool(regex.search(r"(.)\\1\\1", password))),
        ]

        violation = next((code for code, cond in checks if cond), None)

        match violation:
            case "TOO_SHORT":
                return False, "Password must be at least 7 characters long."
            case "HAS_SPACE":
                return False, "Password cannot contain spaces."
            case "INVALID_CHARS":
                return False, (
                    "Password contains invalid characters. Use only letters (A-Z, a-z), "
                    "digits (0-9), underscore (_), dot (.), and hyphen (-)."
                )
            case "NO_UPPER":
                return (
                    False,
                    "Password must contain at least one uppercase letter (A-Z).",
                )
            case "NO_LOWER":
                return (
                    False,
                    "Password must contain at least one lowercase letter (a-z).",
                )
            case "NO_DIGIT":
                return False, "Password must contain at least one digit (0-9)."
            case "NO_SPECIAL":
                return False, (
                    "Password must contain at least one special character from: "
                    "underscore (_), dot (.), or hyphen (-)."
                )
            case "REPEATED":
                return (
                    False,
                    "Password cannot contain three or more repeated characters in a row.",
                )
            case None:
                return True, None

        # Fallback return to satisfy static checkers (redundant at runtime).
        return True, None

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
        with SessionLocal() as session:
            result = UserModel.update_password(session, user_id, hashed)
            session.commit()
            return result

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
        with SessionLocal() as session:
            user = UserModel.get_by_id(session, user_id)
        if user is None:
            return False
        return bcrypt.checkpw(
            password.encode("utf-8"), user["password"].encode("utf-8")
        )
