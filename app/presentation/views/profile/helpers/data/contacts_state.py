import tkinter as tk
from typing import Callable, List, Optional


class ContactsState:
    """
    Runtime state for the Contacts admin window.

    Implements the same interface expected by ``PaginationManager`` and
    ``build_listbox_pagination`` so the shared pagination infrastructure can
    be reused without inheriting ``BasePhotoState`` (contacts have no photos).

    Attribute overview
    ------------------
    all_contacts        Full (unfiltered) list of enriched contact dicts.
    selected_contact    The currently selected contact dict, or ``None``.
    resolve_btn         "Mark as Resolved" button; enabled only when a
                        contact is selected.
    win                 The Toplevel window reference.

    Pagination (PaginationManager interface)
    ----------------------------------------
    photos              Current-page slice of contacts (name reused for
                        compatibility with PaginationManager which always
                        writes to ``state.photos``).
    current_page        1-based current page number.
    items_per_page      Number of contacts shown per page.
    total_items         Total contacts across all pages.
    data_provider       Callable(page) → list[dict]; set by PaginationManager.
    selected_index      Local page index of the selected contact (or ``None``).

    Detail panel refs (set by builder, updated by interactions)
    -----------------------------------------------------------
    _author_label       Label showing the author's username.
    _title_label        Label showing the contact title.
    _message_text       Text widget showing the contact message.
    _placeholder_frame  Frame displayed when no contact is selected.
    _detail_frame       Frame displayed when a contact is selected.
    _empty_frame        Empty-state frame (no contacts at all).
    _content_frame      Two-column content frame (list + detail).
    """

    def __init__(self) -> None:
        # ── Contacts list ─────────────────────────────────────────────────────
        self.all_contacts: List[dict] = []
        self.selected_contact: Optional[dict] = None

        # ── Action button ref ─────────────────────────────────────────────────
        self.resolve_btn: Optional[tk.Button] = None

        # ── Window ────────────────────────────────────────────────────────────
        self.win: Optional[tk.Toplevel] = None

        # ── PaginationManager interface ───────────────────────────────────────
        self.photos: list = []  # current page of contacts
        self.current_page: int = 1
        self.items_per_page: int = 10
        self.total_items: int = 0
        self.data_provider: Optional[Callable[[int], List[dict]]] = None
        self.selected_index: Optional[int] = None

        # ── build_listbox_pagination / PaginationUIController refs ────────────
        self.prev_page_btn = None
        self.next_page_btn = None
        self.page_info_label = None
        self.listbox_widget = None  # ListboxWidget ref
        self._pagination_ui_controller = None
        self.tree = None  # unused; kept for PaginationUIController compat

        # ── Detail panel widget refs ──────────────────────────────────────────
        self._author_label: Optional[tk.Label] = None
        self._title_label: Optional[tk.Label] = None
        self._message_text: Optional[tk.Text] = None
        self._placeholder_frame = None
        self._detail_frame = None

        # ── Frame refs for empty/content toggle ───────────────────────────────
        self._empty_frame = None
        self._content_frame = None
