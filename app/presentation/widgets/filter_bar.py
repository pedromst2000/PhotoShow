import tkinter as tk
from typing import Callable, Optional

from app.presentation.styles.colors import colors
from app.presentation.styles.fonts import quickSandBold
from app.presentation.views.explore.helpers.data.catalog import (
    SORT_OPTIONS,
    get_category_options,
    load_catalog,
)
from app.presentation.widgets.helpers.button import make_button
from app.presentation.widgets.helpers.icon_label import add_icon_canvas
from app.presentation.widgets.helpers.input import on_focus_in, on_focus_out


def build_option_filter(
    parent: tk.Frame,
    var: tk.StringVar,
    options: list[str],
    on_change: Callable,
    *,
    width: int = 12,
    bg: Optional[str] = None,
) -> tk.OptionMenu:
    """
    Create a styled OptionMenu and return the widget without packing it.

    Shared by any view that needs a compact dropdown filter (reports window,
    and internally by ``FilterBarWidget``).

    Args:
        parent: Parent frame to attach the OptionMenu to.
        var: The ``StringVar`` bound to the menu selection.
        options: List of option strings (first entry used as default).
        on_change: Callable invoked whenever the selection changes.
        width: Width of the menu widget in characters.
        bg: Background colour for the menu (defaults to ``secondary-400``).

    Returns:
        tk.OptionMenu: The configured menu widget (caller must pack/place it).
    """
    _bg = bg or colors["secondary-400"]
    menu = tk.OptionMenu(parent, var, *options, command=lambda _: on_change())
    menu.config(
        bg=_bg,
        fg=colors["primary-50"],
        activebackground=colors["secondary-500"],
        activeforeground=colors["primary-50"],
        font=quickSandBold(10),
        borderwidth=0,
        highlightthickness=0,
        cursor="hand2",
        width=width,
        relief="flat",
    )
    menu["menu"].config(
        bg=_bg,
        fg=colors["primary-50"],
        activebackground=colors["secondary-500"],
        activeforeground=colors["primary-50"],
        font=quickSandBold(10),
        bd=0,
    )
    return menu


class FilterBarWidget(tk.Frame):
    """
    Filter bar widget.

    Two modes:
    - **Generic mode** (``rows`` provided): renders any list of row configs using
      ``pack`` layout.  Caller packs/places the widget itself.
    - **Explore mode** (``rows=None``): legacy Author / Category / Sort bar that
      places content directly in ``parent`` using absolute coordinates.
    """

    def __init__(
        self,
        parent: tk.Toplevel,
        state=None,
        rows: Optional[list[list[dict]]] = None,
        width: int = 1300,
        bg: Optional[str] = None,
        btn_bg: Optional[str] = None,
        btn_fg: Optional[str] = None,
    ):
        """
        Create the filter bar.

        Args:
            parent: Parent window or frame.
            state: Shared state object.  In explore mode the state must expose
                ``is_unsigned``.  In generic mode it is only used for
                ``store_as`` refs (may be *None*).
            rows: Generic-mode row definitions.  Each row is a list of section
                dicts with keys ``type`` (``"entry"``, ``"option"``, or
                ``"button"``), ``label`` (optional), ``var`` (StringVar),
                ``entry_width`` / ``menu_width`` / ``options`` / ``on_change``
                / ``text`` / ``cmd`` / ``store_as`` as appropriate.
                When *None* the widget falls back to the legacy explore bar.
            width: Width used by the legacy explore bar.
            bg: Background colour; inherits from parent if *None*.
            btn_bg: Button background colour.
            btn_fg: Button foreground colour.
        """
        self.parent = parent
        self.state = state
        self.width = width
        self._rows = rows

        # Color scheme (allow overriding via bg or inherit from parent)
        bg_value = bg
        if bg_value is None:
            try:
                bg_value = parent.cget("bg")
            except Exception:
                bg_value = None
        if not bg_value:
            bg_value = colors["primary-50"]
        self._page_bg = bg_value
        self._btn_bg = btn_bg if btn_bg is not None else colors["accent-300"]
        self._btn_fg = btn_fg if btn_fg is not None else colors["secondary-500"]
        self._icon_dir = "app/assets/images/UI_Icons/"

        if rows is not None:
            # Generic mode: self IS the container Frame
            super().__init__(parent, bg=self._page_bg)
            self._build_custom_rows()
        else:
            # Legacy explore mode: places widgets in self.parent
            self._build_filter_bar()

    # ── Generic mode helpers ───────────────────────────────────────────────────

    def _build_custom_rows(self) -> None:
        """Build dynamic filter rows using pack layout.

        Special single-item rows:
        - ``{"type": "header", "text": "..."}`` — renders a subtle section title.
        - ``{"type": "divider"}`` — renders a thin horizontal separator line.
        """
        assert self._rows is not None
        for row_items in self._rows:
            if len(row_items) == 1:
                stype = row_items[0].get("type")
                if stype == "header":
                    tk.Label(
                        self,
                        text=row_items[0]["text"],
                        font=quickSandBold(9),
                        bg=self._page_bg,
                        fg=colors["secondary-300"],
                        anchor="w",
                    ).pack(fill="x", padx=8, pady=(6, 0))
                    continue
                if stype == "divider":
                    tk.Frame(self, bg=colors["secondary-400"], height=1).pack(
                        fill="x", padx=8, pady=(4, 0)
                    )
                    continue
            row = tk.Frame(self, bg=self._page_bg)
            row.pack(fill="x", padx=8, pady=(4, 2))
            for section in row_items:
                self._build_section(row, section)

    def _build_section(self, parent_row: tk.Frame, section: dict) -> None:
        """Render one filter section (entry, option, or button) inside a row.

        Args:
            parent_row: Row frame to pack the section into.
            section: Section config dict.
        """
        stype = section.get("type")
        label = section.get("label")

        if label:
            tk.Label(
                parent_row,
                text=label,
                font=quickSandBold(10),
                bg=self._page_bg,
                fg=colors["primary-50"],
            ).pack(side="left", padx=(0, 4))

        if stype == "entry":
            entry = tk.Entry(
                parent_row,
                textvariable=section["var"],
                width=section.get("entry_width", 14),
                borderwidth=0,
                font=quickSandBold(10),
                bg=colors["secondary-400"],
                fg=colors["primary-50"],
                highlightthickness=0,
                cursor="xterm",
                insertbackground=colors["primary-50"],
            )
            entry.pack(side="left", padx=(0, 8))
            entry.bind("<FocusIn>", lambda e: on_focus_in(e, entry))
            entry.bind("<FocusOut>", lambda e: on_focus_out(e, entry))

        elif stype == "option":
            menu = build_option_filter(
                parent_row,
                section["var"],
                section["options"],
                section.get("on_change", lambda: None),
                width=section.get("menu_width", 12),
                bg=colors["secondary-400"],
            )
            menu.pack(side="left", padx=(0, 8))

        elif stype == "button":
            btn = make_button(
                parent_row,
                section["text"],
                cmd=section["cmd"],
                font=quickSandBold(10),
                bg=self._btn_bg,
                fg=self._btn_fg,
                borderwidth=0,
                highlightthickness=0,
                cursor="hand2",
                relief="flat",
                padx=8,
                pady=3,
            )
            btn.pack(side="left")
            store_as = section.get("store_as")
            if store_as and self.state is not None:
                setattr(self.state, store_as, btn)

    def _build_filter_bar(self):
        """Build the Author / Category / Sort filter bar at the top."""
        filters_enabled = not self.state.is_unsigned

        # Single-row compact container
        filter_container = tk.Frame(self.parent, bg=self._page_bg)
        filter_container.place(x=10, y=34, height=34, width=self.width - 20)

        # ── Author section ──────────────────────────────────────────────
        author_section = tk.Frame(filter_container, bg=self._page_bg)
        author_section.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5)

        add_icon_canvas(
            "filter",
            author_section,
            self._icon_dir + "Filter_Icon.png",
            icon_pos=(0, 0),
            icon_size=(24, 24),
            canvas_size=(24, 24),
        ).pack(side=tk.LEFT, padx=(0, 4))

        tk.Label(
            author_section,
            text="Author",
            font=quickSandBold(11),
            bg=self._page_bg,
            fg=colors["secondary-500"],
        ).pack(side=tk.LEFT, padx=(0, 6))

        author_var = tk.StringVar()
        self.state.author_var = author_var
        author_entry = tk.Entry(
            author_section,
            textvariable=author_var,
            width=16,
            borderwidth=0,
            font=quickSandBold(10),
            bg=colors["secondary-300"],
            fg=colors["primary-50"],
            disabledbackground=colors["secondary-300"],
            highlightthickness=0,
            cursor="xterm",
            state=tk.NORMAL if filters_enabled else tk.DISABLED,
        )
        author_entry.pack(side=tk.LEFT, padx=(0, 6))
        author_entry.bind("<FocusIn>", lambda e: on_focus_in(e, author_entry))
        author_entry.bind("<FocusOut>", lambda e: on_focus_out(e, author_entry))

        search_btn = make_button(
            author_section,
            "Search",
            cmd=lambda: load_catalog(self.state),
            font=quickSandBold(10),
            bg=self._btn_bg,
            fg=self._btn_fg,
            borderwidth=0,
            highlightthickness=0,
            cursor="hand2",
            relief="flat",
            padx=8,
            pady=3,
            state=tk.NORMAL if filters_enabled else tk.DISABLED,
        )
        search_btn.pack(side=tk.LEFT)

        # ── Category section ────────────────────────────────────────────
        category_section = tk.Frame(filter_container, bg=self._page_bg)
        category_section.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5)

        add_icon_canvas(
            "filter",
            category_section,
            self._icon_dir + "Filter_Icon.png",
            icon_pos=(0, 0),
            icon_size=(24, 24),
            canvas_size=(24, 24),
        ).pack(side=tk.LEFT, padx=(0, 4))

        tk.Label(
            category_section,
            text="Category",
            font=quickSandBold(11),
            bg=self._page_bg,
            fg=colors["secondary-500"],
        ).pack(side=tk.LEFT, padx=(0, 6))

        # Get categories from controller (includes "All" as first option)
        categories = get_category_options()
        cat_var = tk.StringVar(value="All")
        self.state.category_var = cat_var
        cat_menu = build_option_filter(
            category_section,
            cat_var,
            categories,
            lambda: load_catalog(self.state),
        )
        cat_menu.pack(side=tk.LEFT)
        if not filters_enabled:
            cat_menu.config(state=tk.DISABLED)

        # ── Sort section ────────────────────────────────────────────────
        sort_section = tk.Frame(filter_container, bg=self._page_bg)
        sort_section.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5)

        add_icon_canvas(
            "sort",
            sort_section,
            self._icon_dir + "Sort_Icon.png",
            icon_pos=(0, 0),
            icon_size=(24, 24),
            canvas_size=(24, 24),
        ).pack(side=tk.LEFT, padx=(0, 4))

        tk.Label(
            sort_section,
            text="Sort by",
            font=quickSandBold(11),
            bg=self._page_bg,
            fg=colors["secondary-500"],
        ).pack(side=tk.LEFT, padx=(0, 6))

        sort_var = tk.StringVar(value="Most Recent")
        self.state.sort_var = sort_var
        sort_options = list(SORT_OPTIONS.keys())
        sort_menu = build_option_filter(
            sort_section,
            sort_var,
            sort_options,
            lambda: load_catalog(self.state),
        )
        sort_menu.pack(side=tk.LEFT)
        if not filters_enabled:
            sort_menu.config(state=tk.DISABLED)

        # Separator line
        sep = tk.Frame(self.parent, bg=colors["secondary-400"], height=2)
        sep.place(x=0, y=70, width=self.width)
