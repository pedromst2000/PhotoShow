import tkinter as tk
from typing import Any

from app.presentation.views.helpers.ui.preview import reset_preview

# ── Photo panel reset ──────────────────────────────────────────────────────────


def reset_photo_panel(state: Any, msg: str) -> None:
    """Clear the photo list and reset the preview placeholder.

    Args:
        state: Any profile view state that has ``photos``, ``selected_index``,
               and optionally ``listbox_widget``, ``_pagination_ui_controller``,
               and ``delete_photo_btn``.
        msg: Placeholder message to pass to ``reset_preview``.
    """
    state.photos = []
    state.selected_index = None

    widget = getattr(state, "listbox_widget", None)
    if widget is not None:
        widget.refresh([])

    ctrl = getattr(state, "_pagination_ui_controller", None)
    if ctrl is not None:
        ctrl.refresh_ui()

    reset_preview(state, msg)

    btn = getattr(state, "delete_photo_btn", None)
    if btn is not None:
        btn.config(state=tk.DISABLED)


# ── Page-change handlers ───────────────────────────────────────────────────────


def on_photo_page_changed(state: Any) -> None:
    """Reset photo selection and preview when the photo-list page changes.

    Shared handler for the albums-profile window (where it also disables the
    Delete Photo button when present) and the favorites window (no such button).

    Args:
        state: Any profile view state.
    """
    reset_preview(state, "Select a photo")

    btn = getattr(state, "delete_photo_btn", None)
    if btn is not None:
        btn.config(state=tk.DISABLED)


def on_album_page_changed(state: Any) -> None:
    """Reset album selection and clear the photo panel when the album page changes.

    Shared handler for the albums-profile window and the favorites window.
    Uses ``getattr`` to disable whichever action buttons exist on the state
    (``remove_fav_btn``, ``delete_album_btn``, ``edit_album_btn``).

    Args:
        state: Any profile view state that has ``selected_album`` and
               ``album_list_state``.
    """
    state.selected_album = None
    state.album_list_state.selected_index = None

    for attr in ("remove_fav_btn", "delete_album_btn", "edit_album_btn"):
        btn = getattr(state, attr, None)
        if btn is not None:
            btn.config(state=tk.DISABLED)

    reset_photo_panel(state, "Select an album")


def on_contacts_page_changed(state: Any) -> None:
    """Reset contact selection and the detail panel when the contacts page changes.

    Shared handler for the contacts window.  Uses ``getattr`` to locate the
    resolve button, detail frame, and placeholder frame on the state — so no
    contacts-specific types are imported here.

    Args:
        state: Contacts view state (or any state with the expected attributes).
    """
    state.selected_contact = None
    state.selected_index = None

    btn = getattr(state, "resolve_btn", None)
    if btn is not None:
        btn.config(state=tk.DISABLED)

    detail = getattr(state, "_detail_frame", None)
    placeholder = getattr(state, "_placeholder_frame", None)
    if detail is not None:
        detail.pack_forget()
    if placeholder is not None:
        placeholder.pack(fill="both", expand=True)
