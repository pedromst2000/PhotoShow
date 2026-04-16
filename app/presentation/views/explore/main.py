import tkinter as tk

from app.core.state.session import session
from app.presentation.styles.fonts import quickSandRegular
from app.presentation.views.explore.helpers.data.catalog import load_catalog
from app.presentation.views.explore.helpers.data.state import ExploreState
from app.presentation.views.explore.helpers.ui.builder import (
    _PAGE_BG,
    _WIN_H,
    _WIN_W,
    build_filter_bar,
    build_preview_panel,
    build_treeview_panel,
)
from app.presentation.widgets.helpers.icon_label import add_label
from app.presentation.widgets.helpers.ui_dialogs import show_limited_access
from app.presentation.widgets.window import create_toplevel


def exploreWindow():
    """
    Main function to create and display the Explore window.
    """
    # Create window
    win = create_toplevel(
        title="🔍 Explore 🔍",
        width=_WIN_W,
        height=_WIN_H,
        icon_path="app/assets/PhotoShowIcon.ico",
        bg_color=_PAGE_BG,
    )

    # Initialize state (Model)
    state = ExploreState()
    state.win = win
    role = session.role
    state.is_unsigned = role not in ("regular", "admin")

    # Show limited access warning
    if role == "unsigned":
        show_limited_access(
            win,
            "You can browse the top photos but interactions are disabled.",
        )

    # Add info label
    add_label(
        "info",
        win,
        "Close the window to navigate to the menu",
        font=quickSandRegular(10),
        label_pos=(14, 14),
    )

    build_filter_bar(win, state)  # build filter bar at the top

    body = tk.Frame(
        win, bg=_PAGE_BG
    )  # main content area for treeview and preview panels
    body.place(
        x=0, y=76, width=_WIN_W, height=_WIN_H - 76
    )  # leave space for filter bar at the top

    build_treeview_panel(body, state)  # build left treeview panel in the body
    build_preview_panel(body, state)  # build right preview panel in the body

    load_catalog(state)  # load catalog data

    win.grab_set()
