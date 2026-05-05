import tkinter as tk
from typing import Optional

from app.presentation.styles.colors import colors
from app.presentation.styles.fonts import quickSandBold
from app.presentation.views.explore.helpers.data.catalog import (
    SORT_OPTIONS,
    apply_filters,
    get_category_options,
)
from app.presentation.widgets.helpers.button import on_enter as button_on_enter
from app.presentation.widgets.helpers.button import on_leave as button_on_leave
from app.presentation.widgets.helpers.icon_label import add_icon_canvas
from app.presentation.widgets.helpers.input import on_focus_in, on_focus_out


class FilterBarWidget(tk.Frame):
    """
    Filter bar widget with Author, Category, and Sort filters.
    """

    def __init__(
        self,
        parent: tk.Toplevel,
        state,
        width: int = 1300,
        bg: Optional[str] = None,
        btn_bg: Optional[str] = None,
        btn_fg: Optional[str] = None,
    ):
        """
        Create and place filter bar.

        Args:
            parent (tk.Toplevel): The parent window or frame to attach the filter bar to.
            state: The shared state object that holds filter variables and other relevant data.
            width (int): The width of the filter bar. Default is 1300 pixels.
            bg (str, optional): Background color for the filter bar. If None, it will inherit from the parent or use a default color.
            btn_bg (str, optional): Background color for buttons. If None, it will use a default color.
            btn_fg (str, optional): Foreground color for buttons. If None, it will use a default color.
        """
        self.parent = parent
        self.state = state
        self.width = width

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

        # Build the filter bar
        self._build_filter_bar()

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

        search_btn = tk.Button(
            author_section,
            text="Search",
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
            command=lambda: apply_filters(self.state),
        )
        search_btn.pack(side=tk.LEFT)
        search_btn.bind("<Enter>", lambda e: button_on_enter(e, search_btn))
        search_btn.bind("<Leave>", lambda e: button_on_leave(e, search_btn))

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
        cat_menu = tk.OptionMenu(
            category_section,
            cat_var,
            *categories,
            command=lambda _: apply_filters(self.state)
        )
        cat_menu.config(
            bg=colors["secondary-400"],
            fg=colors["primary-50"],
            activebackground=colors["secondary-500"],
            activeforeground=colors["primary-50"],
            font=quickSandBold(10),
            borderwidth=0,
            highlightthickness=0,
            cursor="hand2",
            width=14,
            relief="flat",
        )
        cat_menu["menu"].config(
            bg=colors["secondary-400"],
            fg=colors["primary-50"],
            activebackground=colors["secondary-500"],
            activeforeground=colors["primary-50"],
            font=quickSandBold(10),
            bd=0,
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
        sort_menu = tk.OptionMenu(
            sort_section,
            sort_var,
            *sort_options,
            command=lambda _: apply_filters(self.state)
        )
        sort_menu.config(
            bg=colors["secondary-400"],
            fg=colors["primary-50"],
            activebackground=colors["secondary-500"],
            activeforeground=colors["primary-50"],
            font=quickSandBold(10),
            borderwidth=0,
            highlightthickness=0,
            cursor="hand2",
            width=14,
            relief="flat",
        )
        sort_menu["menu"].config(
            bg=colors["secondary-400"],
            fg=colors["primary-50"],
            activebackground=colors["secondary-500"],
            activeforeground=colors["primary-50"],
            font=quickSandBold(10),
            bd=0,
        )
        sort_menu.pack(side=tk.LEFT)
        if not filters_enabled:
            sort_menu.config(state=tk.DISABLED)

        # Separator line
        sep = tk.Frame(self.parent, bg=colors["secondary-400"], height=2)
        sep.place(x=0, y=70, width=self.width)
