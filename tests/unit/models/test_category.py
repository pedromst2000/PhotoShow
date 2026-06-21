"""Unit tests for CategoryModel - name validation, uniqueness, to_dict()."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.db.engine import Base
from app.core.db.models.category import CategoryModel


@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


class TestCategoryModel:
    """Test CategoryModel."""

    def test_to_dict(self, test_db):
        category = CategoryModel(category="Nature")
        test_db.add(category)
        test_db.commit()

        result = category.to_dict()
        assert result["category"] == "Nature"

    def test_name_must_be_unique(self, test_db):
        cat1 = CategoryModel(category="Duplicate")
        cat2 = CategoryModel(category="Duplicate")
        test_db.add(cat1)
        test_db.commit()
        test_db.add(cat2)

        with pytest.raises(Exception):
            test_db.commit()

    def test_name_required(self, test_db):
        category = CategoryModel(category="")
        test_db.add(category)

        with pytest.raises(Exception):
            test_db.commit()

    def test_get_by_id(self, test_db):
        category = CategoryModel(category="Landscapes")
        test_db.add(category)
        test_db.commit()

        retrieved = CategoryModel.get_by_id(test_db, category.id)
        assert retrieved is not None
