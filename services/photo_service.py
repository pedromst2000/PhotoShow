from datetime import datetime, timezone
from typing import Optional, Tuple

from db.models import CategoryModel, LikeModel, PhotoModel, UserModel


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
        Retrieve all photos uploaded by a specific user.

        Parameters:
            user_id: The ID of the user.

        Returns:
            list: A list of photo dictionaries uploaded by the user.
        """
        return PhotoModel.get_by_user(user_id)

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
            return PhotoModel.get_by_category(category["categoryID"])
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

        # Helper to get category name for a photo
        def get_category_name(photo: dict) -> str:
            """
            Get the category name for a photo.

            Parameters:
                photo (dict): The photo dictionary containing "categoryID".
            Returns:
                str: The name of the category, or empty string if not found.
            """

            match = next(
                (c for c in categories if c["categoryID"] == photo["categoryID"]), {}
            )
            return match.get("category", "")

        # Helper to get username for a photo
        def get_username(photo: dict) -> str:
            """
            Get the username for a photo.

            Parameters:
                photo (dict): The photo dictionary containing "userID".
            Returns:
                str: The username of the photo's uploader, or empty string if not found.
            """

            match = next((u for u in users if u["userID"] == photo["userID"]), {})
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
        user_id: int,
        album_id: int = None,
        category_id: int = None,
        description: str = "",
        published_date=None,
    ) -> dict:
        """

        Create a new photo entry in the database.

        Parameters:
            image_path (str): The file path of the photo image.
            user_id (int): The ID of the user uploading the photo.
            album_id (int, optional): The ID of the album to associate with the photo. Defaults to None.
            category_id (int, optional): The ID of the category to associate with the photo. Defaults to None.
            description (str, optional): A description for the photo. Defaults to an empty string.
            published_date (datetime, optional): The date and time when the photo was published. Defaults to current UTC time if not provided.

        Returns:
            dict: The created photo as a dictionary.
        """

        return PhotoModel.create(
            image=image_path,
            userID=user_id,
            albumID=album_id,
            categoryID=category_id,
            description=description,
            publishedDate=published_date or datetime.now(timezone.utc),
        )

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
    def count_photos_by_user(user_id: int) -> int:
        """
        Count all photos uploaded by a specific user.

        Parameters:
            user_id: The ID of the user.

        Returns:
            int: The number of photos the user has uploaded.
        """
        return PhotoModel.count_by_user(user_id)

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
            PhotoModel.get_by_id(r["photoID"])
            for r in like_rows
            if PhotoModel.get_by_id(r["photoID"])
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
        Delete a category and cascade-delete all photos in it.

        Parameters:
            name: The name of the category to delete.

        Returns:
            Tuple of (success, message)
        """
        categories = CategoryModel.get_all()
        photos = PhotoModel.get_all()
        for cat in categories:
            if cat["category"] == name:
                photo_ids = [
                    p["photoID"] for p in photos if p["categoryID"] == cat["categoryID"]
                ]
                if photo_ids:
                    PhotoModel.delete_many(*photo_ids)
                CategoryModel.delete(name)
                return True, f"{name} was deleted successfully"
        return False, "Category not found"
