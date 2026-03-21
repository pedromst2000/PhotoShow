from datetime import datetime, timezone
from typing import Optional, Tuple

from db.models import (
    CategoryModel,
    LikeModel,
    PhotoImageModel,
    PhotoModel,
    RatingModel,
    UserModel,
)


class PhotoService:
    """
    Service class for photo management business logic.
    """

    @staticmethod
    def get_all_photos() -> list:
        """
        Retrieve all photos from the database.

        Returns:
            list: A list of all photo dictionaries.
        """
        return PhotoModel.get_all()

    @staticmethod
    def get_photo_by_id(photo_id: int) -> Optional[dict]:
        """
        Retrieve a specific photo by ID.

        Parameters:
            photo_id: The ID of the photo.

        Returns:
            dict or None: The photo data if found, None otherwise.
        """
        return PhotoModel.get_by_id(photo_id)

    @staticmethod
    def get_photos_by_album(album_id: int) -> list:
        """
        Retrieve all photos in a specific album.

        Parameters:
            album_id: The ID of the album.

        Returns:
            list: A list of photo dictionaries in the album.
        """
        return PhotoModel.get_by_album(album_id)

    @staticmethod
    def get_photos_by_user(user_id: int) -> list:
        """
        Retrieve all photos uploaded by a specific user (through their albums).

        Parameters:
            user_id: The ID of the user.

        Returns:
            list: A list of photo dictionaries owned by the user.
        """
        from db.models import AlbumModel

        albums = AlbumModel.get_by_creator(user_id)
        result = []
        for album in albums:
            result.extend(PhotoModel.get_by_album(album["id"]))
        return result

    @staticmethod
    def get_photos_by_category(category_name: str) -> list:
        """
        Retrieve all photos in a specific category.

        Parameters:
            category_name: The name of the category.

        Returns:
            list: A list of photo dictionaries in the category.
        """
        categories = CategoryModel.get_all()
        category = next((c for c in categories if c["category"] == category_name), None)
        if category:
            return PhotoModel.get_by_category(category["id"])
        return []

    @staticmethod
    def get_filtered_photos(category: str = "all", username: str = None) -> list:
        """
        Retrieve photos filtered by category and/or username.
        Enriches photos with category name and username.

        Parameters:
            category: The category to filter by. Use "all" for all categories.
            username: The username to filter by. None to not filter by user.

        Returns:
            list: A list of enriched photo dictionaries.
        """
        photos = PhotoModel.get_all()
        categories = CategoryModel.get_all()
        users = UserModel.get_all()
        from db.models import AlbumModel

        albums = AlbumModel.get_all()

        # Helper to get category name for a photo
        def get_category_name(photo: dict) -> str:
            """
            Get the category name for a photo.

            Parameters:
                photo (dict): The photo dictionary containing "categoryID".
            Returns:
                str: The name of the category, or empty string if not found.
            """

            match = next((c for c in categories if c["id"] == photo["categoryId"]), {})
            return match.get("category", "")

        # Helper to get username for a photo via its album's creatorID
        def get_username(photo: dict) -> str:
            """
            Get the username for a photo via the owning album's creatorID.

            Parameters:
                photo (dict): The photo dictionary containing "albumID".
            Returns:
                str: The username of the photo's owner, or empty string if not found.
            """

            album = next((a for a in albums if a["id"] == photo["albumId"]), None)
            if not album:
                return ""
            match = next((u for u in users if u["id"] == album["creatorId"]), {})
            return match.get("username", "")

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
        album_id: int = None,
        category_id: int = None,
        description: str = "",
        published_date=None,
    ) -> dict:
        """

        Create a new photo entry in the database.

        Parameters:
            image_path (str): The file path of the photo image.
            album_id (int, optional): The ID of the album to associate with the photo. Defaults to None.
            category_id (int, optional): The ID of the category to associate with the photo. Defaults to None.
            description (str, optional): A description for the photo. Defaults to an empty string.
            published_date (datetime, optional): The date and time when the photo was published. Defaults to current UTC time if not provided.

        Returns:
            dict: The created photo as a dictionary.
        """

        # Create photo row first (without image), then create PhotoImage
        photo = PhotoModel.create(
            description=description,
            publishedDate=published_date or datetime.now(timezone.utc),
            categoryId=category_id,
            albumId=album_id,
        )
        PhotoImageModel.create(photo_id=photo["id"], image=image_path)
        # return enriched photo dict
        return PhotoModel.get_by_id(photo["id"])

    @staticmethod
    def delete_photo(photo_id: int) -> bool:
        """
        Delete a photo.

        Parameters:
            photo_id: The ID of the photo to delete.

        Returns:
            bool: True if deleted successfully, False otherwise.
        """
        return PhotoModel.delete(photo_id)

    @staticmethod
    def delete_photo_for_user(user_id: int, photo_id: int) -> bool:
        """
        Delete a photo if the given user is the owner (via album creator) or an admin.

        Parameters:
            user_id: The ID of the requesting user.
            photo_id: The ID of the photo to delete.

        Returns:
            bool: True if deleted, False otherwise.
        """
        photo = PhotoModel.get_by_id(photo_id)
        if not photo:
            return False
        from db.models import AlbumModel

        album = (
            AlbumModel.get_by_id(photo.get("albumId")) if photo.get("albumId") else None
        )
        owner_id = album["creatorId"] if album else None
        # if owner matches, delete
        if owner_id == user_id:
            return PhotoModel.delete(photo_id)
        # otherwise deny
        return False

    @staticmethod
    def update_photo(photo_id: int, updates: dict) -> bool:
        """
        Update photo information.

        Parameters:
            photo_id: The ID of the photo to update.
            updates: Dictionary of fields to update.

        Returns:
            bool: True if updated successfully, False otherwise.
        """
        photo = PhotoModel.get_by_id(photo_id)
        if photo:
            return PhotoModel.update({**photo, **updates})
        return False

    @staticmethod
    def update_photo_for_user(user_id: int, photo_id: int, updates: dict) -> bool:
        """
        Update a photo if the given user owns it.

        Parameters:
            user_id: The ID of the requesting user.
            photo_id: The ID of the photo to update.
            updates: Fields to update.

        Returns:
            bool: True if updated, False otherwise.
        """
        photo = PhotoModel.get_by_id(photo_id)
        if not photo:
            return False
        from db.models import AlbumModel

        album = (
            AlbumModel.get_by_id(photo.get("albumId")) if photo.get("albumId") else None
        )
        owner_id = album["creatorId"] if album else None
        if owner_id == user_id:
            return PhotoModel.update({**photo, **updates})
        return False

    @staticmethod
    def count_photos_by_user(user_id: int) -> int:
        """
        Count all photos uploaded by a specific user.

        Parameters:
            user_id: The ID of the user.

        Returns:
            int: The number of photos the user has uploaded.
        """
        return len(PhotoService.get_photos_by_user(user_id))

    @staticmethod
    def like_photo(user_id: int, photo_id: int) -> bool:
        """
        Like a photo.

        Parameters:
            user_id (int): The ID of the user liking the photo.
            photo_id (int): The ID of the photo to like.
        Returns:
            bool: True if the photo was liked successfully, False otherwise.
        """

        return LikeModel.like(user_id, photo_id) is not None

    @staticmethod
    def add_rating(user_id: int, photo_id: int, rating_value: int) -> dict:
        """
        Add a rating (1-5) to a photo by a user.

        Parameters:
            user_id (int): The ID of the user adding the rating.
            photo_id (int): The ID of the photo being rated.
            rating_value (int): The rating value (1-5).
        Returns:
            dict: The created rating as a dictionary.
        """
        return RatingModel.create(
            user_id=user_id, photo_id=photo_id, rating_value=rating_value
        )

    @staticmethod
    def get_average_rating(photo_id: int) -> float:
        from db.models.rating import RatingModel

        return RatingModel.get_average_for_photo(photo_id) or 0.0

    @staticmethod
    def unlike_photo(user_id: int, photo_id: int) -> bool:
        """
        Unlike a photo.

        Parameters:
            user_id (int): The ID of the user unliking the photo.
            photo_id (int): The ID of the photo to unlike.
        Returns:
            bool: True if the photo was unliked successfully, False otherwise.

        """
        return LikeModel.unlike(user_id, photo_id)

    @staticmethod
    def has_liked(user_id: int, photo_id: int) -> bool:
        """
        Check if a user has liked a specific photo.

        Parameters:
            user_id (int): The ID of the user.
            photo_id (int): The ID of the photo to check.
        Returns:
            bool: True if the user has liked the photo, False otherwise.
        """
        return LikeModel.has_liked(user_id, photo_id)

    @staticmethod
    def count_likes(photo_id: int) -> int:
        """
        Count the number of likes for a specific photo.

        Parameters:
            photo_id (int): The ID of the photo to count likes for.
        Returns:
            int: The number of likes the photo has received.
        """
        return LikeModel.count_by_photo(photo_id)

    @staticmethod
    def get_liked_photos(user_id: int) -> list:
        """
        Get all photos liked by a specific user.

        Parameters:
            user_id (int): The ID of the user to get liked photos for.
        Returns:
            list: A list of photo dictionaries that the user has liked.
        """
        like_rows = LikeModel.get_liked_photos(user_id)
        return [
            PhotoModel.get_by_id(r["photoId"])
            for r in like_rows
            if PhotoModel.get_by_id(r["photoId"])
        ]

    @staticmethod
    def get_all_categories() -> list:
        """
        Retrieve all categories from the database.

        Returns:
            list: A list of category dictionaries.
        """
        return CategoryModel.get_all()

    @staticmethod
    def get_category_names() -> list:
        """
        Retrieve all category names.

        Returns:
            list: A list of category name strings.
        """
        return [c["category"] for c in CategoryModel.get_all()]

    @staticmethod
    def category_exists(name: str) -> bool:
        """
        Check if a category with the given name already exists (case-insensitive).

        Parameters:
            name: The category name to check.

        Returns:
            bool: True if it exists, False otherwise.
        """
        return any(
            c["category"].lower() == name.lower() for c in CategoryModel.get_all()
        )

    @staticmethod
    def create_category(name: str) -> None:
        """
        Create a new category.

        Parameters:
            name: The name of the category to create.
        """
        CategoryModel.create(name)

    @staticmethod
    def delete_category_with_photos(name: str) -> Tuple[bool, str]:
        """
        Delete a category. Photos in the category are automatically removed
        by the database CASCADE on photos.categoryID.

        Parameters:
            name: The name of the category to delete.

        Returns:
            Tuple of (success, message)
        """
        categories = CategoryModel.get_all()
        for cat in categories:
            if cat["category"] == name:
                CategoryModel.delete(name)
                return True, f"{name} was deleted successfully"
        return False, "Category not found"
