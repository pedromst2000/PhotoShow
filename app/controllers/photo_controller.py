from typing import List, Optional, Tuple

from app.core.services.photo_service import PhotoService
from app.core.state.session import session
from app.utils.log_utils import log_exception, log_operation


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
            List[dict]: List of all photo dictionaries.
        """
        return PhotoService.get_all_photos()

    @staticmethod
    def get_photo_details(photo_id: int) -> Optional[dict]:
        """
        Get a photo enriched with like stats and owner info.

        Args:
            photo_id: The photo's ID.

        Returns:
            Optional[dict]: Enriched photo data (includes likes, has_liked, username).
        """
        return PhotoService.get_photo_details(photo_id, session.user_id)

    @staticmethod
    def get_photos_by_album(album_id: int) -> List[dict]:
        """
        Get all photos in an album.

        Args:
            album_id: The album's ID.

        Returns:
            List[dict]: List of photo dictionaries in the album.
        """
        return PhotoService.get_photos_by_album(album_id)

    @staticmethod
    def get_photos_by_user(user_id: Optional[int] = None) -> List[dict]:
        """
        Get all photos uploaded by a user.

        Args:
            user_id: The user's ID. If None, uses current user.

        Returns:
            List[dict]: List of photo dictionaries.
        """
        target_user_id = user_id if user_id is not None else session.user_id
        if target_user_id is None:
            return []
        return PhotoService.get_photos_by_user(target_user_id)

    @staticmethod
    def get_filtered_photos(
        category: str = "all", username: Optional[str] = None
    ) -> List[dict]:
        """
        Get photos filtered by category and/or username.

        Args:
            category: The category to filter by. "all" for all categories.
            username: The username to filter by. None to not filter by user.

        Returns:
            List[dict]: List of enriched photo dictionaries.
        """
        return PhotoService.get_filtered_photos(category, username)

    @staticmethod
    def get_photos_by_category(category_name: str) -> List[dict]:
        """
        Get all photos in a category.

        Args:
            category_name: The name of the category.

        Returns:
            List[dict]: List of photo dictionaries in the category.
        """
        return PhotoService.get_photos_by_category(category_name)

    @staticmethod
    def upload_photo(
        image_path: str,
        album_id: Optional[int] = None,
        category_id: Optional[int] = None,
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
            Tuple[bool, str]: Tuple of (success, message)

        Raises:
            Exception: Any unexpected error during photo creation is caught and logged.
        """

        if not image_path:
            return False, "Image path is required"
        if album_id is None:
            return False, "Album ID is required"
        try:
            PhotoService.create_photo(
                image_path=image_path,
                album_id=album_id,
                category_id=category_id,
                description=description,
                published_date=published_date,
            )
            log_operation(
                "photo.upload_photo",
                "success",
                "Photo uploaded successfully",
                user_id=session.user_id,
            )
            return True, "Photo uploaded successfully"
        except Exception as e:
            log_exception(
                "photo.upload_photo",
                e,
                user_id=session.user_id,
                context={
                    "image_path": image_path,
                    "album_id": album_id,
                    "category_id": category_id,
                },
            )
            return False, f"Failed to upload photo: {str(e)}"

    @staticmethod
    def delete_photo(photo_id: int) -> Tuple[bool, str]:
        """
        Delete a photo.

        Args:
            photo_id: The ID of the photo to delete.

        Returns:
            Tuple[bool, str]: Tuple of (success, message)

        Raises:
            Exception: Any unexpected error during photo deletion is caught and logged.
        """
        assert session.user_id is not None

        try:
            # Delegate ownership check and deletion to service (business logic)
            success, message = PhotoService.delete_photo(photo_id)
            if success:
                log_operation(
                    "photo.delete_photo",
                    "success",
                    f"Photo {photo_id} deleted",
                    user_id=session.user_id,
                )
            else:
                log_operation(
                    "photo.delete_photo",
                    "validation_error",
                    message,
                    user_id=session.user_id,
                )
            return success, message
        except Exception as e:
            log_exception(
                "photo.delete_photo",
                e,
                user_id=session.user_id,
                context={"photo_id": photo_id},
            )
            return False, "Something went wrong. Please try again later."

    @staticmethod
    def update_photo(photo_id: int, updates: dict) -> Tuple[bool, str]:
        """
        Update photo information.

        Args:
            photo_id: The ID of the photo to update.
            updates: Dictionary of fields to update.

        Returns:
            Tuple[bool, str]: Tuple of (success, message)

        Raises:
            Exception: Any unexpected error during photo update is caught and logged.
        """
        assert session.user_id is not None

        try:
            # Delegate ownership check and update to service (business logic)
            if PhotoService.update_photo_for_user(session.user_id, photo_id, updates):
                log_operation(
                    "photo.update_photo",
                    "success",
                    f"Photo {photo_id} updated",
                    user_id=session.user_id,
                )
                return True, "Photo updated successfully"
            log_operation(
                "photo.update_photo",
                "validation_error",
                f"Failed to update photo {photo_id}",
                user_id=session.user_id,
            )
            return False, "Failed to update photo or insufficient permissions"
        except Exception as e:
            log_exception(
                "photo.update_photo",
                e,
                user_id=session.user_id,
                context={"photo_id": photo_id},
            )
            return False, "Something went wrong. Please try again later."

    @staticmethod
    def like_photo(photo_id: int) -> Tuple[bool, str]:
        """
        Like a photo.

        Args:
            photo_id: The ID of the photo to like.

        Returns:
            Tuple[bool, str]: Tuple of (success, message)

        Raises:
            Exception: Any unexpected error during like operation is caught and logged.
        """
        assert session.user_id is not None
        try:
            if PhotoService.like_photo(session.user_id, photo_id):
                log_operation(
                    "photo.like_photo",
                    "success",
                    f"Photo {photo_id} liked",
                    user_id=session.user_id,
                )
                return True, "Photo liked"
            log_operation(
                "photo.like_photo",
                "validation_error",
                f"Already liked photo {photo_id}",
                user_id=session.user_id,
            )
            return False, "You have already liked this photo"
        except Exception as e:
            log_exception(
                "photo.like_photo",
                e,
                user_id=session.user_id,
                context={"photo_id": photo_id},
            )
            return False, "Something went wrong. Please try again later."

    @staticmethod
    def unlike_photo(photo_id: int) -> Tuple[bool, str]:
        """
        Unlike a photo.
        Args:
            photo_id: The ID of the photo to unlike.

        Returns:
            Tuple[bool, str]: Tuple of (success, message)

        Raises:
            Exception: Any unexpected error during unlike operation is caught and logged.
        """
        assert session.user_id is not None
        try:
            if PhotoService.unlike_photo(session.user_id, photo_id):
                log_operation(
                    "photo.unlike_photo",
                    "success",
                    f"Photo {photo_id} unliked",
                    user_id=session.user_id,
                )
                return True, "Photo unliked"
            log_operation(
                "photo.unlike_photo",
                "validation_error",
                f"Haven't liked photo {photo_id}",
                user_id=session.user_id,
            )
            return False, "You have not liked this photo"
        except Exception as e:
            log_exception(
                "photo.unlike_photo",
                e,
                user_id=session.user_id,
                context={"photo_id": photo_id},
            )
            return False, "Something went wrong. Please try again later."

    @staticmethod
    def rate_photo(photo_id: int, rating_value: int) -> Tuple[bool, str]:
        """
        Rate a photo (1-5) by the current user.

        Args:
            photo_id: The ID of the photo to rate.
            rating_value: The rating value (1-5).

        Returns:
            Tuple[bool, str]: Tuple of (success, message)

        Raises:
            Exception: Any unexpected error during rating operation is caught and logged.
        """
        assert session.user_id is not None
        try:
            PhotoService.rate_photo(session.user_id, photo_id, rating_value)
            return True, "Rating submitted"
        except Exception as e:
            return False, f"Failed to submit rating: {e}"

    @staticmethod
    def get_liked_photos(user_id: Optional[int] = None) -> List[dict]:
        """
        Get all photos liked by a user.

        Args:
            user_id: The user's ID. If None, uses current user.

        Returns:
            List[dict]: List of photo dictionaries liked by the user.

        Raises:
            Exception: Any unexpected error during retrieval is caught and logged; empty list returned.
        """
        try:
            target_user_id = user_id if user_id is not None else session.user_id
            if target_user_id is None:
                return []
            return PhotoService.get_liked_photos(target_user_id)
        except Exception as e:
            log_exception(
                "photo.get_liked_photos",
                e,
                user_id=session.user_id,
                context={"target_user_id": user_id},
            )
            return []
