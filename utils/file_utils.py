from pathlib import Path

ROOT = Path(__file__).parent.parent
FILES_DIR = ROOT / "files"
EXCLUDE_DIRS = {"__pycache__", ".git", ".venv", "venv", "node_modules", ".tox"}


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


def iter_python_files(root: Path = None):
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
