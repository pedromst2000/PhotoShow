from app.presentation.views.album.helpers.data.album import load_album_data
from app.presentation.views.album.helpers.data.state import AlbumState
from app.presentation.views.album.helpers.ui.builder import (
    _WIN_H,
    _WIN_W,
    build_body,
    build_header,
)
from app.presentation.views.helpers.data.state import BasePhotoState
from app.presentation.views.helpers.ui.preview import reset_preview, update_preview
from app.presentation.widgets.window import create_toplevel


def open_album(state: BasePhotoState) -> None:
    """
    Open the album details window for the album containing the selected photo.

    Displays an album header, a scrollable photo listbox on the left, and a
    full PreviewPanelWidget on the right for photo interaction.

    Args:
        state: Explore view state containing selected photo info.
    """
    if state.selected_photo is None:
        return

    album_id = state.selected_photo.get("albumId")
    if not album_id:
        return

    default_photo_id = state.selected_photo.get("id")

    album_state = AlbumState()
    album_state.is_unsigned = state.is_unsigned

    load_album_data(album_state, album_id, default_photo_id)

    win = create_toplevel(
        title="\U0001f5c2 Album Details",
        width=_WIN_W,
        height=_WIN_H,
        icon_path="app/assets/PhotoShowIcon.ico",
        bg_color="white",
    )
    album_state.win = win

    build_header(win, album_state)
    build_body(win, album_state, default_photo_id)

    if album_state.selected_photo:
        update_preview(album_state)
    else:
        reset_preview(album_state, "No photos in this album")

    win.grab_set()
