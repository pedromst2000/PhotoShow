from typing import List, Tuple

from app.core.services.category_service import CategoryService
from app.utils.log_utils import log_exception, log_operation


class CategoryController:
    """
    Controller for category management operations.

    Coordinates between views and services for:
    - Retrieving available categories
    - Adding new categories
    """

    @staticmethod
    def get_categories() -> List[str]:
        """
        Return all available category names for dropdowns and filters.

        Returns a list with "All" as the first option, followed by actual categories
        (deduped case-insensitively). This ensures consistent dropdown behavior across
        the UI without redundant logic in widgets.

        Returns:
            list[str]: ["All"] followed by sorted category names (no duplicates).
        """
        all_categories = CategoryService.get_all_categories()
        categories = sorted(c["category"] for c in all_categories)
        # Ensure "All" is first and remove case-insensitive duplicates
        categories = ["All"] + [c for c in categories if c.lower() != "all"]
        return categories

    @staticmethod
    def add_category(category_name: str) -> Tuple[bool, str]:
        """
        Add a new category.

        Args:
            category_name: The name of the category to add.

        Returns:
            Tuple[bool, str]: Tuple of (success, message)

        Raises:
            Exception: Any unexpected error during category addition is caught and logged.
        """
        if not category_name or not category_name.strip():
            log_operation(
                "category.add_category", "validation_error", "Category name is required"
            )
            return False, "Category name is required"
        try:
            success, message = CategoryService.add_category(category_name.strip())
            if success:
                log_operation(
                    "category.add_category",
                    "success",
                    f"Category '{category_name}' added",
                )
            else:
                log_operation("category.add_category", "validation_error", message)
            return success, message
        except Exception as e:
            log_exception(
                "category.add_category", e, context={"category_name": category_name}
            )
            return False, "Something went wrong. Please try again later."

    @staticmethod
    def update_category(category_id: int, new_name: str) -> Tuple[bool, str]:
        """
        Update an existing category's name.

        Args:
            category_id: The ID of the category to update.
            new_name: The new name for the category.

        Returns:
            Tuple[bool, str]: Tuple of (success, message)

        Raises:
            Exception: Any unexpected error during category update is caught and logged.
        """
        if not new_name or not new_name.strip():
            log_operation(
                "category.update_category",
                "validation_error",
                "Category name is required",
            )
            return False, "Category name is required"
        try:
            success, message = CategoryService.update_category(
                category_id, new_name.strip()
            )
            if success:
                log_operation(
                    "category.update_category",
                    "success",
                    f"Category {category_id} updated to '{new_name}'",
                )
            else:
                log_operation("category.update_category", "validation_error", message)
            return success, message
        except Exception as e:
            log_exception(
                "category.update_category",
                e,
                context={"category_id": category_id, "new_name": new_name},
            )
            return False, "Something went wrong. Please try again later."
