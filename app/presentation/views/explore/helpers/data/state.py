import tkinter as tk
from tkinter import ttk
from typing import Callable, List, Optional

from app.presentation.widgets.photo_carousel import PhotoCarouselWidget
from app.presentation.widgets.star_rating import StarRatingWidget


class ExploreState:
    """Holds runtime state for the Explore window."""

    def __init__(self) -> None:
        """Initialize the ExploreState with default values."""
        self.photos: list = []
        self.selected_index: Optional[int] = None
        self.is_unsigned: bool = False
        self.win: Optional[tk.Toplevel] = None

        # tkinter vars
        self.sort_var: Optional[tk.StringVar] = None
        self.author_var: Optional[tk.StringVar] = None
        self.category_var: Optional[tk.StringVar] = None

        # Widget references
        self.tree: Optional[ttk.Treeview] = None
        self.carousel: Optional[PhotoCarouselWidget] = None
        self.avatar_canvas: Optional[tk.Canvas] = None
        self.username_label: Optional[tk.Label] = None
        self.star_widget: Optional[StarRatingWidget] = None
        self.rating_count_label: Optional[tk.Label] = None
        self.likes_label: Optional[tk.Label] = None
        self.comments_label: Optional[tk.Label] = None
        self.like_btn: Optional[tk.Button] = None
        self.details_btn: Optional[tk.Button] = None
        self.comments_btn: Optional[tk.Button] = None
        self.album_btn: Optional[tk.Button] = None
        self.report_btn: Optional[tk.Button] = None
        self.metadata_frame: Optional[tk.Frame] = None
        self.btns_frame: Optional[tk.Frame] = None

        # Pagination controls
        self.page_info_label: Optional[tk.Label] = None
        self.prev_page_btn: Optional[tk.Button] = None
        self.next_page_btn: Optional[tk.Button] = None

        # GC guards
        self._avatar_img_ref = None
        self._btn_icon_refs: list = []

        # Cache to avoid reloading same avatar on repeated navigation
        self._cached_avatar_owner_id: Optional[int] = None

        # Pagination state
        self.current_page: int = 1
        self.items_per_page: int = 10  # Changed from 20 to 10 items per page
        self.total_items: int = 0  # Updated after filtering or from total_items param
        self._tree_id_to_global_idx: dict = (
            {}
        )  # Maps tree local IDs to global photo indices
        self._pagination_ui_controller = None  # Will be set by photo_treeview.py

        # Lazy-loading support
        self.data_provider: Optional[Callable[[int], List[dict]]] = (
            None  # Function to fetch page data
        )

    @property
    def selected_photo(self) -> Optional[dict]:
        """Get the currently selected photo data, or None if no valid selection."""
        if self.selected_index is not None and 0 <= self.selected_index < len(
            self.photos
        ):
            return self.photos[self.selected_index]
        return None
