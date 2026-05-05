import tkinter as tk
from typing import Optional

from app.presentation.views.helpers.data.state import BasePhotoState


class AlbumState(BasePhotoState):
    """
    Runtime state for the Album Details view.

    Extends BasePhotoState with album-specific data and widget references:
    - album: The album's data dictionary.
    - creator: The album creator's data dictionary.
    - avg_category: The average category of photos in the album.
    - is_favorite: Whether the current user has favorited this album.
    - favorite_btn: Reference to the "Favorite" button widget.
    - listbox_widget: Reference to the PhotoListboxWidget instance.
    - header_category_lbl: Reference to the category label in the header.
    """

    def __init__(self) -> None:
        super().__init__()
        # Album-level data
        self.album: Optional[dict] = None
        self.creator: Optional[dict] = None
        self.avg_category: Optional[str] = None
        self.is_favorite: bool = False

        # Extra widget refs owned by the album view
        self.favorite_btn: Optional[tk.Button] = None
        self.listbox_widget = None  # PhotoListboxWidget reference
        self.header_category_lbl: Optional[tk.Label] = None
