import tkinter as tk

from app.controllers.comment_controller import CommentController
from app.presentation.styles.fonts import quickSandRegular
from app.presentation.views.comments.helpers.ui.builder import (
    _BG,
    _TEXT_FG,
    _WIN_W,
    build_comment_card,
)
from app.presentation.views.helpers.data.state import ExploreState


def load_and_render(
    state: ExploreState,
    list_canvas: tk.Canvas,
    list_frame: tk.Frame,
    win: tk.Toplevel,
    img_refs: list,
    card_img_refs: list,
):
    """
    Fetch fresh comments from the controller and re-render the list.

    Args:
        state: ExploreState containing selected photo info.
        list_canvas: The canvas containing the comment list (for scrollregion update).
        list_frame: The frame inside the canvas where comment cards are rendered.
        win: The comments window (for context in logging).
        img_refs: List to hold image references for the window lifetime (e.g. photo image, add icon).
        card_img_refs: List to hold image references for the comment cards (e.g. avatars, action icons); cleared and repopulated on each render.
    """
    photo = state.selected_photo
    if photo is None:
        return
    comments = CommentController.get_comments(photo.get("id"))
    render_comments(
        list_canvas, list_frame, comments, win, state, img_refs, card_img_refs
    )


def render_comments(
    list_canvas: tk.Canvas,
    list_frame: tk.Frame,
    comments: list,
    win: tk.Toplevel,
    state: ExploreState,
    img_refs: list,
    card_img_refs: list,
):
    """
    Clear and re-render all comment cards in the scrollable list.

    Args:
        list_canvas: The canvas containing the comment list (for scrollregion update).
        list_frame: The frame inside the canvas where comment cards are rendered.
        comments: List of comments to render.
        win: The comments window (for context in logging).
        state: ExploreState containing selected photo info.
        img_refs: List to hold image references for the window lifetime (e.g. photo image, add icon).
        card_img_refs: List to hold image references for the comment cards (e.g. avatars, action icons); cleared and repopulated on each render.
    """
    for widget in list_frame.winfo_children():
        widget.destroy()
    card_img_refs.clear()

    if not comments:
        tk.Label(
            list_frame,
            text="No comments yet. Be the first to comment!",
            font=quickSandRegular(11),
            bg=_BG,
            fg=_TEXT_FG,
            wraplength=_WIN_W - 80,
            justify="center",
        ).pack(expand=True, pady=30)
    else:
        for comment in comments:
            build_comment_card(
                list_frame, comment, win, state, list_canvas, img_refs, card_img_refs
            )

    list_canvas.configure(scrollregion=list_canvas.bbox("all"))
