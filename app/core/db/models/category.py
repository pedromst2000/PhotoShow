from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, Column, DateTime, Integer, String

from app.core.db.engine import Base, SessionLocal


class CategoryModel(Base):
    """
    CategoryModel represents a category in the database, with methods to create, retrieve, and delete categories.
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
    def get_all(cls) -> list:
        """
        Retrieve all categories from the database and return them as a list of dictionaries.

        Returns:
            list: A list of dictionaries, each representing a category.
        """
        with SessionLocal() as session:
            return [c.to_dict() for c in session.query(cls).all()]

    @classmethod
    def create(cls, category: str) -> dict:
        """
        Create a new category in the database.

        Args:
            category (str): The name of the category to create.

        Returns:
            dict: A dictionary representation of the newly created category.
        """
        # application-level validation: trim and ensure non-empty and within length
        trimmed = category.strip() if category is not None else ""
        if not trimmed:
            raise ValueError("Category name must not be empty")
        if len(trimmed) > 25:
            raise ValueError("Category name must be at most 25 characters")

        with SessionLocal() as session:
            with session.begin():
                obj: CategoryModel = cls(category=trimmed)
                session.add(obj)
                session.flush()
                return obj.to_dict()

    @classmethod
    def delete(cls, category: str) -> None:
        """
        Delete a category from the database by name.

        Args:
            category (str): The name of the category to delete.
        """
        trimmed = category.strip() if category is not None else ""
        if not trimmed:
            return
        with SessionLocal() as session:
            with session.begin():
                session.query(cls).filter_by(category=trimmed).delete()
