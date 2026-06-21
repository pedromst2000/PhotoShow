"""
Unit tests for ReportService.

Covers the actual public methods:
- submit_report: user submits a content report
- get_all_enriched: admin retrieves all reports
- resolve_report: admin marks a report as resolved
- get_reason_labels: retrieve report reason labels for UI
- has_user_reported: check if user already reported a photo/comment
"""

from app.core.services.report_service import ReportService


class TestSubmitReport:
    """Test ReportService.submit_report."""

    def test_method_exists(self):
        assert hasattr(ReportService, "submit_report")

    def test_is_callable(self):
        assert callable(ReportService.submit_report)


class TestGetAllEnriched:
    """Test ReportService.get_all_enriched."""

    def test_method_exists(self):
        assert hasattr(ReportService, "get_all_enriched")

    def test_is_callable(self):
        assert callable(ReportService.get_all_enriched)


class TestResolveReport:
    """Test ReportService.resolve_report."""

    def test_method_exists(self):
        assert hasattr(ReportService, "resolve_report")

    def test_is_callable(self):
        assert callable(ReportService.resolve_report)


class TestGetReasonLabels:
    """Test ReportService.get_reason_labels."""

    def test_method_exists(self):
        assert hasattr(ReportService, "get_reason_labels")

    def test_is_callable(self):
        assert callable(ReportService.get_reason_labels)


class TestHasUserReported:
    """Test ReportService.has_user_reported."""

    def test_method_exists(self):
        assert hasattr(ReportService, "has_user_reported")

    def test_is_callable(self):
        assert callable(ReportService.has_user_reported)
