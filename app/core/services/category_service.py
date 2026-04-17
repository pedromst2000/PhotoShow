from typing import Tuple

from app.core.db.engine import SessionLocal
from app.core.db.models.category import CategoryModel
from app.utils.log_utils import log_exception, log_operation


class CategoryService:
    """
    Service for category management business logic.

    Business rules:
    - Categories cannot be deleted once created (permanent).
    - Category names must be unique (case-insensitive).
    - Category names must be non-empty and <= 25 chars.
    """

    @staticmethod
    def get_all_categories() -> list:
        """
        Retrieve all categories from the database.

        Returns:
            list: A list of category dictionaries.

        Raises:
            Exception: Any database error is caught and logged; empty list returned.
        """
        try:
            with SessionLocal() as session:
                categories = CategoryModel.get_all(session)
                log_operation(
                    "category.get_all",
                    "success",
                    f"Retrieved {len(categories)} categories",
                )
                return categories
        except Exception as e:
            log_exception("category.get_all", e)
            return []

    @staticmethod
    def category_exists(name: str) -> bool:
        """
        Check if a category with the given name already exists (case-insensitive).

        Args:
            name: The category name to check.

        Returns:
            bool: True if it exists, False otherwise.

        Raises:
            Exception: Any database error is caught and logged; False returned.
        """
        try:
            with SessionLocal() as session:
                categories = CategoryModel.get_all(session)
                exists = any(c["category"].lower() == name.lower() for c in categories)
                if exists:
                    log_operation(
                        "category.exists", "success", f"Category '{name}' found"
                    )
                return exists
        except Exception as e:
            log_exception("category.exists", e, context={"name": name})
            return False

    @staticmethod
    def add_category(name: str) -> Tuple[bool, str]:
        """
        Add a new category.

        Business rules:
        - Name must be non-empty.
        - Name must be unique (case-insensitive).
        - Name must be <= 25 characters.

        Args:
            name: The category name to add.

        Returns:
            Tuple[bool, str]: (success, message)

        Raises:
            Exception: Any database error is caught and logged; (False, message) returned.
        """
        if not name or not name.strip():
            log_operation(
                "category.add_category", "validation_error", "Category name required"
            )
            return False, "Category name is required"

        name_stripped = name.strip()

        if len(name_stripped) > 25:
            log_operation(
                "category.add_category",
                "validation_error",
                f"Category name too long: {len(name_stripped)} chars",
            )
            return False, "Category name must be 25 characters or less"

        if CategoryService.category_exists(name_stripped):
            log_operation(
                "category.add_category",
                "validation_error",
                f"Duplicate category: '{name_stripped}'",
            )
            return False, "This category already exists"

        try:
            with SessionLocal() as session:
                CategoryModel.create(session, name_stripped)
                session.commit()
            log_operation(
                "category.add_category",
                "success",
                f"Created category: '{name_stripped}'",
            )
            return True, "Category added successfully"
        except Exception as e:
            log_exception("category.add_category", e, context={"name": name_stripped})
            return False, "Something went wrong. Please try again later."

    @staticmethod
    def update_category(category_id: int, new_name: str) -> Tuple[bool, str]:
        """
        Update an existing category's name.

        Business rules:
        - Name must be non-empty.
        - Name must be unique (case-insensitive).
        - Name must be <= 25 characters.

        Args:
            category_id: The ID of the category to update.
            new_name: The new name for the category.

        Returns:
            Tuple[bool, str]: (success, message)

        Raises:
            ValueError: If new_name is invalid.
            Exception: Any database error is caught and logged; (False, message) returned.
        """
        if not new_name or not new_name.strip():
            log_operation(
                "category.update_category", "validation_error", "Category name required"
            )
            return False, "Category name is required"

        new_name_stripped = new_name.strip()

        if len(new_name_stripped) > 25:
            log_operation(
                "category.update_category",
                "validation_error",
                f"Category name too long: {len(new_name_stripped)} chars",
            )
            return False, "Category name must be 25 characters or less"

        try:
            with SessionLocal() as session:
                category = (
                    session.query(CategoryModel).filter_by(id=category_id).first()
                )
                if not category:
                    log_operation(
                        "category.update_category",
                        "validation_error",
                        f"Category not found: id={category_id}",
                    )
                    return False, "Category not found"

                if (
                    category.category.lower() != new_name_stripped.lower()
                    and CategoryService.category_exists(new_name_stripped)
                ):
                    log_operation(
                        "category.update_category",
                        "validation_error",
                        f"Duplicate category: '{new_name_stripped}'",
                    )
                    return False, "This category name already exists"

                CategoryModel.update(session, category_id, new_name_stripped)
                session.commit()

            log_operation(
                "category.update_category",
                "success",
                f"Updated category id={category_id} to '{new_name_stripped}'",
            )
            return True, "Category updated successfully"
        except ValueError as e:
            log_operation(
                "category.update_category", "validation_error", f"ValueError: {str(e)}"
            )
            return False, "Invalid category data"
        except Exception as e:
            log_exception(
                "category.update_category",
                e,
                context={"category_id": category_id, "new_name": new_name_stripped},
            )
            return False, "Something went wrong. Please try again later."
