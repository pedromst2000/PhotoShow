import tkinter as tk
from tkinter import ttk
from typing import Optional

from app.controllers.pagination_controller import PaginationUIController
from app.presentation.styles.colors import colors
from app.presentation.styles.fonts import quickSandBold, quickSandRegular
from app.presentation.views.explore.helpers.ui.treeview import on_treeview_select
from app.presentation.widgets.helpers.button import on_enter, on_leave


class PhotoTreeviewWidget(tk.Frame):
    """
    Treeview widget for displaying photo lists.

    Displays: Album, Author, Category columns.
    """

    def __init__(
        self,
        parent: tk.Frame,
        state,
        width: int = 460,
        height: int = 674,
        bg: Optional[str] = None,
    ):
        """
        Create and place treeview panel.

        Args:
            parent: Parent frame (body)
            state: Explore state object
            width: Panel width
            height: Panel height
        """
        self.parent = parent
        self.state = state
        self.width = width
        self.height = height

        # Color scheme: inherit from provided bg or parent's bg, otherwise use theme token
        bg_value = bg
        if bg_value is None:
            try:
                bg_value = parent.cget("bg")
            except Exception:
                bg_value = None
        if not bg_value:
            bg_value = colors["primary-50"]
        self._page_bg = bg_value

        # Build the treeview panel
        self._build_treeview_panel()

    def _build_treeview_panel(self):
        """Build the left treeview panel showing photo list."""
        left = tk.Frame(self.parent, bg=self._page_bg)
        left.place(x=0, y=0, width=self.width, height=self.height)

        # Title and description
        title_frame = tk.Frame(left, bg=self._page_bg)
        title_frame.pack(fill="x", padx=15, pady=(10, 2))

        tk.Label(
            title_frame,
            text="Explore Photos & Albums",
            font=quickSandBold(14),
            bg=self._page_bg,
            fg=colors["secondary-500"],
        ).pack(anchor="w")

        desc = tk.Label(
            title_frame,
            text="Browse photos, open albums, and interact with the photos.",
            font=quickSandRegular(11),
            bg=self._page_bg,
            fg=colors["secondary-400"],
        )
        desc.pack(anchor="w")

        # Treeview styling
        # Removed the `name` (photo) column — photos are shown in the preview.
        columns = ("album", "author", "category")
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Explore.Treeview",
            background=colors["secondary-400"],
            foreground=colors["primary-50"],
            fieldbackground=colors["secondary-400"],
            rowheight=28,
            font=("Quicksand", 10),
            borderwidth=0,
            relief="flat",
        )
        style.configure(
            "Explore.Treeview.Heading",
            background=colors["secondary-500"],
            foreground=colors["primary-50"],
            font=("Quicksand Bold", 11),
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
            "Explore.Treeview.Heading", background=[("active", colors["secondary-500"])]
        )

        # Minimal padding to maximize treeview space (left=2 for scrollbar, right=0 for clean edge)
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
            columns=columns,
            show="headings",
            style="Explore.Treeview",
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set,
            height=15,
        )
        tree.heading("album", text="Album")
        tree.heading("author", text="Author")
        tree.heading("category", text="Category")
        # Adjust column widths to better fill the (now wider) left panel
        tree.column("album", width=180, stretch=tk.NO)
        tree.column("author", width=140, stretch=tk.NO)
        tree.column("category", width=190, stretch=tk.NO)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.config(command=tree.yview)
        h_scrollbar.config(command=tree.xview)

        self.state.tree = tree
        tree.bind("<<TreeviewSelect>>", lambda e: on_treeview_select(e, self.state))

        # ── Pagination controls ────────────────────────────────────────
        # Create pagination UI controller (handles all pagination logic)
        def _on_page_changed():
            """Callback when page changes - update preview."""
            from app.presentation.views.explore.helpers.ui.preview import reset_preview

            reset_preview(self.state)

        pagination_controller = PaginationUIController(
            self.state, on_page_changed=_on_page_changed
        )
        # Store in state so load_catalog() can access it
        self.state._pagination_ui_controller = pagination_controller

        pagination_frame = tk.Frame(left, bg=self._page_bg, height=36)
        pagination_frame.pack(fill="x", padx=6, pady=(6, 0), side=tk.BOTTOM)

        prev_btn = tk.Button(
            pagination_frame,
            text="← Prev Page",
            font=quickSandBold(10),
            bg=colors["accent-300"],
            fg=colors["secondary-500"],
            borderwidth=0,
            highlightthickness=0,
            cursor="hand2",
            relief="flat",
            padx=8,
            pady=5,
            command=lambda: pagination_controller.go_to_prev_page(),
        )
        prev_btn.pack(side=tk.LEFT, padx=2)
        prev_btn.bind("<Enter>", lambda e: on_enter(e, prev_btn))
        prev_btn.bind("<Leave>", lambda e: on_leave(e, prev_btn))

        page_info_lbl = tk.Label(
            pagination_frame,
            text="Page 1/1",
            font=quickSandBold(10),
            bg=self._page_bg,
            fg=colors["secondary-500"],
        )
        page_info_lbl.pack(side=tk.LEFT, padx=10, expand=True)
        self.state.page_info_label = page_info_lbl

        next_btn = tk.Button(
            pagination_frame,
            text="Next Page →",
            font=quickSandBold(10),
            bg=colors["accent-300"],
            fg=colors["secondary-500"],
            borderwidth=0,
            highlightthickness=0,
            cursor="hand2",
            relief="flat",
            padx=8,
            pady=5,
            command=lambda: pagination_controller.go_to_next_page(),
        )
        next_btn.pack(side=tk.RIGHT, padx=2)
        next_btn.bind("<Enter>", lambda e: on_enter(e, next_btn))
        next_btn.bind("<Leave>", lambda e: on_leave(e, next_btn))

        self.state.prev_page_btn = prev_btn
        self.state.next_page_btn = next_btn

    def refresh_pagination(self):
        """Refresh pagination UI (called by explore controller)."""
        # Pagination is initialized in catalog.py with lazy-loading
        # This just refreshes the UI display
        if hasattr(self, "pagination_controller"):
            self.pagination_controller.refresh_ui()
