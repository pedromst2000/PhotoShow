"""
Smoke tests — verify that critical modules import cleanly.

These tests run in seconds and act as the first gate in CI before deeper
test suites execute, checking that no circular imports or syntax errors
prevent module loading.
"""


class TestModuleImports:
    """All core service and utility modules must be importable."""

    def test_auth_service(self):
        from app.core.services.auth_service import AuthService  # noqa: F401

    def test_album_service(self):
        from app.core.services.album_service import AlbumService  # noqa: F401

    def test_photo_service(self):
        from app.core.services.photo_service import PhotoService  # noqa: F401

    def test_comment_service(self):
        from app.core.services.comment_service import CommentService  # noqa: F401

    def test_user_service(self):
        from app.core.services.user_service import UserService  # noqa: F401

    def test_notification_service(self):
        from app.core.services.notification_service import (  # noqa: F401
            NotificationService,
        )

    def test_category_service(self):
        from app.core.services.category_service import CategoryService  # noqa: F401

    def test_report_service(self):
        from app.core.services.report_service import ReportService  # noqa: F401

    def test_catalog_service(self):
        from app.core.services.catalog_service import CatalogService  # noqa: F401

    def test_date_utils(self):
        from app.utils.date_utils import format_timestamp  # noqa: F401

    def test_hash_utils(self):
        from app.utils.hash_utils import hash_password  # noqa: F401

    def test_weighted_rating(self):
        from app.core.services.helpers.weighted_rating import (  # noqa: F401
            calculate_weighted_rating,
        )

    def test_cloudinary_config(self):
        from app.config.cloudinary_config import (  # noqa: F401
            DEFAULT_AVATAR_URL,
            FOLDER_PHOTOS_PROD,
        )
