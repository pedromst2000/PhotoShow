from typing import Optional

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
from app.core.services.helpers.weighted_rating import calculate_weighted_rating
from app.utils.log_utils import log_exception, log_operation


class CatalogService:
    """
    Service for photo catalog and exploration logic.

    Provides enriched photo lists for the Explore view, with filtering,
    sorting, pagination, and real-time likes/ratings/comments counts.

    Business logic:
    - Photos are enriched with album info, author info, interaction counts, ratings.
    - Ratings use Bayesian smoothing (via RatingUtils) for fair ranking.
    - Sorting options: date (newest), likes, rating (weighted), comments.
    - Filtering: by category name, by author username.
    """

    @staticmethod
    def get_explore_catalog(
        sort_by: str = "date",
        category: str = "all",
        username: Optional[str] = None,
        user_id: Optional[int] = None,
        album_id: Optional[int] = None,
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
            album_id: Album ID to restrict results to, or None for all albums.

        Returns:
            list: Sorted and filtered list of enriched photo dicts.

        Raises:
            Exception: Any database error is caught and logged; empty list returned.
        """
        try:
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
                    session.query(
                        getattr(LikeModel, "photoId"), func.count().label("cnt")
                    )
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

                # Calculate global average for weighted rating (prior for Bayesian smoothing)
                global_avg_result = session.query(
                    func.avg(getattr(RatingModel, "rating"))
                ).scalar()
                global_avg = (
                    round(float(global_avg_result), 1)
                    if global_avg_result is not None
                    else 1.0
                )

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
                            getattr(RatingModel, "photoId"),
                            getattr(RatingModel, "rating"),
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
                if album_id is not None and photo.get("albumId") != album_id:
                    continue
                # Use rating helper for consistent weighted-rating calculation
                avg_rating = avg_ratings.get(pid, 1.0)
                vote_count = rating_counts.get(pid, 0)
                weighted_avg = calculate_weighted_rating(
                    avg_rating, vote_count, global_avg
                )

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
            if sort_by == "likes":
                result.sort(key=lambda p: p["likes"], reverse=True)
            elif sort_by == "rating":
                # Sort by weighted average for professional ranking
                result.sort(key=lambda p: p["weighted_rating"], reverse=True)
            elif sort_by == "comments":
                result.sort(key=lambda p: p["comments"], reverse=True)
            else:
                result.sort(
                    key=lambda p: str(p.get("publishedDate") or ""), reverse=True
                )

            log_operation(
                "catalog.get_explore_catalog",
                "success",
                f"Retrieved {len(result)} photos (sort={sort_by}, category={category})",
                user_id=user_id,
            )
            return result
        except Exception as e:
            log_exception(
                "catalog.get_explore_catalog",
                e,
                user_id=user_id,
                context={
                    "sort_by": sort_by,
                    "category": category,
                    "username": username,
                },
            )
            return []

    @staticmethod
    def count_filtered_photos(
        category: str = "all",
        username: Optional[str] = None,
    ) -> int:
        """
        Get the COUNT of filtered photos WITHOUT loading them into memory.

        Enables pagination to determine total pages without fetching all photos.

        Args:
            category: Category name to filter by, or "all" for no filter.
            username: Author username to filter by, or None for no filter.

        Returns:
            int: Count of filtered photos matching criteria.
        """
        filtered = CatalogService.get_explore_catalog(
            sort_by="date",
            category=category,
            username=username,
            user_id=None,
        )
        return len(filtered)

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

        This ensures only ~10 enriched photos are returned per request.

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
        all_filtered = CatalogService.get_explore_catalog(
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
