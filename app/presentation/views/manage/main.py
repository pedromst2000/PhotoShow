import tkinter as tk

from app.presentation.styles.colors import colors
from app.presentation.views.manage.helpers.data.manage_data import (
    load_categories,
    load_users,
    refresh_tree,
)
from app.presentation.views.manage.helpers.data.manage_state import ManageState
from app.presentation.views.manage.helpers.ui.manage_builder import (
    build_manage_body,
    build_manage_header,
)
from app.presentation.widgets.window import create_toplevel

_WIN_W = 1100
_WIN_H = 660


def manageWindow() -> None:
    """
    Open the admin Manage window (modal Toplevel).

    Builds the two-column layout:
    - Left: FilterBar (username/email/role/status) + users Treeview.
    - Right: Category input + Add/Edit buttons + categories ListboxWidget.

    The window is modal; the caller's UI is blocked until it is closed.
    """
    win: tk.Toplevel = create_toplevel(
        title="Manage",
        width=_WIN_W,
        height=_WIN_H,
        icon_path="app/assets/PhotoShowIcon.ico",
        bg_color=colors["secondary-500"],
    )

    state = ManageState()
    state.win = win

    # Load data before building the UI
    load_users(state)
    load_categories(state)

    # Build UI
    build_manage_header(win, state)
    build_manage_body(win, state)

    # Populate the Treeview with the full user list
    refresh_tree(state, state.all_users)

    win.grab_set()
