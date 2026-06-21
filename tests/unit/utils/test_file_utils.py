"""
Unit tests for app/utils/file_utils.py

Tests pure utility functions for path resolution and file operations.
"""

from pathlib import Path

from app.utils.file_utils import (
    has_imports,
    iter_python_files,
    resolve_image_path,
    resolve_resource_path,
)


class TestResolveResourcePath:
    """Tests for resolve_resource_path()."""

    def test_absolute_existing_path_returned_as_is(self, tmp_path):
        """An absolute path that exists is returned unchanged."""
        f = tmp_path / "resource.png"
        f.write_bytes(b"")
        result = resolve_resource_path(str(f))
        assert result == str(f)

    def test_relative_existing_path_resolved(self, tmp_path, monkeypatch):
        """A relative path that exists from cwd is resolved."""
        f = tmp_path / "myfile.txt"
        f.write_text("hello")
        monkeypatch.chdir(tmp_path)
        result = resolve_resource_path("myfile.txt")
        assert Path(result).name == "myfile.txt"

    def test_nonexistent_path_returns_string(self):
        """Non-existent path still returns a string (not raises)."""
        result = resolve_resource_path("nonexistent_file_xyz.png")
        assert isinstance(result, str)

    def test_empty_string_returns_string(self):
        """Empty string input returns a string."""
        result = resolve_resource_path("")
        assert isinstance(result, str)


class TestResolveAvatarPath:
    """Tests for resolve_avatar_path()."""

    def test_http_url_returned_as_is(self):
        """HTTP URLs are returned unchanged."""
        from app.utils.file_utils import resolve_avatar_path

        url = "http://example.com/avatar.jpg"
        assert resolve_avatar_path(url) == url

    def test_https_url_returned_as_is(self):
        """HTTPS URLs are returned unchanged."""
        from app.utils.file_utils import resolve_avatar_path

        url = "https://res.cloudinary.com/demo/image/upload/avatar.jpg"
        assert resolve_avatar_path(url) == url

    def test_none_returns_fallback(self):
        """None input falls back to default URL (string result)."""
        from app.utils.file_utils import resolve_avatar_path

        result = resolve_avatar_path(None)
        assert isinstance(result, str)

    def test_empty_string_returns_fallback(self):
        """Empty string falls back to default URL (string result)."""
        from app.utils.file_utils import resolve_avatar_path

        result = resolve_avatar_path("")
        assert isinstance(result, str)

    def test_non_url_string_returns_fallback(self):
        """Non-URL string falls back to default URL."""
        from app.utils.file_utils import resolve_avatar_path

        result = resolve_avatar_path("local/path/avatar.jpg")
        assert isinstance(result, str)


class TestHasImports:
    """Tests for has_imports()."""

    def test_file_with_import_statement(self, tmp_path):
        """Returns True for a file with an import statement."""
        f = tmp_path / "module.py"
        f.write_text("import os\n\nx = 1\n")
        assert has_imports(f) is True

    def test_file_with_from_import(self, tmp_path):
        """Returns True for a file with a from...import statement."""
        f = tmp_path / "module.py"
        f.write_text("from pathlib import Path\n")
        assert has_imports(f) is True

    def test_file_without_imports(self, tmp_path):
        """Returns False for a file with no import statements."""
        f = tmp_path / "module.py"
        f.write_text("x = 1\ny = 2\n")
        assert has_imports(f) is False

    def test_empty_file(self, tmp_path):
        """Returns False for an empty file."""
        f = tmp_path / "empty.py"
        f.write_text("")
        assert has_imports(f) is False

    def test_nonexistent_file_returns_false(self, tmp_path):
        """Returns False (does not raise) for a non-existent file."""
        f = tmp_path / "does_not_exist.py"
        assert has_imports(f) is False

    def test_import_in_comment_not_counted(self, tmp_path):
        """A commented-out import is not counted."""
        f = tmp_path / "module.py"
        f.write_text("# import os\nx = 1\n")
        assert has_imports(f) is False


class TestIterPythonFiles:
    """Tests for iter_python_files()."""

    def test_yields_py_files(self, tmp_path):
        """Yields .py files from the given root."""
        (tmp_path / "a.py").write_text("")
        (tmp_path / "b.py").write_text("")
        (tmp_path / "c.txt").write_text("")
        results = list(iter_python_files(tmp_path))
        names = [p.name for p in results]
        assert "a.py" in names
        assert "b.py" in names
        assert "c.txt" not in names

    def test_recurses_into_subdirectories(self, tmp_path):
        """Recursively finds .py files in subdirectories."""
        sub = tmp_path / "sub"
        sub.mkdir()
        (sub / "nested.py").write_text("")
        results = list(iter_python_files(tmp_path))
        assert any(p.name == "nested.py" for p in results)

    def test_excludes_pycache(self, tmp_path):
        """Skips files inside __pycache__ directories."""
        cache = tmp_path / "__pycache__"
        cache.mkdir()
        (cache / "cached.py").write_text("")
        (tmp_path / "real.py").write_text("")
        results = list(iter_python_files(tmp_path))
        names = [p.name for p in results]
        assert "cached.py" not in names
        assert "real.py" in names

    def test_empty_directory(self, tmp_path):
        """Returns empty iterator for directory with no .py files."""
        (tmp_path / "readme.txt").write_text("")
        results = list(iter_python_files(tmp_path))
        assert results == []


class TestResolveImagePath:
    """Tests for resolve_image_path()."""

    def test_http_url_returned_as_is(self):
        """HTTP URLs are returned unchanged."""
        url = "http://example.com/photo.jpg"
        assert resolve_image_path(url) == url

    def test_https_url_returned_as_is(self):
        """HTTPS (Cloudinary) URLs are returned unchanged."""
        url = "https://res.cloudinary.com/demo/image/upload/photo.jpg"
        assert resolve_image_path(url) == url

    def test_none_returns_none(self):
        """None input returns None."""
        assert resolve_image_path(None) is None

    def test_empty_string_returns_none(self):
        """Empty string returns None."""
        assert resolve_image_path("") is None

    def test_whitespace_only_returns_none(self):
        """Whitespace-only string returns None."""
        assert resolve_image_path("   ") is None

    def test_nonexistent_local_path_returns_none(self):
        """A non-existent local path returns None."""
        result = resolve_image_path("nonexistent/path/photo.jpg")
        assert result is None

    def test_existing_absolute_path(self, tmp_path):
        """An existing absolute file path is returned."""
        f = tmp_path / "photo.jpg"
        f.write_bytes(b"img")
        result = resolve_image_path(str(f))
        assert result == str(f)
