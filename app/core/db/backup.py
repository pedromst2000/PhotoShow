import csv
import os
import shutil
from datetime import datetime
from pathlib import Path

from app.core.db.engine import SessionLocal
from app.core.db.models import (
    AlbumModel,
    AvatarModel,
    CategoryModel,
    CommentModel,
    ContactModel,
    FavoriteModel,
    FollowModel,
    LikeModel,
    NotificationModel,
    NotificationTypeModel,
    PhotoImageModel,
    PhotoModel,
    RatingModel,
    RoleModel,
    UserModel,
)
from app.utils.log_utils import log_check, log_issue, log_success

# How many timestamped backup folders to keep. Oldest are pruned when the limit is exceeded.
MAX_BACKUPS = 5


def backup_db_to_csv(output_dir: str | None = None) -> str:
    """
    Export all current rows from tables to CSV files under `backups/<timestamp>/`.

    Args:
        output_dir: Optional path to write backup CSV files. If not provided, defaults to `backups/<timestamp>/`.

    Returns:
        str: Path to the directory containing the backup CSV files.

    WARNING: backups may contain sensitive data (password hashes, emails).
    Do NOT commit backup files to source control — add the backup path to
    your `.gitignore` and store backups securely. If you must skip backups
    set env `SKIP_DB_BACKUP=1`.
    """
    if os.getenv("SKIP_DB_BACKUP") in ("1", "true", "True"):
        log_check("SKIP_DB_BACKUP set; skipping DB backup")
        return ""

    if output_dir:
        out_dir = Path(output_dir)
        out_dir_parent = out_dir.parent
    else:
        out_dir_parent = Path("backups")
        # Human-readable timestamp: 2026-03-20_00h35m35s
        ts = datetime.now().strftime("%Y-%m-%d_%Hh%Mm%Ss")
        out_dir = out_dir_parent / ts

    # Prune oldest backups so we keep at most MAX_BACKUPS − 1 before adding the new one.
    if not output_dir:
        if out_dir_parent.exists():
            existing = sorted(
                [d for d in out_dir_parent.iterdir() if d.is_dir()],
                key=lambda d: d.stat().st_mtime,
                reverse=True,
            )
            # Keep the (MAX_BACKUPS - 1) most recent; delete the rest.
            for old_dir in existing[MAX_BACKUPS - 1 :]:
                try:
                    shutil.rmtree(old_dir)
                except Exception as e:
                    log_issue(
                        "Failed to remove old backup folder", exc=e, path=str(old_dir)
                    )
                    raise
    out_dir.mkdir(parents=True, exist_ok=True)

    models = [
        RoleModel,
        CategoryModel,
        UserModel,
        AvatarModel,
        AlbumModel,
        PhotoModel,
        PhotoImageModel,
        RatingModel,
        CommentModel,
        FavoriteModel,
        ContactModel,
        NotificationTypeModel,
        NotificationModel,
        FollowModel,
        LikeModel,
    ]

    try:
        with SessionLocal() as session:
            for m in models:
                table_name: str = m.__tablename__
                rows = session.query(m).all()
                cols = [c.name for c in m.__table__.columns]
                path = out_dir / f"{table_name}.csv"
                with path.open("w", encoding="utf-8", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(cols)
                    for r in rows:
                        writer.writerow([getattr(r, c) for c in cols])
        log_success(
            f"Database backup written to {out_dir} (keeping last {MAX_BACKUPS} backups)"
        )
        log_check(
            "WARNING: backup files may contain sensitive data — ensure they are ignored in git and stored securely."
        )
        return str(out_dir)
    except Exception as e:
        log_issue("Failed to export DB backup", exc=e)
        raise
