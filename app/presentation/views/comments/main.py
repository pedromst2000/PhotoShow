import tkinter as tk

from app.presentation.views.comments.helpers.data.comments import (
    initialize_comments_pagination,
    render_comments,
)
from app.presentation.views.comments.helpers.data.state import CommentsWindowState
from app.presentation.views.comments.helpers.ui.builder import (
    _BG,
    _WIN_H,
    _WIN_W,
    build_comment_list,
    build_comments_pagination,
    build_input_area,
)
from app.presentation.views.helpers.data.state import BasePhotoState
from app.presentation.views.helpers.ui.builder import build_photo_canvas
from app.presentation.widgets.window import create_toplevel


def open_comments(state: BasePhotoState):
    """
    Open the photo comments window.

    Displays comments on the selected photo (5 per page) with the ability to
    add, delete and report comments.  Uses PaginationManager + PaginationUIController
    for navigation — no comments are cached on state.

    Args:
        state: Parent view state (ExploreState, AlbumState, …) containing the
               selected photo and the panel's comments-count label.
    """
    if state.selected_photo is None:
        return

    photo = state.selected_photo

    # Create a window-scoped state that wraps the parent for photo/label access
    # while owning its own comment pagination state.
    cstate = CommentsWindowState(state)

    win = create_toplevel(
        title="💬 Photo Comments",
        width=_WIN_W,
        height=_WIN_H,
        icon_path="app/assets/PhotoShowIcon.ico",
        bg_color=_BG,
    )
    cstate.win = win

    # Two separate ref lists to avoid unbounded growth:
    img_refs: list = []  # window-lifetime refs (photo image, add-icon)
    card_img_refs: list = []  # per-render refs; cleared each reload
    cstate.img_refs = img_refs
    cstate.card_img_refs = card_img_refs

    outer = tk.Frame(win, bg=_BG)
    outer.pack(fill="both", expand=True, padx=16, pady=12)

    build_photo_canvas(outer, cstate, img_refs)

    list_canvas, list_frame, comment_container = build_comment_list(outer)
    cstate.list_canvas = list_canvas
    cstate.list_frame = list_frame
    comment_container.pack(side=tk.TOP, fill=tk.X, pady=(0, 0))

    # Initialise pagination (page 1 fetched into cstate.photos).
    initialize_comments_pagination(cstate, photo.get("id"))

    # Build the prev/next pagination row and wire PaginationUIController.
    build_comments_pagination(outer, cstate)

    build_input_area(outer, win, cstate, img_refs, card_img_refs)

    # Render first page.
    render_comments(list_frame, cstate.photos, win, cstate, img_refs, card_img_refs)

    win.grab_set()
