"""
Functional tests: Album business rules.

Tests that the system enforces business rules for album management:
  1. Duplicate album names are rejected per-user (business rule)
  2. Different users can share album names (no global uniqueness constraint)

NOTE: Format validation (empty, length limits, whitespace trimming) is tested
in the unit layer (tests/unit/services/test_album_service.py). This functional
layer focuses on business OUTCOMES, not input format.
"""

import pytest

from app.core.services.album_service import AlbumService
from app.core.services.auth_service import AuthService


@pytest.fixture()
def creator(integration_db):
    """Register a user to act as album creator for all album business rule tests."""
    return AuthService.register_user(
        username="albumuser",
        email="albumuser@gmail.com",
        password="Test1_abc",
    )


# ═══════════════════════════════════════════════════════════════════
# Business rule: Duplicate album names per-user
# ═══════════════════════════════════════════════════════════════════


class TestAlbumBusinessRules:
    def test_system_prevents_duplicate_album_names_per_user(
        self, integration_db, creator
    ):
        AlbumService.create_album("Holidays", creator_id=creator["id"])
        with pytest.raises(ValueError, match="already have"):
            AlbumService.create_album("Holidays", creator_id=creator["id"])

    def test_system_prevents_duplicate_album_names_case_insensitive(
        self, integration_db, creator
    ):
        AlbumService.create_album("Summer", creator_id=creator["id"])
        with pytest.raises(ValueError, match="already have"):
            # "summer" (lowercase) must also be blocked — case-insensitive check
            AlbumService.create_album("summer", creator_id=creator["id"])

    def test_different_users_can_independently_create_albums_with_same_name(
        self, integration_db
    ):
        user_a = AuthService.register_user("user_a", "user_a@gmail.com", "Test1_abc")
        user_b = AuthService.register_user("user_b", "user_b@gmail.com", "Test2_abc")
        album_a = AlbumService.create_album("My Photos", creator_id=user_a["id"])
        album_b = AlbumService.create_album("My Photos", creator_id=user_b["id"])
        assert album_a is not None
        assert album_b is not None
