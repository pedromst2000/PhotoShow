"""Unit tests for database models: serialization, validators, properties, class methods.

Tests verify that each model's:
- to_dict() produces correct serialized output
- Properties work correctly (relationships, computed values)
- Field constraints are enforced (length, format, required fields)
- Class methods (get_by_id, get_all) work as expected

Models tested:
    test_user.py          → User (usernames, emails, roles, is_admin)
    test_album.py         → Album (name constraints, timestamps)
    test_photo.py         → Photo (descriptions, category links, albums)
    test_comment.py       → Comment (text, nesting, photo links)
    test_category.py      → Category (names, uniqueness)
    test_like.py          → Like (user-photo relationships)
    test_rating.py        → Rating (ratings, weighted averages)
    test_follow.py        → Follow (user relationships)
    test_favorite.py      → Favorite (favorite photos)
    test_avatar.py        → Avatar (user avatars, file paths)
    test_photo_image.py   → PhotoImage (photo variants, dimensions)
    test_notification.py  → Notification (types, read status)
    test_report.py        → Report (report reasons, content)
    test_contact.py       → Contact (contact messages)
    test_notification_type.py  → NotificationType (notification lookups)
    test_report_reason.py      → ReportReason (report reason lookups)
    test_role.py               → Role (user role lookups)
"""
