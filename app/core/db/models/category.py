from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, Column, DateTime, Integer, String
from sqlalchemy.orm import Session

from app.core.db.engine import Base


class CategoryModel(Base):
    """
    CategoryModel represents a category in the database.
    """

    __tablename__: str = "categories"

    __table_args__ = (
        CheckConstraint("id > 0 AND id < 10000000", name="ck_categories_id_range"),
        CheckConstraint(
            "length(trim(category)) > 0", name="ck_categories_name_not_empty"
        ),
        CheckConstraint("length(category) <= 25", name="ck_categories_name_maxlen"),
    )

    id: int = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    category: str = Column(String(25), unique=True, nullable=False)
    createdAt: DateTime = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updatedAt: DateTime = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    @property
    def photos(self):
        return self.photos_rel

    def to_dict(self) -> dict:
        """
        Convert the CategoryModel instance to a dictionary.

        Returns:
            dict: A dictionary representation of the CategoryModel instance.
        """
        return {
            "id": self.id,
            "category": self.category,
            "createdAt": self.createdAt,
            "updatedAt": self.updatedAt,
        }

    @classmethod
    def get_all(cls, session: Session) -> list:
        """
        Retrieve all categories from the database.

        Args:
            session: Active SQLAlchemy session.

        Returns:
            list: A list of dictionaries, each representing a category.
        """
        return [c.to_dict() for c in session.query(cls).all()]

    @classmethod
    def create(cls, session: Session, category: str) -> dict:
        """
        Create a new category in the database.

        Args:
            session: Active SQLAlchemy session.
            category (str): The name of the category to create (pre-validated).

        Returns:
            dict: A dictionary representation of the newly created category.
        """
        obj: CategoryModel = cls(category=category)
        session.add(obj)
        session.flush()
        return obj.to_dict()

    @classmethod
    def update(cls, session: Session, category_id: int, new_name: str) -> dict:
        """
        Update an existing category's name.

        Args:
            session: Active SQLAlchemy session.
            category_id (int): The ID of the category to update.
            new_name (str): The new name for the category (pre-validated).

        Returns:
            dict: A dictionary representation of the updated category.

        Raises:
            ValueError: If the category with the given ID does not exist.
        """
        obj: CategoryModel = session.query(cls).filter_by(id=category_id).first()
        if not obj:
            raise ValueError("Category not found")

        obj.category = new_name
        session.flush()
        return obj.to_dict()
