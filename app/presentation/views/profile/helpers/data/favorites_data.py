from app.controllers.album_controller import AlbumController
from app.presentation.views.helpers.data.pagination_helpers import (
    init_list_pagination,
    refresh_listbox_ui,
)
from app.presentation.views.profile.helpers.data.favorites_state import FavoritesState
from app.utils.log_utils import log_exception

_ALBUMS_PER_PAGE = 5
_PHOTOS_PER_PAGE = 5


def load_user_favorites(state: FavoritesState) -> bool:
    """
    Load all favorite albums for the current profile owner into *state*.

    Populates ``all_favorites`` and initialises the album-list pagination so
    the left listbox can display the first page of favorites.

    Args:
        state: The ``FavoritesState`` instance to populate.

    Returns:
        bool: True on success, False on unexpected error.
    """
    try:
        albums = AlbumController.get_enriched_favorite_albums(state.user_id)
        state.all_favorites = albums

        als = state.album_list_state
        init_list_pagination(als, albums, _ALBUMS_PER_PAGE)
        return True
    except Exception as e:
        log_exception(
            "favorites.load_user_favorites",
            e,
            context={"user_id": state.user_id},
        )
        return False


def load_favorite_album_photos(state: FavoritesState, album_id: int) -> bool:
    """Load photos for *album_id* into the photo-list pagination on *state*.

    Resets the photo portion of *state* (inherited ``BasePhotoState`` attrs)
    so the middle listbox and preview panel reflect the selected favorite album.

    Args:
        state: The ``FavoritesState`` instance.
        album_id: ID of the album whose photos should be loaded.

    Returns:
        bool: True on success, False on unexpected error.
    """
    try:
        details = AlbumController.get_album_details(album_id)
        if details is None:
            return False

        all_photos = details.get("photos", [])

        init_list_pagination(state, all_photos, _PHOTOS_PER_PAGE)
        state.selected_index = 0 if all_photos else None
        if not all_photos:
            state.photos = []
        return True
    except Exception as e:
        log_exception(
            "favorites.load_favorite_album_photos",
            e,
            context={"album_id": album_id},
        )
        return False


def refresh_favorites_list(state: FavoritesState) -> None:
    """Reload all favorites from the controller and reinitialise album pagination.

    Used after removing a favorite so the left listbox reflects the current DB
    state without reopening the window.

    Args:
        state: The ``FavoritesState`` instance.
    """
    try:
        albums = AlbumController.get_enriched_favorite_albums(state.user_id)
        state.all_favorites = albums

        als = state.album_list_state
        init_list_pagination(als, albums, _ALBUMS_PER_PAGE)

        # Preserve visual selection of the current album across refreshes.
        selected_album = getattr(state, "selected_album", None)
        selected_id = selected_album.get("id") if selected_album else None
        refresh_listbox_ui(als, selected_item_id=selected_id)
    except Exception as e:
        log_exception(
            "favorites.refresh_favorites_list",
            e,
            context={"user_id": state.user_id},
        )
