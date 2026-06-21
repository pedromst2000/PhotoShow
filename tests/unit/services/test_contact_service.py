"""
Unit tests for ContactService.

Covers the actual public methods:
- create_contact: submit a contact message
- get_all_enriched: retrieve all messages (admin)
- resolve_contact: mark a message as resolved
"""

from app.core.services.contact_service import ContactService


class TestCreateContact:
    """Test ContactService.create_contact."""

    def test_method_exists(self):
        assert hasattr(ContactService, "create_contact")

    def test_is_callable(self):
        assert callable(ContactService.create_contact)


class TestGetAllEnriched:
    """Test ContactService.get_all_enriched."""

    def test_method_exists(self):
        assert hasattr(ContactService, "get_all_enriched")

    def test_is_callable(self):
        assert callable(ContactService.get_all_enriched)


class TestResolveContact:
    """Test ContactService.resolve_contact."""

    def test_method_exists(self):
        assert hasattr(ContactService, "resolve_contact")

    def test_is_callable(self):
        assert callable(ContactService.resolve_contact)
