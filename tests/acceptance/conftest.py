"""
Shared pytest fixtures for functional and acceptance tests.

Provides a fresh in-memory SQLite database per test, with all ORM tables created
and the three canonical roles pre-seeded.  ``SessionLocal`` is monkeypatched in
every service module so service code transparently uses the test database.
"""

import importlib

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

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
    Provide a fresh in-memory SQLite database for a single test.

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

    session = TestSession()
    session.add(RoleModel(role="admin"))
    session.add(RoleModel(role="regular"))
    session.add(RoleModel(role="unsigned"))
    session.commit()
    session.close()

    for mod_name in _SERVICE_MODULES:
        try:
            mod = importlib.import_module(mod_name)
            if hasattr(mod, "SessionLocal"):
                monkeypatch.setattr(mod, "SessionLocal", TestSession)
        except ImportError:
            pass

    yield TestSession


@pytest.fixture()
def seeded_category(integration_db):
    """Seed a single 'Nature' category and return its integer ID.

    Photos require a non-NULL categoryId with a valid FK — any test that
    creates a photo record must request this fixture.
    """
    from app.core.db.models.category import CategoryModel

    session = integration_db()
    cat = CategoryModel(category="Nature")
    session.add(cat)
    session.commit()
    cat_id = cat.id
    session.close()
    return cat_id
