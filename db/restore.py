import csv
from datetime import datetime
from pathlib import Path

from sqlalchemy import Boolean, DateTime, Integer

from db.engine import Base, SessionLocal, engine, init_db
from db.models import (
    AlbumModel,
    AvatarModel,
    CategoryModel,
    CommentModel,
    ContactModel,
    FavoriteModel,
    FollowModel,
    LikeModel,
    NotificationModel,
    NotificationSettingsModel,
    PhotoImageModel,
    PhotoModel,
    RatingModel,
    RoleModel,
    UserModel,
)
from utils.log_utils import log_check, log_issue, log_success

# ── Table restore order (must respect FK dependencies) ────────────────────────
# Mirrors _CSV_ORDER in migration.py but uses actual DB table names (from __table__.name).
_TABLE_ORDER = [
    "roles",
    "categories",
    "users",
    "avatars",
    "albuns",
    "photos",
    "photo_images",
    "ratings",
    "comments",
    "favorites",
    "contacts",
    "notification_settings",
    "notifications",
    "follows",
    "likes",
]

_TABLE_MODEL_MAP = {
    "roles": RoleModel,
    "categories": CategoryModel,
    "users": UserModel,
    "avatars": AvatarModel,
    "albuns": AlbumModel,
    "photos": PhotoModel,
    "photo_images": PhotoImageModel,
    "ratings": RatingModel,
    "comments": CommentModel,
    "favorites": FavoriteModel,
    "contacts": ContactModel,
    "notification_settings": NotificationSettingsModel,
    "notifications": NotificationModel,
    "follows": FollowModel,
    "likes": LikeModel,
}


def _list_backups() -> list[Path]:
    """
    List backup folders in `backups/`, sorted by modified time (newest first).

    Returns:
        list[Path]: List of backup folder paths, sorted newest first. Empty if no backups found.
    """

    backups_root = Path("backups")
    if not backups_root.exists():
        return []
    return sorted(
        [d for d in backups_root.iterdir() if d.is_dir()],
        key=lambda d: d.stat().st_mtime,
        reverse=True,
    )


def _cast(value: str, col) -> object:
    """
    Cast a CSV string value to the appropriate type based on the SQLAlchemy column type.

    Handles Boolean, Integer, DateTime (ISO format), and defaults to string for other types.
    Empty strings or None are treated as NULL (None in Python).

    Parameters:
        value: The string value from the CSV to be cast.
        col: The SQLAlchemy column object, used to determine the target type.

    Returns:
        object: The value cast to the appropriate type for insertion into the database.
    """
    if value == "" or value is None:
        return None
    # Note: for Booleans we expect "True" or "False" as string values in the CSV (consistent with how Python bools are stringified).
    if isinstance(col.type, Boolean):
        return value == "True"
    if isinstance(col.type, Integer):
        return int(value)
    if isinstance(col.type, DateTime):
        try:
            return datetime.fromisoformat(value)
        except Exception:
            return None
    return value


def _restore_table(session, model, csv_file: Path) -> int:
    """
    Restore a single table from its corresponding CSV file.
    Reads the CSV, casts values to the correct types based on the model's column definitions,
    and inserts the rows into the database using the provided session.

    Parameters:
        session: The active SQLAlchemy session to use for database operations.
        model: The SQLAlchemy ORM model class corresponding to the table being restored.
        csv_file: Path to the CSV file containing the backup data for this table.
    Returns:
        int: The number of rows successfully restored from the CSV file.
    """
    cols = {c.name: c for c in model.__table__.columns}
    rows = []
    with csv_file.open("r", encoding="utf-8", newline="") as f:
        for row_dict in csv.DictReader(f):
            kwargs = {
                name: _cast(val, cols[name])
                for name, val in row_dict.items()
                if name in cols
            }
            rows.append(model(**kwargs))
    if rows:
        session.add_all(rows)
        session.flush()
    return len(rows)


def _print_available_backups(backups: list[Path] | None = None) -> None:
    """
    Print available backup folders in `backups/` to the console, sorted by modified time (newest first).
    If `backups` is provided, it is used directly; otherwise, the function lists backups from the filesystem.

    Parameters:
        backups: Optional list of Path objects representing backup folders. If None, the function will list backups from the `backups/` directory.

    Returns:
        None: This function only prints information to the console and does not return any value.
    """

    if backups is None:
        backups = _list_backups()
    if not backups:
        log_check("[restoreDB] No backups found in backups/")
        return
    log_check(f"[restoreDB] Available backups ({len(backups)} found, newest first):")
    for i, folder in enumerate(backups, start=1):
        marker = " ← latest" if i == 1 else ""
        log_check(f"  [{i}] {folder}{marker}")
    log_check("  To restore a specific backup, run:")
    log_check("      python main.py --restoreDB backups/<folder-name>")


def restore_db_from_backup(backup_dir: str | None = None) -> None:
    """
    Restore the database from backup CSV files.

    If `backup_dir` is not provided, the latest folder in `backups/` is used
    automatically. Drops and recreates all tables before inserting, so this
    is a full restore — it replaces whatever is currently in the DB.

    Usage:
        python main.py --restoreDB                              # use latest backup
        python main.py --restoreDB backups/2026-03-20_00h35m35s  # use specific backup

    WARNING: all current DB data will be replaced by the backup contents.
    """
    if backup_dir:
        source = Path(backup_dir)
        if not source.exists():
            log_issue(f"[restoreDB] Backup directory not found: {source}")
            _print_available_backups()
            return
        log_check(f"[restoreDB] Restoring from specified backup: {source}")
    else:
        available = _list_backups()
        if not available:
            log_issue("[restoreDB] Cannot restore — no backups found in backups/")
            return
        # Always use the latest backup!
        _print_available_backups(available)
        source = available[0]
        log_check(f"[restoreDB] No path given — using latest: {source}")

    # Drop everything → clean slate → restore data
    log_check("[restoreDB] Dropping all tables...")
    Base.metadata.drop_all(engine)
    log_check("[restoreDB] Recreating schema...")
    init_db()
    log_success("[restoreDB] Schema ready.")

    total = 0
    try:
        with SessionLocal() as session:
            with session.begin():
                for table_name in _TABLE_ORDER:
                    model = _TABLE_MODEL_MAP.get(table_name)
                    if not model:
                        continue
                    csv_file = source / f"{table_name}.csv"
                    if not csv_file.exists():
                        log_check(
                            f"[restoreDB] {csv_file.name} missing in backup — skipping"
                        )
                        continue
                    count = _restore_table(session, model, csv_file)
                    log_success(f"[restoreDB] Restored {count} rows → {table_name}")
                    total += count
    except Exception as e:
        log_issue(
            "[restoreDB] Failed to restore from backup — DB may be in partial state",
            exc=e,
        )
        return

    log_success(
        f"[restoreDB] Restore complete — {total} total rows restored from {source}"
    )
