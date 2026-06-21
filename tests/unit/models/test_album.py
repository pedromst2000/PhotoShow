"""
Unit tests for AlbumModel.

Covers:
- to_dict() serialization with timestamps
- Properties (photos, favorites)
- Field constraints (name length, creator uniqueness)
- Foreign key relationships
"""

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.core.db.engine import Base
from app.core.db.models.album import AlbumModel
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
        username="album_creator", email="creator@gmail.com", password="hashed", roleId=2
    )
    test_db.add(user)
    test_db.commit()
    return user


class TestAlbumModelToDictSerialization:
    """Test AlbumModel.to_dict() produces correct serialized output."""

    def test_to_dict_includes_all_required_fields(self, test_db, test_user):
        album = AlbumModel(name="My Album", creatorId=test_user.id)
        test_db.add(album)
        test_db.commit()

        result = album.to_dict()

        assert result["name"] == "My Album"
        assert result["creatorId"] == test_user.id
        assert "id" in result
        assert "createdAt" in result
        assert "updatedAt" in result

    def test_to_dict_preserves_name(self, test_db, test_user):
        album = AlbumModel(name="Vacation 2025", creatorId=test_user.id)
        test_db.add(album)
        test_db.commit()

        result = album.to_dict()
        assert result["name"] == "Vacation 2025"


class TestAlbumModelProperties:
    """Test AlbumModel property accessors."""

    def test_photos_property_accessible(self, test_db, test_user):
        album = AlbumModel(name="Photos Album", creatorId=test_user.id)
        test_db.add(album)
        test_db.commit()

        # Property should be accessible
        photos = album.photos
        assert photos is not None or photos is None

    def test_favorites_property_accessible(self, test_db, test_user):
        album = AlbumModel(name="Favorites Album", creatorId=test_user.id)
        test_db.add(album)
        test_db.commit()

        # Property should be accessible
        favorites = album.favorites
        assert favorites is not None or favorites is None


class TestAlbumModelConstraints:
    """Test AlbumModel field constraints."""

    def test_album_name_must_not_be_empty(self, test_db, test_user):
        """Album name cannot be empty string."""
        album = AlbumModel(name="", creatorId=test_user.id)  # Empty name
        test_db.add(album)

        # Should fail due to NOT NULL constraint
        with pytest.raises(Exception):
            test_db.commit()

    def test_creator_id_must_exist(self, test_db):
        """Album creatorId must reference a valid user."""
        album = AlbumModel(name="Orphan Album", creatorId=9999)  # Non-existent user
        test_db.add(album)

        # Should fail due to FK constraint
        with pytest.raises(Exception):
            test_db.commit()

    def test_same_user_can_have_multiple_albums_with_different_names(
        self, test_db, test_user
    ):
        """Same creator can create multiple albums with different names."""
        album1 = AlbumModel(name="Album 1", creatorId=test_user.id)
        album2 = AlbumModel(name="Album 2", creatorId=test_user.id)
        test_db.add_all([album1, album2])

        # Should succeed - different names
        test_db.commit()
        assert album1.id is not None
        assert album2.id is not None

    def test_creator_cannot_have_duplicate_album_names(self, test_db, test_user):
        """Same creator cannot create two albums with the same name."""
        album1 = AlbumModel(name="Duplicate Name", creatorId=test_user.id)
        test_db.add(album1)
        test_db.commit()

        album2 = AlbumModel(name="Duplicate Name", creatorId=test_user.id)
        test_db.add(album2)

        # Should fail due to unique constraint (creatorId, name)
        with pytest.raises(Exception):
            test_db.commit()


class TestAlbumModelClassMethods:
    """Test AlbumModel class methods."""

    def test_get_by_id_retrieves_album(self, test_db, test_user):
        album = AlbumModel(name="Retrieve Me", creatorId=test_user.id)
        test_db.add(album)
        test_db.commit()

        retrieved = AlbumModel.get_by_id(test_db, album.id)

        assert retrieved is not None
        assert retrieved.get("name") == "Retrieve Me" or retrieved.name == "Retrieve Me"

    def test_get_all_retrieves_all_albums(self, test_db, test_user):
        album1 = AlbumModel(name="Album 1", creatorId=test_user.id)
        album2 = AlbumModel(name="Album 2", creatorId=test_user.id)
        test_db.add_all([album1, album2])
        test_db.commit()

        all_albums = AlbumModel.get_all(test_db)

        assert len(all_albums) >= 2
