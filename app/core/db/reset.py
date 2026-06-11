import app.core.db.migration as migration
from app.core.db.backup import backup_db_to_csv
from app.core.db.engine import (
    SessionLocal,
    drop_all_tables_raw,
    engine,
    init_db,
)
from app.core.db.models import AvatarModel, PhotoImageModel
from app.core.services.cloudinary_service import CloudinaryService
from app.utils.log_utils import log_check, log_issue, log_success


def reset_db() -> None:
    """
    Drop ALL tables, recreate them, and re-seed everything from CSV files.
    Also deletes all production Cloudinary assets to keep the database and cloud in sync.
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

    # Delete only PROD folder assets from Cloudinary to keep in sync
    # Keep DEV folder assets (hardcoded seed data) untouched
    log_check(
        "[resetDB] Deleting user-uploaded assets from prod folder to sync DB and cloud..."
    )
    try:
        with SessionLocal() as session:
            # Delete avatars ONLY from prod folder
            avatars = session.query(AvatarModel).all()
            prod_avatars_deleted = 0
            for avatar in avatars:
                if avatar.provider_id and "photo-show/prod/" in avatar.provider_id:
                    CloudinaryService.delete_image(avatar.provider_id)
                    prod_avatars_deleted += 1
            if prod_avatars_deleted > 0:
                log_check(
                    f"  Deleted {prod_avatars_deleted} user avatars from prod folder"
                )

            # Delete photo images ONLY from prod folder
            photo_images = session.query(PhotoImageModel).all()
            prod_photos_deleted = 0
            for photo_image in photo_images:
                if (
                    photo_image.provider_image_id
                    and "photo-show/prod/" in photo_image.provider_image_id
                ):
                    CloudinaryService.delete_image(photo_image.provider_image_id)
                    prod_photos_deleted += 1
            if prod_photos_deleted > 0:
                log_check(
                    f"  Deleted {prod_photos_deleted} user photos from prod folder"
                )

            log_check("  Dev folder assets (hardcoded seed data) kept in cloud ✓")
    except Exception as e:
        log_issue(
            "[resetDB] Error deleting prod folder assets — continuing with reset", exc=e
        )

    log_check("[resetDB] Dropping all tables...")
    try:
        drop_all_tables_raw()
    except Exception as e:
        log_issue("[resetDB] Failed to drop tables — aborting reset", exc=e)
        return

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
