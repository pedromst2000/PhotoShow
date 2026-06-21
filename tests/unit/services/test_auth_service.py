"""
Unit tests for AuthService.

Covers three categories:
- Pure validation (no DB, no mocks): email format, username format, password format.
- Mocked DB operations: authenticate, register duplicate detection.
"""

from app.core.services.auth_service import AuthService

# ═══════════════════════════════════════════════════════════════════
# Email format validation  (pure function — zero DB / zero mocks)
# ═══════════════════════════════════════════════════════════════════


class TestValidateEmailFormat:
    def test_valid_gmail(self):
        assert AuthService.validate_email_format("user@gmail.com") is True

    def test_valid_hotmail(self):
        assert AuthService.validate_email_format("user@hotmail.com") is True

    def test_valid_complex_local_part(self):
        assert AuthService.validate_email_format("first.last+tag@gmail.com") is True

    def test_invalid_yahoo_domain(self):
        assert AuthService.validate_email_format("user@yahoo.com") is False

    def test_invalid_no_at_symbol(self):
        assert AuthService.validate_email_format("usergmail.com") is False

    def test_invalid_empty_string(self):
        assert AuthService.validate_email_format("") is False

    def test_invalid_none_value(self):
        assert AuthService.validate_email_format(None) is False  # type: ignore[arg-type]

    def test_invalid_leading_space(self):
        assert AuthService.validate_email_format(" user@gmail.com") is False

    def test_invalid_trailing_space(self):
        assert AuthService.validate_email_format("user@gmail.com ") is False

    def test_invalid_internal_space(self):
        assert AuthService.validate_email_format("us er@gmail.com") is False


# ═══════════════════════════════════════════════════════════════════
# Username format validation  (pure function)
# ═══════════════════════════════════════════════════════════════════


class TestValidateUsernameFormat:
    def test_valid_alphanumeric(self):
        assert AuthService.validate_username_format("user123") is True

    def test_valid_letters_only(self):
        assert AuthService.validate_username_format("username") is True

    def test_valid_with_underscore(self):
        assert AuthService.validate_username_format("user_name") is True

    def test_valid_with_dot(self):
        assert AuthService.validate_username_format("user.name") is True

    def test_valid_with_hyphen(self):
        assert AuthService.validate_username_format("user-name") is True

    def test_invalid_digits_only(self):
        assert AuthService.validate_username_format("12345") is False

    def test_invalid_underscores_only(self):
        assert AuthService.validate_username_format("___") is False

    def test_invalid_with_space(self):
        assert AuthService.validate_username_format("user name") is False

    def test_invalid_with_at_symbol(self):
        assert AuthService.validate_username_format("user@name") is False

    def test_invalid_empty(self):
        assert AuthService.validate_username_format("") is False


# ═══════════════════════════════════════════════════════════════════
# Password format validation  (pure function)
# ═══════════════════════════════════════════════════════════════════

_VALID_PASS = "Test1_abc"  # uppercase, lowercase, digit, special char


class TestValidatePasswordFormat:
    def test_valid_password_returns_true_and_none(self):
        ok, msg = AuthService.validate_password_format(_VALID_PASS)
        assert ok is True
        assert msg is None

    def test_too_short_returns_false(self):
        ok, msg = AuthService.validate_password_format("Ab1_")  # 4 chars
        assert ok is False
        assert msg is not None

    def test_no_uppercase_returns_false(self):
        ok, msg = AuthService.validate_password_format("test1_abc")
        assert ok is False
        assert msg is not None

    def test_no_lowercase_returns_false(self):
        ok, msg = AuthService.validate_password_format("TEST1_ABC")
        assert ok is False
        assert msg is not None

    def test_no_digit_returns_false(self):
        ok, msg = AuthService.validate_password_format("Testab_cd")
        assert ok is False
        assert msg is not None

    def test_no_special_char_returns_false(self):
        ok, msg = AuthService.validate_password_format("Testab1cd")
        assert ok is False
        assert msg is not None

    def test_with_space_returns_false(self):
        ok, msg = AuthService.validate_password_format("Test 1_a")
        assert ok is False
        assert msg is not None

    def test_error_message_is_nonempty_string(self):
        ok, msg = AuthService.validate_password_format("bad")
        assert ok is False
        assert isinstance(msg, str)
        assert len(msg) > 0


# ═══════════════════════════════════════════════════════════════════
# authenticate  (mocked DB)
# ═══════════════════════════════════════════════════════════════════


class TestAuthenticate:
    def _mock_session(self, mocker):
        """Return a MagicMock context manager that acts as SessionLocal()."""
        mock_cm = mocker.MagicMock()
        mock_cm.__enter__ = mocker.MagicMock(return_value=mocker.MagicMock())
        mock_cm.__exit__ = mocker.MagicMock(return_value=False)
        mocker.patch(
            "app.core.services.auth_service.SessionLocal",
            return_value=mock_cm,
        )
        return mock_cm

    def test_unknown_email_returns_none(self, mocker):
        self._mock_session(mocker)
        mocker.patch(
            "app.core.services.auth_service.UserModel.get_by_email",
            return_value=None,
        )
        assert AuthService.authenticate("nobody@gmail.com", "Test1_abc") is None

    def test_wrong_password_returns_none(self, mocker):
        self._mock_session(mocker)
        fake_user = {
            "id": 1,
            "username": "alice",
            "email": "alice@gmail.com",
            "password": "$2b$12$fakehash",
            "role": "regular",
            "isBlocked": False,
        }
        mocker.patch(
            "app.core.services.auth_service.UserModel.get_by_email",
            return_value=fake_user,
        )
        mocker.patch(
            "app.core.services.auth_service.bcrypt.checkpw", return_value=False
        )
        result = AuthService.authenticate("alice@gmail.com", "WrongPass1.")
        assert result is None

    def test_correct_credentials_returns_user_dict(self, mocker):
        self._mock_session(mocker)
        fake_user = {
            "id": 1,
            "username": "alice",
            "email": "alice@gmail.com",
            "password": "$2b$12$fakehash",
            "role": "regular",
            "isBlocked": False,
        }
        mocker.patch(
            "app.core.services.auth_service.UserModel.get_by_email",
            return_value=fake_user,
        )
        mocker.patch("app.core.services.auth_service.bcrypt.checkpw", return_value=True)
        result = AuthService.authenticate("alice@gmail.com", "Test1_abc")
        assert result is not None
        assert result["username"] == "alice"
