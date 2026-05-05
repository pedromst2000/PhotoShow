import tkinter as tk

from app.core.state.session import session
from app.presentation.styles.colors import colors
from app.presentation.styles.fonts import quickSandRegular
from app.presentation.views.album.main import open_album
from app.presentation.views.explore.helpers.data.catalog import load_catalog
from app.presentation.views.explore.helpers.data.state import ExploreState
from app.presentation.views.helpers.ui.builder import build_preview_panel
from app.presentation.views.helpers.ui.preview import reset_preview
from app.presentation.views.helpers.ui.treeview import on_treeview_select
from app.presentation.widgets.filter_bar import FilterBarWidget
from app.presentation.widgets.helpers.icon_label import add_label
from app.presentation.widgets.helpers.ui_dialogs import (
    handle_delete_photo,
    show_limited_access,
)
from app.presentation.widgets.treeview import TreeviewWidget
from app.presentation.widgets.window import create_toplevel

_WIN_W = 1300
_WIN_H = 750
_PAGE_BG = colors["primary-50"]
_BTN_BG = colors["accent-300"]
_BTN_FG = colors["secondary-500"]


def exploreWindow():
    """
    Main function to create and display the Explore window.
    """
    win = create_toplevel(
        title="🔍 Explore 🔍",
        width=_WIN_W,
        height=_WIN_H,
        icon_path="app/assets/PhotoShowIcon.ico",
        bg_color=_PAGE_BG,
    )

    state = ExploreState()
    state.win = win
    role = session.role
    state.is_unsigned = role not in ("regular", "admin")

    if role == "unsigned":
        show_limited_access(
            win,
            "You can browse the top photos but interactions are disabled.",
        )

    add_label(
        "info",
        win,
        "Close the window to navigate to the menu",
        font=quickSandRegular(10),
        label_pos=(14, 14),
    )

    FilterBarWidget(
        win, state, width=_WIN_W, bg=_PAGE_BG, btn_bg=_BTN_BG, btn_fg=_BTN_FG
    )

    body = tk.Frame(win, bg=_PAGE_BG)
    body.place(x=0, y=76, width=_WIN_W, height=_WIN_H - 76)

    TreeviewWidget(
        body,
        state,
        columns=[
            {"key": "album", "heading": "Album", "width": 180},
            {"key": "author", "heading": "Author", "width": 140},
            {"key": "category", "heading": "Category", "width": 190},
        ],
        title="Explore Photos & Albums",
        description="Browse photos, open albums, and interact with the photos.",
        on_select=lambda e: on_treeview_select(e, state),
        on_page_changed=lambda: reset_preview(state),
        width=540,
        height=_WIN_H - 76,
        bg=_PAGE_BG,
    )

    build_preview_panel(
        body,
        state,
        title="Preview Photos",
        subtitle=(
            "View the album above  \u2022  Click the username to view the author's profile"
            "  \u2022  Hover over the stars to rate the photo"
        ),
        extra_buttons=[
            {
                "name": "album_btn",
                "label": "  See Album",
                "icon": "Eye_Icon_V2.png",
                "command": lambda: open_album(state),
            },
            {
                "name": "delete_btn",
                "label": "  Delete Photo",
                "icon": "Remove_Icon.png",
                "command": lambda: handle_delete_photo(state),
            },
        ],
        x_pos=545,
        width=_WIN_W - 545,
        height=_WIN_H - 76,
    )

    load_catalog(state)

    win.grab_set()
