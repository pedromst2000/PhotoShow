"""Unit tests for LikeModel - user-photo relationships."""

from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.db.engine import Base
from app.core.db.models.category import CategoryModel
from app.core.db.models.like import LikeModel
from app.core.db.models.photo import PhotoModel
from app.core.db.models.role import RoleModel
from app.core.db.models.user import UserModel


@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:")
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
def fixtures_user_photo(test_db):
    user = UserModel(
        username="liker", email="like@gmail.com", password="hashed", roleId=2
    )
    test_db.add(user)
    test_db.commit()
    category = CategoryModel(category="Nature")
    test_db.add(category)
    test_db.commit()
    photo = PhotoModel(
        description="Nice photo",
        publishedDate=datetime.now(timezone.utc),
        categoryId=category.id,
    )
    test_db.add(photo)
    test_db.commit()
    return user, photo


class TestLikeModel:
    """Test LikeModel."""

    def test_to_dict(self, test_db, fixtures_user_photo):
        user, photo = fixtures_user_photo
        like = LikeModel(userId=user.id, photoId=photo.id)
        test_db.add(like)
        test_db.commit()

        result = like.to_dict()
        assert result["userId"] == user.id
        assert result["photoId"] == photo.id

    def test_unique_user_photo_like(self, test_db, fixtures_user_photo):
        user, photo = fixtures_user_photo
        like1 = LikeModel(userId=user.id, photoId=photo.id)
        test_db.add(like1)
        test_db.commit()

        like2 = LikeModel(userId=user.id, photoId=photo.id)
        test_db.add(like2)

        with pytest.raises(Exception):  # Unique constraint
            test_db.commit()

    def test_like_method(self, test_db, fixtures_user_photo):
        """Test LikeModel.like() classmethod."""
        user, photo = fixtures_user_photo
        result = LikeModel.like(test_db, user.id, photo.id)
        assert result is not None
        assert result["userId"] == user.id

    def test_has_liked(self, test_db, fixtures_user_photo):
        """Test LikeModel.has_liked() method."""
        user, photo = fixtures_user_photo
        LikeModel.like(test_db, user.id, photo.id)
        test_db.commit()

        is_liked = LikeModel.has_liked(test_db, user.id, photo.id)
        assert is_liked is True
