import tkinter as tk

from app.presentation.styles.colors import colors
from app.presentation.styles.fonts import quickSandBold
from app.presentation.views.explore.helpers.data.state import ExploreState
from app.presentation.widgets.window import create_toplevel


def open_photo_details(state: ExploreState) -> None:
    """
    Open the photo details window.

    Displays comprehensive information about the selected photo.

    Args:
        state: Explore view state containing selected photo info.
    """
    if state.selected_photo is None:
        return
    _open_photo_details_stub("📷 Photo Details", 800, 600)


def _open_photo_details_stub(title: str, width: int, height: int) -> None:
    """
    Create and display a stub window placeholder for photo details.

    TODO: Implement full photo details content with metadata, tags, and info.

    Args:
        title: Window title to display.
        width: Window width in pixels.
        height: Window height in pixels.
    """
    win = create_toplevel(
        title=title,
        width=width,
        height=height,
        icon_path="app/assets/PhotoShowIcon.ico",
        bg_color=colors["primary-50"],
    )
    tk.Label(
        win,
        text=title,
        font=quickSandBold(16),
        bg=colors["primary-50"],
        fg=colors["secondary-500"],
    ).pack(expand=True)
