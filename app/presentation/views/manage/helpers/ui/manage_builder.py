import tkinter as tk

from app.presentation.styles.button import ACTION_BTN_STYLE
from app.presentation.styles.colors import colors
from app.presentation.styles.fonts import quickSandBold, quickSandRegular
from app.presentation.styles.theme import (
    BTN_BG,
    BTN_FG,
    HEADER_FG,
    LIST_BG,
    PANEL_BG,
)
from app.presentation.views.helpers.ui.builder import (
    build_admin_window_body,
    build_admin_window_header,
    build_two_column_frames,
)
from app.presentation.views.manage.helpers.data.manage_state import ManageState
from app.presentation.views.manage.helpers.ui.manage_interactions import (
    on_add_category,
    on_apply_user_action,
    on_category_select,
    on_edit_category,
    on_filter_users,
    on_tree_select,
)
from app.presentation.widgets.filter_bar import FilterBarWidget
from app.presentation.widgets.helpers.button import make_button
from app.presentation.widgets.helpers.input import on_focus_in, on_focus_out
from app.presentation.widgets.listbox_widget import ListboxWidget
from app.presentation.widgets.treeview import TreeviewWidget

# ── Layout constants ───────────────────────────────────────────────────────────
_WIN_W: int = 1100
_WIN_H: int = 660
_HEADER_H: int = 80
_LEFT_W: int = 540  # Users panel (Treeview + FilterBar)
_RIGHT_W: int = _WIN_W - _LEFT_W  # Categories panel = 560

_BG = LIST_BG
_LIST_BG = LIST_BG
_PANEL_BG = PANEL_BG
_BTN_BG = BTN_BG
_BTN_FG = BTN_FG
_HEADER_FG = HEADER_FG
_ICON_DIR = "app/assets/images/UI_Icons/"

_FILTER_BAR_H = 150  # height of the filter bar (two labeled sections)
_TREEVIEW_H = _WIN_H - _HEADER_H - _FILTER_BAR_H  # remaining for treeview

_ROLE_OPTIONS = ["All Roles", "unsigned", "regular"]
_CHANGE_ROLE_OPTIONS = ["Select Role", "unsigned", "regular"]
_STATUS_OPTIONS = ["Select Status", "block", "unblock"]


# ── Header ─────────────────────────────────────────────────────────────────────


def build_manage_header(win: tk.Toplevel, state: ManageState) -> None:
    """Build the window header with title and subtitle.

    Args:
        win: The manage Toplevel window.
        state: Manage state (unused; reserved for future adaptation).
    """
    build_admin_window_header(
        win,
        title="Manage",
        subtitle="Manage users and categories \u2014 filter, change roles, block users, and manage categories.",
    )


# ── Body ───────────────────────────────────────────────────────────────────────


def build_manage_body(win: tk.Toplevel, state: ManageState) -> None:
    """Build the two-column body: users (left) and categories (right).

    Args:
        win: The manage Toplevel window.
        state: Manage state with data already loaded.
    """

    def _build_content(content_frame: tk.Frame, body: tk.Frame) -> None:
        left, right = build_two_column_frames(
            content_frame,
            _LEFT_W,
            list_bg=_LIST_BG,
            panel_bg=_PANEL_BG,
        )
        _build_left_panel(left, state)
        _build_right_panel(right, state)

    build_admin_window_body(
        win,
        state,
        has_items=True,  # Always show content; Treeview handles empty state inline
        empty_icon="\U0001f465",
        empty_title="No users found",
        empty_subtitle="There are no manageable users in the system.",
        build_content=_build_content,
    )


# ── Left panel — filter bar + users treeview ──────────────────────────────────

_USER_COLUMNS = [
    {"key": "username", "heading": "Username", "width": 140},
    {"key": "email", "heading": "Email", "width": 190},
    {"key": "role", "heading": "Role", "width": 80},
    {"key": "status", "heading": "Status", "width": 80},
]


def _build_left_panel(left: tk.Frame, state: ManageState) -> None:
    """Build the left column: filter bar above the paginated users Treeview.

    Args:
        left: The left-column frame.
        state: Manage state; widget refs are stored here by the widgets.
    """
    # ── Filter bar (FilterBarWidget in generic/rows mode) ──────────────────
    filter_rows = [
        # ── Section 1: Filter users ────────────────────────────────────────
        [{"type": "header", "text": "FILTER USERS"}],
        [
            {
                "type": "entry",
                "label": "Username",
                "var": state.username_var,
                "entry_width": 14,
            },
            {
                "type": "entry",
                "label": "Email",
                "var": state.email_var,
                "entry_width": 18,
            },
        ],
        [
            {
                "type": "option",
                "label": "Role",
                "var": state.role_var,
                "options": _ROLE_OPTIONS,
                "menu_width": 10,
            },
            {
                "type": "button",
                "text": "Filter",
                "cmd": lambda: on_filter_users(state),
                "store_as": "filter_btn",
            },
        ],
        # ── Separator ──────────────────────────────────────────────────────
        [{"type": "divider"}],
        # ── Section 2: Apply changes to selected user ──────────────────────
        [{"type": "header", "text": "CHANGE ROLE / STATUS  (select a user first)"}],
        [
            {
                "type": "option",
                "label": "Set Role",
                "var": state.change_role_var,
                "options": _CHANGE_ROLE_OPTIONS,
                "menu_width": 9,
            },
            {
                "type": "option",
                "label": "Set Status",
                "var": state.status_var,
                "options": _STATUS_OPTIONS,
                "menu_width": 9,
            },
            {
                "type": "button",
                "text": "Apply",
                "cmd": lambda: on_apply_user_action(state),
                "store_as": "apply_btn",
            },
        ],
    ]

    filter_frame = tk.Frame(left, bg=_LIST_BG, height=_FILTER_BAR_H)
    filter_frame.pack(fill="x")
    filter_frame.pack_propagate(False)

    FilterBarWidget(
        filter_frame,
        state=state,
        rows=filter_rows,
        bg=_LIST_BG,
        btn_bg=_BTN_BG,
        btn_fg=_BTN_FG,
    ).pack(fill="x")

    # ── Users treeview (TreeviewWidget with pagination) ────────────────────
    tree_frame = tk.Frame(left, bg=_LIST_BG)
    tree_frame.pack(fill="both", expand=True)

    TreeviewWidget(
        tree_frame,
        state,
        columns=_USER_COLUMNS,
        title="Users",
        description="Filter, change roles, and block/unblock users.",
        on_select=lambda _e: on_tree_select(state),
        row_fn=lambda u: (
            u.get("username", ""),
            u.get("email", ""),
            u.get("role", ""),
            "Blocked" if u.get("isBlocked") else "Active",
        ),
        empty_label="No users found",
        width=_LEFT_W,
        height=_TREEVIEW_H,
        bg=_LIST_BG,
    )


# ── Right panel — categories management ───────────────────────────────────────


def _build_right_panel(right: tk.Frame, state: ManageState) -> None:
    """Build the right column: category input, Add/Edit buttons, categories listbox.

    Args:
        right: The right-column frame.
        state: Manage state; category widget refs are stored here.
    """
    _build_category_header(right)
    _build_category_input(right, state)
    _build_category_action_buttons(right, state)
    _build_category_separator(right)
    _build_category_list(right, state)


def _build_category_header(parent: tk.Frame) -> None:
    """Render the section title and a horizontal divider.

    Args:
        parent: Right-column frame.
    """
    tk.Label(
        parent,
        text="Manage Categories",
        font=quickSandBold(14),
        bg=_PANEL_BG,
        fg=_HEADER_FG,
        anchor="w",
    ).pack(anchor="w", padx=20, pady=(18, 4))

    tk.Frame(parent, bg=colors["secondary-400"], height=1).pack(
        fill="x", padx=20, pady=(0, 10)
    )


def _build_category_input(parent: tk.Frame, state: ManageState) -> None:
    """Build the category name input row.

    Args:
        parent: Right-column frame.
        state: Manage state; ``category_entry`` ref is stored here.
    """
    row = tk.Frame(parent, bg=_PANEL_BG)
    row.pack(fill="x", padx=20, pady=(0, 8))

    tk.Label(
        row,
        text="Category name",
        font=quickSandBold(10),
        bg=_PANEL_BG,
        fg=colors["secondary-400"],
    ).pack(anchor="w", pady=(0, 4))

    entry = tk.Entry(
        row,
        textvariable=state.category_input_var,
        width=32,
        borderwidth=0,
        font=quickSandRegular(11),
        bg=colors["secondary-400"],
        fg=_HEADER_FG,
        highlightthickness=0,
        cursor="xterm",
        insertbackground=_HEADER_FG,
    )
    entry.pack(fill="x")
    entry.bind("<FocusIn>", lambda e: on_focus_in(e, entry))
    entry.bind("<FocusOut>", lambda e: on_focus_out(e, entry))

    state.category_entry = entry


def _build_category_action_buttons(parent: tk.Frame, state: ManageState) -> None:
    """Build the Add Category and Edit Category buttons side-by-side.

    Follows the album_profile_builder pattern: two action buttons above the list.

    Args:
        parent: Right-column frame.
        state: Manage state; button refs are stored here.
    """
    btn_row = tk.Frame(parent, bg=_PANEL_BG)
    btn_row.pack(fill="x", padx=20, pady=(0, 10))

    add_btn = make_button(
        btn_row,
        text="  Add Category",
        cmd=lambda: on_add_category(state),
        **ACTION_BTN_STYLE,
    )
    add_btn.pack(side="left", padx=(0, 8))
    state.add_category_btn = add_btn

    edit_btn = make_button(
        btn_row,
        text="  Edit Category",
        cmd=lambda: on_edit_category(state),
        **ACTION_BTN_STYLE,
    )
    edit_btn.pack(side="left")
    state.edit_category_btn = edit_btn


def _build_category_separator(parent: tk.Frame) -> None:
    """Render a thin horizontal separator and a sub-section title.

    Args:
        parent: Right-column frame.
    """
    tk.Frame(parent, bg=colors["secondary-400"], height=1).pack(
        fill="x", padx=20, pady=(0, 8)
    )

    tk.Label(
        parent,
        text="Available Categories",
        font=quickSandBold(11),
        bg=_PANEL_BG,
        fg=colors["secondary-400"],
        anchor="w",
    ).pack(anchor="w", padx=20, pady=(0, 6))


def _build_category_list(parent: tk.Frame, state: ManageState) -> None:
    """Build the scrollable ListboxWidget showing available categories.

    Args:
        parent: Right-column frame.
        state: Manage state; ``categories_listbox`` ref is stored here.
    """
    listbox_h = _WIN_H - _HEADER_H - 190  # remaining height after controls

    listbox = ListboxWidget(
        parent,
        items=state.all_categories,
        label_fn=lambda cat: cat.get("category", ""),
        on_select=lambda idx: on_category_select(idx, state),
        width=_RIGHT_W - 40,
        height=listbox_h,
        bg=colors["secondary-400"],
        fg=_HEADER_FG,
        select_bg=_LIST_BG,
        select_fg=_HEADER_FG,
    )
    listbox.pack(padx=20, pady=(0, 12))
    state.categories_listbox = listbox
