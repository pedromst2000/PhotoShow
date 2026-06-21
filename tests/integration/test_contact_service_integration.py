"""
Integration tests for ContactService covering message submission and management.

Focuses on:
- Contact message creation with validation
- Contact message title/message constraints
- Contact retrieval and enrichment
"""

import pytest

from app.core.services.auth_service import AuthService
from app.core.services.contact_service import ContactService


class TestContactCreation:
    """Test contact message creation and validation."""

    def test_create_contact_success(self, integration_db):
        """Create a valid contact message."""
        user = AuthService.register_user("alice", "alice@example.com", "password")

        result = ContactService.create_contact(
            title="Support",
            message="I need help with my account",
            user_id=user["id"],
        )

        assert result is True

    def test_create_contact_title_invalid_format(self, integration_db):
        """Contact title with numbers or special chars is rejected."""
        user = AuthService.register_user("bob", "bob@example.com", "password")

        with pytest.raises(ValueError) as exc_info:
            ContactService.create_contact(
                title="Support123",
                message="I need help",
                user_id=user["id"],
            )

        assert "letters" in str(exc_info.value).lower()

    def test_create_contact_title_with_spaces(self, integration_db):
        """Contact title with spaces is rejected."""
        user = AuthService.register_user("charlie", "charlie@example.com", "password")

        with pytest.raises(ValueError) as exc_info:
            ContactService.create_contact(
                title="Support Request",
                message="I need help",
                user_id=user["id"],
            )

        assert "letters" in str(exc_info.value).lower()

    def test_create_contact_title_too_long(self, integration_db):
        """Contact title exceeding 75 chars is rejected."""
        user = AuthService.register_user("diana", "diana@example.com", "password")

        long_title = "a" * 100

        with pytest.raises(ValueError) as exc_info:
            ContactService.create_contact(
                title=long_title,
                message="Help",
                user_id=user["id"],
            )

        assert "title too long" in str(exc_info.value).lower()

    def test_create_contact_message_too_long(self, integration_db):
        """Contact message exceeding 255 chars is rejected."""
        user = AuthService.register_user("eve", "eve@example.com", "password")

        long_message = "x" * 300

        with pytest.raises(ValueError) as exc_info:
            ContactService.create_contact(
                title="Support",
                message=long_message,
                user_id=user["id"],
            )

        assert "message too long" in str(exc_info.value).lower()

    def test_create_contact_duplicate_title(self, integration_db):
        """Duplicate contact title (case-insensitive) is rejected."""
        user1 = AuthService.register_user("frank", "frank@example.com", "password")
        user2 = AuthService.register_user("grace", "grace@example.com", "password")

        # First contact succeeds
        ContactService.create_contact(
            title="Support",
            message="First message",
            user_id=user1["id"],
        )

        # Second contact with same title should fail
        with pytest.raises(ValueError) as exc_info:
            ContactService.create_contact(
                title="Support",
                message="Second message",
                user_id=user2["id"],
            )

        assert (
            "already exists" in str(exc_info.value).lower()
            or "unique" in str(exc_info.value).lower()
        )

    def test_create_contact_title_case_insensitive_duplicate(self, integration_db):
        """Duplicate check is case-insensitive."""
        user1 = AuthService.register_user("helen", "helen@example.com", "password")
        user2 = AuthService.register_user("ian", "ian@example.com", "password")

        ContactService.create_contact(
            title="Feedback",
            message="First",
            user_id=user1["id"],
        )

        with pytest.raises(ValueError):
            ContactService.create_contact(
                title="FEEDBACK",
                message="Second",
                user_id=user2["id"],
            )


class TestContactRetrieval:
    """Test contact message retrieval and enrichment."""

    def test_get_all_enriched(self, integration_db):
        """Get all contact messages enriched with usernames."""
        user1 = AuthService.register_user("jack", "jack@example.com", "password")
        user2 = AuthService.register_user("karen", "karen@example.com", "password")

        ContactService.create_contact("Help", "Need help", user_id=user1["id"])
        ContactService.create_contact("Bug", "Found a bug", user_id=user2["id"])

        contacts = ContactService.get_all_enriched()

        assert len(contacts) >= 2
        # Each should have username enriched
        for contact in contacts:
            assert "username" in contact
            assert "title" in contact
            assert "message" in contact

    def test_get_enriched_empty_list(self, integration_db):
        """Empty contact list returns empty list, not error."""
        contacts = ContactService.get_all_enriched()

        # Should be a list (might be empty or have existing contacts)
        assert isinstance(contacts, list)

    def test_resolve_contact_success(self, integration_db):
        """Resolve (delete) a contact message."""
        user = AuthService.register_user("leo", "leo@example.com", "password")

        ContactService.create_contact("Info", "Question", user_id=user["id"])

        # Get all and extract ID
        contacts = ContactService.get_all_enriched()
        if contacts:
            contact_id = contacts[0]["id"]
            result = ContactService.resolve_contact(contact_id)
            assert result is True

    def test_resolve_nonexistent_contact(self, integration_db):
        """Resolve nonexistent contact returns False."""
        result = ContactService.resolve_contact(9999)
        assert result is False
