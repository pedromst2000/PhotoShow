from typing import List, Optional, Tuple

from services.photo_service import PhotoService
from state.session import session


class PhotoController:
    """
    Controller for photo operations.

    Coordinates between views and services for:
    - Uploading photos
    - Listing photos
    - Filtering photos
    - Deleting photos
    """

    @staticmethod
    def get_all_photos() -> List[dict]:
        """
        Get all photos in the system.

        Returns:
            list: List of all photo dictionaries.
        """
        return PhotoService.get_all_photos()

    @staticmethod
    def get_photo(photo_id: int) -> Optional[dict]:
        """
        Get a specific photo by ID.

        Args:
            photo_id: The photo's ID.

        Returns:
            dict or None: The photo data if found.
        """
        return PhotoService.get_photo_by_id(photo_id)

    @staticmethod
    def get_photos_by_album(album_id: int) -> List[dict]:
        """
        Get all photos in an album.

        Args:
            album_id: The album's ID.

        Returns:
            list: List of photo dictionaries in the album.
        """
        return PhotoService.get_photos_by_album(album_id)

    @staticmethod
    def get_photos_by_user(user_id: int = None) -> List[dict]:
        """
        Get all photos uploaded by a user.

        Args:
            user_id: The user's ID. If None, uses current user.

        Returns:
            list: List of photo dictionaries.
        """
        target_user_id = user_id if user_id is not None else session.user_id
        if target_user_id is None:
            return []
        return PhotoService.get_photos_by_user(target_user_id)

    @staticmethod
    def get_filtered_photos(category: str = "all", username: str = None) -> List[dict]:
        """
        Get photos filtered by category and/or username.

        Args:
            category: The category to filter by. "all" for all categories.
            username: The username to filter by. None to not filter by user.

        Returns:
            list: List of enriched photo dictionaries.
        """
        return PhotoService.get_filtered_photos(category, username)

    @staticmethod
    def get_photos_by_category(category_name: str) -> List[dict]:
        """
        Get all photos in a category.

        Args:
            category_name: The name of the category.

        Returns:
            list: List of photo dictionaries in the category.
        """
        return PhotoService.get_photos_by_category(category_name)

    @staticmethod
    def upload_photo(
        image_path: str,
        album_id: int = None,
        category_id: int = None,
        description: str = "",
        published_date=None,
    ) -> Tuple[bool, str]:
        """
        Upload a new photo.

        Args:
            image_path: The file path of the photo to upload.
            album_id: Optional album ID to associate with the photo.
            category_id: Optional category ID to associate with the photo.
            description: Optional description of the photo.
            published_date: Optional published date for the photo.

        Returns:
            Tuple of (success, message)
        """

        if not session.is_authenticated:
            return False, "You must be logged in to upload photos"
        if not image_path:
            return False, "Image path is required"
        try:
            PhotoService.create_photo(
                image_path=image_path,
                album_id=album_id,
                category_id=category_id,
                description=description,
                published_date=published_date,
            )
            return True, "Photo uploaded successfully"
        except Exception as e:
            return False, f"Failed to upload photo: {str(e)}"

    @staticmethod
    def delete_photo(photo_id: int) -> Tuple[bool, str]:
        """
        Delete a photo.

        Args:
            photo_id: The ID of the photo to delete.

        Returns:
            Tuple of (success, message)
        """
        if not session.is_authenticated:
            return False, "You must be logged in to delete photos"

        # Delegate ownership check and deletion to service (business logic)
        if PhotoService.delete_photo_for_user(session.user_id, photo_id):
            return True, "Photo deleted successfully"
        return False, "Failed to delete photo or insufficient permissions"

    @staticmethod
    def update_photo(photo_id: int, updates: dict) -> Tuple[bool, str]:
        """
        Update photo information.

        Args:
            photo_id: The ID of the photo to update.
            updates: Dictionary of fields to update.

        Returns:
            Tuple of (success, message)
        """
        if not session.is_authenticated:
            return False, "You must be logged in to update photos"

        # Delegate ownership check and update to service (business logic)
        if PhotoService.update_photo_for_user(session.user_id, photo_id, updates):
            return True, "Photo updated successfully"
        return False, "Failed to update photo or insufficient permissions"

    @staticmethod
    def like_photo(photo_id: int) -> Tuple[bool, str]:
        """
        Like a photo.

        Args:
            photo_id: The ID of the photo to like.
        Returns:
            Tuple of (success, message)
        """

        if not session.is_authenticated:
            return False, "You must be logged in to like photos"
        if PhotoService.like_photo(session.user_id, photo_id):
            return True, "Photo liked"
        return False, "You have already liked this photo"

    @staticmethod
    def unlike_photo(photo_id: int) -> Tuple[bool, str]:
        """
        Unlike a photo.
        Args:
            photo_id: The ID of the photo to unlike.
        Returns:
            Tuple of (success, message)
        """

        if not session.is_authenticated:
            return False, "You must be logged in to unlike photos"
        if PhotoService.unlike_photo(session.user_id, photo_id):
            return True, "Photo unliked"
        return False, "You have not liked this photo"

    @staticmethod
    def rate_photo(photo_id: int, rating_value: int) -> Tuple[bool, str]:
        """
        Rate a photo (1-5) by the current user.

        Args:
            photo_id: The ID of the photo to rate.
            rating_value: The rating value (1-5).
        Returns:
            Tuple of (success, message)
        """
        if not session.is_authenticated:
            return False, "You must be logged in to rate photos"
        try:
            PhotoService.add_rating(session.user_id, photo_id, rating_value)
            return True, "Rating submitted"
        except Exception as e:
            return False, f"Failed to submit rating: {e}"

    @staticmethod
    def has_liked(photo_id: int) -> bool:
        """
        Check if the current user has liked a specific photo.
        Args:
            photo_id: The ID of the photo to check.
        Returns:
            bool: True if the user has liked the photo, False otherwise.
        """

        if not session.is_authenticated:
            return False
        return PhotoService.has_liked(session.user_id, photo_id)

    @staticmethod
    def count_likes(photo_id: int) -> int:
        """
        Get the total number of likes for a specific photo.
        Args:
            photo_id: The ID of the photo.
        Returns:
            int: The total number of likes for the photo.
        """

        return PhotoService.count_likes(photo_id)

    @staticmethod
    def get_liked_photos(user_id: int = None) -> list:
        """
        Get all photos liked by a user.
        Args:
            user_id: The user's ID. If None, uses current user.
        Returns:
            list: List of photo dictionaries liked by the user.
        """

        target_user_id = user_id if user_id is not None else session.user_id
        if target_user_id is None:
            return []
        return PhotoService.get_liked_photos(target_user_id)
