from typing import Optional

import cloudinary
import cloudinary.uploader

from app.config.cloudinary_config import (
    CLOUDINARY_OPTIONS,
    FOLDER_AVATARS,
    FOLDER_PHOTOS,
)
from app.utils.log_utils import log_exception, log_operation

# Configure the Cloudinary SDK once at import time (idempotent).
cloudinary.config(**CLOUDINARY_OPTIONS)


class CloudinaryService:
    """
    Thin wrapper around the Cloudinary SDK.

    Avatars  → uploaded to FOLDER_AVATARS with a deterministic public_id
               (<username>_avatar). Old avatars are EXPLICITLY DELETED before
               upload to ensure no duplicates accumulate in the cloud.
               The caller (handle_save_avatar) must delete the old avatar first.

    Photos   → uploaded to FOLDER_PHOTOS with a deterministic public_id
               (Photo_<photo_id>). Deletion must be called explicitly when a
               photo is removed.
    """

    @staticmethod
    def upload_avatar(file_path: str, username: str) -> Optional[dict]:
        """
        Upload a user avatar to the PROD folder in Cloudinary with a deterministic public_id.

        The public_id is built as <username>_avatar and placed in FOLDER_AVATARS_PROD
        (photo-show/prod/profile_avatars), resulting in a full path like:
        photo-show/prod/profile_avatars/<username>_avatar

        Dev folder avatars (hardcoded seed data) are NEVER deleted or modified.

        Args:
            file_path: Absolute path to the source image file (jpg/png/jpeg).
            username:  The owner's username — used to build the public_id.

        Returns:
            Optional[dict]: with keys ``public_id`` and ``url`` on success, None on error.
        """
        try:
            result = cloudinary.uploader.upload(
                file_path,
                folder=FOLDER_AVATARS,
                public_id=f"{username}_avatar",
                overwrite=True,
                transformation=[
                    {"width": 400, "height": 400, "crop": "fill", "gravity": "face"}
                ],
            )
            log_operation(
                "cloudinary.upload_avatar",
                "success",
                f"Avatar uploaded for {username}: {result['public_id']}",
            )
            return {
                "public_id": result["public_id"],
                "url": result["secure_url"],
            }
        except Exception as e:
            log_exception(
                "cloudinary.upload_avatar",
                e,
                context={"username": username, "file_path": file_path},
            )
            return None

    @staticmethod
    def upload_photo(file_path: str, photo_id: int) -> Optional[dict]:
        """
        Upload a photo image to the PROD folder in Cloudinary with a deterministic public_id.

        The public_id is built as Photo_<photo_id> to link it back to the DB record.
        Cloudinary automatically prepends the folder path, resulting in a full
        public_id like: photo-show/prod/photos_gallery/Photo_45

        Args:
            file_path: Absolute path to the source image file (jpg/png/jpeg).
            photo_id: The database photo ID (used to build the public_id).

        Returns:
            Optional[dict]: with keys ``public_id`` and ``url`` on success, None on error.
        """
        try:
            result = cloudinary.uploader.upload(
                file_path,
                folder=FOLDER_PHOTOS,
                public_id=f"Photo_{photo_id}",
                overwrite=False,
                transformation=[{"width": 1200, "height": 1200, "crop": "limit"}],
            )
            log_operation(
                "cloudinary.upload_photo",
                "success",
                f"Photo uploaded: {result['public_id']}",
            )
            return {
                "public_id": result["public_id"],
                "url": result["secure_url"],
            }
        except Exception as e:
            log_exception(
                "cloudinary.upload_photo",
                e,
                context={"file_path": file_path, "photo_id": photo_id},
            )
            return None

    @staticmethod
    def delete_image(public_id: str) -> bool:
        """
        Delete an asset from Cloudinary by its public_id.

        Args:
            public_id: The Cloudinary public_id of the asset to remove.

        Returns:
            bool: True if deletion succeeded, False otherwise.
        """
        if not public_id:
            return False
        try:
            result = cloudinary.uploader.destroy(public_id)
            ok = result.get("result") == "ok"
            log_operation(
                "cloudinary.delete_image",
                "success" if ok else "failed",
                f"Delete {public_id}: {result.get('result')}",
            )
            return ok
        except Exception as e:
            log_exception(
                "cloudinary.delete_image",
                e,
                context={"public_id": public_id},
            )
            return False
