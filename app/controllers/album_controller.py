from typing import List, Optional, Tuple

from app.core.services.album_service import AlbumService
from app.core.state.session import session


class AlbumController:
    """
    Controller for album operations.

    Coordinates between views and services for:
    - Creating albums
    - Listing albums
    - Editing albums
    - Deleting albums
    """

    @staticmethod
    def get_user_albums(user_id: int = None) -> List[dict]:
        """
        Get albums for a user.

        Args:
            user_id: The user's ID. If None, uses current user.

        Returns:
            list: List of album dictionaries.
        """
        target_user_id = user_id if user_id is not None else session.user_id
        if target_user_id is None:
            return []
        return AlbumService.get_user_albums(target_user_id)

    @staticmethod
    def get_all_albums() -> List[dict]:
        """
        Get all albums in the system.

        Returns:
            list: List of all album dictionaries.
        """
        return AlbumService.get_all_albums()

    @staticmethod
    def get_album(album_id: int) -> Optional[dict]:
        """
        Get a specific album by ID.

        Args:
            album_id: The album's ID.

        Returns:
            dict or None: The album data if found.
        """
        return AlbumService.get_album_by_id(album_id)

    @staticmethod
    def create_album(name: str) -> Tuple[bool, str]:
        """
        Create a new album for the current user.

        Args:
            name: The name for the new album.

        Returns:
            Tuple of (success, message)
        """
        if not session.is_authenticated:
            return False, "You must be logged in to create an album"

        if not name or not name.strip():
            return False, "Album name is required"

        try:
            AlbumService.create_album(name.strip(), session.user_id)
            return True, f"Album '{name}' created successfully"
        except Exception as e:
            return False, f"Failed to create album: {str(e)}"

    @staticmethod
    def rename_album(album_id: int, new_name: str) -> Tuple[bool, str]:
        """
        Rename an existing album.

        Args:
            album_id: The ID of the album to rename.
            new_name: The new name for the album.

        Returns:
            Tuple of (success, message)
        """
        if not session.is_authenticated:
            return False, "You must be logged in to rename an album"

        if not new_name or not new_name.strip():
            return False, "New album name is required"

        try:
            AlbumService.rename_album_for_user(
                session.user_id, album_id, new_name, session.is_admin
            )
            return True, f"Album renamed to '{new_name.strip()}'"
        except ValueError as e:
            return False, str(e)

    @staticmethod
    def delete_album(album_id: int) -> Tuple[bool, str]:
        """
        Delete an album.

        Args:
            album_id: The ID of the album to delete.

        Returns:
            Tuple of (success, message)
        """
        if not session.is_authenticated:
            return False, "You must be logged in to delete an album"

        try:
            if AlbumService.delete_album_for_user(
                session.user_id, album_id, session.is_admin
            ):
                return True, "Album deleted successfully"
            return False, "Failed to delete album"
        except ValueError as e:
            return False, str(e)

    @staticmethod
    def get_album_id_by_name(album_name: str, user_id: int = None) -> Optional[int]:
        """
        Get album ID from album name for a user.

        Args:
            album_name: The name of the album.
            user_id: The user's ID. If None, uses current user.

        Returns:
            int or None: The album ID if found.
        """
        target_user_id = user_id if user_id is not None else session.user_id
        if target_user_id is None:
            return None
        return AlbumService.get_album_id_by_name(target_user_id, album_name)

    @staticmethod
    def get_favorite_albums(user_id: int = None) -> List[dict]:
        """
        Get favorite albums for a user.

        Args:
            user_id: The user's ID. If None, uses current user.

        Returns:
            list: List of dicts with albumID and name.
        """
        target_user_id = user_id if user_id is not None else session.user_id
        if target_user_id is None:
            return []
        return AlbumService.get_favorite_albums(target_user_id)

    @staticmethod
    def album_name_exists(album_name: str) -> bool:
        """
        Check whether an album name already exists system-wide (case-insensitive).

        Args:
            album_name: The album name to check.

        Returns:
            bool: True if the name exists, False otherwise.
        """
        return AlbumService.album_name_exists(album_name)
