import tkinter as tk

from app.presentation.styles.colors import colors
from app.presentation.views.explore.helpers.data.state import ExploreState
from app.presentation.widgets.filter_bar import FilterBarWidget
from app.presentation.widgets.photo_treeview import PhotoTreeviewWidget
from app.presentation.widgets.preview_panel import PreviewPanelWidget

# Layout constants
_WIN_W = 1300
_WIN_H = 750
_PAGE_BG = colors["primary-50"]
_PANEL_BG = colors["secondary-300"]
_BTN_BG = colors["accent-300"]
_BTN_FG = colors["secondary-500"]
_CANVAS_BG = colors["secondary-400"]


def build_filter_bar(win: tk.Toplevel, state: ExploreState):
    """
    Build the Author / Category / Sort filter bar at the top.

    Delegates to FilterBarWidget.

    Args:
        win: Parent window
        state: Explore state object
    """
    # Ensure window background uses the exported page color token
    try:
        win.config(bg=_PAGE_BG)
    except Exception:
        # Best-effort: if parent doesn't support config/bg, ignore
        pass
    FilterBarWidget(
        win, state, width=_WIN_W, bg=_PAGE_BG, btn_bg=_BTN_BG, btn_fg=_BTN_FG
    )


def build_treeview_panel(body: tk.Frame, state: ExploreState):
    """
    Build the left treeview panel showing photo list.

    Delegates to PhotoTreeviewWidget.

    Args:
        body: Parent frame
        state: Explore state object
    """
    # Ensure body background matches page background token
    try:
        body.config(bg=_PAGE_BG)
    except Exception:
        pass
    # Balanced left panel (increased from 460 to 540 for better spacing)
    PhotoTreeviewWidget(body, state, width=540, height=_WIN_H - 76, bg=_PAGE_BG)


def build_preview_panel(body: tk.Frame, state: ExploreState):
    """
    Build the right preview panel with carousel and metadata.

    Delegates to PreviewPanelWidget.

    Args:
        body: Parent frame
        state: Explore state object
    """
    # Ensure body background matches page background token
    try:
        body.config(bg=_PAGE_BG)
    except Exception:
        pass
    # Balanced right panel (positioned at 545 to accommodate increased left panel width of 540)
    PreviewPanelWidget(
        body,
        state,
        x_pos=545,
        width=_WIN_W - 545,
        height=_WIN_H - 76,
        panel_bg=_PANEL_BG,
        btn_bg=_BTN_BG,
        btn_fg=_BTN_FG,
        canvas_bg=_CANVAS_BG,
    )
