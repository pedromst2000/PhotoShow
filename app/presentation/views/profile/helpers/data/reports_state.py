import tkinter as tk
from typing import Callable, List, Optional


class ReportsState:
    """
    Runtime state for the Reports admin window.

    Implements the same interface expected by ``PaginationManager`` and
    ``build_listbox_pagination`` so the shared pagination infrastructure can
    be reused without any reports-specific coupling.

    Attribute overview
    ------------------
    all_reports         Full (unfiltered) list of enriched report dicts.
    filtered_reports    Reports visible after applying type / reason filters.
    reason_labels       Reason label strings loaded from the DB (for the
                        filter dropdown).
    selected_report     The currently selected report dict, or ``None``.
    remove_btn          "Remove Report" button; enabled only when a report
                        is selected.
    win                 The Toplevel window reference.

    Filter vars
    -----------
    type_var            StringVar bound to the Type dropdown (All/Photo/Comment).
    reason_var          StringVar bound to the Reason dropdown.

    Pagination (PaginationManager interface)
    ----------------------------------------
    photos              Current-page slice of reports (name reused for
                        compatibility with PaginationManager which always
                        writes to ``state.photos``).
    current_page        1-based current page number.
    items_per_page      Number of reports shown per page.
    total_items         Total reports across all pages.
    data_provider       Callable(page) → list[dict]; set by PaginationManager.
    selected_index      Local page index of the selected report (or ``None``).

    Detail panel refs (set by builder, updated by interactions)
    -----------------------------------------------------------
    _type_label         Label showing "Photo Report" or "Comment Report".
    _reason_label       Label showing the report reason.
    _content_text       Read-only Text widget showing comment text
                        (packed only for comment reports).
    _content_photo_canvas  Canvas showing the photo image
                           (packed only for photo reports).
    _creator_avatar_canvas Canvas showing the content creator's avatar.
    _creator_username_label Label showing the content creator's username.
    _description_frame  Frame containing the description field; shown only
                        when the reason is "Other" and description is present.
    _description_label  Label showing the reporter’s description
                        (only visible when reason is “Other”).
    _delete_btn         "Delete Content" button in the detail panel.
    _placeholder_frame  Frame shown when no report is selected.
    _detail_frame       Frame shown when a report is selected.
    _empty_frame        Empty-state frame (no reports at all).
    _content_frame      Two-column content frame (list + detail).
    """

    def __init__(self) -> None:
        # ── Reports list ──────────────────────────────────────────────────────
        self.all_reports: List[dict] = []
        self.filtered_reports: List[dict] = []
        self.reason_labels: List[str] = []
        self.selected_report: Optional[dict] = None

        # ── Filter vars ───────────────────────────────────────────────────────
        self.type_var: Optional[tk.StringVar] = None
        self.reason_var: Optional[tk.StringVar] = None

        # ── Action button ref ─────────────────────────────────────────────────
        self.remove_btn: Optional[tk.Button] = None

        # ── Window ────────────────────────────────────────────────────────────
        self.win: Optional[tk.Toplevel] = None

        # ── PaginationManager interface ───────────────────────────────────────
        self.photos: list = []  # current page of reports
        self.current_page: int = 1
        self.items_per_page: int = 8
        self.total_items: int = 0
        self.data_provider: Optional[Callable[[int], List[dict]]] = None
        self.selected_index: Optional[int] = None

        # ── build_listbox_pagination / PaginationUIController refs ────────────
        self.prev_page_btn = None
        self.next_page_btn = None
        self.page_info_label = None
        self.listbox_widget = None
        self._pagination_ui_controller = None
        self.tree = None  # unused; kept for PaginationUIController compat

        # ── Detail panel widget refs ──────────────────────────────────────────
        self._type_label: Optional[tk.Label] = None
        self._reason_label: Optional[tk.Label] = None
        self._content_text: Optional[tk.Text] = None
        self._content_photo_canvas: Optional[tk.Canvas] = None
        self._creator_avatar_canvas: Optional[tk.Canvas] = None
        self._creator_username_label: Optional[tk.Label] = None
        self._description_frame = None
        self._description_label: Optional[tk.Label] = None
        self._delete_btn: Optional[tk.Button] = None
        self._placeholder_frame = None
        self._detail_frame = None

        # ── Frame refs for empty/content toggle ───────────────────────────────
        self._empty_frame = None
        self._content_frame = None
