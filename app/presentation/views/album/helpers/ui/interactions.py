import tkinter as tk

from app.controllers.album_controller import AlbumController
from app.presentation.views.album.helpers.data.state import AlbumState
from app.presentation.views.helpers.ui.carousel import (
    listbox_navigate_next,
    listbox_navigate_prev,
)
from app.presentation.views.helpers.ui.preview import update_preview
from app.presentation.widgets.helpers.images import load_image

_ICON_DIR = "app/assets/images/UI_Icons/"


def on_photo_select(idx: int, state: AlbumState) -> None:
    """Handle listbox photo selection — update the preview panel.

    Args:
        idx: Index into state.photos for the selected photo.
        state: Album view state.
    """
    if 0 <= idx < len(state.photos):
        state.selected_index = idx
        update_preview(state)


def album_navigate_prev(state: AlbumState) -> None:
    """Navigate to the previous photo and sync the listbox selection.

    Args:
        state: Album view state.
    """
    listbox_navigate_prev(state)


def album_navigate_next(state: AlbumState) -> None:
    """Navigate to the next photo and sync the listbox selection.

    Args:
        state: Album view state.
    """
    listbox_navigate_next(state)


def handle_toggle_favorite(state: AlbumState, _parent: tk.Widget) -> None:
    """Toggle the album's favorite status and update the favorite button label.

    Args:
        state: Album view state.
        _parent: Unused parent widget (reserved for future modal parenting).
    """
    if state.album is None:
        return
    album_id = state.album.get("id")
    if album_id is None:
        return
    success, _message, is_now_favorite = AlbumController.toggle_favorite(album_id)
    if success:
        state.is_favorite = is_now_favorite
        _update_favorite_btn(state)


def _sync_listbox(state: AlbumState) -> None:
    """Sync the listbox widget selection to match state.selected_index."""
    from app.presentation.views.helpers.ui.carousel import _sync_listbox_selection

    _sync_listbox_selection(state)


def _update_favorite_btn(state: AlbumState) -> None:
    """Update the favorite button label and icon to reflect the current favorite state."""
    btn = state.favorite_btn
    if btn is None:
        return
    if state.is_favorite:
        label = "  \u2605 Remove from Favorites"
        icon_name = "Remove_Icon.png"
    else:
        label = "  \u2606 Add to Favorites"
        icon_name = "Favorite_Icon.png"
    try:
        new_icon = load_image(f"{_ICON_DIR}{icon_name}", size=(20, 20))
        btn.config(text=label, image=new_icon)
        btn.image = new_icon  # type: ignore[attr-defined]  # GC guard
    except Exception:
        btn.config(text=label)
