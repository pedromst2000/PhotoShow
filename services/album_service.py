from typing import Optional

from db.models import AlbumModel


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

        Parameters:
            album_id: The ID of the album.

        Returns:
            dict or None: The album data if found, None otherwise.
        """
        return AlbumModel.get_by_id(album_id)

    @staticmethod
    def get_user_albums(user_id: int) -> list:
        """
        Retrieve all albums created by a specific user.

        Parameters:
            user_id: The ID of the user.

        Returns:
            list: A list of album dictionaries created by the user.
        """
        return AlbumModel.get_by_creator(user_id)

    @staticmethod
    def create_album(name: str, creator_id: int) -> dict:
        """
        Create a new album.

        Parameters:
            name: The name of the new album.
            creator_id: The ID of the user creating the album.

        Returns:
            dict: The newly created album data.
        """
        return AlbumModel.create(name=name, creatorID=creator_id)

    @staticmethod
    def rename_album(album_id: int, new_name: str) -> bool:
        """
        Rename an existing album.

        Parameters:
            album_id: The ID of the album to rename.
            new_name: The new name for the album.

        Returns:
            bool: True if renamed successfully, False otherwise.
        """
        album = AlbumModel.get_by_id(album_id)
        if album:
            return AlbumModel.update({**album, "name": new_name})
        return False

    @staticmethod
    def delete_album(album_id: int) -> bool:
        """
        Delete an album.

        Parameters:
            album_id: The ID of the album to delete.

        Returns:
            bool: True if deleted successfully, False otherwise.
        """
        return AlbumModel.delete(album_id)

    @staticmethod
    def get_album_id_by_name(user_id: int, album_name: str) -> Optional[int]:
        """
        Get album ID from album name for a specific user.

        Parameters:
            user_id: The ID of the user.
            album_name: The name of the album.

        Returns:
            int or None: The album ID if found, None otherwise.
        """
        albums = AlbumModel.get_by_creator(user_id)
        for album in albums:
            if album["name"] == album_name:
                return album["albumID"]
        return None

    @staticmethod
    def get_favorite_albums(user_id: int) -> list:
        """
        Retrieve all favorite albums for a specific user.

        Parameters:
            user_id: The ID of the user.

        Returns:
            list: A list of dicts with albumID and name for each favorited album.
        """
        from db.models import FavoriteModel

        favorites = FavoriteModel.get_all()
        if not favorites:
            return []
        albums = AlbumModel.get_all()
        return [
            {"albumID": fav["albumID"], "name": album["name"]}
            for fav in favorites
            for album in albums
            if fav["userID"] == user_id and fav["albumID"] == album["albumID"]
        ]

    @staticmethod
    def album_name_exists(album_name: str) -> bool:
        """
        Check if an album name already exists (case-insensitive).

        Parameters:
            album_name: The album name to check.

        Returns:
            bool: True if the name already exists, False otherwise.
        """
        albums = AlbumModel.get_all()
        return any(a["name"].lower() == album_name.lower() for a in albums)
