from typing import Optional

from app.core.db.engine import SessionLocal
from app.core.db.models.album import AlbumModel
from app.core.db.models.favorite import FavoriteModel
from app.utils.log_utils import log_exception, log_operation


class AlbumService:
    """
    Service class for album management business logic.

    Business rules enforced in this service:
    - Album names must be non-empty and max 50 characters.
    - Users cannot have multiple albums with the same name (case-insensitive).
    - Only album creators (or admins) can rename or delete albums.
        - Deleting an album also deletes all associated photos (handled by DB cascade).
        - When renaming, the new name must also pass validation and uniqueness checks.
        - Favorite albums are retrieved with their names for display purposes.
    """

    @staticmethod
    def get_user_albums(user_id: int) -> list:
        """
        Get all albums for a specific user.

        Args:
            user_id: The ID of the user.

        Returns:
            list: List of album dictionaries.

        Raises:
            Exception: Any database error is caught and logged; empty list returned.
        """
        try:
            with SessionLocal() as session:
                albums = AlbumModel.get_by_creator(session, user_id)
            log_operation(
                "album.get_user_albums",
                "success",
                f"Retrieved {len(albums)} albums for user {user_id}",
                user_id=user_id,
            )
            return albums
        except Exception as e:
            log_exception("album.get_user_albums", e, user_id=user_id)
            return []

    @staticmethod
    def get_all_albums() -> list:
        """
        Get all albums in the system.

        Returns:
            list: List of all album dictionaries.

        Raises:
            Exception: Any database error is caught and logged; empty list returned.
        """
        try:
            with SessionLocal() as session:
                albums = AlbumModel.get_all(session)
            log_operation(
                "album.get_all_albums", "success", f"Retrieved {len(albums)} albums"
            )
            return albums
        except Exception as e:
            log_exception("album.get_all_albums", e)
            return []

    @staticmethod
    def get_album(album_id: int) -> Optional[dict]:
        """
        Get a specific album by ID.

        Args:
            album_id: The album's ID.

        Returns:
            dict or None: The album data if found.

        Raises:
            Exception: Any database error is caught and logged; None returned.
        """
        try:
            with SessionLocal() as session:
                album = AlbumModel.get_by_id(session, album_id)
            if album:
                log_operation(
                    "album.get_album", "success", f"Retrieved album {album_id}"
                )
            return album
        except Exception as e:
            log_exception("album.get_album", e, context={"album_id": album_id})
            return None

    @staticmethod
    def album_name_exists(album_name: str) -> bool:
        """
        Check whether an album name already exists system-wide (case-insensitive).

        Args:
            album_name: The album name to check.

        Returns:
            bool: True if the name exists, False otherwise.

        Raises:
            Exception: Any database error is caught and logged; False returned.
        """
        try:
            with SessionLocal() as session:
                albums = AlbumModel.get_all(session)
            exists = any(a["name"].lower() == album_name.lower() for a in albums)
            if exists:
                log_operation(
                    "album.album_name_exists",
                    "success",
                    f"Album name '{album_name}' already exists",
                )
            return exists
        except Exception as e:
            log_exception("album.album_name_exists", e, context={"name": album_name})
            return False

    @staticmethod
    def create_album(name: str, creator_id: int) -> Optional[dict]:
        """
        Create a new album.

        Args:
            name: The name of the new album.
            creator_id: The ID of the user creating the album.

        Returns:
            Optional[dict]: The newly created album data.

        Raises:
            ValueError: If album name is empty, too long, or duplicate.
            Exception: Any database error is caught and logged; None returned.
        """
        try:
            # application-level validation
            trimmed = name.strip() if name is not None else ""
            if not trimmed:
                log_operation(
                    "album.create_album",
                    "validation_error",
                    "Album name required",
                    user_id=creator_id,
                )
                raise ValueError("Album name is required")
            if (
                len(trimmed) > 50
            ):  # enforce max length at service level to prevent DB errors and provide user-friendly messages
                log_operation(
                    "album.create_album",
                    "validation_error",
                    f"Album name too long: '{trimmed}'",
                    user_id=creator_id,
                )
                raise ValueError("Album name too long (max 50 characters)")

            # ensure user doesn't already have an album with the same name (case-insensitive)
            existing_id = AlbumService.get_album_id_by_name(creator_id, trimmed)
            if existing_id is not None:
                log_operation(
                    "album.create_album",
                    "validation_error",
                    f"Duplicate album name: '{trimmed}'",
                    user_id=creator_id,
                )
                raise ValueError("You already have an album with that name")

            with SessionLocal() as session:
                result = AlbumModel.create(session, name=trimmed, creatorId=creator_id)
                session.commit()
            log_operation(
                "album.create_album",
                "success",
                f"Created album '{trimmed}'",
                user_id=creator_id,
            )
            return result
        except ValueError:
            raise
        except Exception as e:
            log_exception(
                "album.create_album", e, user_id=creator_id, context={"name": name}
            )
            return None

    @staticmethod
    def rename_album(album_id: int, new_name: str) -> Optional[dict]:
        """
        Rename an existing album.

        Args:
            album_id: The ID of the album to rename.
            new_name: The new name for the album.

        Returns:
            Optional[dict]: Updated album dict, or None if not found.

        Raises:
            ValueError: If new name is empty, too long, or duplicate.
            Exception: Any database error is caught and logged; None returned.
        """
        try:
            trimmed = new_name.strip() if new_name is not None else ""
            if not trimmed:
                log_operation(
                    "album.rename_album", "validation_error", "Album name required"
                )
                raise ValueError("Album name is required")
            if len(trimmed) > 50:
                log_operation(
                    "album.rename_album",
                    "validation_error",
                    f"Album name too long: '{trimmed}'",
                )
                raise ValueError("Album name too long (max 50 characters)")

            with SessionLocal() as session:
                album = AlbumModel.get_by_id(session, album_id)
                if not album:
                    log_operation(
                        "album.rename_album",
                        "validation_error",
                        f"Album {album_id} not found",
                    )
                    return None

                # prevent renaming to a name already used by the same creator
                existing_id = AlbumService.get_album_id_by_name(
                    album["creatorId"], trimmed
                )
                if existing_id is not None and existing_id != album_id:
                    log_operation(
                        "album.rename_album",
                        "validation_error",
                        f"Duplicate album name: '{trimmed}'",
                        user_id=album["creatorId"],
                    )
                    raise ValueError("You already have an album with that name")

                result = AlbumModel.update(session, {**album, "name": trimmed})
                session.commit()
            log_operation(
                "album.rename_album",
                "success",
                f"Renamed album to '{trimmed}'",
                user_id=album["creatorId"],
            )
            return result
        except ValueError:
            raise
        except Exception as e:
            log_exception(
                "album.rename_album",
                e,
                context={"album_id": album_id, "new_name": new_name},
            )
            return None

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
        with SessionLocal() as session:
            album = AlbumModel.get_by_id(session, album_id)
        if not album:
            raise ValueError("Album not found")
        if album["creatorId"] != user_id and not is_admin:
            raise ValueError("You can only rename your own albums")
        return bool(AlbumService.rename_album(album_id, new_name))

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
            Exception: Any database error is caught and logged; False returned.
        """
        try:
            with SessionLocal() as session:
                album = AlbumModel.get_by_id(session, album_id)
                if not album:
                    log_operation(
                        "album.delete_album_for_user",
                        "validation_error",
                        f"Album {album_id} not found",
                        user_id=user_id,
                    )
                    raise ValueError("Album not found")
                if album["creatorId"] != user_id and not is_admin:
                    log_operation(
                        "album.delete_album_for_user",
                        "validation_error",
                        f"User {user_id} doesn't own album {album_id}",
                        user_id=user_id,
                    )
                    raise ValueError("You can only delete your own albums")
                result = AlbumModel.delete(session, album_id)
                session.commit()
            log_operation(
                "album.delete_album_for_user",
                "success",
                f"Deleted album {album_id}",
                user_id=user_id,
            )
            return result
        except ValueError:
            raise
        except Exception as e:
            log_exception(
                "album.delete_album_for_user",
                e,
                user_id=user_id,
                context={"album_id": album_id},
            )
            return False

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
        with SessionLocal() as session:
            albums = AlbumModel.get_by_creator(session, user_id)
        target = album_name.strip().lower()
        for album in albums:
            if album["name"].strip().lower() == target:
                return int(album["id"])
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
        with SessionLocal() as session:
            favorites = FavoriteModel.get_by_user(session, user_id)
            if not favorites:
                return []
            result = []
            for fav in favorites:
                album = AlbumModel.get_by_id(session, fav["albumId"])
                if album:
                    result.append({"albumId": fav["albumId"], "name": album["name"]})
            return result
