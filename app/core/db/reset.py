import app.core.db.migration as migration
from app.core.db.backup import backup_db_to_csv
from app.core.db.engine import (
    SessionLocal,
    drop_all_tables_raw,
    engine,
    init_db,
)
from app.utils.file_utils import clear_latest_media
from app.utils.log_utils import log_check, log_issue, log_success


def reset_db() -> None:
    """
    Drop ALL tables, recreate them, and re-seed everything from CSV files.
    This function lives in `db.reset` so migration.py stays focused on
    CSV->ORM migration logic.
    """
    # Backup first (may raise) — caller can set SKIP_DB_BACKUP to skip.
    log_check("[resetDB] Creating backup before drop...")
    try:
        backup_db_to_csv()
    except Exception as e:
        log_issue("Failed to create DB backup — aborting reset", exc=e)
        return

    log_check("[resetDB] Dropping all tables...")
    try:
        drop_all_tables_raw()
    except Exception as e:
        log_issue("[resetDB] Failed to drop tables — aborting reset", exc=e)
        return

    log_check("[resetDB] Clearing latest media files...")
    clear_latest_media()
    log_success("[resetDB] Latest media cleared.")

    log_check("[resetDB] Re-initializing database...")
    init_db()
    # Critical: dispose engine after init_db() so next SessionLocal() uses fresh connections
    # This ensures we read the newly created tables, not stale schema from memory
    engine.dispose()
    log_success("[resetDB] Tables recreated.")

    log_check("[resetDB] Seeding from CSV files...")
    data = migration._read_all()

    try:
        with SessionLocal() as session:
            with session.begin():
                for key in migration._CSV_ORDER:
                    objs = data.get(key, [])
                    if objs:
                        session.add_all(objs)
                    session.flush()
    except Exception as e:
        log_issue("[resetDB] Failed to seed DB from CSV files", exc=e)
        return

    log_success("[resetDB] Database reset and seeded successfully.")
