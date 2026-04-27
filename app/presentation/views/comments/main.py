import tkinter as tk

from app.presentation.views.comments.helpers.data.comments import load_and_render
from app.presentation.views.comments.helpers.ui.builder import (
    _BG,
    _WIN_H,
    _WIN_W,
    build_comment_list,
    build_input_area,
    build_photo_canvas,
)
from app.presentation.views.helpers.data.state import ExploreState
from app.presentation.widgets.window import create_toplevel


def open_comments(state: ExploreState):
    """
    Open the photo comments window.

    Displays all comments on the selected photo with the ability to
    add, delete and report comments.

    Args:
        state: Explore view state containing selected photo info.
    """
    if state.selected_photo is None:
        return  # No photo selected, should not happen as button is disabled, but guard just in case

    win = create_toplevel(
        title="💬 Photo Comments",
        width=_WIN_W,
        height=_WIN_H,
        icon_path="app/assets/PhotoShowIcon.ico",
        bg_color=_BG,
    )

    # Two separate ref lists to avoid unbounded growth:
    img_refs: list = []  # window-lifetime refs (photo image, add-icon)
    card_img_refs: list = (
        []
    )  # per-render refs (avatars, card action icons); cleared each reload

    # outer frame to hold everything and provide padding; also allows comment list to expand while keeping input area fixed at bottom
    outer = tk.Frame(win, bg=_BG)
    outer.pack(
        fill="both", expand=True, padx=16, pady=12
    )  # padding to prevent content from touching edges and give some breathing room

    build_photo_canvas(outer, state, img_refs)
    list_canvas, list_frame, comment_container = build_comment_list(outer)
    comment_container.pack(
        side=tk.TOP, fill=tk.X, pady=(0, 14)
    )  # pack before input so everything stacks top-to-top with no gap
    build_input_area(
        outer, win, state, list_canvas, list_frame, img_refs, card_img_refs
    )

    load_and_render(state, list_canvas, list_frame, win, img_refs, card_img_refs)

    win.grab_set()
