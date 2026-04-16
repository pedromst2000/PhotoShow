from typing import List, Optional, Tuple

from app.core.db.engine import SessionLocal
from app.core.db.models.category import CategoryModel
from app.core.db.models.like import LikeModel
from app.core.services.photo_service import PhotoService
from app.core.state.session import session


class ExploreController:
    """
    Controller for the Explore (catalog) view.

    Coordinates between the view and services for:
    - Loading the photo catalog with filters and sorting
    - Toggling likes on photos
    - Rating photos
    - Retrieving category options for the filter dropdown
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
            list: Enriched photo dicts with image, stats, and user flags.
        """
        return PhotoService.get_explore_catalog(
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
        """
        user_id = session.user_id

        if user_id is None:
            return False, "Authentication required", False

        with SessionLocal() as db:
            already_liked = LikeModel.has_liked(db, user_id, photo_id)

        if already_liked:
            success = PhotoService.unlike_photo(user_id, photo_id)
            return success, "Photo unliked" if success else "Failed to unlike", False
        else:
            success = PhotoService.like_photo(user_id, photo_id)
            return success, "Photo liked" if success else "Failed to like", True

    @staticmethod
    def rate_photo(photo_id: int, rating_value: int) -> Tuple[bool, str]:
        """
        Submit or update a star rating (1-5) for a photo.

        Args:
            photo_id: The ID of the photo to rate.
            rating_value: Integer rating from 1 to 5.

        Returns:
            Tuple[bool, str]: (success, message)
        """
        user_id = session.user_id
        if user_id is None:
            return False, "Authentication required"
        try:
            PhotoService.rate_photo(user_id, photo_id, rating_value)
            return True, "Rating submitted"
        except Exception as exc:
            return False, str(exc)

    @staticmethod
    def get_photo_by_id(photo_id: int) -> Optional[dict]:
        """
        Return fresh rating stats for a photo after a rating change.

        Args:
            photo_id: The ID of the photo.

        Returns:
            dict: Keys avg_rating, rating_count, weighted_rating.
        """
        return PhotoService.get_photo_rating_stats(photo_id)

    @staticmethod
    def get_categories() -> List[str]:
        """
        Return all available category names for the filter dropdown.

        Returns a list with "All" as the first option, followed by actual categories
        (deduped case-insensitively). This ensures consistent dropdown behavior across
        the UI without redundant logic in widgets.

        Returns:
            list[str]: ["All"] followed by sorted category names (no duplicates).
        """
        with SessionLocal() as db:
            categories = sorted(c["category"] for c in CategoryModel.get_all(db))
            # Ensure "All" is first and remove case-insensitive duplicates
            categories = ["All"] + [c for c in categories if c.lower() != "all"]
            return categories
