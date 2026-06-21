"""
Unit tests for CategoryService.

Name validation fires before any DB call — no mocking needed for those cases.
"""

from app.core.services.category_service import CategoryService


class TestAddCategoryValidation:
    def test_empty_name_returns_error(self):
        ok, msg = CategoryService.add_category("")
        assert ok is False
        assert "required" in msg.lower()

    def test_whitespace_only_returns_error(self):
        ok, msg = CategoryService.add_category("   ")
        assert ok is False

    def test_name_over_25_chars_returns_error(self):
        ok, msg = CategoryService.add_category("A" * 26)
        assert ok is False
        assert "25" in msg or "long" in msg.lower()

    def test_name_exactly_25_chars_passes_to_db(self, mocker):
        """25-character name passes length validation and moves to DB."""
        mock_session = mocker.MagicMock()
        mock_cm = mocker.MagicMock()
        mock_cm.__enter__ = mocker.MagicMock(return_value=mock_session)
        mock_cm.__exit__ = mocker.MagicMock(return_value=False)
        mocker.patch(
            "app.core.services.category_service.SessionLocal",
            return_value=mock_cm,
        )
        mocker.patch(
            "app.core.services.category_service.CategoryModel.get_all",
            return_value=[],
        )
        mocker.patch(
            "app.core.services.category_service.CategoryModel.create",
            return_value=None,
        )
        # category_exists also uses SessionLocal — patch it too
        mocker.patch(
            "app.core.services.category_service.CategoryService.category_exists",
            return_value=False,
        )
        ok, msg = CategoryService.add_category("A" * 25)
        assert ok is True

    def test_duplicate_name_returns_error(self, mocker):
        """When category_exists returns True the service rejects the add."""
        mocker.patch(
            "app.core.services.category_service.CategoryService.category_exists",
            return_value=True,
        )
        ok, msg = CategoryService.add_category("Nature")
        assert ok is False
        assert "already exists" in msg.lower()
