from datetime import datetime, timezone
from typing import Optional, Tuple

from sqlalchemy import func

from app.core.db.engine import SessionLocal
from app.core.db.models.album import AlbumModel
from app.core.db.models.category import CategoryModel
from app.core.db.models.like import LikeModel
from app.core.db.models.photo import PhotoModel
from app.core.db.models.photo_image import PhotoImageModel
from app.core.db.models.rating import RatingModel
from app.core.db.models.user import UserModel
from app.core.services.helpers.weighted_rating import calculate_weighted_rating
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
    def get_photos_by_user(user_id: int) -> list:
        """
        Retrieve all photos uploaded by a specific user (through their albums).

        Args:
            user_id: The ID of the user.

        Returns:
            list: A list of photo dictionaries owned by the user.

        Raises:
            Exception: Any database error is caught and logged; empty list returned.
        """
        try:
            with SessionLocal() as session:
                albums = AlbumModel.get_by_creator(session, user_id)
                # Batch-fetch photos for all the user's albums to avoid N+1 queries
                album_ids = [a["id"] for a in albums] if albums else []
                if not album_ids:
                    return []
                photos = (
                    session.query(PhotoModel)
                    .filter(getattr(PhotoModel, "albumId").in_(album_ids))
                    .all()
                )
            log_operation(
                "photo.get_photos_by_user",
                "success",
                f"Retrieved {len(photos)} photos for user {user_id}",
                user_id=user_id,
            )
            return [p.to_dict() for p in photos]
        except Exception as e:
            log_exception("photo.get_photos_by_user", e, user_id=user_id)
            return []

    @staticmethod
    def get_photos_by_album(album_id: int) -> list:
        """
        Get all photos in a specific album.

        Args:
            album_id: The album's ID.

        Returns:
            list: List of photo dictionaries in the album.

        Raises:
            Exception: Any database error is caught and logged; empty list returned.
        """
        try:
            with SessionLocal() as session:
                photos = PhotoModel.get_by_album(session, album_id)
            log_operation(
                "photo.get_photos_by_album",
                "success",
                f"Retrieved {len(photos)} photos from album {album_id}",
            )
            return photos
        except Exception as e:
            log_exception(
                "photo.get_photos_by_album", e, context={"album_id": album_id}
            )
            return []

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
    def get_photos_by_category(category_name: str) -> list:
        """
        Retrieve all photos in a specific category.

        Args:
            category_name: The name of the category.

        Returns:
            list: A list of photo dictionaries in the category.
        """
        with SessionLocal() as session:
            categories = CategoryModel.get_all(session)
            category = next(
                (c for c in categories if c["category"] == category_name), None
            )
            if category:
                return PhotoModel.get_by_category(session, category["id"])
            return []

    @staticmethod
    def get_filtered_photos(
        category: str = "all", username: Optional[str] = None
    ) -> list:
        """
        Retrieve photos filtered by category and/or username.
        Enriches photos with category name and username.

        Args:
            category: The category to filter by. Use "all" for all categories.
            username: The username to filter by. None to not filter by user.

        Returns:
            list: A list of enriched photo dictionaries.
        """
        with SessionLocal() as session:
            photos = PhotoModel.get_all(session)
            categories = CategoryModel.get_all(session)
            users = UserModel.get_all(session)
            albums = AlbumModel.get_all(session)

        # Helper to get category name for a photo
        def get_category_name(photo: dict) -> str:
            m: dict = next(
                (c for c in categories if c["id"] == photo["categoryId"]), {}
            )
            return str(m.get("category", ""))

        # Helper to get username for a photo via its album's creatorID
        def get_username(photo: dict) -> str:
            album = next((a for a in albums if a["id"] == photo["albumId"]), None)
            if not album:
                return ""
            m: dict = next((u for u in users if u["id"] == album["creatorId"]), {})
            return str(m.get("username", ""))

        result = []
        for photo in photos:
            cat_name = get_category_name(photo)
            user_name = get_username(photo)

            # Filter by category
            if category != "all" and cat_name != category:
                continue

            # Filter by username
            if username and user_name != username:
                continue

            enriched_photo = {
                **photo,
                "category": cat_name,
                "user": user_name,
            }
            result.append(enriched_photo)

        return result

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
            return PhotoModel.get_by_id(session, photo["id"])
        except Exception as e:
            log_exception(
                "photo.create_photo",
                e,
                context={"album_id": album_id, "image_path": image_path},
            )
            return None

    @staticmethod
    def delete_photo(photo_id: int) -> Tuple[bool, str]:
        """
        Delete a photo by ID.

        The database cascade handles removal of all related records
        (likes, comments, ratings, images).

        Args:
            photo_id: The ID of the photo to delete.

        Returns:
            Tuple[bool, str]: (success, message)

        Raises:
            Exception: Any database error is caught and logged; (False, message) returned.
        """
        try:
            with SessionLocal() as db:
                if not PhotoModel.get_by_id(db, photo_id):
                    log_operation(
                        "photo.delete_photo",
                        "validation_error",
                        f"Photo {photo_id} not found",
                    )
                    return False, "Photo not found"
                PhotoModel.delete(db, photo_id)
                db.commit()
            log_operation("photo.delete_photo", "success", f"Deleted photo {photo_id}")
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
    def get_all_photos() -> list:
        """
        Return all photos sorted by published date, newest first.

        Returns:
            list: A list of photo dictionaries sorted by published date descending.

        Raises:
            Exception: Any database error is caught and logged; empty list returned.
        """
        try:
            with SessionLocal() as session:
                photos = PhotoModel.get_all(session)
            log_operation(
                "photo.get_all_photos", "success", f"Retrieved {len(photos)} photos"
            )
            return sorted(
                photos,
                key=lambda p: str(p.get("publishedDate") or ""),
                reverse=True,
            )
        except Exception as e:
            log_exception("photo.get_all_photos", e)
            return []

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
        # Return both 'username' (legacy) and 'user' (consistent across services)
        username = owner["username"] if owner else None
        owner_is_admin = owner["roleId"] == 1 if owner else False
        return {
            **photo,
            "likes": likes,
            "has_liked": has_liked,
            "username": username,
            "user": username,
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
        with SessionLocal() as session:
            result = LikeModel.like(session, user_id, photo_id) is not None
            session.commit()
            return result

    @staticmethod
    def unlike_photo(user_id: int, photo_id: int) -> bool:
        """
        Unlike a photo.

        Args:
            user_id: The ID of the user unliking the photo.
            photo_id: The ID of the photo to unlike.

        Returns:
            bool: True if the like was removed, False if it didn't exist.
        """
        with SessionLocal() as session:
            result = LikeModel.unlike(session, user_id, photo_id)
            session.commit()
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
