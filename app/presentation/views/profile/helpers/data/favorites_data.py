from app.controllers.album_controller import AlbumController
from app.presentation.views.helpers.data.pagination import PaginationManager
from app.presentation.views.profile.helpers.data.favorites_state import FavoritesState
from app.utils.log_utils import log_exception

_ALBUMS_PER_PAGE = 5
_PHOTOS_PER_PAGE = 5


def _get_page_slice(items: list, page_num: int, per_page: int) -> list:
    """
    Return the slice of *items* that belongs to *page_num*.

    Args:
        items (list): The list of items to paginate.
        page_num (int): The page number (1-based).
        per_page (int): The number of items per page.


    Returns:
        list: The slice of items for the specified page.
    """
    start = (page_num - 1) * per_page
    return items[start : start + per_page]


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

        PaginationManager.initialize_pagination(
            als,  # type: ignore[arg-type]
            items_per_page=_ALBUMS_PER_PAGE,
            data_provider=lambda p: _get_page_slice(albums, p, _ALBUMS_PER_PAGE),
            total_items=len(albums),
        )
        als.photos = PaginationManager.get_paginated_items(als)  # type: ignore[arg-type]
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

        PaginationManager.initialize_pagination(
            state,
            items_per_page=_PHOTOS_PER_PAGE,
            data_provider=lambda p: _get_page_slice(all_photos, p, _PHOTOS_PER_PAGE),
            total_items=len(all_photos),
        )
        if all_photos:
            state.photos = PaginationManager.get_paginated_items(state)
            state.selected_index = 0
        else:
            state.photos = []
            state.selected_index = None
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

        PaginationManager.initialize_pagination(
            als,  # type: ignore[arg-type]
            items_per_page=_ALBUMS_PER_PAGE,
            data_provider=lambda p: _get_page_slice(albums, p, _ALBUMS_PER_PAGE),
            total_items=len(albums),
        )
        als.photos = PaginationManager.get_paginated_items(als)  # type: ignore[arg-type]

        widget = getattr(als, "listbox_widget", None)
        if widget is not None:
            # Preserve the visual selection of the currently selected album so
            # that a focus-triggered refresh does not clear the highlight.
            selected_id = None
            selected_album = getattr(state, "selected_album", None)
            if selected_album is not None:
                selected_id = selected_album.get("id")
            widget.refresh(als.photos, selected_item_id=selected_id)

        ctrl = getattr(als, "_pagination_ui_controller", None)
        if ctrl is not None:
            ctrl.refresh_ui()
    except Exception as e:
        log_exception(
            "favorites.refresh_favorites_list",
            e,
            context={"user_id": state.user_id},
        )
