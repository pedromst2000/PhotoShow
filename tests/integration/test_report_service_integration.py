"""
Integration tests for ReportService covering report submission, validation, and retrieval.

Focuses on:
- Report submission business rules (reason validation, admin prevention, duplicate checks)
- Report resolution and retrieval
- Enriched report data with content details and creator information
"""

from app.core.services.album_service import AlbumService
from app.core.services.auth_service import AuthService
from app.core.services.comment_service import CommentService
from app.core.services.photo_service import PhotoService
from app.core.services.report_service import ReportService


class TestReportSubmissionValidation:
    """Test report submission business rules and validation."""

    def test_submit_report_missing_reason(self, integration_db):
        """Empty reason is rejected."""
        # Create a regular user
        user = AuthService.register_user("alice", "alice@example.com", "password_alice")
        # Create album and photo for reporting
        album = AlbumService.create_album("Album 1", user["id"])
        photo = PhotoService.create_photo_record(
            album_id=album["id"], category_id=1, description="Photo 1"
        )

        success, msg = ReportService.submit_report(
            reporter_id=user["id"],
            reason="",
            photo_id=photo["id"],
        )

        assert success is False
        assert "reason is required" in msg.lower()

    def test_submit_report_missing_both_photo_and_comment(self, integration_db):
        """Must specify exactly one of photo_id or comment_id."""
        user = AuthService.register_user("bob", "bob@example.com", "password_bob")

        success, msg = ReportService.submit_report(
            reporter_id=user["id"],
            reason="Offensive",
        )

        assert success is False
        assert "exactly one" in msg.lower()

    def test_submit_report_both_photo_and_comment(self, integration_db):
        """Cannot specify both photo and comment."""
        user = AuthService.register_user(
            "charlie", "charlie@example.com", "password_charlie"
        )
        album = AlbumService.create_album("Album 1", user["id"])
        photo = PhotoService.create_photo_record(
            album_id=album["id"], category_id=1, description="Photo 1"
        )
        _, _, comment = CommentService.add_comment(
            user["id"], photo["id"], "Test comment"
        )
        assert comment is not None

        success, msg = ReportService.submit_report(
            reporter_id=user["id"],
            reason="Offensive",
            photo_id=photo["id"],
            comment_id=comment["id"],
        )

        assert success is False
        assert "exactly one" in msg.lower()

    def test_submit_report_other_reason_missing_description(self, integration_db):
        """Reason 'Other' requires description."""
        user = AuthService.register_user("diana", "diana@example.com", "password_diana")
        album = AlbumService.create_album("Album 1", user["id"])
        photo = PhotoService.create_photo_record(
            album_id=album["id"], category_id=1, description="Photo 1"
        )

        success, msg = ReportService.submit_report(
            reporter_id=user["id"],
            reason="Other",
            photo_id=photo["id"],
        )

        assert success is False
        assert "details" in msg.lower()

    def test_submit_report_description_too_long(self, integration_db):
        """Description exceeding 255 characters is rejected."""
        user = AuthService.register_user("eve", "eve@example.com", "password_eve")
        album = AlbumService.create_album("Album 1", user["id"])
        photo = PhotoService.create_photo_record(
            album_id=album["id"], category_id=1, description="Photo 1"
        )

        long_description = "x" * 300

        success, msg = ReportService.submit_report(
            reporter_id=user["id"],
            reason="Other",
            photo_id=photo["id"],
            description=long_description,
        )

        assert success is False
        assert "exceed" in msg.lower()

    def test_submit_report_invalid_reason(self, integration_db):
        """Invalid reason label is rejected."""
        user = AuthService.register_user("frank", "frank@example.com", "password_frank")
        album = AlbumService.create_album("Album 1", user["id"])
        photo = PhotoService.create_photo_record(
            album_id=album["id"], category_id=1, description="Photo 1"
        )

        success, msg = ReportService.submit_report(
            reporter_id=user["id"],
            reason="NonExistentReason",
            photo_id=photo["id"],
        )

        assert success is False
        assert "invalid reason" in msg.lower()

    def test_submit_report_admin_cannot_report(self, integration_db):
        """Admin user cannot submit reports."""
        user = AuthService.register_user("grace", "grace@example.com", "password_grace")
        album = AlbumService.create_album("Album 1", user["id"])
        photo = PhotoService.create_photo_record(
            album_id=album["id"], category_id=1, description="Photo 1"
        )

        # Manually set role to admin for this user
        from app.core.db.engine import SessionLocal
        from app.core.db.models.user import UserModel

        with SessionLocal() as session:
            user_obj = session.query(UserModel).filter_by(id=user["id"]).first()
            if user_obj:
                user_obj.roleId = 1  # admin role
                session.commit()

        success, msg = ReportService.submit_report(
            reporter_id=user["id"],
            reason="Offensive",
            photo_id=photo["id"],
        )

        assert success is False
        assert "admin" in msg.lower()


class TestReportDuplicatePrevention:
    """Test that users cannot submit duplicate reports."""

    def test_submit_duplicate_photo_report(self, integration_db):
        """User cannot report same photo twice."""
        user = AuthService.register_user("helen", "helen@example.com", "password_helen")
        album = AlbumService.create_album("Album 1", user["id"])
        photo = PhotoService.create_photo_record(
            album_id=album["id"], category_id=1, description="Photo 1"
        )

        # First report succeeds
        success1, msg1 = ReportService.submit_report(
            reporter_id=user["id"],
            reason="Offensive",
            photo_id=photo["id"],
        )

        assert success1 is True

        # Second report fails
        success2, msg2 = ReportService.submit_report(
            reporter_id=user["id"],
            reason="Offensive",
            photo_id=photo["id"],
        )

        assert success2 is False
        assert "already reported" in msg2.lower()

    def test_submit_duplicate_comment_report(self, integration_db):
        """User cannot report same comment twice."""
        user = AuthService.register_user("ian", "ian@example.com", "password_ian")
        album = AlbumService.create_album("Album 1", user["id"])
        photo = PhotoService.create_photo_record(
            album_id=album["id"], category_id=1, description="Photo 1"
        )
        _, _, comment = CommentService.add_comment(
            user["id"], photo["id"], "Test comment"
        )
        assert comment is not None

        success1, _ = ReportService.submit_report(
            reporter_id=user["id"],
            reason="Offensive",
            comment_id=comment["id"],
        )
        assert success1 is True

        success2, msg2 = ReportService.submit_report(
            reporter_id=user["id"],
            reason="Offensive",
            comment_id=comment["id"],
        )
        assert success2 is False
        assert "already reported" in msg2.lower()


class TestReportSubmissionSuccess:
    """Test successful report submissions."""

    def test_submit_photo_report_success(self, integration_db):
        """Valid photo report is created."""
        user = AuthService.register_user("jack", "jack@example.com", "password_jack")
        album = AlbumService.create_album("Album 1", user["id"])
        photo = PhotoService.create_photo_record(
            album_id=album["id"], category_id=1, description="Photo 1"
        )

        success, msg = ReportService.submit_report(
            reporter_id=user["id"],
            reason="Offensive",
            photo_id=photo["id"],
        )

        assert success is True
        assert "submitted" in msg.lower()

    def test_submit_comment_report_success(self, integration_db):
        """Valid comment report is created."""
        user = AuthService.register_user("karen", "karen@example.com", "password_karen")
        album = AlbumService.create_album("Album 1", user["id"])
        photo = PhotoService.create_photo_record(
            album_id=album["id"], category_id=1, description="Photo 1"
        )
        _, _, comment = CommentService.add_comment(
            user["id"], photo["id"], "Test comment"
        )
        assert comment is not None

        success, msg = ReportService.submit_report(
            reporter_id=user["id"],
            reason="Offensive",
            comment_id=comment["id"],
        )

        assert success is True
        assert "submitted" in msg.lower()

    def test_submit_report_with_description(self, integration_db):
        """Report with 'Other' reason and description succeeds."""
        user = AuthService.register_user("leo", "leo@example.com", "password_leo")
        album = AlbumService.create_album("Album 1", user["id"])
        photo = PhotoService.create_photo_record(
            album_id=album["id"], category_id=1, description="Photo 1"
        )

        success, msg = ReportService.submit_report(
            reporter_id=user["id"],
            reason="Other",
            photo_id=photo["id"],
            description="This photo violates community guidelines",
        )

        assert success is True
        assert "submitted" in msg.lower()


class TestReportRetrieval:
    """Test report retrieval and resolution."""

    def test_get_reason_labels(self, integration_db):
        """Get all valid report reason labels."""
        labels = ReportService.get_reason_labels()

        assert len(labels) > 0
        assert "Offensive" in labels or "offensive" in [
            label.lower() for label in labels
        ]

    def test_has_user_reported_photo(self, integration_db):
        """Check if user has reported a photo."""
        user = AuthService.register_user("mary", "mary@example.com", "password_mary")
        album = AlbumService.create_album("Album 1", user["id"])
        photo = PhotoService.create_photo_record(
            album_id=album["id"], category_id=1, description="Photo 1"
        )

        assert (
            ReportService.has_user_reported(user["id"], photo_id=photo["id"]) is False
        )

        ReportService.submit_report(
            reporter_id=user["id"],
            reason="Offensive",
            photo_id=photo["id"],
        )

        assert ReportService.has_user_reported(user["id"], photo_id=photo["id"]) is True

    def test_resolve_report(self, integration_db):
        """Resolve (delete) a report."""
        user = AuthService.register_user("nancy", "nancy@example.com", "password_nancy")
        album = AlbumService.create_album("Album 1", user["id"])
        photo = PhotoService.create_photo_record(
            album_id=album["id"], category_id=1, description="Photo 1"
        )

        success, _ = ReportService.submit_report(
            reporter_id=user["id"],
            reason="Offensive",
            photo_id=photo["id"],
        )
        assert success is True

        # Get all reports to extract report ID
        all_reports = ReportService.get_all_enriched()
        assert len(all_reports) > 0
        report_id = all_reports[0]["id"]

        # Resolve the report
        result = ReportService.resolve_report(report_id)
        assert result is True

        # Verify it's gone
        all_reports = ReportService.get_all_enriched()
        assert len(all_reports) == 0

    def test_resolve_nonexistent_report(self, integration_db):
        """Resolving nonexistent report returns False."""
        result = ReportService.resolve_report(9999)
        assert result is False

    def test_get_all_enriched_reports(self, integration_db):
        """Get all reports with enriched data."""
        user = AuthService.register_user("oscar", "oscar@example.com", "password_oscar")
        album = AlbumService.create_album("Album 1", user["id"])
        photo = PhotoService.create_photo_record(
            album_id=album["id"], category_id=1, description="Photo 1"
        )

        ReportService.submit_report(
            reporter_id=user["id"],
            reason="Offensive",
            photo_id=photo["id"],
        )

        reports = ReportService.get_all_enriched()
        assert len(reports) > 0
        report = reports[0]
        assert "reason" in report
        assert "reporter_username" in report
        assert "content" in report
        assert "content_creator" in report
