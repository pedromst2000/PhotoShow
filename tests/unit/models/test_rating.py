"""Unit tests for RatingModel - photo ratings."""

from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.db.engine import Base
from app.core.db.models.category import CategoryModel
from app.core.db.models.photo import PhotoModel
from app.core.db.models.rating import RatingModel
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
        username="rater", email="rate@gmail.com", password="hashed", roleId=2
    )
    test_db.add(user)
    test_db.commit()
    category = CategoryModel(category="Nature")
    test_db.add(category)
    test_db.commit()
    photo = PhotoModel(
        description="Photo",
        publishedDate=datetime.now(timezone.utc),
        categoryId=category.id,
    )
    test_db.add(photo)
    test_db.commit()
    return user, photo


class TestRatingModel:
    """Test RatingModel."""

    def test_to_dict(self, test_db, fixtures_user_photo):
        user, photo = fixtures_user_photo
        rating = RatingModel(userId=user.id, photoId=photo.id, rating=5)
        test_db.add(rating)
        test_db.commit()

        result = rating.to_dict()
        assert result["userId"] == user.id
        assert result["photoId"] == photo.id
        assert result["rating"] == 5

    def test_rating_value_range(self, test_db, fixtures_user_photo):
        user, photo = fixtures_user_photo
        rating = RatingModel(userId=user.id, photoId=photo.id, rating=1)
        test_db.add(rating)
        test_db.commit()
        assert rating.rating == 1

    def test_unique_user_photo_rating(self, test_db, fixtures_user_photo):
        user, photo = fixtures_user_photo
        rating1 = RatingModel(userId=user.id, photoId=photo.id, rating=4)
        test_db.add(rating1)
        test_db.commit()

        rating2 = RatingModel(userId=user.id, photoId=photo.id, rating=5)
        test_db.add(rating2)

        with pytest.raises(Exception):
            test_db.commit()

    def test_create_method(self, test_db, fixtures_user_photo):
        """Test RatingModel.create() method."""
        user, photo = fixtures_user_photo
        result = RatingModel.create(test_db, user.id, photo.id, 3)
        test_db.commit()
        assert result is not None
        assert result["rating"] == 3
