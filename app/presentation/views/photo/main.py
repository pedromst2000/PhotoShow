import tkinter as tk

from app.presentation.styles.colors import colors
from app.presentation.views.helpers.data.state import BasePhotoState
from app.presentation.views.helpers.ui.builder.detail_panel import build_detail_panel
from app.presentation.widgets.window import create_toplevel


def open_photo_details(state: BasePhotoState) -> None:
    """
    Open the photo details window for the currently selected photo.

    Displays a rich detail view with the photo image, metadata (author avatar,
    username, category, star rating, likes and comment counts), the photo
    description, and action buttons (Like, See Comments, See Album, Report).

    Args:
        state: Any ``BasePhotoState`` subclass whose ``selected_photo`` is set.
    """
    if state.selected_photo is None:
        return

    win: tk.Toplevel = create_toplevel(
        title="📷 Photo Details",
        width=600,
        height=600,
        icon_path="app/assets/PhotoShowIcon.ico",
        bg_color=colors["primary-50"],
    )

    img_refs: list = []

    outer = tk.Frame(win, bg=colors["primary-50"])
    outer.pack(fill=tk.BOTH, expand=True, padx=16, pady=12)

    build_detail_panel(outer, state, win=win, img_refs=img_refs)

    # Keep image references alive for the window lifetime.
    win._img_refs = img_refs

    win.grab_set()
