from typing import Optional, Tuple

from app.core.db.engine import SessionLocal
from app.core.db.models.album import AlbumModel
from app.core.db.models.favorite import FavoriteModel
from app.core.db.models.photo import PhotoModel
from app.core.db.models.photo_image import PhotoImageModel
from app.core.db.models.user import UserModel
from app.utils.file_utils import delete_from_latest
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

            # CRITICAL FIX: Consolidate all DB operations into a single session to avoid SQLite lock timeouts.
            # Opening multiple SessionLocal() contexts in sequence causes "database is locked" errors.
            with SessionLocal() as session:
                # Check for duplicate album name (case-insensitive) - WITHIN SAME TRANSACTION
                existing_albums = AlbumModel.get_by_creator(session, creator_id)
                target = trimmed.lower()
                for album in existing_albums:
                    if album["name"].strip().lower() == target:
                        log_operation(
                            "album.create_album",
                            "validation_error",
                            f"Duplicate album name: '{trimmed}'",
                            user_id=creator_id,
                        )
                        raise ValueError("You already have an album with that name")

                # Create the album in the SAME session/transaction
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
    def rename_album(
        user_id: int, album_id: int, new_name: str, is_admin: bool = False
    ) -> bool:
        """
        Rename an album after verifying ownership, name validity, and duplicate check.

        Args:
            user_id: The ID of the requesting user.
            album_id: The ID of the album to rename.
            new_name: The new name for the album.
            is_admin: Whether the requesting user is an admin.

        Returns:
            bool: True if renamed successfully.

        Raises:
            ValueError: If validation fails, album not found, or ownership check fails.
            Exception: Any database error is caught and logged; False returned.
        """
        try:
            trimmed = new_name.strip() if new_name is not None else ""
            if not trimmed:
                raise ValueError("Album name is required")
            if len(trimmed) > 50:
                raise ValueError("Album name too long (max 50 characters)")

            # CRITICAL FIX: Consolidate all DB operations into a single session to avoid SQLite lock timeouts.
            with SessionLocal() as session:
                album = AlbumModel.get_by_id(session, album_id)
                if not album:
                    raise ValueError("Album not found")
                if album["creatorId"] != user_id and not is_admin:
                    raise ValueError("You can only rename your own albums")

                # prevent renaming to a name already used by the same creator - WITHIN SAME TRANSACTION
                existing_albums = AlbumModel.get_by_creator(session, album["creatorId"])
                target = trimmed.lower()
                for existing_album in existing_albums:
                    if (
                        existing_album["id"] != album_id
                        and existing_album["name"].strip().lower() == target
                    ):
                        raise ValueError("You already have an album with that name")

                AlbumModel.update(session, {**album, "name": trimmed})
                session.commit()

            log_operation(
                "album.rename_album",
                "success",
                f"Renamed album {album_id} to '{trimmed}'",
                user_id=user_id,
            )
            return True
        except ValueError:
            raise
        except Exception as e:
            log_exception(
                "album.rename_album",
                e,
                user_id=user_id,
                context={"album_id": album_id, "new_name": new_name},
            )
            return False

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

                # Collect image paths for disk cleanup before the cascade wipes them.
                photos_in_album = PhotoModel.get_by_album(session, album_id)
                image_paths = []
                for p in photos_in_album:
                    img = PhotoImageModel.get_for_photo(session, p["id"])
                    if img and img.get("image"):
                        image_paths.append(img["image"])

                # Deleting the album triggers the DB CASCADE which removes all
                # associated photos, photo_image, likes, comments, ratings, and
                # reports automatically (PRAGMA foreign_keys=ON is active).
                result = AlbumModel.delete(session, album_id)
                session.commit()

            # Remove latest-tier image files from disk (default-tier files are skipped).
            for img_path in image_paths:
                delete_from_latest(img_path)

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
    def get_album_details(
        album_id: int, user_id: Optional[int] = None
    ) -> Optional[dict]:
        """
        Return enriched album details including photos with stats and creator info.

        Args:
            album_id: The ID of the album.
            user_id: Optional user ID for personalised data (liked/rated, is_favorite).

        Returns:
            Optional[dict]: Album info, enriched photos, is_favorite.
        """
        # Late import to avoid circular dependency
        from app.core.services.catalog_service import CatalogService

        try:
            with SessionLocal() as session:
                album = AlbumModel.get_by_id(session, album_id)
                if not album:
                    return None

                is_favorite = False
                if user_id is not None:
                    favs = FavoriteModel.get_by_user(session, user_id)
                    is_favorite = any(f["albumId"] == album_id for f in favs)

            # Reuse CatalogService enrichment — filters by album_id so only this
            # album's photos are returned, with all interaction counts already set.
            enriched_photos = CatalogService.get_explore_catalog(
                album_id=album_id, user_id=user_id
            )

            log_operation(
                "album.get_album_details",
                "success",
                f"Retrieved details for album {album_id}",
            )
            return {
                "album": album,
                "photos": enriched_photos,
                "is_favorite": is_favorite,
            }
        except Exception as e:
            log_exception("album.get_album_details", e, context={"album_id": album_id})
            return None

    @staticmethod
    def toggle_favorite(album_id: int, user_id: int) -> Tuple[bool, str, bool]:
        """
        Add or remove an album from the user's favorites.

        Args:
            album_id: The ID of the album.
            user_id: The ID of the user.

        Returns:
            Tuple[bool, str, bool]: (success, message, is_now_favorite).
        """
        try:
            with SessionLocal() as session:
                favs = FavoriteModel.get_by_user(session, user_id)
                is_currently_favorite = any(f["albumId"] == album_id for f in favs)
                if is_currently_favorite:
                    FavoriteModel.delete_for_user(session, album_id, user_id)
                    session.commit()
                    log_operation(
                        "album.toggle_favorite",
                        "success",
                        f"Removed album {album_id} from favorites",
                        user_id=user_id,
                    )
                    return True, "Album removed from favorites.", False
                else:
                    FavoriteModel.create(session, albumId=album_id, userId=user_id)
                    session.commit()
                    log_operation(
                        "album.toggle_favorite",
                        "success",
                        f"Added album {album_id} to favorites",
                        user_id=user_id,
                    )
                    return True, "Album added to favorites.", True
        except Exception as e:
            log_exception(
                "album.toggle_favorite",
                e,
                context={"album_id": album_id},
            )
            return False, "Something went wrong. Please try again later.", False

    @staticmethod
    def get_enriched_favorite_albums(user_id: int) -> list:
        """
        Retrieve favorite albums for a user, enriched with creator username.

        Each returned dict uses ``id`` (not ``albumId``) so it is compatible
        with the ``ListboxWidget`` default ``id_key="id"`` contract.

        Args:
            user_id: The ID of the user whose favorites are retrieved.

        Returns:
            list: Dicts with ``id``, ``name``, and ``creator_username``.
        """
        try:
            with SessionLocal() as session:
                favorites = FavoriteModel.get_by_user(session, user_id)
                if not favorites:
                    return []
                result = []
                for fav in favorites:
                    album = AlbumModel.get_by_id(session, fav["albumId"])
                    if album:
                        creator = UserModel.get_by_id(session, album["creatorId"])
                        creator_username = creator["username"] if creator else "Unknown"
                        result.append(
                            {
                                "id": fav["albumId"],
                                "favorite_id": fav["id"],
                                "name": album["name"],
                                "creator_username": creator_username,
                            }
                        )
                return result
        except Exception as e:
            log_exception(
                "album.get_enriched_favorite_albums",
                e,
                context={"user_id": user_id},
            )
            return []

    @staticmethod
    def remove_favorite(album_id: int, user_id: int) -> Tuple[bool, str]:
        """
        Remove a specific album from the user's favorites.

        Unlike ``toggle_favorite``, this always removes without checking the
        current state first, making it safe to call from the Favorites window.

        Args:
            album_id: The ID of the album to remove.
            user_id: The ID of the user whose favorite entry is removed.

        Returns:
            Tuple[bool, str]: ``(True, success_msg)`` or ``(False, error_msg)``.
        """
        try:
            with SessionLocal() as session:
                deleted = FavoriteModel.delete_for_user(session, album_id, user_id)
                session.commit()
            if deleted:
                log_operation(
                    "album.remove_favorite",
                    "success",
                    f"Removed album {album_id} from favorites",
                    user_id=user_id,
                )
                return True, "Album removed from favorites."
            log_operation(
                "album.remove_favorite",
                "not_found",
                f"Album {album_id} was not in favorites for user {user_id}",
                user_id=user_id,
            )
            return False, "Album was not in your favorites."
        except Exception as e:
            log_exception(
                "album.remove_favorite",
                e,
                context={"album_id": album_id, "user_id": user_id},
            )
            return False, "Something went wrong. Please try again later."
