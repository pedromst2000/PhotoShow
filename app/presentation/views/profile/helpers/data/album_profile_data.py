from app.controllers.album_controller import AlbumController
from app.presentation.views.helpers.data.pagination_helpers import (
    init_list_pagination,
    refresh_listbox_ui,
)
from app.presentation.views.profile.helpers.data.album_profile_state import (
    AlbumProfileState,
)
from app.utils.log_utils import log_exception

_ALBUMS_PER_PAGE = 5
_PHOTOS_PER_PAGE = 5


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
        init_list_pagination(als, albums, _ALBUMS_PER_PAGE)
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

        init_list_pagination(state, all_photos, _PHOTOS_PER_PAGE)
        state.selected_index = 0 if all_photos else None
        if not all_photos:
            state.photos = []
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
        init_list_pagination(als, albums, _ALBUMS_PER_PAGE)
        refresh_listbox_ui(als)
    except Exception as e:
        log_exception(
            "album_profile.refresh_album_list",
            e,
            context={"user_id": state.user_id},
        )
