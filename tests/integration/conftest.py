"""
Integration test fixtures.

Each integration test function receives a fresh in-memory SQLite database via
the ``integration_db`` fixture.  The database is fully isolated:

- All ORM tables are created from the project's SQLAlchemy models.
- The three canonical roles (admin, regular, unsigned) are pre-seeded.
- ``SessionLocal`` is patched inside every service module so that service code
  transparently uses the test database instead of the real one.

``monkeypatch`` automatically restores every patched attribute after the test,
so there is no cross-test leakage.
"""

import importlib

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

# All service modules that access the database through SessionLocal
_SERVICE_MODULES = [
    "app.core.services.auth_service",
    "app.core.services.album_service",
    "app.core.services.photo_service",
    "app.core.services.comment_service",
    "app.core.services.category_service",
    "app.core.services.user_service",
    "app.core.services.notification_service",
    "app.core.services.report_service",
    "app.core.services.contact_service",
    "app.core.services.catalog_service",
]


def _ensure_models_registered() -> None:
    """Import every ORM model so Base.metadata knows about all tables."""
    import app.core.db.models.album  # noqa: F401
    import app.core.db.models.avatar  # noqa: F401
    import app.core.db.models.category  # noqa: F401
    import app.core.db.models.comment  # noqa: F401
    import app.core.db.models.contact  # noqa: F401
    import app.core.db.models.favorite  # noqa: F401
    import app.core.db.models.follow  # noqa: F401
    import app.core.db.models.like  # noqa: F401
    import app.core.db.models.notification  # noqa: F401
    import app.core.db.models.notification_types  # noqa: F401
    import app.core.db.models.photo  # noqa: F401
    import app.core.db.models.photo_image  # noqa: F401
    import app.core.db.models.rating  # noqa: F401
    import app.core.db.models.report  # noqa: F401
    import app.core.db.models.report_reason  # noqa: F401
    import app.core.db.models.role  # noqa: F401
    import app.core.db.models.user  # noqa: F401


@pytest.fixture()
def integration_db(monkeypatch):
    """
    Provide a fresh in-memory SQLite database for a single integration test.

    Yields a ``sessionmaker`` bound to the test database.  After the test,
    monkeypatch automatically restores every patched ``SessionLocal``.
    """
    _ensure_models_registered()

    from app.core.db.engine import Base
    from app.core.db.models.role import RoleModel

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )

    @event.listens_for(engine, "connect")
    def _set_fk_pragma(dbapi_con, _record):
        cur = dbapi_con.cursor()
        cur.execute("PRAGMA foreign_keys=ON")
        cur.close()

    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine)

    # Seed required lookup data — roles must exist before any user can be created
    from app.core.db.models.category import CategoryModel
    from app.core.db.models.notification_types import NotificationTypeModel

    session = TestSession()
    session.add(RoleModel(role="admin"))
    session.add(RoleModel(role="regular"))
    session.add(RoleModel(role="unsigned"))

    # Seed default categories for photos
    session.add(CategoryModel(category="Landscape"))
    session.add(CategoryModel(category="Portrait"))
    session.add(CategoryModel(category="Abstract"))
    session.add(CategoryModel(category="Nature"))
    session.add(CategoryModel(category="Urban"))

    # Seed canonical notification types
    for type_key, label in [
        ("comment_on_photo", "commented on your photo"),
        ("like_photo", "liked your photo"),
        ("album_favorited", "added your album to favorites"),
        ("new_follower", "started following you"),
        ("admin_delete_comment", "Your comment was deleted by an admin"),
        ("admin_delete_photo", "Your photo was deleted by an admin"),
    ]:
        session.add(NotificationTypeModel(type=type_key, label=label, isEnabled=True))

    # Seed canonical report reasons
    from app.core.db.models.report_reason import ReportReasonModel

    for reason_label in [
        "Offensive",
        "Spam",
        "Misinformation",
        "Inappropriate",
        "Other",
    ]:
        session.add(ReportReasonModel(label=reason_label))

    session.commit()
    session.close()

    # Patch SessionLocal in every service module so service calls use the test DB
    for mod_name in _SERVICE_MODULES:
        try:
            mod = importlib.import_module(mod_name)
            if hasattr(mod, "SessionLocal"):
                monkeypatch.setattr(mod, "SessionLocal", TestSession)
        except ImportError:
            pass

    # Also patch SessionLocal in app.core.db.engine so test code that imports it uses the test DB
    from app.core.db import engine as db_engine

    monkeypatch.setattr(db_engine, "SessionLocal", TestSession)

    yield TestSession

    engine.dispose()


@pytest.fixture()
def seeded_category(integration_db):
    """
    Return the integer ID of the 'Nature' category already seeded by integration_db.

    Photos require a non-NULL ``categoryId`` — any test that creates a photo
    must request this fixture and pass the returned ID to ``PhotoService.upload``.
    """
    from app.core.db.models.category import CategoryModel

    session = integration_db()
    cat = session.query(CategoryModel).filter_by(category="Nature").first()
    session.close()
    return cat.id
