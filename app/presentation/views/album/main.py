import tkinter as tk

from app.presentation.styles.colors import colors
from app.presentation.styles.fonts import quickSandBold
from app.presentation.views.explore.helpers.data.state import ExploreState
from app.presentation.widgets.window import create_toplevel


def open_album(state: ExploreState) -> None:
    """
    Open the album view window.

    Displays all photos in the album containing the selected photo.

    Args:
        state: Explore view state containing selected photo info.
    """
    if state.selected_photo is None:
        return
    _open_album_stub("🗂 Album", 900, 600)


def _open_album_stub(title: str, width: int, height: int) -> None:
    """
    Create and display a stub window placeholder for album view.

    TODO: Implement full album view with photo grid, album info, and filtering options.

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
