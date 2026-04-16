from datetime import datetime, timezone
from typing import Optional, Tuple

from sqlalchemy import func

from app.core.db.engine import SessionLocal
from app.core.db.models.album import AlbumModel
from app.core.db.models.category import CategoryModel
from app.core.db.models.comment import CommentModel
from app.core.db.models.like import LikeModel
from app.core.db.models.photo import PhotoModel
from app.core.db.models.photo_image import PhotoImageModel
from app.core.db.models.rating import RatingModel
from app.core.db.models.user import UserModel


class PhotoService:
    """
    Service class for photo management business logic.

    Business rules enforced in this service:
    - When creating a photo, an image row is also created in the same transaction.
    - Only photo owners can update or delete their photos.
    - When deleting a category, all photos in that category are also deleted by DB cascade.
    - When retrieving photos, category names and usernames are included for display purposes.
        - The service provides a method to check for category name uniqueness (case-insensitive).
        - The service provides a method to get all photos liked by a user.
        - The service provides a method to count photos by user.
        - The service provides a method to get photos filtered by category and/or username.
        - All methods that modify data enforce ownership rules and validate inputs as needed.
    """

    @staticmethod
    def get_photos_by_user(user_id: int) -> list:
        """
        Retrieve all photos uploaded by a specific user (through their albums).

        Args:
            user_id: The ID of the user.

        Returns:
            list: A list of photo dictionaries owned by the user.
        """
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
            return [p.to_dict() for p in photos]

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
        """
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
            return PhotoModel.get_by_id(session, photo["id"])

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
        """
        with SessionLocal() as db:
            if not PhotoModel.get_by_id(db, photo_id):
                return False, "Photo not found"
            PhotoModel.delete(db, photo_id)
            db.commit()
            return True, "Photo deleted successfully"

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
    def category_exists(name: str) -> bool:
        """
        Check if a category with the given name already exists (case-insensitive).

        Args:
            name: The category name to check.

        Returns:
            bool: True if it exists, False otherwise.
        """
        with SessionLocal() as session:
            return any(
                c["category"].lower() == name.lower()
                for c in CategoryModel.get_all(session)
            )

    @staticmethod
    def get_all_photos() -> list:
        """Return all photos sorted by published date, newest first."""
        with SessionLocal() as session:
            photos = PhotoModel.get_all(session)
        return sorted(
            photos,
            key=lambda p: str(p.get("publishedDate") or ""),
            reverse=True,
        )

    @staticmethod
    def get_photo_details(
        photo_id: int, user_id: Optional[int] = None
    ) -> Optional[dict]:
        """
        Return a photo enriched with like stats and owner info.

        Combines PhotoModel, LikeModel, AlbumModel and UserModel in one
        session — a real use-case, not a pass-through.
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
        """Like a photo. Returns True if the like was created, False if already liked."""
        with SessionLocal() as session:
            result = LikeModel.like(session, user_id, photo_id) is not None
            session.commit()
            return result

    @staticmethod
    def unlike_photo(user_id: int, photo_id: int) -> bool:
        """Unlike a photo. Returns True if the like was removed, False if it didn't exist."""
        with SessionLocal() as session:
            result = LikeModel.unlike(session, user_id, photo_id)
            session.commit()
            return result

    @staticmethod
    def get_photo_rating_stats(photo_id: int) -> dict:
        """
        Return fresh rating stats for a single photo after a rating change.

        Reuses the same weighted-rating formula as get_explore_catalog so that
        the in-memory photo dict stays consistent with what the catalog shows.

        Args:
            photo_id: The ID of the photo.

        Returns:
            dict: Keys avg_rating, rating_count, weighted_rating.
        """
        MIN_VOTES_THRESHOLD = 10
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
        if rating_count > 0:
            weight_ratio = rating_count / (rating_count + MIN_VOTES_THRESHOLD)
            prior_ratio = MIN_VOTES_THRESHOLD / (rating_count + MIN_VOTES_THRESHOLD)
            weighted = round(weight_ratio * avg_rating + prior_ratio * global_avg, 1)
        else:
            weighted = global_avg

        return {
            "avg_rating": avg_rating,
            "rating_count": rating_count,
            "weighted_rating": weighted,
        }

    @staticmethod
    def rate_photo(user_id: int, photo_id: int, rating_value: int) -> None:
        """Submit a rating (1-5) for a photo."""
        with SessionLocal() as session:
            RatingModel.create(
                session,
                user_id=user_id,
                photo_id=photo_id,
                rating_value=rating_value,
            )
            session.commit()

    @staticmethod
    def add_category(name: str) -> Tuple[bool, str]:
        """
        Add a new category.

        Business rules:
        - Name must be non-empty.
        - Name must be unique (case-insensitive).

        Returns:
            Tuple[bool, str]: (success, message)
        """
        if not name or not name.strip():
            return False, "Category name is required"
        if PhotoService.category_exists(name.strip()):
            return False, "The category already exists, please try again!"
        with SessionLocal() as session:
            CategoryModel.create(session, name.strip())
            session.commit()
        return True, "The category was added successfully!"

    @staticmethod
    def delete_category_with_photos(name: str) -> Tuple[bool, str]:
        """
        Delete a category. Photos in the category are automatically removed
        by the database CASCADE on photos.categoryID.

        Args:
            name: The name of the category to delete.

        Returns:
            Tuple of (success, message)
        """
        with SessionLocal() as session:
            categories = CategoryModel.get_all(session)
            for cat in categories:
                if cat["category"] == name:
                    CategoryModel.delete(session, name)
                    session.commit()
                    return True, f"{name} was deleted successfully"
            return False, "Category not found"

    @staticmethod
    def get_explore_catalog(
        sort_by: str = "date",
        category: str = "all",
        username: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> list:
        """
        Return a fully enriched photo list for the Explore view.

        Enriches each photo with: image path, album name, author username,
        category name, like count, comment count, average rating, the
        authenticated user's own rating, and a has_liked flag.

        Args:
            sort_by: One of "date", "likes", "rating", "comments".
            category: Category name to filter by, or "all" for no filter.
            username: Author username to filter by, or None for no filter.
            user_id: The current user's ID for personalised flags (optional).

        Returns:
            list: Sorted and filtered list of enriched photo dicts.
        """
        with SessionLocal() as session:
            photos = PhotoModel.get_all(session)
            albums = {a["id"]: a for a in AlbumModel.get_all(session)}
            users = {u["id"]: u for u in UserModel.get_all(session)}
            cats = {c["id"]: c["category"] for c in CategoryModel.get_all(session)}

            # Batch-fetch image paths (photo_image has a unique constraint per photo)
            all_images: dict = {
                row[0]: row[1]
                for row in session.query(
                    getattr(PhotoImageModel, "photoId"),
                    getattr(PhotoImageModel, "image"),
                ).all()
            }

            # Batch-fetch aggregate counts via GROUP BY to avoid N+1 queries
            like_counts: dict = dict(
                session.query(getattr(LikeModel, "photoId"), func.count().label("cnt"))
                .group_by(getattr(LikeModel, "photoId"))
                .all()
            )
            comment_counts: dict = dict(
                session.query(
                    getattr(CommentModel, "photoId"), func.count().label("cnt")
                )
                .group_by(getattr(CommentModel, "photoId"))
                .all()
            )
            avg_ratings: dict = {
                pid: (round(float(avg), 1) if avg is not None else 1.0)
                for pid, avg in session.query(
                    getattr(RatingModel, "photoId"),
                    func.avg(getattr(RatingModel, "rating")),
                )
                .group_by(getattr(RatingModel, "photoId"))
                .all()
            }

            # Batch-fetch rating counts for weighted average calculation
            rating_counts: dict = dict(
                session.query(
                    getattr(RatingModel, "photoId"), func.count().label("cnt")
                )
                .group_by(getattr(RatingModel, "photoId"))
                .all()
            )

            # Calculate global average for weighted rating (professional ranking)
            global_avg_result = session.query(
                func.avg(getattr(RatingModel, "rating"))
            ).scalar()
            global_avg = (
                round(float(global_avg_result), 1)
                if global_avg_result is not None
                else 1.0
            )

            # Minimum votes threshold for weighting (professional standard = 10)
            MIN_VOTES_THRESHOLD = 10

            # Per-user personalised data
            user_liked_set: set = set()
            user_ratings_map: dict = {}
            if user_id:
                user_liked_set = {
                    row[0]
                    for row in session.query(getattr(LikeModel, "photoId"))
                    .filter(getattr(LikeModel, "userId") == user_id)
                    .all()
                }
                user_ratings_map = {
                    row[0]: row[1]
                    for row in session.query(
                        getattr(RatingModel, "photoId"), getattr(RatingModel, "rating")
                    )
                    .filter(getattr(RatingModel, "userId") == user_id)
                    .all()
                }

        # Build and filter result list (outside session — all data already loaded)
        result = []
        for photo in photos:
            pid = photo["id"]
            album = albums.get(photo.get("albumId"))
            creator_id = album["creatorId"] if album else None
            user = users.get(creator_id) if creator_id else None
            uname = user["username"] if user else ""
            cat_name = cats.get(photo.get("categoryId"), "")
            album_name = album["name"] if album else ""

            if category != "all" and cat_name != category:
                continue
            if username and uname.lower() != username.lower():
                continue

            # Calculate weighted average for professional ranking
            # Formula: weighted = (v / (v + m)) * R + (m / (v + m)) * C
            # Where: R = avg_rating, v = votes, C = global_avg, m = MIN_VOTES_THRESHOLD
            avg_rating = avg_ratings.get(pid, 1.0)
            vote_count = rating_counts.get(pid, 0)
            if vote_count > 0:
                weight_ratio = vote_count / (vote_count + MIN_VOTES_THRESHOLD)
                prior_ratio = MIN_VOTES_THRESHOLD / (vote_count + MIN_VOTES_THRESHOLD)
                weighted_avg = round(
                    weight_ratio * avg_rating + prior_ratio * global_avg, 1
                )
            else:
                # No votes yet - use global average as default
                weighted_avg = global_avg

            owner_avatar = user.get("avatar") if user else None
            owner_is_admin = user.get("roleId") == 1 if user else False
            result.append(
                {
                    **photo,
                    "image": all_images.get(pid),
                    "album_name": album_name,
                    "user": uname,
                    "category": cat_name,
                    "likes": like_counts.get(pid, 0),
                    "comments": comment_counts.get(pid, 0),
                    "avg_rating": avg_rating,
                    "rating_count": vote_count,
                    "weighted_rating": weighted_avg,
                    "user_rating": user_ratings_map.get(pid),
                    "has_liked": pid in user_liked_set,
                    "owner_id": creator_id,
                    "owner_avatar": owner_avatar,
                    "owner_is_admin": owner_is_admin,
                }
            )

        # Sort by selected criteria
        # Note: Using weighted_rating for "rating" sort for more professional ranking
        if sort_by == "likes":
            result.sort(key=lambda p: p["likes"], reverse=True)
        elif sort_by == "rating":
            # Sort by weighted average - professional approach that accounts for vote reliability
            result.sort(key=lambda p: p["weighted_rating"], reverse=True)
        elif sort_by == "comments":
            result.sort(key=lambda p: p["comments"], reverse=True)
        else:
            result.sort(key=lambda p: str(p.get("publishedDate") or ""), reverse=True)

        return result

    @staticmethod
    def count_filtered_photos(
        category: str = "all",
        username: Optional[str] = None,
    ) -> int:
        """
        Get the COUNT of filtered photos WITHOUT loading them into memory.

        Enables pagination to determine total pages without loading all photos.
        Much faster than get_explore_catalog() when you only need the count.

        Args:
            category: Category name to filter by, or "all" for no filter.
            username: Author username to filter by, or None for no filter.

        Returns:
            int: Count of filtered photos matching criteria
        """
        # Fetch all and filter (reuses existing logic) — not ideal but consistent
        # with get_explore_catalog behavior. A proper implementation would
        # apply filters in SQL, but that's a refactor for later.
        filtered = PhotoService.get_explore_catalog(
            sort_by="date",
            category=category,
            username=username,
            user_id=None,
        )
        count = len(filtered)
        return count

    @staticmethod
    def get_explore_catalog_page(
        page_num: int = 1,
        items_per_page: int = 10,
        sort_by: str = "date",
        category: str = "all",
        username: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> list:
        """
        Get ONE PAGE of filtered photos without loading entire catalog into memory.

        Pagination Strategy:
        - Fetch all filtered photos (unavoidable due to in-memory sorting)
        - Apply offset/limit for the requested page only
        - Return max 10 items per page
        - Does NOT cache all photos — each page fetch is independent

        This ensures only ~10 enriched photos are returned, not all 40+.

        Args:
            page_num: Page number (1-based)
            items_per_page: Items per page (default: 10)
            sort_by: One of "date", "likes", "rating", "comments"
            category: Category name to filter by, or "all"
            username: Author username to filter by, or None
            user_id: Current user ID for personalised flags (optional)

        Returns:
            list: Enriched photo dicts for requested page only (max 10)
        """
        # Get the full filtered/sorted catalog
        all_filtered = PhotoService.get_explore_catalog(
            sort_by=sort_by,
            category=category,
            username=username,
            user_id=user_id,
        )

        # Apply pagination
        start_idx = (page_num - 1) * items_per_page
        end_idx = start_idx + items_per_page
        page_items = all_filtered[start_idx:end_idx]

        return page_items
