from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.utils.log_utils import log_issue, log_success

# SQLite database file at project root
DATABASE_URL: str = "sqlite:///photoshow.db"
DB_PATH: str = "photoshow.db"

engine = create_engine(DATABASE_URL, echo=False)


# Enforce foreign key constraints on every SQLite connection (automatically called by SQLAlchemy)
@event.listens_for(engine, "connect")
def _set_sqlite_pragma(dbapi_connection, _connection_record):
    """Enable SQLite foreign key constraints on each new connection (called by SQLAlchemy event system)."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


SessionLocal: sessionmaker = sessionmaker(
    bind=engine, autocommit=False, autoflush=False
)


class Base(DeclarativeBase):
    pass


def _apply_schema_migrations() -> None:
    """
    Add any columns present in ORM models but missing in the live database.
    Uses raw sqlite3 to bypass SQLAlchemy transaction management for DDL.
    Called automatically by init_db() after create_all().
    """
    import sqlite3

    db_file = DATABASE_URL.replace("sqlite:///", "")
    con = sqlite3.connect(db_file)
    cur = con.cursor()
    try:
        for table in Base.metadata.sorted_tables:
            cur.execute(f'PRAGMA table_info("{table.name}")')
            rows = cur.fetchall()
            if not rows:  # table doesn't exist yet — create_all will handle it
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
    finally:
        con.close()


def init_db() -> None:
    """Create all tables registered with Base if they don't exist yet,
    then apply any missing column migrations to existing tables.
    Call this after importing db.models so all ORM classes are registered."""
    Base.metadata.create_all(engine)
    _apply_schema_migrations()


def check_db() -> tuple:
    """
    Verify the database connection and check that all expected tables exist.

    Returns:
        Tuple of (ok: bool, message: str)
    """
    try:
        with engine.connect() as conn:
            from sqlalchemy import inspect, text

            conn.execute(text("SELECT 1"))
            inspector = inspect(engine)
            existing = set(inspector.get_table_names())
            expected = {
                "users",
                "roles",
                "avatars",
                "categories",
                "albuns",
                "photos",
                "photo_image",
                "ratings",
                "comments",
                "favorites",
                "contacts",
                "notifications",
                "notification_types",
                "follows",
                "likes",
            }
            missing = expected - existing
            if missing:
                return False, f"Missing tables: {', '.join(sorted(missing))}"
            return True, "Database OK"
    except Exception as e:
        return False, f"Database connection failed: {e}"
