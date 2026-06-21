"""Unit tests for the services layer: AuthService, AlbumService, PhotoService, etc.

Tests validation rules, error handling, and business logic that execute BEFORE
any database transaction. Uses mocking for DB-dependent operations.

Modules tested:
    test_auth_service.py       → AuthService (password validation, email format, bcrypt)
    test_album_service.py      → AlbumService (name validation, ownership checks)
    test_comment_service.py    → CommentService (text length, emptiness)
    test_category_service.py   → CategoryService (name uniqueness, length)
    test_user_service.py       → UserService (role validation)
    test_notification_service.py → NotificationService (type checks, error safety)
"""
