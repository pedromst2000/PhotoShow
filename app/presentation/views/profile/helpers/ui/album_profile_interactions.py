import tkinter as tk
from typing import Literal

from app.controllers.album_controller import AlbumController
from app.controllers.photo_controller import PhotoController
from app.presentation.views.helpers.ui.preview import reset_preview, update_preview
from app.presentation.views.profile.albuns.add_photo import open_add_photo_window
from app.presentation.views.profile.helpers.data.album_profile_data import (
    load_album_photos,
    refresh_album_list,
)
from app.presentation.views.profile.helpers.data.album_profile_state import (
    AlbumProfileState,
)
from app.presentation.views.profile.helpers.ui.album_dialog import open_album_dialog
from app.presentation.widgets.helpers.ui_dialogs import (
    show_confirmation,
    show_error,
    show_info,
)

# ── Module-level action helpers ──────────────────────────────────────────────────


def _do_create_album(name: str, state: AlbumProfileState, body: tk.Widget) -> None:
    """Create an album with *name* and refresh the UI."""
    success, msg = AlbumController.create_album(name)
    if success:
        refresh_album_list(state)
        _rebuild_empty_or_content(state, body)
        show_info(body, "Create Album", f'Album "{name}" created successfully!')
    else:
        show_error(body, "Create Album", msg)


def _do_rename_album(
    new_name: str,
    album_id: int,
    state: AlbumProfileState,
    body: tk.Widget,
) -> None:
    """Rename *album_id* to *new_name* and refresh the album list."""
    success, msg = AlbumController.rename_album(album_id, new_name)
    if success:
        refresh_album_list(state)
        show_info(body, "Edit Album", f'Album renamed to "{new_name}" successfully!')
    else:
        show_error(body, "Edit Album", msg)


def _reload_album_photos(state: AlbumProfileState, album_id: int) -> None:
    """Reload photos for *album_id* and refresh the photo listbox and pagination UI."""
    load_album_photos(state, album_id)
    photo_widget = getattr(state, "listbox_widget", None)
    if photo_widget is not None:
        photo_widget.refresh(state.photos)
    ctrl = getattr(state, "_pagination_ui_controller", None)
    if ctrl is not None:
        ctrl.refresh_ui()


def on_album_select(idx: int, state: AlbumProfileState) -> None:
    """Handle selection of an album in the left listbox.

    Loads photos for the selected album into the photo-list section of *state*
    and refreshes the middle listbox and preview panel.

    Args:
        idx: Local page index of the selected album.
        state: Album profile view state.
    """
    albums_on_page = state.album_list_state.photos
    if not (0 <= idx < len(albums_on_page)):
        return

    state.album_list_state.selected_index = idx
    state.selected_album = albums_on_page[idx]

    # Enable album management buttons.
    _set_album_btns_state(state, enabled=True)

    # Load photos for the newly selected album.
    album_id = state.selected_album.get("id")
    if album_id is None:
        return

    ok = load_album_photos(state, album_id)
    if not ok:
        _reset_photo_panel(state, "Could not load photos.")
        return

    # Refresh the photo listbox.
    photo_widget = getattr(state, "listbox_widget", None)
    if photo_widget is not None:
        photo_widget.refresh(state.photos)

    # Refresh photo pagination UI.
    ctrl = getattr(state, "_pagination_ui_controller", None)
    if ctrl is not None:
        ctrl.refresh_ui()

    # Refresh preview.
    if state.photos:
        state.selected_index = 0
        if photo_widget is not None:
            photo_widget.select_index(0)
        update_preview(state)
    else:
        _reset_photo_panel(state, "No photos in this album")

    # Delete Photo button: enable only when there is a photo selection.
    _sync_delete_photo_btn(state)


def on_photo_select(idx: int, state: AlbumProfileState) -> None:
    """Handle selection of a photo in the middle listbox.

    Args:
        idx: Local page index of the selected photo.
        state: Album profile view state.
    """
    if 0 <= idx < len(state.photos):
        state.selected_index = idx
        update_preview(state)
        _sync_delete_photo_btn(state)


def on_add_photo(state: AlbumProfileState, body: tk.Widget) -> None:
    """Open the Add Photo window for the currently selected album.

    Does nothing when no album is selected.

    Args:
        state: Album profile view state.
        body: Parent widget used for modality.
    """
    if state.selected_album is None:
        show_info(body, "Add Photo", "Please select an album first.")
        return

    album_id = state.selected_album.get("id")

    open_add_photo_window(
        body,
        album_id=album_id,
        on_created=lambda: _reload_album_photos(state, album_id),
    )


# ── Album CRUD ─────────────────────────────────────────────────────────────────


def on_add_album(state: AlbumProfileState, body: tk.Widget) -> None:
    """Open the Add Album dialog and create a new album on submit.

    Args:
        state: Album profile view state.
        body: Parent widget for the dialog (for modality positioning).
    """
    open_album_dialog(
        body, mode="add", on_submit=lambda name: _do_create_album(name, state, body)
    )


def on_edit_album(state: AlbumProfileState, body: tk.Widget) -> None:
    """Open the Edit Album dialog and rename the selected album on submit.

    Does nothing when no album is selected.

    Args:
        state: Album profile view state.
        body: Parent widget for the dialog.
    """
    if state.selected_album is None:
        return

    album_id = state.selected_album.get("id")
    current_name = state.selected_album.get("name", "")

    open_album_dialog(
        body,
        mode="edit",
        current_name=current_name,
        on_submit=lambda new_name: _do_rename_album(new_name, album_id, state, body),
    )


def on_delete_album(state: AlbumProfileState, body: tk.Widget) -> None:
    """Delete the currently selected album after user confirmation.

    Args:
        state: Album profile view state.
        body: Parent widget used for the confirmation dialog.
    """
    if state.selected_album is None:
        return

    album_name = state.selected_album.get("name", "this album")
    album_id = state.selected_album.get("id")

    confirmed = show_confirmation(
        body,
        "Delete Album",
        f'Are you sure you want to delete "{album_name}" and all its photos?\n\nThis action cannot be undone.',
    )
    if not confirmed:
        return

    success, msg = AlbumController.delete_album(album_id)
    if success:
        state.selected_album = None
        state.album_list_state.selected_index = None
        _set_album_btns_state(state, enabled=False)
        _reset_photo_panel(state, "Select an album")
        refresh_album_list(state)
        _rebuild_empty_or_content(state, body)
        show_info(body, "Delete Album", f'Album "{album_name}" deleted successfully.')
    else:
        show_error(body, "Delete Album", msg)


# ── Photo CRUD ─────────────────────────────────────────────────────────────────


def on_delete_photo(state: AlbumProfileState, body: tk.Widget) -> None:
    """Delete the currently selected photo after user confirmation.

    Args:
        state: Album profile view state.
        body: Parent widget for the confirmation dialog.
    """
    photo = state.selected_photo
    if photo is None:
        return

    photo_id = photo.get("id")
    confirmed = show_confirmation(
        body,
        "Delete Photo",
        "Are you sure you want to delete this photo?\n\nThis action cannot be undone.",
    )
    if not confirmed:
        return

    success, msg = PhotoController.delete_photo(photo_id)
    if success:
        # Reload photos for the same album.
        album_id = state.selected_album.get("id") if state.selected_album else None
        if album_id is not None:
            _reload_album_photos(state, album_id)
        if state.photos:
            state.selected_index = 0
            photo_widget = getattr(state, "listbox_widget", None)
            if photo_widget is not None:
                photo_widget.select_index(0)
            update_preview(state)
        else:
            _reset_photo_panel(state, "No photos in this album")
        _sync_delete_photo_btn(state)
        show_info(body, "Delete Photo", "Photo deleted successfully.")
    else:
        show_error(body, "Delete Photo", msg)


# ── Helpers ────────────────────────────────────────────────────────────────────


def _set_album_btns_state(state: AlbumProfileState, *, enabled: bool) -> None:
    """Enable or disable the Delete Album and Edit Album buttons."""
    tk_state: Literal["normal", "disabled"] = "normal" if enabled else "disabled"
    for btn in (state.delete_album_btn, state.edit_album_btn):
        if btn is not None:
            btn.config(state=tk_state)


def _sync_delete_photo_btn(state: AlbumProfileState) -> None:
    """Enable the Delete Photo button only when a photo is selected."""
    has_photo = state.selected_photo is not None
    if state.delete_photo_btn is not None:
        state.delete_photo_btn.config(state=tk.NORMAL if has_photo else tk.DISABLED)


def _reset_photo_panel(state: AlbumProfileState, message: str) -> None:
    """Clear the photo listbox and reset the preview panel."""
    state.photos = []
    state.selected_index = None
    photo_widget = getattr(state, "listbox_widget", None)
    if photo_widget is not None:
        photo_widget.refresh([])
    reset_preview(state, message)
    if state.delete_photo_btn is not None:
        state.delete_photo_btn.config(state=tk.DISABLED)


def _rebuild_empty_or_content(state: AlbumProfileState, body: tk.Widget) -> None:
    """Show or hide the empty state depending on whether the user now has albums.

    When the album list transitions between empty and non-empty (or vice-versa)
    the body frame needs to rebuild its children.  Rather than tracking individual
    widget refs for the empty-state, we simply check if albums exist and toggle
    visibility of the content frame stored on the state.
    """
    content_frame = getattr(state, "_content_frame", None)
    empty_frame = getattr(state, "_empty_frame", None)

    has_albums = bool(state.all_albums)

    if content_frame is not None:
        if has_albums:
            content_frame.pack(fill="both", expand=True)
        else:
            content_frame.pack_forget()

    if empty_frame is not None:
        if has_albums:
            empty_frame.pack_forget()
        else:
            empty_frame.pack(fill="both", expand=True)
