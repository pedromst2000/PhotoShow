import tkinter as tk
from typing import List, Optional

from app.presentation.views.helpers.data.state import BasePhotoState
from app.presentation.views.profile.helpers.data.album_list_state import AlbumListState


class FavoritesState(BasePhotoState):
    """
    Runtime state for the Favorites Albums window.

    Extends ``BasePhotoState`` (which manages photo-list pagination and the
    preview panel) with album-list pagination via a separate ``AlbumListState``
    instance so the two listboxes do not share pagination state.

    Attribute overview
    ------------------
    album_list_state     Pagination/widget state for the *left* favorites album
                         listbox.
    all_favorites        Full (unfiltered) list of favorite albums for the current
                         user; kept to allow cheap refreshes after removal.
    selected_album       Dict of the currently selected favorite album (or None).
    album_listbox_widget Reference to the left ``ListboxWidget`` instance.
    remove_fav_btn       "Remove from Favorites" button; enabled only when an
                         album is selected.
    user_id              ID of the profile owner being viewed.
    is_own               True when the logged-in user is viewing their own
                         favorites.
    username             Display name of the profile owner (used in visitor
                         messages).
    read_only            Always ``True`` — the Favorites window is display-only;
                         no rating, liking, or commenting interactions are shown.
    """

    def __init__(self) -> None:
        super().__init__()

        # ── Favorites album list (left panel) ─────────────────────────────────
        self.album_list_state: AlbumListState = AlbumListState()
        self.all_favorites: List[dict] = []
        self.selected_album: Optional[dict] = None
        self.album_listbox_widget = None  # ListboxWidget ref

        # ── Action button ref ─────────────────────────────────────────────────
        self.remove_fav_btn: Optional[tk.Button] = None

        # ── Profile context ───────────────────────────────────────────────────
        self.user_id: Optional[int] = None
        self.is_own: bool = True
        self.username: Optional[str] = None

        # Favorites window is always display-only (no interactions on preview).
        self.read_only: bool = True
