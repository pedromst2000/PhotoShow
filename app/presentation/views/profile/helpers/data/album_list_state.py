from typing import Callable, List, Optional


class AlbumListState:
    """
    Minimal pagination state for the album listbox in the Albums Profile window.

    Mirrors the interface expected by ``PaginationManager``,
    ``build_listbox_pagination``, and ``PaginationUIController`` so that the
    shared pagination infrastructure can be reused for the album list without
    conflicting with the photo-list pagination stored on ``AlbumProfileState``
    (which inherits ``BasePhotoState``).

    ``photos`` is intentionally used instead of ``albums`` because
    ``PaginationManager`` writes paginated results back to ``state.photos``.
    """

    def __init__(self) -> None:
        # ── PaginationManager interface ───────────────────────────────────────
        self.current_page: int = 1
        self.items_per_page: int = 10
        self.total_items: int = 0
        self.data_provider: Optional[Callable[[int], List[dict]]] = None
        # Holds the *current page* of albums (PaginationManager writes here).
        self.photos: list = []
        self.selected_index: Optional[int] = None

        # ── build_listbox_pagination / PaginationUIController refs ────────────
        self.prev_page_btn = None
        self.next_page_btn = None
        self.page_info_label = None
        self.listbox_widget = None  # ListboxWidget reference
        self._pagination_ui_controller = None

        # ── TreeViewController (safely ignored when tree is None) ─────────────
        self.tree = None
