import os
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).parent.parent
FILES_DIR = ROOT / "files"
EXCLUDE_DIRS = {"__pycache__", ".git", ".venv", "venv", "node_modules", ".tox"}

_DEFAULT_AVATAR = "app/assets/images/profile_avatars/default_avatar.jpg"


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
