"""
Unit tests for UserService.

Role validation fires before any DB access — those tests need no mocking.
"""

import pytest

from app.core.services.user_service import UserService


def _mock_session(mocker):
    mock_session = mocker.MagicMock()
    mock_cm = mocker.MagicMock()
    mock_cm.__enter__ = mocker.MagicMock(return_value=mock_session)
    mock_cm.__exit__ = mocker.MagicMock(return_value=False)
    mocker.patch(
        "app.core.services.user_service.SessionLocal",
        return_value=mock_cm,
    )
    return mock_session


class TestChangeRole:
    def test_unknown_role_raises_value_error(self):
        """Roles outside ('regular', 'unsigned') are rejected before the DB."""
        with pytest.raises(ValueError, match="Invalid role"):
            UserService.change_role(username="bob", new_role="superadmin")

    def test_admin_role_is_not_assignable(self):
        """'admin' cannot be assigned through the public API."""
        with pytest.raises(ValueError, match="Invalid role"):
            UserService.change_role(username="bob", new_role="admin")

    def test_valid_role_regular_delegates_to_db(self, mocker):
        _mock_session(mocker)
        mocker.patch(
            "app.core.services.user_service.UserModel.get_by_username",
            return_value={"id": 2, "username": "bob", "roleId": 3},
        )
        mocker.patch(
            "app.core.services.user_service.RoleModel.get_by_name",
            return_value={"id": 2, "role": "regular"},
        )
        mocker.patch(
            "app.core.services.user_service.UserModel.update",
            return_value={},
        )
        result = UserService.change_role(username="bob", new_role="regular")
        assert result is True

    def test_valid_role_unsigned_delegates_to_db(self, mocker):
        _mock_session(mocker)
        mocker.patch(
            "app.core.services.user_service.UserModel.get_by_username",
            return_value={"id": 3, "username": "carol", "roleId": 2},
        )
        mocker.patch(
            "app.core.services.user_service.RoleModel.get_by_name",
            return_value={"id": 3, "role": "unsigned"},
        )
        mocker.patch(
            "app.core.services.user_service.UserModel.update",
            return_value={},
        )
        result = UserService.change_role(username="carol", new_role="unsigned")
        assert result is True

    def test_user_not_found_returns_false(self, mocker):
        _mock_session(mocker)
        mocker.patch(
            "app.core.services.user_service.UserModel.get_by_username",
            return_value=None,
        )
        result = UserService.change_role(username="ghost", new_role="regular")
        assert result is False
