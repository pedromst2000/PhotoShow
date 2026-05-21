import tkinter as tk
from typing import List, Optional

from app.presentation.views.helpers.data.state import BasePhotoState
from app.presentation.views.profile.helpers.data.album_list_state import AlbumListState


class AlbumProfileState(BasePhotoState):
    """
    Runtime state for the Albums Profile window.

    Extends ``BasePhotoState`` (which manages photo-list pagination and
    the preview panel) with album-list pagination via a separate
    ``AlbumListState`` instance so the two listboxes do not share state.

    Attribute overview
    ------------------
    album_list_state    Pagination/widget state for the *left* album listbox.
    all_albums          Full (unfiltered) album list for the current user;
                        kept to allow cheap refreshes after add/edit/delete.
    selected_album      Dict of the currently selected album (or None).
    album_listbox_widget  Reference to the left ``ListboxWidget`` instance.
    delete_album_btn    "Delete Album" button; enabled only when an album
                        is selected.
    edit_album_btn      "Edit Album" button; enabled only when an album
                        is selected.
    delete_photo_btn    "Delete Photo" button; enabled only when a photo
                        is selected.
    user_id             ID of the profile owner being viewed.
    is_own              True when the logged-in user is viewing their own
                        albums (controls write-action visibility).
    """

    def __init__(self) -> None:
        super().__init__()

        # ── Album list (left panel) ───────────────────────────────────────────
        self.album_list_state: AlbumListState = AlbumListState()
        self.all_albums: List[dict] = []
        self.selected_album: Optional[dict] = None
        self.album_listbox_widget = None  # ListboxWidget ref

        # ── Album management button refs ──────────────────────────────────────
        self.delete_album_btn: Optional[tk.Button] = None
        self.edit_album_btn: Optional[tk.Button] = None

        # ── Photo management button ref ───────────────────────────────────────
        self.delete_photo_btn: Optional[tk.Button] = None

        # ── Profile context ───────────────────────────────────────────────────
        self.user_id: Optional[int] = None
        self.is_own: bool = True
