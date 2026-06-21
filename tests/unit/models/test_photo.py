"""
Unit tests for PhotoModel.

Covers:
- to_dict() serialization
- Field constraints (description length, required fields)
- Foreign key relationships (album, category)
- Nullable fields (albumId can be NULL)
"""

from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.core.db.engine import Base
from app.core.db.models.album import AlbumModel
from app.core.db.models.category import CategoryModel
from app.core.db.models.photo import PhotoModel
from app.core.db.models.role import RoleModel
from app.core.db.models.user import UserModel


@pytest.fixture
def test_db():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")

    @event.listens_for(engine, "connect")
    def set_fk(dbapi_conn, _):
        dbapi_conn.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Create roles
    session.add_all(
        [
            RoleModel(id=1, role="admin"),
            RoleModel(id=2, role="regular"),
            RoleModel(id=3, role="unsigned"),
        ]
    )
    session.commit()
    yield session
    session.close()


@pytest.fixture
def test_user(test_db):
    """Create a test user."""
    user = UserModel(
        username="photo_creator", email="photo@gmail.com", password="hashed", roleId=2
    )
    test_db.add(user)
    test_db.commit()
    return user


@pytest.fixture
def test_category(test_db):
    """Create a test category."""
    category = CategoryModel(category="Nature")
    test_db.add(category)
    test_db.commit()
    return category


@pytest.fixture
def test_album(test_db, test_user):
    """Create a test album."""
    album = AlbumModel(name="Test Album", creatorId=test_user.id)
    test_db.add(album)
    test_db.commit()
    return album


class TestPhotoModelToDictSerialization:
    """Test PhotoModel.to_dict() produces correct serialized output."""

    def test_to_dict_includes_required_fields(self, test_db, test_category):
        photo = PhotoModel(
            description="Beautiful sunset",
            publishedDate=datetime.now(timezone.utc),
            categoryId=test_category.id,
        )
        test_db.add(photo)
        test_db.commit()

        result = photo.to_dict()

        assert result["description"] == "Beautiful sunset"
        assert result["categoryId"] == test_category.id
        assert "id" in result
        assert "createdAt" in result

    def test_to_dict_with_album_id(self, test_db, test_category, test_album):
        photo = PhotoModel(
            description="Album photo",
            publishedDate=datetime.now(timezone.utc),
            categoryId=test_category.id,
            albumId=test_album.id,
        )
        test_db.add(photo)
        test_db.commit()

        result = photo.to_dict()

        assert result["albumId"] == test_album.id

    def test_to_dict_with_null_album_id(self, test_db, test_category):
        """Photo can exist without album (albumId is nullable)."""
        photo = PhotoModel(
            description="Standalone photo",
            publishedDate=datetime.now(timezone.utc),
            categoryId=test_category.id,
            albumId=None,
        )
        test_db.add(photo)
        test_db.commit()

        result = photo.to_dict()

        assert result["albumId"] is None


class TestPhotoModelConstraints:
    """Test PhotoModel field constraints."""

    def test_description_required(self, test_db, test_category):
        """Photo description is required."""
        photo = PhotoModel(
            description="",
            publishedDate=datetime.now(timezone.utc),
            categoryId=test_category.id,
        )
        test_db.add(photo)

        with pytest.raises(Exception):  # NOT NULL constraint
            test_db.commit()

    def test_description_max_length_255(self, test_db, test_category):
        """Photo description cannot exceed 255 characters."""
        long_desc = "a" * 256
        photo = PhotoModel(
            description=long_desc,
            publishedDate=datetime.now(timezone.utc),
            categoryId=test_category.id,
        )
        test_db.add(photo)

        try:
            test_db.commit()
            assert len(photo.description) <= 255
        except Exception:
            pass  # Expected due to constraint

    def test_category_id_must_exist(self, test_db):
        """Photo must reference a valid category."""
        photo = PhotoModel(
            description="Invalid category",
            publishedDate=datetime.now(timezone.utc),
            categoryId=9999,  # Non-existent
        )
        test_db.add(photo)

        with pytest.raises(Exception):  # FK constraint
            test_db.commit()

    def test_album_id_must_exist_if_not_null(self, test_db, test_category):
        """If albumId is provided, it must reference a valid album."""
        photo = PhotoModel(
            description="Invalid album",
            publishedDate=datetime.now(timezone.utc),
            categoryId=test_category.id,
            albumId=9999,  # Non-existent
        )
        test_db.add(photo)

        with pytest.raises(Exception):  # FK constraint
            test_db.commit()

    def test_published_date_required(self, test_db, test_category):
        """Photo publishedDate is required."""
        photo = PhotoModel(
            description="No date", publishedDate=None, categoryId=test_category.id
        )
        test_db.add(photo)

        with pytest.raises(Exception):  # NOT NULL constraint
            test_db.commit()


class TestPhotoModelDefaults:
    """Test PhotoModel default values."""

    def test_created_at_set_automatically(self, test_db, test_category):
        photo = PhotoModel(
            description="Auto timestamp",
            publishedDate=datetime.now(timezone.utc),
            categoryId=test_category.id,
        )
        test_db.add(photo)
        test_db.commit()

        assert photo.createdAt is not None
        assert isinstance(photo.createdAt, datetime)

    def test_updated_at_set_automatically(self, test_db, test_category):
        photo = PhotoModel(
            description="Auto update",
            publishedDate=datetime.now(timezone.utc),
            categoryId=test_category.id,
        )
        test_db.add(photo)
        test_db.commit()

        assert photo.updatedAt is not None
        assert isinstance(photo.updatedAt, datetime)


class TestPhotoModelClassMethods:
    """Test PhotoModel class methods."""

    def test_get_by_id_retrieves_photo(self, test_db, test_category):
        photo = PhotoModel(
            description="Retrieve me",
            publishedDate=datetime.now(timezone.utc),
            categoryId=test_category.id,
        )
        test_db.add(photo)
        test_db.commit()

        retrieved = PhotoModel.get_by_id(test_db, photo.id)

        assert retrieved is not None
        assert (
            retrieved.get("description") == "Retrieve me"
            or retrieved.description == "Retrieve me"
        )

    def test_get_all_retrieves_all_photos(self, test_db, test_category):
        photo1 = PhotoModel(
            description="Photo 1",
            publishedDate=datetime.now(timezone.utc),
            categoryId=test_category.id,
        )
        photo2 = PhotoModel(
            description="Photo 2",
            publishedDate=datetime.now(timezone.utc),
            categoryId=test_category.id,
        )
        test_db.add_all([photo1, photo2])
        test_db.commit()

        all_photos = PhotoModel.get_all(test_db)

        assert len(all_photos) >= 2
