from typing import List, Optional, Tuple

from app.core.services.cloudinary_service import CloudinaryService
from app.core.services.photo_service import PhotoService
from app.core.state.session import session
from app.utils.log_utils import log_exception, log_operation


class PhotoController:
    """
    Controller for photo operations.

    Coordinates between views and services for:
    - Uploading photos
    - Deleting photos
    - Fetching photo details
    """

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
    def upload_photo(
        image_path: str,
        album_id: Optional[int] = None,
        category_id: Optional[int] = None,
        description: str = "",
        published_date=None,
    ) -> Tuple[bool, str]:
        """
        Upload a new photo to Cloudinary and record it in the database.

        Flow:
        1. Create a photo record (gets photo_id).
        2. Upload the local file to Cloudinary using Photo_<photo_id> as public_id.
        3. Create the photo_image record linking the Cloudinary data.
        4. On any failure, rollback the photo record and Cloudinary upload.

        Args:
            image_path:    Full path to the source image chosen by the user.
            album_id:      Album ID to associate with the photo.
            category_id:   Optional category ID.
            description:   Optional description.
            published_date: Optional published date.

        Returns:
            Tuple[bool, str]: (success, message)
        """
        if not image_path:
            return False, "Image path is required"
        if album_id is None:
            return False, "Album ID is required"

        # Step 1: Create photo record (no image yet).
        photo = PhotoService.create_photo_record(
            album_id=album_id,
            category_id=category_id,
            description=description,
            published_date=published_date,
        )
        if photo is None:
            return False, "Failed to initialize photo record"

        photo_id = photo.get("id")
        if not photo_id:
            return False, "Failed to get photo ID"

        # Step 2: Upload to Cloudinary with photo_id in public_id.
        upload_result = CloudinaryService.upload_photo(image_path, photo_id)
        if upload_result is None:
            # Rollback photo record.
            PhotoService.delete_photo_record(photo_id)
            return False, "Failed to upload image to cloud storage"

        provider_image_id = upload_result["public_id"]
        provider_image_url = upload_result["url"]

        # Step 3: Create photo_image record linking to Cloudinary.
        try:
            if not PhotoService.create_photo(
                photo_id=photo_id,
                provider_image_id=provider_image_id,
                provider_image_url=provider_image_url,
            ):
                # Rollback photo record and Cloudinary upload.
                CloudinaryService.delete_image(provider_image_id)
                PhotoService.delete_photo_record(photo_id)
                return False, "Failed to save photo metadata"

            log_operation(
                "photo.upload_photo",
                "success",
                "Photo uploaded successfully",
            )
            return True, "Photo uploaded successfully"
        except Exception as e:
            # Rollback on unexpected exception.
            CloudinaryService.delete_image(provider_image_id)
            PhotoService.delete_photo_record(photo_id)
            log_exception(
                "photo.upload_photo",
                e,
                context={
                    "image_path": image_path,
                    "album_id": album_id,
                    "photo_id": photo_id,
                    "provider_image_id": provider_image_id,
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
            success, message = PhotoService.delete_photo(
                photo_id, requesting_user_id=session.user_id
            )
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
