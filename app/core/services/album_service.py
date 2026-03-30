from typing import Optional

from app.core.db.models import AlbumModel


class AlbumService:
    """
    Service class for album management business logic.
    """

    @staticmethod
    def get_all_albums() -> list:
        """
        Retrieve all albums from the database.

        Returns:
            list: A list of all album dictionaries.
        """
        return AlbumModel.get_all()

    @staticmethod
    def get_album_by_id(album_id: int) -> Optional[dict]:
        """
        Retrieve a specific album by ID.

        Args:
            album_id: The ID of the album.

        Returns:
            dict or None: The album data if found, None otherwise.
        """
        return AlbumModel.get_by_id(album_id)

    @staticmethod
    def get_user_albums(user_id: int) -> list:
        """
        Retrieve all albums created by a specific user.

        Args:
            user_id: The ID of the user.

        Returns:
            list: A list of album dictionaries created by the user.
        """
        return AlbumModel.get_by_creator(user_id)

    @staticmethod
    def create_album(name: str, creator_id: int) -> dict:
        """
        Create a new album.

        Args:
            name: The name of the new album.
            creator_id: The ID of the user creating the album.

        Returns:
            dict: The newly created album data.
        """
        # application-level validation
        trimmed = name.strip() if name is not None else ""
        if not trimmed:
            raise ValueError("Album name is required")
        if len(trimmed) > 50:
            raise ValueError("Album name too long (max 50 characters)")

        # ensure user doesn't already have an album with the same name (case-insensitive)
        existing_id = AlbumService.get_album_id_by_name(creator_id, trimmed)
        if existing_id is not None:
            raise ValueError("You already have an album with that name")

        return AlbumModel.create(name=trimmed, creatorId=creator_id)

    @staticmethod
    def rename_album(album_id: int, new_name: str) -> bool:
        """
        Rename an existing album.

        Args:
            album_id: The ID of the album to rename.
            new_name: The new name for the album.

        Returns:
            bool: True if renamed successfully, False otherwise.
        """
        trimmed = new_name.strip() if new_name is not None else ""
        if not trimmed:
            raise ValueError("Album name is required")
        if len(trimmed) > 50:
            raise ValueError("Album name too long (max 50 characters)")

        album = AlbumModel.get_by_id(album_id)
        if not album:
            return False

        # prevent renaming to a name already used by the same creator
        existing_id = AlbumService.get_album_id_by_name(album["creatorId"], trimmed)
        if existing_id is not None and existing_id != album_id:
            raise ValueError("You already have an album with that name")

        return AlbumModel.update({**album, "name": trimmed})

    @staticmethod
    def rename_album_for_user(
        user_id: int, album_id: int, new_name: str, is_admin: bool = False
    ) -> bool:
        """
        Rename an album after verifying ownership.

        Args:
            user_id: The ID of the requesting user.
            album_id: The ID of the album.
            new_name: The new name for the album.
            is_admin: Whether the requesting user is an admin.

        Returns:
            bool: True if renamed successfully.

        Raises:
            ValueError: If album not found, ownership fails, or name is invalid.
        """
        album = AlbumModel.get_by_id(album_id)
        if not album:
            raise ValueError("Album not found")
        if album["creatorId"] != user_id and not is_admin:
            raise ValueError("You can only rename your own albums")
        return AlbumService.rename_album(album_id, new_name)

    @staticmethod
    def delete_album(album_id: int) -> bool:
        """
        Delete an album.

        Args:
            album_id: The ID of the album to delete.

        Returns:
            bool: True if deleted successfully, False otherwise.
        """
        return AlbumModel.delete(album_id)

    @staticmethod
    def delete_album_for_user(
        user_id: int, album_id: int, is_admin: bool = False
    ) -> bool:
        """
        Delete an album after verifying ownership.

        Args:
            user_id: The ID of the requesting user.
            album_id: The ID of the album to delete.
            is_admin: Whether the requesting user is an admin.

        Returns:
            bool: True if deleted successfully.

        Raises:
            ValueError: If album not found or ownership check fails.
        """
        album = AlbumModel.get_by_id(album_id)
        if not album:
            raise ValueError("Album not found")
        if album["creatorId"] != user_id and not is_admin:
            raise ValueError("You can only delete your own albums")
        return AlbumModel.delete(album_id)

    @staticmethod
    def get_album_id_by_name(user_id: int, album_name: str) -> Optional[int]:
        """
        Get album ID from album name for a specific user.

        Args:
            user_id: The ID of the user.
            album_name: The name of the album.

        Returns:
            int or None: The album ID if found, None otherwise.
        """
        albums = AlbumModel.get_by_creator(user_id)
        target = album_name.strip().lower()
        for album in albums:
            if album["name"].strip().lower() == target:
                return album["id"]
        return None

    @staticmethod
    def get_favorite_albums(user_id: int) -> list:
        """
        Retrieve all favorite albums for a specific user.

        Args:
            user_id: The ID of the user.

        Returns:
            list: A list of dicts with albumID and name for each favorited album.
        """
        from db.models import FavoriteModel

        favorites = FavoriteModel.get_by_user(user_id)
        if not favorites:
            return []
        result = []
        for fav in favorites:
            album = AlbumModel.get_by_id(fav["albumId"])
            if album:
                result.append({"albumId": fav["albumId"], "name": album["name"]})
        return result

    @staticmethod
    def album_name_exists(album_name: str) -> bool:
        """
        Check if an album name already exists (case-insensitive).

        Args:
            album_name: The album name to check.

        Returns:
            bool: True if the name already exists, False otherwise.
        """
        albums = AlbumModel.get_all()
        return any(a["name"].lower() == album_name.lower() for a in albums)
