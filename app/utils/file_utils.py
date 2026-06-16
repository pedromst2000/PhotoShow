import sys
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).parent.parent
FILES_DIR = ROOT / "files"
EXCLUDE_DIRS = {"__pycache__", ".git", ".venv", "venv", "node_modules", ".tox"}


def resolve_resource_path(path: str) -> str:
    """Resolve a project resource path for source and PyInstaller runs.

    Args:
        path: The relative or absolute path to the resource.

    Returns:
        str: The resolved absolute path to the resource.
    """
    resource_path = Path(path)
    if resource_path.is_absolute() and resource_path.exists():
        return str(resource_path)
    if resource_path.exists():
        return str(resource_path)

    project_root = ROOT.parent
    source_candidate = project_root / path
    if source_candidate.exists():
        return str(source_candidate)

    if getattr(sys, "frozen", False):
        bundle_root = Path(sys._MEIPASS)  # type: ignore[attr-defined]
        bundle_candidate = bundle_root / path
        if bundle_candidate.exists():
            return str(bundle_candidate)

    return str(resource_path)


def resolve_avatar_path(avatar: Optional[str]) -> str:
    """
    Return a valid avatar URL/path for display.

    After the Cloudinary migration, avatars are stored as remote URLs.
    This function simply returns the URL as-is, or falls back to the
    configured Cloudinary default avatar URL when the value is empty/None.

    Args:
        avatar: Cloudinary secure_url from the data store (may be None/empty).

    Returns:
        str: A Cloudinary URL, or empty string if no default is configured.
    """
    if avatar and (avatar.startswith("http://") or avatar.startswith("https://")):
        return avatar
    # Fall back to the configured default avatar URL.
    from app.config.cloudinary_config import DEFAULT_AVATAR_URL

    return DEFAULT_AVATAR_URL or ""


def has_imports(filepath: Path) -> bool:
    """Return True if the file contains at least one import statement.

    Args:
        filepath: Path to the Python file to check
    Returns:
        bool: True if the file has import statements, False otherwise
    """
    try:
        with open(filepath, encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if stripped.startswith("import ") or stripped.startswith("from "):
                    return True
    except (OSError, UnicodeDecodeError):
        pass
    return False


def iter_python_files(root: Optional[Path] = None):
    """Recursively yield all .py files, excluding non-source directories.

    Args:
        root: Optional Path to start from (defaults to ROOT)
    """
    if root is None:
        root = ROOT
    for path in sorted(root.rglob("*.py")):
        if any(part in EXCLUDE_DIRS for part in path.parts):
            continue
        yield path


def resolve_image_path(url_or_path: Optional[str]) -> Optional[str]:
    """
    Resolve an image reference for display.

    After the Cloudinary migration, photo images are stored as Cloudinary URLs.
    Remote URLs are returned as-is.  Legacy local paths are resolved against
    the working directory for backwards compatibility during transition.

    Args:
        url_or_path: Cloudinary URL or legacy local path.

    Returns:
        Optional[str]: A displayable URL/path, or None if not resolvable.
    """
    if not url_or_path or not str(url_or_path).strip():
        return None

    s = str(url_or_path)
    if s.startswith("http://") or s.startswith("https://"):
        return s

    resolved_path = resolve_resource_path(s)
    if Path(resolved_path).exists():
        return resolved_path

    # Legacy local path fallback (kept for data-restore compatibility)
    candidate = Path(s)
    if candidate.is_absolute() and candidate.exists():
        return s
    if candidate.exists():
        return s
    prefixed = Path("app") / s
    if prefixed.exists():
        return str(prefixed)

    return None
