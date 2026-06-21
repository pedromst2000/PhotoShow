"""
Unit tests for CommentModel.

Covers:
- to_dict() serialization
- Field constraints (text length, required fields)
- Foreign key relationships (photo, user)
- Timestamps
"""

from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.core.db.engine import Base
from app.core.db.models.category import CategoryModel
from app.core.db.models.comment import CommentModel
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
    user = UserModel(
        username="commenter", email="comment@gmail.com", password="hashed", roleId=2
    )
    test_db.add(user)
    test_db.commit()
    return user


@pytest.fixture
def test_photo(test_db):
    category = CategoryModel(category="Test")
    test_db.add(category)
    test_db.commit()
    photo = PhotoModel(
        description="Test photo",
        publishedDate=datetime.now(timezone.utc),
        categoryId=category.id,
    )
    test_db.add(photo)
    test_db.commit()
    return photo


class TestCommentModelToDictSerialization:
    """Test CommentModel.to_dict()."""

    def test_to_dict_includes_all_fields(self, test_db, test_user, test_photo):
        comment = CommentModel(
            comment="Great photo!", authorId=test_user.id, photoId=test_photo.id
        )
        test_db.add(comment)
        test_db.commit()

        result = comment.to_dict()

        assert result["comment"] == "Great photo!"
        assert result["authorId"] == test_user.id
        assert result["photoId"] == test_photo.id


class TestCommentModelConstraints:
    """Test CommentModel constraints."""

    def test_text_required(self, test_db, test_user, test_photo):
        comment = CommentModel(comment="", authorId=test_user.id, photoId=test_photo.id)
        test_db.add(comment)

        with pytest.raises(Exception):
            test_db.commit()

    def test_user_id_must_exist(self, test_db, test_photo):
        comment = CommentModel(comment="Test", authorId=9999, photoId=test_photo.id)
        test_db.add(comment)

        with pytest.raises(Exception):
            test_db.commit()

    def test_photo_id_must_exist(self, test_db, test_user):
        comment = CommentModel(comment="Test", authorId=test_user.id, photoId=9999)
        test_db.add(comment)

        with pytest.raises(Exception):
            test_db.commit()


class TestCommentModelClassMethods:
    """Test CommentModel class methods."""

    def test_get_by_id(self, test_db, test_user, test_photo):
        comment = CommentModel(
            comment="Find me", authorId=test_user.id, photoId=test_photo.id
        )
        test_db.add(comment)
        test_db.commit()

        retrieved = CommentModel.get_by_id(test_db, comment.id)
        assert retrieved is not None


class TestCommentModelDefaults:
    """Test CommentModel defaults."""

    def test_timestamps_set_automatically(self, test_db, test_user, test_photo):
        comment = CommentModel(
            comment="Timestamped", authorId=test_user.id, photoId=test_photo.id
        )
        test_db.add(comment)
        test_db.commit()

        assert comment.createdAt is not None
        assert comment.updatedAt is not None
