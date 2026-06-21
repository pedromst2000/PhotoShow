"""Acceptance test layer: complete user workflows and journeys.

Acceptance tests verify that complete user workflows work end-to-end through
the service layer. These tests simulate realistic user actions spanning multiple
operations and services, verifying critical functionality from a user perspective.

KEY DISTINCTION FROM INTEGRATION:
  Integration tests verify individual service operations and interactions.
  Acceptance tests verify complete workflows (multi-step journeys).

  Example:
    Integration: "test_user_can_like_photo()" - single operation
    Acceptance: "test_user_registers_creates_album_uploads_photos()" - workflow

SCOPE:
  ✓ Registration → Login → Album creation → Feature usage chains
  ✓ Complete user workflows through the application
  ✓ Multi-step operations verified together
  ✓ Success criteria for key user scenarios

OUT OF SCOPE:
  ✗ Individual service operations (use integration tests)
  ✗ Business rule violations (use functional tests)
  ✗ Input validation (use unit tests)
  ✗ Service-to-service interactions in isolation

Test files:
    test_user_workflows.py    Complete journeys: Registration→Login→Albums

REFACTORING CHANGES:
  ✂️ Deleted: test_album_business_rules.py (duplicate integration tests)
  ✂️ Deleted: test_photo_business_rules.py (duplicate integration tests)
  ✂️ Deleted: test_comment_business_rules.py (validation tests - moved to unit)

Result: Acceptance tests now focus ONLY on complete workflows,
avoiding duplication with integration layer.

Each test uses a fresh in-memory SQLite database with all ORM models
registered and role data pre-seeded.

Run:
    pytest tests/acceptance/ -v
    pytest tests/acceptance/ -v -k "workflow"  # Single workflow
"""
