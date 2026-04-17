from typing import List, Optional, Tuple

from app.core.services.catalog_service import CatalogService
from app.core.services.photo_service import PhotoService
from app.core.state.session import session
from app.utils.log_utils import log_exception, log_operation


class ExploreController:
    """
    Controller for the Explore (catalog) view.

    Coordinates between the view and services for:
    - Loading the photo catalog with filters and sorting
    - Toggling likes on photos
    - Rating photos
    """

    @staticmethod
    def get_catalog(
        sort_by: str = "date",
        category: str = "all",
        username: Optional[str] = None,
    ) -> List[dict]:
        """
        Return the enriched photo catalog, filtered and sorted.

        Args:
            sort_by: Sort key — one of "date", "likes", "rating", "comments".
            category: Category name to filter by, or "all".
            username: Author username to filter by, or None.

        Returns:
            List[dict]: Enriched photo dicts with image, stats, and user flags.
        """
        return CatalogService.get_explore_catalog(
            sort_by=sort_by,
            category=category,
            username=username,
            user_id=session.user_id,
        )

    @staticmethod
    def toggle_like(photo_id: int) -> Tuple[bool, str, bool]:
        """
        Like or unlike a photo depending on the current like state.

        Args:
            photo_id: The ID of the photo to toggle the like on.

        Returns:
            Tuple[bool, str, bool]: (success, message, is_liked_now)

        Raises:
            Exception: Any unexpected error during toggle operation is caught and logged.
        """
        user_id = session.user_id

        if user_id is None:
            log_operation(
                "explore.toggle_like", "validation_error", "Authentication required"
            )
            return False, "Authentication required", False

        try:
            already_liked = PhotoService.check_if_liked(user_id, photo_id)

            if already_liked:
                success = PhotoService.unlike_photo(user_id, photo_id)
                if success:
                    log_operation(
                        "explore.toggle_like",
                        "success",
                        f"Photo {photo_id} unliked",
                        user_id=user_id,
                    )
                return (
                    success,
                    "Photo unliked" if success else "Failed to unlike",
                    False,
                )
            else:
                success = PhotoService.like_photo(user_id, photo_id)
                if success:
                    log_operation(
                        "explore.toggle_like",
                        "success",
                        f"Photo {photo_id} liked",
                        user_id=user_id,
                    )
                return success, "Photo liked" if success else "Failed to like", True
        except Exception as e:
            log_exception(
                "explore.toggle_like",
                e,
                user_id=user_id,
                context={"photo_id": photo_id},
            )
            return False, "Something went wrong. Please try again later.", False

    @staticmethod
    def rate_photo(photo_id: int, rating_value: int) -> Tuple[bool, str]:
        """
        Submit or update a star rating (1-5) for a photo.

        Args:
            photo_id: The ID of the photo to rate.
            rating_value: Integer rating from 1 to 5.

        Returns:
            Tuple[bool, str]: (success, message)

        Raises:
            Exception: Any unexpected error during rating operation is caught and logged.
        """
        user_id = session.user_id
        if user_id is None:
            log_operation(
                "explore.rate_photo", "validation_error", "Authentication required"
            )
            return False, "Authentication required"
        try:
            PhotoService.rate_photo(user_id, photo_id, rating_value)
            log_operation(
                "explore.rate_photo",
                "success",
                f"Photo {photo_id} rated {rating_value}/5",
                user_id=user_id,
            )
            return True, "Rating submitted"
        except Exception as exc:
            log_exception(
                "explore.rate_photo",
                exc,
                user_id=user_id,
                context={"photo_id": photo_id, "rating_value": rating_value},
            )
            return False, "Something went wrong. Please try again later."

    @staticmethod
    def get_photo_by_id(photo_id: int) -> Optional[dict]:
        """
        Return fresh rating stats for a photo after a rating change.

        Args:
            photo_id: The ID of the photo.

        Returns:
            Optional[dict]: Keys avg_rating, rating_count, weighted_rating.
        """
        return PhotoService.get_photo_rating_stats(photo_id)
