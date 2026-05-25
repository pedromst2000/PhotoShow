import tkinter as tk

from app.controllers.album_controller import AlbumController
from app.presentation.views.helpers.ui.preview import reset_preview, update_preview
from app.presentation.views.profile.helpers.data.favorites_data import (
    load_favorite_album_photos,
    refresh_favorites_list,
)
from app.presentation.views.profile.helpers.data.favorites_state import FavoritesState
from app.presentation.widgets.helpers.ui_dialogs import (
    show_confirmation,
    show_error,
    show_info,
)

# ── Internal helpers ──────────────────────────────────────────────────────────


def _reset_photo_panel(state: FavoritesState, msg: str) -> None:
    """Clear the photo listbox and reset the preview to a placeholder message.

    Args:
        state: Favorites view state.
        msg: Message to display in the empty preview placeholder.
    """
    state.photos = []
    state.selected_index = None

    photo_widget = getattr(state, "listbox_widget", None)
    if photo_widget is not None:
        photo_widget.refresh([])

    photo_ctrl = getattr(state, "_pagination_ui_controller", None)
    if photo_ctrl is not None:
        photo_ctrl.refresh_ui()

    reset_preview(state, msg)


def _rebuild_empty_or_content(state: FavoritesState, body: tk.Widget) -> None:
    """Show the empty frame or the three-column content frame as appropriate.

    Args:
        state: Favorites view state.
        body: The outer body frame containing both child frames.
    """
    content_frame = getattr(state, "_content_frame", None)
    empty_frame = getattr(state, "_empty_frame", None)

    has_favorites = bool(state.all_favorites)

    if content_frame is not None:
        if has_favorites:
            content_frame.pack(fill="both", expand=True)
        else:
            content_frame.pack_forget()

    if empty_frame is not None:
        if has_favorites:
            empty_frame.pack_forget()
        else:
            empty_frame.pack(fill="both", expand=True)


def _set_remove_btn_state(state: FavoritesState, *, enabled: bool) -> None:
    """Enable or disable the Remove Favorite button.

    Args:
        state: Favorites view state carrying the button reference.
        enabled: True to enable, False to disable.
    """
    btn = state.remove_fav_btn
    if btn is not None:
        btn.config(state=tk.NORMAL if enabled else tk.DISABLED)


# ── Album selection ───────────────────────────────────────────────────────────


def on_fav_album_select(idx: int, state: FavoritesState) -> None:
    """Handle selection of a favorite album in the left listbox.

    Loads photos for the selected album and refreshes the middle listbox and
    preview panel.

    Args:
        idx: Local page index of the selected album.
        state: Favorites view state.
    """
    albums_on_page = state.album_list_state.photos
    if not (0 <= idx < len(albums_on_page)):
        return

    state.album_list_state.selected_index = idx
    state.selected_album = albums_on_page[idx]

    _set_remove_btn_state(state, enabled=True)

    album_id = state.selected_album.get("id")
    if album_id is None:
        return

    ok = load_favorite_album_photos(state, album_id)
    if not ok:
        _reset_photo_panel(state, "Could not load photos.")
        return

    photo_widget = getattr(state, "listbox_widget", None)
    if photo_widget is not None:
        photo_widget.refresh(state.photos)

    photo_ctrl = getattr(state, "_pagination_ui_controller", None)
    if photo_ctrl is not None:
        photo_ctrl.refresh_ui()

    if state.photos:
        state.selected_index = 0
        if photo_widget is not None:
            photo_widget.select_index(0)
        update_preview(state)
    else:
        _reset_photo_panel(state, "No photos in this album")


# ── Photo selection ───────────────────────────────────────────────────────────


def on_fav_photo_select(idx: int, state: FavoritesState) -> None:
    """Handle selection of a photo in the middle listbox.

    Args:
        idx: Local page index of the selected photo.
        state: Favorites view state.
    """
    if 0 <= idx < len(state.photos):
        state.selected_index = idx
        update_preview(state)


# ── Remove favorite ───────────────────────────────────────────────────────────


def on_remove_favorite(state: FavoritesState, body: tk.Widget) -> None:
    """Remove the currently selected album from the user's favorites.

    Only removes the entry from the favorites table — the album and its photos
    are not deleted from the database.

    Args:
        state: Favorites view state.
        body: Parent widget used for confirmation/info dialogs.
    """
    if state.selected_album is None:
        show_info(body, "Remove Favorite", "Please select an album first.")
        return

    album_name = state.selected_album.get("name", "this album")
    album_id = state.selected_album.get("id")

    confirmed = show_confirmation(
        body,
        "Remove Favorite",
        f'Remove "{album_name}" from your favorites?\n\nThe album will not be deleted.',
    )
    if not confirmed:
        return

    success, msg = AlbumController.remove_favorite(album_id)
    if success:
        state.selected_album = None
        state.album_list_state.selected_index = None
        _set_remove_btn_state(state, enabled=False)
        _reset_photo_panel(state, "Select an album")
        refresh_favorites_list(state)
        _rebuild_empty_or_content(state, body)
        show_info(
            body,
            "Remove Favorite",
            f'"{album_name}" has been removed from your favorites.',
        )
    else:
        show_error(body, "Remove Favorite", msg)


# ── Focus-triggered sync ──────────────────────────────────────────────────────


def sync_favorites_on_focus(state: FavoritesState) -> None:
    """Refresh the favorites list whenever the window regains focus.

    Called via a ``<FocusIn>`` binding on the Toplevel so that changes made in
    other windows (e.g. toggling a favorite from the album details window) are
    reflected without the user having to reopen the favorites window.

    Behaviour:
    - Reloads the full favorites list from the DB and refreshes the listbox.
    - Toggles empty/content frames when the count transitions between 0 and 1+.
    - Clears the photo panel when the currently selected album was removed.
    """
    body = getattr(state, "_body_frame", None)
    old_count = len(state.all_favorites)

    refresh_favorites_list(state)

    new_count = len(state.all_favorites)

    # Rebuild empty/content frame when the list goes empty or becomes non-empty.
    if old_count != new_count and body is not None:
        _rebuild_empty_or_content(state, body)

    # If the currently selected album was removed externally, clear the panel.
    if state.selected_album is not None:
        # Use favorite_id as the stable unique key rather than album id.
        fav_id = state.selected_album.get("favorite_id")
        still_there = any(f.get("favorite_id") == fav_id for f in state.all_favorites)
        if not still_there:
            state.selected_album = None
            state.album_list_state.selected_index = None
            _set_remove_btn_state(state, enabled=False)
            _reset_photo_panel(state, "Select an album")
