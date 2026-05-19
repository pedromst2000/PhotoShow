import os
import shutil
import time
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).parent.parent
FILES_DIR = ROOT / "files"
EXCLUDE_DIRS = {"__pycache__", ".git", ".venv", "venv", "node_modules", ".tox"}

_DEFAULT_AVATAR = (
    "app/assets/images/local_cloud_media/default/profile_avatars/default_avatar.jpg"
)

# NOTE: THE PATHS WILL BE REPLACED BY CDN PATHS IN PRODUCTION, BUT THIS LAYER OF ABSOLUTE PATH RESOLUTION AND FILE MANAGEMENT

LATEST_AVATARS_DIR = Path("app/assets/images/local_cloud_media/latest/profile_avatars")
LATEST_PHOTOS_DIR = Path("app/assets/images/local_cloud_media/latest/photos_gallery")

_LATEST_MEDIA_DIRS = [LATEST_AVATARS_DIR, LATEST_PHOTOS_DIR]

_LATEST_PREFIX = str(Path("app/assets/images/local_cloud_media/latest"))


def clear_latest_media() -> None:
    """
    Delete all files inside the latest media subdirectories.

    Called on database reset/restore so that runtime-uploaded content (new
    avatars, new photos) is wiped in sync with the DB rollback.  The
    directories themselves are preserved so the application can still write
    to them without re-creating them.
    """
    for folder in _LATEST_MEDIA_DIRS:
        if not folder.exists():
            continue
        for item in folder.iterdir():
            if item.is_file():
                item.unlink(missing_ok=True)
            elif item.is_dir():
                shutil.rmtree(item, ignore_errors=True)


def replace_avatar_in_latest(username: str, source_path: str) -> str:
    """Copy a new avatar for *username* into the latest tier, removing any
    previous avatar for that user regardless of extension.

    Args:
        username: The user's username (used to build the avatar filename stem).
        source_path: Absolute path to the chosen source image.

    Returns:
        str: The stored relative path written to the database,
             e.g. ``"assets/images/local_cloud_media/latest/profile_avatars/alice_avatar.jpg"``.

    Raises:
        ValueError: If the file extension is not supported.
        OSError: If the file cannot be copied.
    """
    _, ext = os.path.splitext(source_path)
    if ext.lower() not in {".png", ".jpg", ".jpeg"}:
        raise ValueError(f"Unsupported image format: {ext}")

    LATEST_AVATARS_DIR.mkdir(parents=True, exist_ok=True)

    # Remove all existing avatars for this user (any extension).
    stem = f"{username}_avatar"
    for old_file in LATEST_AVATARS_DIR.glob(f"{stem}.*"):
        old_file.unlink(missing_ok=True)

    new_filename = f"{stem}{ext.lower()}"
    destination = LATEST_AVATARS_DIR / new_filename
    shutil.copy2(source_path, destination)

    return f"assets/images/local_cloud_media/latest/profile_avatars/{new_filename}"


def copy_to_latest_photos(source_path: str) -> str:
    """Copy a photo from *source_path* into the latest tier with a unique name.

    The generated filename uses a millisecond timestamp so concurrent uploads
    from the same session don't collide.

    Args:
        source_path: Absolute path to the source image chosen by the user.

    Returns:
        str: The stored relative path written to the database,
             e.g. ``"app/assets/images/local_cloud_media/latest/photos_gallery/photo_1716123456789.jpg"``.

    Raises:
        ValueError: If the file extension is not supported.
        OSError: If the file cannot be copied.
    """
    _, ext = os.path.splitext(source_path)
    if ext.lower() not in {".png", ".jpg", ".jpeg"}:
        raise ValueError(f"Unsupported image format: {ext}")

    LATEST_PHOTOS_DIR.mkdir(parents=True, exist_ok=True)

    timestamp_ms = int(time.time() * 1000)
    new_filename = f"photo_{timestamp_ms}{ext.lower()}"
    destination = LATEST_PHOTOS_DIR / new_filename
    shutil.copy2(source_path, destination)

    return f"app/assets/images/local_cloud_media/latest/photos_gallery/{new_filename}"


def delete_from_latest(stored_path: str) -> None:
    """Delete a media file from the latest tier if the stored path points there.

    Silently ignores paths that belong to the default tier or that no longer
    exist on disk — deleting a non-existent file is not an error.

    Args:
        stored_path: The path as stored in the database.
    """
    if not stored_path:
        return

    # Normalise separators for comparison.
    normalised = stored_path.replace("\\", "/")
    if "local_cloud_media/latest/" not in normalised:
        return  # Default-tier file — never touch it.

    # Try the path as-is, then with the "app/" prefix stripped/added.
    candidates = [Path(stored_path), Path("app") / stored_path]
    for candidate in candidates:
        if candidate.exists():
            candidate.unlink(missing_ok=True)
            return


def resolve_avatar_path(avatar: Optional[str]) -> str:
    """Resolve an avatar path to one that actually exists on disk.

    Tries in order:
    1. The path as-is.
    2. The path prefixed with "app/" (for legacy paths stored without the prefix).
    3. The default avatar fallback.

    Args:
        avatar: Raw avatar path from the data store (may be None or use legacy prefix).

    Returns:
        str: A valid file path that exists, or the default avatar path.
    """
    if avatar:
        if os.path.exists(avatar):
            return avatar
        prefixed = os.path.join("app", avatar)
        if os.path.exists(prefixed):
            return prefixed
    return _DEFAULT_AVATAR


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


def resolve_image_path(relative_or_absolute_path: Optional[str]) -> Optional[str]:
    """
    Resolve an image path to one that actually exists on disk.

    Resolution strategy (in order):
    1. If the path is absolute and exists, return it.
    2. If the path exists as given (relative to the current working directory), return it.
    3. If prefixing the path with "app/" exists (legacy values), return that.
    4. Try resolving the path relative to the application's `ROOT` (app/).

    Args:
        relative_or_absolute_path: The image path to resolve (may be relative or absolute).
    Returns:
        Optional[str]: A valid file path that exists, or None if no valid path is found.
    """
    if not relative_or_absolute_path or not str(relative_or_absolute_path).strip():
        return None

    candidate = Path(relative_or_absolute_path)
    # Absolute path provided
    if candidate.is_absolute():
        return str(candidate) if candidate.exists() else None

    # As given (relative to cwd)
    if candidate.exists():
        return str(candidate)

    # Legacy prefix (some stored paths omit/contain the 'app/' prefix inconsistently)
    prefixed = Path("app") / relative_or_absolute_path
    if prefixed.exists():
        return str(prefixed)

    # Resolve relative to the known project ROOT (app/)
    resolved = ROOT / relative_or_absolute_path
    if resolved.exists():
        return str(resolved)

    return None
