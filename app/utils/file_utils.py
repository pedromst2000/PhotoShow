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
