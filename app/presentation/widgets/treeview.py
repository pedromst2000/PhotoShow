import tkinter as tk
from tkinter import ttk
from typing import Callable, List, Optional

from app.controllers.ui.pagination_controller import PaginationUIController
from app.presentation.styles.colors import colors
from app.presentation.styles.fonts import quickSandBold, quickSandRegular
from app.presentation.widgets.helpers.button import make_button


class TreeviewWidget(tk.Frame):
    """
    Generic treeview widget for displaying tabular data with pagination.

    Columns, title, description, and behaviour callbacks are all provided by
    the caller, making this widget reusable for photos, users, reports, or any
    other data set without requiring changes to the widget itself.

    Column config dict schema::

        {
            "key":     str,              # unique column identifier
            "heading": str,              # visible column heading text
            "width":   int,              # column pixel width
            "stretch": bool (optional),  # whether the column stretches (default False)
        }
    """

    def __init__(
        self,
        parent: tk.Frame,
        state,
        columns: List[dict],
        title: str = "Browse Items",
        description: str = "Browse and select items.",
        on_select: Optional[Callable] = None,
        on_page_changed: Optional[Callable] = None,
        row_fn: Optional[Callable] = None,
        empty_label: Optional[str] = None,
        width: int = 460,
        height: int = 674,
        bg: Optional[str] = None,
    ):
        """
        Create and place a treeview panel.

        Args:
            parent: Parent frame.
            state: Any state object that exposes ``tree``, ``page_info_label``,
                ``prev_page_btn``, ``next_page_btn``, and pagination attributes.
            columns: List of column config dicts (see class docstring).
            title: Panel title label text.
            description: Panel subtitle/description label text.
            on_select: Callback invoked with the Tkinter ``<<TreeviewSelect>>``
                event when the user selects a row. If *None*, no selection
                handler is bound.
            on_page_changed: No-arg callable invoked whenever the active page
                changes (e.g. to reset a preview panel). If *None*, ignored.
            row_fn: Optional callable ``(item: dict) -> tuple`` that converts a
                data item to a tuple of column values.  When *None* the widget
                falls back to the photo-specific format (album, author, category).
            empty_label: Text shown in the first column when there are no items.
                Defaults to ``"No photos found"`` when *None*.
            width: Panel pixel width.
            height: Panel pixel height.
            bg: Background colour; falls back to parent bg then theme token.
        """
        self.parent = parent
        self.state = state
        self.columns = columns
        self.title = title
        self.description = description
        self.on_select = on_select
        self.on_page_changed = on_page_changed
        self.row_fn = row_fn
        self.empty_label = empty_label
        self.width = width
        self.height = height

        # Resolve background colour
        bg_value = bg
        if bg_value is None:
            try:
                bg_value = parent.cget("bg")
            except Exception:
                bg_value = None
        if not bg_value:
            bg_value = colors["primary-50"]
        self._page_bg = bg_value

        self._build_treeview_panel()

    def _build_treeview_panel(self):
        """Build the treeview panel."""
        left = tk.Frame(self.parent, bg=self._page_bg)
        left.place(x=0, y=0, width=self.width, height=self.height)

        # ── Title and description ──────────────────────────────────────
        title_frame = tk.Frame(left, bg=self._page_bg)
        title_frame.pack(fill="x", padx=15, pady=(10, 2))

        tk.Label(
            title_frame,
            text=self.title,
            font=quickSandBold(14),
            bg=self._page_bg,
            fg=colors["secondary-500"],
        ).pack(anchor="w")

        tk.Label(
            title_frame,
            text=self.description,
            font=quickSandRegular(11),
            bg=self._page_bg,
            fg=colors["secondary-400"],
        ).pack(anchor="w")

        # ── Treeview styling ──────────────────────────────────────────
        col_keys = tuple(c["key"] for c in self.columns)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Explore.Treeview",
            background=colors["secondary-400"],
            foreground=colors["primary-50"],
            fieldbackground=colors["secondary-400"],
            rowheight=28,
            font=quickSandRegular(10),
            borderwidth=0,
            relief="flat",
        )
        style.configure(
            "Explore.Treeview.Heading",
            background=colors["secondary-500"],
            foreground=colors["primary-50"],
            font=quickSandBold(11),
            borderwidth=0,
            relief="flat",
            padding=3,
        )
        style.configure(
            "CustomTreeview.Vertical.TScrollbar",
            background=colors["secondary-400"],
            troughcolor=colors["primary-50"],
            darkcolor=colors["secondary-500"],
            lightcolor=colors["secondary-300"],
            arrowcolor=colors["secondary-500"],
        )
        style.configure(
            "CustomTreeview.Horizontal.TScrollbar",
            background=colors["secondary-400"],
            troughcolor=colors["primary-50"],
            darkcolor=colors["secondary-500"],
            lightcolor=colors["secondary-300"],
            arrowcolor=colors["secondary-500"],
        )
        style.map(
            "Explore.Treeview",
            background=[("selected", colors["secondary-300"])],
            foreground=[("selected", colors["primary-50"])],
        )
        style.map(
            "Explore.Treeview.Heading",
            background=[("active", colors["secondary-500"])],
        )

        # ── Scrollbars + Treeview ─────────────────────────────────────
        tree_frame = tk.Frame(left, bg=self._page_bg)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=(2, 0), pady=2)

        v_scrollbar = ttk.Scrollbar(
            tree_frame, orient="vertical", style="CustomTreeview.Vertical.TScrollbar"
        )
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar = ttk.Scrollbar(
            tree_frame,
            orient="horizontal",
            style="CustomTreeview.Horizontal.TScrollbar",
        )
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        tree = ttk.Treeview(
            tree_frame,
            columns=col_keys,
            show="headings",
            style="Explore.Treeview",
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set,
            height=15,
        )

        for col in self.columns:
            tree.heading(col["key"], text=col["heading"])
            tree.column(
                col["key"],
                width=col["width"],
                stretch=col.get("stretch", tk.NO),
            )

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.config(command=tree.yview)
        h_scrollbar.config(command=tree.xview)

        self.state.tree = tree

        # Store custom row renderer and empty label on state for TreeViewController
        if self.row_fn is not None:
            self.state._tree_row_fn = self.row_fn
        if self.empty_label is not None:
            self.state._tree_empty_label = self.empty_label

        if self.on_select is not None:
            tree.bind("<<TreeviewSelect>>", self.on_select)

        # ── Pagination controls ───────────────────────────────────────
        def _on_page_changed():
            """Internal callback for when the page changes; invokes external callback if provided."""
            if self.on_page_changed is not None:
                self.on_page_changed()

        pagination_controller = PaginationUIController(
            self.state, on_page_changed=_on_page_changed
        )
        self.state._pagination_ui_controller = pagination_controller

        pagination_frame = tk.Frame(left, bg=self._page_bg, height=36)
        pagination_frame.pack(fill="x", padx=6, pady=(6, 0), side=tk.BOTTOM)

        prev_btn = make_button(
            pagination_frame,
            "← Prev Page",
            cmd=lambda: pagination_controller.go_to_prev_page(),
            font=quickSandBold(10),
            bg=colors["accent-300"],
            fg=colors["secondary-500"],
            borderwidth=0,
            highlightthickness=0,
            cursor="hand2",
            relief="flat",
            padx=8,
            pady=5,
        )
        prev_btn.pack(side=tk.LEFT, padx=2)

        page_info_lbl = tk.Label(
            pagination_frame,
            text="Page 1/1",
            font=quickSandBold(10),
            bg=self._page_bg,
            fg=colors["secondary-500"],
        )
        page_info_lbl.pack(side=tk.LEFT, padx=10, expand=True)
        self.state.page_info_label = page_info_lbl

        next_btn = make_button(
            pagination_frame,
            "Next Page →",
            cmd=lambda: pagination_controller.go_to_next_page(),
            font=quickSandBold(10),
            bg=colors["accent-300"],
            fg=colors["secondary-500"],
            borderwidth=0,
            highlightthickness=0,
            cursor="hand2",
            relief="flat",
            padx=8,
            pady=5,
        )
        next_btn.pack(side=tk.RIGHT, padx=2)

        self.state.prev_page_btn = prev_btn
        self.state.next_page_btn = next_btn

    def refresh_pagination(self):
        """Refresh pagination UI (called by external controllers)."""
        if hasattr(self, "pagination_controller"):
            self.pagination_controller.refresh_ui()
