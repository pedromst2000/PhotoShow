"""
Unit tests for app/utils/log_utils.py

Tests logging utility functions — verifying they execute without error,
produce output, and format messages as expected.
"""

import re

from app.utils.log_utils import (
    _format_timestamp,
    _get_caller_info,
    log_check,
    log_exception,
    log_issue,
    log_operation,
    log_success,
)


class TestFormatTimestamp:
    """Tests for _format_timestamp()."""

    def test_returns_string(self):
        """Returns a string."""
        assert isinstance(_format_timestamp(), str)

    def test_matches_time_format(self):
        """Matches HH:MM:SS format."""
        ts = _format_timestamp()
        assert re.match(r"^\d{2}:\d{2}:\d{2}$", ts) is not None

    def test_hours_valid(self):
        """Hour component is 0–23."""
        ts = _format_timestamp()
        hours = int(ts.split(":")[0])
        assert 0 <= hours <= 23

    def test_minutes_valid(self):
        """Minute component is 0–59."""
        ts = _format_timestamp()
        minutes = int(ts.split(":")[1])
        assert 0 <= minutes <= 59

    def test_seconds_valid(self):
        """Seconds component is 0–59."""
        ts = _format_timestamp()
        seconds = int(ts.split(":")[2])
        assert 0 <= seconds <= 59


class TestGetCallerInfo:
    """Tests for _get_caller_info()."""

    def test_returns_tuple_of_three(self):
        """Returns a 3-tuple (filename, lineno, funcname)."""
        result = _get_caller_info()
        assert isinstance(result, tuple)
        assert len(result) == 3

    def test_filename_is_string(self):
        """Filename element is a string."""
        filename, _, _ = _get_caller_info()
        assert isinstance(filename, str)

    def test_lineno_is_int(self):
        """Line number element is an integer."""
        _, lineno, _ = _get_caller_info()
        assert isinstance(lineno, int)

    def test_funcname_is_string(self):
        """Function name element is a string."""
        _, _, funcname = _get_caller_info()
        assert isinstance(funcname, str)


class TestLogCheck:
    """Tests for log_check()."""

    def test_does_not_raise(self, capsys):
        """log_check() does not raise an exception."""
        log_check("checking something")

    def test_output_contains_message(self, capsys):
        """Output contains the provided message."""
        log_check("test check message")
        captured = capsys.readouterr()
        assert "test check message" in captured.out

    def test_output_contains_check_tag(self, capsys):
        """Output contains the [CHECK] tag."""
        log_check("anything")
        captured = capsys.readouterr()
        assert "[CHECK]" in captured.out


class TestLogSuccess:
    """Tests for log_success()."""

    def test_does_not_raise(self, capsys):
        """log_success() does not raise an exception."""
        log_success("operation completed")

    def test_output_contains_message(self, capsys):
        """Output contains the provided message."""
        log_success("success test msg")
        captured = capsys.readouterr()
        assert "success test msg" in captured.out

    def test_output_contains_success_tag(self, capsys):
        """Output contains the [SUCCESS] tag."""
        log_success("anything")
        captured = capsys.readouterr()
        assert "[SUCCESS]" in captured.out


class TestLogIssue:
    """Tests for log_issue()."""

    def test_does_not_raise(self, capsys):
        """log_issue() does not raise an exception."""
        log_issue("something went wrong")

    def test_output_contains_message(self, capsys):
        """Output contains the provided message."""
        log_issue("issue message here")
        captured = capsys.readouterr()
        assert "issue message here" in captured.out

    def test_output_contains_issue_tag(self, capsys):
        """Output contains the [ISSUE] tag."""
        log_issue("anything")
        captured = capsys.readouterr()
        assert "[ISSUE]" in captured.out

    def test_with_exception(self, capsys):
        """log_issue() with an exception includes exception info."""
        exc = ValueError("test error")
        log_issue("operation failed", exc=exc)
        captured = capsys.readouterr()
        assert "ValueError" in captured.out

    def test_with_path(self, capsys):
        """log_issue() with a path includes path info."""
        log_issue("file error", path="/some/path/file.txt")
        captured = capsys.readouterr()
        assert "Path" in captured.out or "file.txt" in captured.out

    def test_with_exception_and_path(self, capsys):
        """log_issue() with both exception and path works."""
        exc = OSError("file not found")
        log_issue("read error", exc=exc, path="/tmp/test.txt")
        captured = capsys.readouterr()
        assert "[ISSUE]" in captured.out


class TestLogOperation:
    """Tests for log_operation()."""

    def test_success_status(self, capsys):
        """Status 'success' prints with [SUCCESS] tag."""
        log_operation("user.register", "success", "user created")
        captured = capsys.readouterr()
        assert "[SUCCESS]" in captured.out

    def test_failed_status(self, capsys):
        """Status 'failed' prints with [FAILED] tag."""
        log_operation("user.login", "failed", "wrong password")
        captured = capsys.readouterr()
        assert "[FAILED]" in captured.out

    def test_validation_error_status(self, capsys):
        """Status 'validation_error' prints with [VALIDATION] tag."""
        log_operation("user.register", "validation_error", "email invalid")
        captured = capsys.readouterr()
        assert "[VALIDATION]" in captured.out

    def test_with_user_id(self, capsys):
        """Includes user_id in output when provided."""
        log_operation("album.create", "success", "album created", user_id=42)
        captured = capsys.readouterr()
        assert "42" in captured.out

    def test_without_details(self, capsys):
        """Works without details argument."""
        log_operation("photo.delete", "success")
        captured = capsys.readouterr()
        assert "photo.delete" in captured.out

    def test_operation_name_in_output(self, capsys):
        """Operation name is present in output."""
        log_operation("comment.add", "success")
        captured = capsys.readouterr()
        assert "comment.add" in captured.out


class TestLogException:
    """Tests for log_exception()."""

    def test_does_not_raise(self, capsys):
        """log_exception() does not raise."""
        exc = RuntimeError("unexpected error")
        log_exception("photo.upload", exc)

    def test_output_contains_exception_tag(self, capsys):
        """Output contains [EXCEPTION] tag."""
        exc = ValueError("bad input")
        log_exception("service.call", exc)
        captured = capsys.readouterr()
        assert "[EXCEPTION]" in captured.out

    def test_output_contains_operation(self, capsys):
        """Output contains the operation name."""
        exc = KeyError("missing")
        log_exception("user.update", exc)
        captured = capsys.readouterr()
        assert "user.update" in captured.out

    def test_with_user_id(self, capsys):
        """Includes user_id in output when provided."""
        exc = PermissionError("denied")
        log_exception("photo.delete", exc, user_id=7)
        captured = capsys.readouterr()
        assert "7" in captured.out

    def test_with_context(self, capsys):
        """Includes context dict in output when provided."""
        exc = TypeError("type mismatch")
        log_exception("album.rename", exc, context={"album_id": 99})
        captured = capsys.readouterr()
        assert "album_id" in captured.out

    def test_exception_type_in_output(self, capsys):
        """Exception type name appears in output."""
        exc = AttributeError("no attribute")
        log_exception("model.query", exc)
        captured = capsys.readouterr()
        assert "AttributeError" in captured.out
