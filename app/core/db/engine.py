import sqlite3
import threading

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import NullPool

from app.utils.log_utils import log_issue, log_success

# SQLite database file at project root
DATABASE_URL: str = "sqlite:///photoshow.db"
DB_PATH: str = "photoshow.db"

# NullPool ensures each `with SessionLocal()` block gets a fresh connection that is
# fully released on exit — no pooled connections retain implicit SQLite locks.
# timeout=5: wait up to 5 seconds for any lock to clear (needed for PRAGMA operations).
engine = create_engine(
    DATABASE_URL,
    echo=False,
    poolclass=NullPool,
    connect_args={"check_same_thread": False, "timeout": 5},
)


# SQLite pragmas applied on every new connection
@event.listens_for(engine, "connect")
def _set_sqlite_pragma(dbapi_connection, _connection_record):
    """Apply SQLite pragmas on each new connection (called by SQLAlchemy event system)."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


SessionLocal: sessionmaker = sessionmaker(
    bind=engine, autocommit=False, autoflush=False
)


class Base(DeclarativeBase):
    pass  # Base class for ORM models to inherit from (provides metadata and common functionality)


def _setup_wal_mode() -> None:
    """
    Enable WAL mode synchronously. Must run before app logic touches the database.
    WAL persists once enabled, so subsequent calls are instant (no-op).
    This is critical for preventing "database is locked" errors in concurrent access.
    """

    db_file = DATABASE_URL.replace("sqlite:///", "")
    try:
        con = sqlite3.connect(db_file, timeout=5)
        cur = con.cursor()

        # Check current mode
        cur.execute("PRAGMA journal_mode")
        mode = cur.fetchone()[0]

        # If already WAL, return early (no-op on subsequent runs)
        if mode.upper() == "WAL":
            con.close()
            return

        # First-time setup: enable WAL (takes ~5.5s on fresh database)
        cur.execute("PRAGMA journal_mode=WAL")
        con.commit()  # Critical: must commit to persist WAL mode
        cur.close()
        con.close()
        log_success("WAL mode enabled for database")
    except Exception as e:
        log_issue("Failed to enable WAL mode (will use fallback lock handling)", exc=e)


def _setup_wal_mode_async() -> None:
    """
    Enable WAL mode asynchronously (after app startup).
    WAL persists once enabled, so this doesn't need to block initialization.
    """

    def _enable_wal():
        try:
            db_file = DATABASE_URL.replace("sqlite:///", "")
            con = sqlite3.connect(db_file)
            con.execute("PRAGMA journal_mode=WAL")
            con.close()
        except Exception:
            pass

    # Run in background thread to not block startup
    thread = threading.Thread(target=_enable_wal, daemon=True)
    thread.start()


def _apply_schema_migrations() -> None:
    """
    Add any columns present in ORM models but missing in the live database.
    Uses raw sqlite3 to bypass SQLAlchemy transaction management for DDL.
    Called automatically by init_db() after create_all().
    Optimized: skips I/O if no migrations needed.
    """

    db_file = DATABASE_URL.replace("sqlite:///", "")
    con = sqlite3.connect(db_file, timeout=5)  # Add timeout for lock handling
    cur = con.cursor()
    migrations_needed = False

    try:
        # First pass: check if ANY migrations are needed
        for table in Base.metadata.sorted_tables:
            try:
                cur.execute(f'PRAGMA table_info("{table.name}")')
                rows = cur.fetchall()
                if not rows:  # table doesn't exist — create_all will handle it
                    continue
                existing_cols = {row[1] for row in rows}
                for col in table.columns:
                    if col.name not in existing_cols:
                        migrations_needed = True
                        break
                if migrations_needed:
                    break
            except sqlite3.OperationalError:
                # Table doesn't exist — create_all will handle it
                continue

        # If no migrations needed, return early (avoid slow PRAGMA iteration)
        if not migrations_needed:
            return

        # Second pass: apply migrations
        for table in Base.metadata.sorted_tables:
            try:
                cur.execute(f'PRAGMA table_info("{table.name}")')
                rows = cur.fetchall()
                if not rows:
                    continue
                existing_cols = {row[1] for row in rows}
                for col in table.columns:
                    if col.name in existing_cols:
                        continue
                    col_type = col.type.compile(dialect=engine.dialect)
                    try:
                        cur.execute(
                            f'ALTER TABLE "{table.name}" ADD COLUMN "{col.name}" {col_type}'
                        )
                        con.commit()
                        log_success(
                            f"Schema migration: added '{col.name}' to table '{table.name}'"
                        )
                    except sqlite3.OperationalError as e:
                        log_issue(
                            f"Schema migration failed: could not add '{col.name}' to '{table.name}'",
                            exc=e,
                            path=db_file,
                        )
            except sqlite3.OperationalError:
                continue
    finally:
        con.close()


def init_db() -> None:
    """Create all tables registered with Base if they don't exist yet,
    then apply any missing column migrations to existing tables.
    Call this after importing db.models so all ORM classes are registered."""
    Base.metadata.create_all(engine)
    _setup_wal_mode()  # Critical: set up WAL before any user code runs
    _apply_schema_migrations()


def check_db() -> tuple:
    """
    Quick verification that the database connection works and the file exists.
    Since init_db() already verified schema, this is just a sanity check.

    Returns:
        Tuple of (ok: bool, message: str)
    """
    try:
        # Fast check: try a simple query (no expensive schema reflection)
        with engine.connect() as conn:
            from sqlalchemy import text

            conn.execute(text("SELECT 1"))
        return True, "Database OK"
    except Exception as e:
        return False, f"Database connection failed: {e}"


def drop_all_tables_raw() -> None:
    """
    Drop every table in the SQLite database using a raw sqlite3 connection.
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
        # Explicitly flush WAL and checkpoint to ensure changes are persisted to disk
        con.execute("PRAGMA wal_checkpoint(RESTART)")
        con.close()
    finally:
        con.close()

    # Critical: dispose engine again after dropping tables to clear any cached connections
    # This ensures the next SessionLocal() gets a fresh connection that reads the new schema
    engine.dispose()
