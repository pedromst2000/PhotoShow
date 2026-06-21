"""
Unit tests for format_timestamp — a pure utility function with no side effects.
"""

from datetime import datetime, timedelta, timezone

from app.utils.date_utils import format_timestamp


def _ago(seconds: int) -> datetime:
    """Return a timezone-aware datetime *seconds* in the past."""
    return datetime.now(timezone.utc) - timedelta(seconds=seconds)


class TestFormatTimestamp:
    def test_none_returns_empty_string(self):
        assert format_timestamp(None) == ""  # type: ignore[arg-type]

    # ── "just now" boundary ────────────────────────────────────────

    def test_zero_seconds_is_just_now(self):
        assert format_timestamp(_ago(0)) == "just now"

    def test_59_seconds_is_just_now(self):
        assert format_timestamp(_ago(59)) == "just now"

    # ── minutes ───────────────────────────────────────────────────

    def test_60_seconds_is_one_minute_ago(self):
        assert format_timestamp(_ago(60)) == "1 minute ago"

    def test_singular_minute_has_no_plural_suffix(self):
        result = format_timestamp(_ago(60))
        assert result == "1 minute ago"  # NOT "1 minutes ago"

    def test_5_minutes_ago(self):
        assert format_timestamp(_ago(5 * 60)) == "5 minutes ago"

    def test_59_minutes_ago(self):
        assert format_timestamp(_ago(59 * 60)) == "59 minutes ago"

    # ── hours ─────────────────────────────────────────────────────

    def test_1_hour_ago(self):
        assert format_timestamp(_ago(3600)) == "1 hour ago"

    def test_singular_hour_has_no_plural_suffix(self):
        result = format_timestamp(_ago(3600))
        assert result == "1 hour ago"  # NOT "1 hours ago"

    def test_7_hours_ago(self):
        assert format_timestamp(_ago(7 * 3600)) == "7 hours ago"

    # ── days ──────────────────────────────────────────────────────

    def test_1_day_ago(self):
        assert format_timestamp(_ago(86400)) == "1 day ago"

    def test_10_days_ago(self):
        assert format_timestamp(_ago(10 * 86400)) == "10 days ago"

    # ── months ────────────────────────────────────────────────────

    def test_1_month_ago(self):
        # 31 days → days=31, months = 31 // 30 = 1
        assert format_timestamp(_ago(31 * 86400)) == "1 month ago"

    def test_3_months_ago(self):
        # 90 days → days=90, months = 90 // 30 = 3
        assert format_timestamp(_ago(90 * 86400)) == "3 months ago"

    # ── years ─────────────────────────────────────────────────────

    def test_1_year_ago(self):
        # 365 days → months=12 → years=1
        assert format_timestamp(_ago(365 * 86400)) == "1 year ago"

    def test_2_years_ago(self):
        assert format_timestamp(_ago(730 * 86400)) == "2 years ago"

    # ── edge cases ────────────────────────────────────────────────

    def test_naive_datetime_is_handled(self):
        """Naive datetime (no tzinfo) should produce a valid string, not raise."""
        naive = datetime.utcnow() - timedelta(minutes=5)
        result = format_timestamp(naive)
        assert isinstance(result, str)
        assert "minute" in result
