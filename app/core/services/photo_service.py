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
from app.utils.file_utils import delete_from_latest
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
        image_path: str,
        album_id: int,
        category_id: Optional[int] = None,
        description: str = "",
        published_date=None,
    ) -> Optional[dict]:
        """
        Create a new photo entry in the database together with its image row.

        Args:
            image_path: The file path of the photo image.
            album_id: The ID of the album to associate with the photo (mandatory).
            category_id: The ID of the category to associate with the photo.
            description: A description for the photo.
            published_date: The date/time when the photo was published.

        Returns:
            dict: The created photo as a dictionary.

        Raises:
            Exception: Any database error is caught and logged; None returned.
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
                PhotoImageModel.create(session, photo_id=photo["id"], image=image_path)
                session.commit()
            log_operation(
                "photo.create_photo", "success", f"Created photo in album {album_id}"
            )
            return photo
        except Exception as e:
            log_exception(
                "photo.create_photo",
                e,
                context={"album_id": album_id, "image_path": image_path},
            )
            return None

    @staticmethod
    def delete_photo(
        photo_id: int, requesting_user_id: Optional[int] = None
    ) -> Tuple[bool, str]:
        """
        Delete a photo by ID.

        Fetches the stored image path before deletion so the corresponding
        file can be removed from the latest media tier after the database
        cascade completes.  Default-tier files are never touched.

        Args:
            photo_id: The ID of the photo to delete.
            requesting_user_id: The user requesting deletion (used to send
                admin_delete_photo notification to the owner when an admin deletes).

        Returns:
            Tuple[bool, str]: (success, message)

        Raises:
            Exception: Any database error is caught and logged; (False, message) returned.
        """
        try:
            owner_id: Optional[int] = None
            with SessionLocal() as db:
                if not PhotoModel.get_by_id(db, photo_id):
                    log_operation(
                        "photo.delete_photo",
                        "validation_error",
                        f"Photo {photo_id} not found",
                    )
                    return False, "Photo not found"

                # Capture owner before cascade wipes the record.
                photo_row = PhotoModel.get_by_id(db, photo_id)
                if photo_row and photo_row.get("albumId"):
                    album = AlbumModel.get_by_id(db, int(photo_row["albumId"]))
                    owner_id = album.get("creatorId") if album else None

                # Capture the image path before the cascade wipes it.
                image_record = PhotoImageModel.get_for_photo(db, photo_id)
                stored_image_path = image_record.get("image") if image_record else None

                # Delete all notifications related to this photo BEFORE deleting the photo
                # (FK constraint requires photo to exist when notification.photoId is not NULL)
                NotificationModel.delete_by_photo_id(db, photo_id)

                PhotoModel.delete(db, photo_id)
                db.commit()

            # Remove from latest tier only — default-tier files are preserved.
            if stored_image_path:
                delete_from_latest(stored_image_path)

            log_operation("photo.delete_photo", "success", f"Deleted photo {photo_id}")

            # Notify owner when an admin deletes their photo.
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
        image_path = image_record.get("image") if image_record else None
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
