import sqlite3

import db.migration as migration
from db.backup import backup_db_to_csv
from db.engine import DB_PATH, SessionLocal, engine, init_db
from utils.log_utils import log_check, log_issue, log_success


def _drop_all_tables_raw() -> None:
    """
    Drop every table in the SQLite file using a raw sqlite3 connection.
    Disables FK constraints first so no ordering issues arise from stale
    FK columns that no longer appear in the SQLAlchemy metadata.
    """
    engine.dispose()  # return all pooled connections before we take the file
    con = sqlite3.connect(DB_PATH)
    try:
        cur = con.cursor()
        cur.execute("PRAGMA foreign_keys=OFF")
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cur.fetchall() if not row[0].startswith("sqlite_")]
        for table in tables:
            cur.execute(f'DROP TABLE IF EXISTS "{table}"')
        con.commit()
    finally:
        con.close()


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
        _drop_all_tables_raw()
    except Exception as e:
        log_issue("[resetDB] Failed to drop tables — aborting reset", exc=e)
        return

    log_check("[resetDB] Re-initializing database...")
    init_db()
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
