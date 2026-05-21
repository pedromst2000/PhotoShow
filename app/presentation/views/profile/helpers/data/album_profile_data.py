from app.controllers.album_controller import AlbumController
from app.presentation.views.helpers.data.pagination import PaginationManager
from app.presentation.views.profile.helpers.data.album_profile_state import (
    AlbumProfileState,
)
from app.utils.log_utils import log_exception

_ALBUMS_PER_PAGE = 5
_PHOTOS_PER_PAGE = 5


def _get_page_slice(items: list, page_num: int, per_page: int) -> list:
    """Return the slice of *items* that belongs to *page_num*."""
    start = (page_num - 1) * per_page
    return items[start : start + per_page]


def load_user_albums(state: AlbumProfileState) -> bool:
    """
    Load all albums for the current profile owner into *state*.

    Populates the ``all_albums`` attribute with the full album list for the
    profile owner, and initialises the album-list pagination state on the
    ``album_list_state`` attribute so the left listbox can display the first page of albums.

    Args:
        state: The ``AlbumProfileState`` instance to populate.

    Returns:
        bool: True on success, False on unexpected error.
    """
    try:
        albums = AlbumController.get_user_albums(state.user_id)
        state.all_albums = albums

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
            "album_profile.load_user_albums",
            e,
            context={"user_id": state.user_id},
        )
        return False


def load_album_photos(state: AlbumProfileState, album_id: int) -> bool:
    """Load photos for *album_id* into the photo-list pagination on *state*.

    Resets the photo-list portion of ``state`` (inherited ``BasePhotoState``
    attrs) so the middle listbox and preview panel reflect the selected album.

    Args:
        state: The ``AlbumProfileState`` instance.
        album_id: ID of the album whose photos should be loaded.

    Returns:
        True on success, False on unexpected error.
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
            "album_profile.load_album_photos",
            e,
            context={"album_id": album_id},
        )
        return False


def refresh_album_list(state: AlbumProfileState) -> None:
    """Reload all albums from the controller and reinitialise album pagination.

    Used after creating, renaming, or deleting an album so the left listbox
    reflects the current DB state without reopening the window.

    Args:
        state: The ``AlbumProfileState`` instance.
    """
    try:
        albums = AlbumController.get_user_albums(state.user_id)
        state.all_albums = albums

        als = state.album_list_state

        PaginationManager.initialize_pagination(
            als,  # type: ignore[arg-type]
            items_per_page=_ALBUMS_PER_PAGE,
            data_provider=lambda p: _get_page_slice(albums, p, _ALBUMS_PER_PAGE),
            total_items=len(albums),
        )
        als.photos = PaginationManager.get_paginated_items(als)  # type: ignore[arg-type]

        # Refresh the album listbox widget if it exists.
        widget = getattr(als, "listbox_widget", None)
        if widget is not None:
            widget.refresh(als.photos)

        # Refresh pagination UI (page label + button states).
        ctrl = getattr(als, "_pagination_ui_controller", None)
        if ctrl is not None:
            ctrl.refresh_ui()
    except Exception as e:
        log_exception(
            "album_profile.refresh_album_list",
            e,
            context={"user_id": state.user_id},
        )
