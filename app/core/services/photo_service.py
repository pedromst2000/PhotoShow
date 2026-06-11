from datetime import datetime, timezone
from typing import Optional, Tuple

from sqlalchemy import func

from app.core.db.engine import SessionLocal
from app.core.db.models.album import AlbumModel
from app.core.db.models.category import CategoryModel
from app.core.db.models.comment import CommentModel
from app.core.db.models.like import LikeModel
from app.core.db.models.notification import NotificationModel
from app.core.db.models.photo import PhotoModel
from app.core.db.models.photo_image import PhotoImageModel
from app.core.db.models.rating import RatingModel
from app.core.db.models.user import UserModel
from app.core.services.helpers.weighted_rating import calculate_weighted_rating
from app.core.services.notification_service import NotificationService
from app.utils.log_utils import log_exception, log_operation


class PhotoService:
    """
    Service for photo management business logic.

    Focused on photo CRUD operations and interactions (likes, ratings, comments).
    Does NOT handle:
    - Category logic (see CategoryService)
    - Catalog/Explore view logic (see CatalogService)
    - Rating formula calculations (see RatingUtils)

    Business rules enforced:
    - When creating a photo, an image row is also created in same transaction.
    - Only photo owners can update or delete their photos.
    - When deleting a photo, all related records cascade (likes, comments, ratings, images).
    - When retrieving photos, category names and usernames are included.
    """

    @staticmethod
    def check_if_liked(user_id: int, photo_id: int) -> bool:
        """
        Check if a user has already liked a photo.

        Args:
            user_id: The user's ID.
            photo_id: The photo's ID.

        Returns:
            bool: True if the user has liked the photo, False otherwise.

        Raises:
            Exception: Any database error is caught and logged; False returned.
        """
        try:
            with SessionLocal() as session:
                return LikeModel.has_liked(session, user_id, photo_id)
        except Exception as e:
            log_exception(
                "photo.check_if_liked",
                e,
                user_id=user_id,
                context={"photo_id": photo_id},
            )
            return False

    @staticmethod
    def create_photo(
        photo_id: int,
        provider_image_id: str,
        provider_image_url: str,
    ) -> bool:
        """
        Link Cloudinary image data to an existing photo record.

        The photo record must already exist in the database. This method
        creates the associated PhotoImageModel record.

        Args:
            photo_id:           The ID of the existing photo.
            provider_image_id:  Cloudinary public_id of the uploaded image.
            provider_image_url: Cloudinary secure_url of the uploaded image.

        Returns:
            bool: True if the image record was created successfully.

        Raises:
            Exception: Any database error is caught and logged; False returned.
        """
        try:
            with SessionLocal() as session:
                PhotoImageModel.create(
                    session,
                    photo_id=photo_id,
                    provider_image_id=provider_image_id,
                    provider_image_url=provider_image_url,
                )
                session.commit()
            log_operation(
                "photo.create_photo", "success", f"Linked image for photo {photo_id}"
            )
            return True
        except Exception as e:
            log_exception(
                "photo.create_photo",
                e,
                context={
                    "photo_id": photo_id,
                    "provider_image_id": provider_image_id,
                },
            )
            return False

    @staticmethod
    def create_photo_record(
        album_id: int,
        category_id: Optional[int] = None,
        description: str = "",
        published_date=None,
    ) -> Optional[dict]:
        """
        Create a photo record in the database (without image data).

        Used before uploading to Cloudinary so we have a photo_id to use
        in the Cloudinary public_id naming.

        Args:
            album_id:       The ID of the album to associate with the photo (mandatory).
            category_id:    The ID of the category to associate with the photo.
            description:    A description for the photo.
            published_date: The date/time when the photo was published.

        Returns:
            dict: The created photo as a dictionary, or None on error.
        """
        try:
            with SessionLocal() as session:
                photo = PhotoModel.create(
                    session,
                    description=description,
                    publishedDate=published_date or datetime.now(timezone.utc),
                    categoryId=category_id,
                    albumId=album_id,
                )
                session.commit()
            log_operation(
                "photo.create_photo_record",
                "success",
                f"Created photo record in album {album_id}",
            )
            return photo
        except Exception as e:
            log_exception(
                "photo.create_photo_record",
                e,
                context={"album_id": album_id},
            )
            return None

    @staticmethod
    def delete_photo_record(photo_id: int) -> bool:
        """
        Delete a photo record from the database (used for rollback on upload failure).

        Args:
            photo_id: The ID of the photo to delete.

        Returns:
            bool: True if deleted, False otherwise.
        """
        try:
            with SessionLocal() as db:
                # Delete notifications first (FK constraint).
                NotificationModel.delete_by_photo_id(db, photo_id)
                db.flush()  # Ensure notifications are deleted

                # Delete the photo and verify it was deleted
                deleted = PhotoModel.delete(db, photo_id)
                if not deleted:
                    log_operation(
                        "photo.delete_photo_record",
                        "validation_error",
                        f"Photo record {photo_id} not found for deletion",
                    )
                    return False

                db.flush()  # Ensure photo is marked for deletion
                db.commit()  # Persist all changes to database
            log_operation(
                "photo.delete_photo_record",
                "success",
                f"Deleted photo record {photo_id}",
            )
            return True
        except Exception as e:
            log_exception(
                "photo.delete_photo_record", e, context={"photo_id": photo_id}
            )
            return False

    @staticmethod
    def delete_photo(
        photo_id: int, requesting_user_id: Optional[int] = None
    ) -> Tuple[bool, str]:
        """
        Delete a photo by ID, removing it from both the database and Cloudinary.

        Fetches the stored Cloudinary public_id before DB deletion so the cloud
        asset can be removed after the database cascade completes.

        IMPORTANT: Only deletes from PROD folder (user uploads). Dev folder assets
        (hardcoded seed data) are never deleted from the cloud.

        Args:
            photo_id:            The ID of the photo to delete.
            requesting_user_id:  The user requesting deletion (used to send
                                 admin_delete_photo notification to the owner
                                 when an admin deletes).

        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            owner_id: Optional[int] = None
            provider_image_id: Optional[str] = None

            with SessionLocal() as db:
                # Verify photo exists
                photo_check = PhotoModel.get_by_id(db, photo_id)
                if not photo_check:
                    log_operation(
                        "photo.delete_photo",
                        "validation_error",
                        f"Photo {photo_id} not found",
                    )
                    return False, "Photo not found"

                photo_row = PhotoModel.get_by_id(db, photo_id)
                if photo_row and photo_row.get("albumId"):
                    album = AlbumModel.get_by_id(db, int(photo_row["albumId"]))
                    owner_id = album.get("creatorId") if album else None

                # Capture the Cloudinary public_id before the cascade wipes it.
                image_record = PhotoImageModel.get_for_photo(db, photo_id)
                provider_image_id = (
                    image_record.get("provider_image_id") if image_record else None
                )

                # Delete notifications first (FK constraint).
                NotificationModel.delete_by_photo_id(db, photo_id)
                db.flush()  # Ensure notifications are deleted before cascading

                # Delete the photo
                deleted = PhotoModel.delete(db, photo_id)
                if not deleted:
                    return False, "Photo could not be deleted"

                db.flush()  # Ensure photo is marked for deletion
                db.commit()  # Persist all changes to database

                log_operation(
                    "photo.delete_photo",
                    "success",
                    f"Database deletion committed for photo {photo_id}",
                )

            # Remove the asset from Cloudinary ONLY if it's in prod folder
            # Dev folder assets (seed data) are never deleted
            if provider_image_id and "photo-show/prod/" in provider_image_id:
                from app.core.services.cloudinary_service import CloudinaryService

                CloudinaryService.delete_image(provider_image_id)

            log_operation("photo.delete_photo", "success", f"Deleted photo {photo_id}")

            if owner_id and requesting_user_id and requesting_user_id != owner_id:
                NotificationService.send(
                    "admin_delete_photo",
                    "Your photo was deleted by an admin",
                    user_id=owner_id,
                    sender_id=requesting_user_id,
                )

            return True, "Photo deleted successfully"
        except Exception as e:
            log_exception("photo.delete_photo", e, context={"photo_id": photo_id})
            return False, "Failed to delete photo"

    @staticmethod
    def update_photo_for_user(user_id: int, photo_id: int, updates: dict) -> bool:
        """
        Update a photo if the given user owns it.

        Args:
            user_id: The ID of the requesting user.
            photo_id: The ID of the photo to update.
            updates: Fields to update.

        Returns:
            bool: True if updated, False otherwise.
        """
        with SessionLocal() as session:
            photo = PhotoModel.get_by_id(session, photo_id)
            if not photo:
                return False
            album_id = photo.get("albumId")
            album = (
                AlbumModel.get_by_id(session, int(album_id))
                if album_id is not None
                else None
            )
            owner_id = album["creatorId"] if album else None
            if owner_id == user_id:
                PhotoModel.update(session, {**photo, **updates})
                session.commit()
                return True
            return False

    @staticmethod
    def get_liked_photos(user_id: int) -> list:
        """
        Get all photos liked by a specific user.

        Args:
            user_id: The ID of the user to get liked photos for.
        Returns:
            list: A list of photo dictionaries that the user has liked.
        """
        with SessionLocal() as session:
            # Fetch like rows first, then batch fetch photos by id to avoid N+1
            like_rows = LikeModel.get_liked_photos(session, user_id)
            photo_ids = [r["photoId"] for r in like_rows]
            if (
                not photo_ids
            ):  # User has not liked any photos, return empty list early to avoid unnecessary query
                return []
            photos = (
                session.query(PhotoModel)
                .filter(getattr(PhotoModel, "id").in_(photo_ids))
                .all()
            )
            return [p.to_dict() for p in photos]

    @staticmethod
    def get_photo_details(
        photo_id: int, user_id: Optional[int] = None
    ) -> Optional[dict]:
        """
        Get detailed information for a single photo, including like count, whether the user has liked it, and the owner's username.

        Args:
            photo_id: The ID of the photo to retrieve.
            user_id: The ID of the current user (optional, for personalized like status).
        Returns:
            dict: A dictionary containing photo details, or None if the photo does not exist.
        """
        with SessionLocal() as session:
            photo = PhotoModel.get_by_id(session, photo_id)
            if not photo:
                return None
            likes = LikeModel.count_by_photo(session, photo_id)
            has_liked = (
                LikeModel.has_liked(session, user_id, photo_id) if user_id else False
            )
            album = (
                AlbumModel.get_by_id(session, int(photo["albumId"]))
                if photo.get("albumId")
                else None
            )
            owner = UserModel.get_by_id(session, album["creatorId"]) if album else None
            image_record = PhotoImageModel.get_for_photo(session, photo_id)
            comments = (
                session.query(func.count())
                .select_from(CommentModel)
                .filter(getattr(CommentModel, "photoId") == photo_id)
                .scalar()
                or 0
            )
            avg_result = (
                session.query(func.avg(getattr(RatingModel, "rating")))
                .filter(getattr(RatingModel, "photoId") == photo_id)
                .scalar()
            )
            count_result = (
                session.query(func.count(getattr(RatingModel, "id")))
                .filter(getattr(RatingModel, "photoId") == photo_id)
                .scalar()
            )
            category_row = (
                session.query(CategoryModel)
                .filter_by(id=photo.get("categoryId"))
                .first()
            )
        # Return both 'username' (legacy) and 'user' (consistent across services)
        username = owner["username"] if owner else None
        owner_is_admin = owner["roleId"] == 1 if owner else False
        owner_id = album["creatorId"] if album else None
        owner_avatar = owner.get("avatar") if owner else None
        image_path = image_record.get("provider_image_url") if image_record else None
        avg_rating = round(float(avg_result), 1) if avg_result is not None else 0.0
        rating_count = int(count_result) if count_result else 0
        category_name = category_row.category if category_row else ""
        return {
            **photo,
            "image": image_path,
            "likes": likes,
            "has_liked": has_liked,
            "comments": comments,
            "avg_rating": avg_rating,
            "rating_count": rating_count,
            "category": category_name,
            "username": username,
            "user": username,
            "owner_id": owner_id,
            "owner_avatar": owner_avatar,
            "owner_is_admin": owner_is_admin,
        }

    @staticmethod
    def like_photo(user_id: int, photo_id: int) -> bool:
        """
        Like a photo.

        Args:
            user_id: The ID of the user liking the photo.
            photo_id: The ID of the photo to like.

        Returns:
            bool: True if the like was created, False if already liked.
        """
        owner_id: Optional[int] = None
        with SessionLocal() as session:
            result = LikeModel.like(session, user_id, photo_id) is not None
            if result:
                photo = PhotoModel.get_by_id(session, photo_id)
                if photo and photo.get("albumId"):
                    album = AlbumModel.get_by_id(session, int(photo["albumId"]))
                    owner_id = album.get("creatorId") if album else None
            session.commit()
        if result and owner_id and owner_id != user_id:
            NotificationService.send(
                "like_photo",
                "liked your photo",
                user_id=owner_id,
                sender_id=user_id,
                photo_id=photo_id,
            )
        return result

    @staticmethod
    def unlike_photo(user_id: int, photo_id: int) -> bool:
        """
        Unlike a photo and remove the related notification.

        Args:
            user_id: The ID of the user unliking the photo.
            photo_id: The ID of the photo to unlike.

        Returns:
            bool: True if the like was removed, False if it didn't exist.
        """
        with SessionLocal() as session:
            result = LikeModel.unlike(session, user_id, photo_id)
            session.commit()
        # Remove the like_photo notification when user unlikes
        if result:
            NotificationService.delete_by_like(user_id, photo_id)
        return result

    @staticmethod
    def get_photo_rating_stats(photo_id: int) -> dict:
        """
        Return fresh rating stats for a single photo after a rating change.

        Uses RatingUtils for consistent weighted-rating calculation with catalog view.

        Args:
            photo_id: The ID of the photo.

        Returns:
            dict: Keys avg_rating, rating_count, weighted_rating.
        """
        with SessionLocal() as session:
            avg_result = (
                session.query(func.avg(getattr(RatingModel, "rating")))
                .filter(getattr(RatingModel, "photoId") == photo_id)
                .scalar()
            )
            count_result = (
                session.query(func.count(getattr(RatingModel, "id")))
                .filter(getattr(RatingModel, "photoId") == photo_id)
                .scalar()
            )
            global_avg_result = session.query(
                func.avg(getattr(RatingModel, "rating"))
            ).scalar()

        avg_rating = round(float(avg_result), 1) if avg_result is not None else 1.0
        rating_count = int(count_result) if count_result else 0
        global_avg = (
            round(float(global_avg_result), 1) if global_avg_result is not None else 1.0
        )
        weighted_rating = calculate_weighted_rating(
            avg_rating, rating_count, global_avg
        )

        return {
            "avg_rating": avg_rating,
            "rating_count": rating_count,
            "weighted_rating": weighted_rating,
        }

    @staticmethod
    def rate_photo(user_id: int, photo_id: int, rating_value: int):
        """
        Submit a rating (1-5) for a photo.
        If the user has already rated the photo, their rating is updated.

        Args:
            user_id: The ID of the user submitting the rating.
            photo_id: The ID of the photo being rated.
            rating_value: The rating value (1-5).
        """
        with SessionLocal() as session:
            RatingModel.create(
                session,
                user_id=user_id,
                photo_id=photo_id,
                rating_value=rating_value,
            )
            session.commit()
