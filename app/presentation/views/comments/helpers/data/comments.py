import tkinter as tk

from app.controllers.comment_controller import CommentController
from app.presentation.styles.fonts import quickSandRegular
from app.presentation.views.comments.helpers.ui.builder import (
    _BG,
    _TEXT_FG,
    _WIN_W,
    build_comment_card,
)
from app.presentation.views.helpers.data.pagination import PaginationManager
from app.presentation.views.helpers.data.pagination_helpers import init_list_pagination

_ITEMS_PER_PAGE = 5


def initialize_comments_pagination(cstate, photo_id: int):
    """Initialise (or re-initialise) comment pagination for *cstate*.

    This function sets up pagination state in *cstate* using PaginationManager with

    Re-calling this function after a comment is added or deleted creates a
    fresh closure with the updated comment list and resets to page 1.

    Args:
        cstate: CommentsWindowState to initialise pagination on.
        photo_id: The ID of the photo whose comments should be paginated.
    """
    all_comments = CommentController.get_comments(photo_id)
    init_list_pagination(cstate, all_comments, _ITEMS_PER_PAGE)


def load_and_render(cstate, win: tk.Toplevel, img_refs: list, card_img_refs: list):
    """Re-initialise comment pagination and render the first page.

    Called on initial open and after each add/delete to reflect changes.
    Pagination is reset to page 1 because the comment list may have changed
    (a comment was added or removed).

    Args:
        cstate: CommentsWindowState that owns the pagination and UI refs.
        win: The comments window (passed through to card builders).
        img_refs: Window-lifetime image references.
        card_img_refs: Per-render image references; cleared on each call.
    """
    photo = cstate.selected_photo
    if photo is None:
        return

    initialize_comments_pagination(cstate, photo.get("id"))
    render_comments(
        cstate.list_frame, cstate.photos, win, cstate, img_refs, card_img_refs
    )

    # Sync pagination UI (buttons + page label) after re-init.
    ctrl = getattr(cstate, "_pagination_ui_controller", None)
    if ctrl is not None:
        ctrl._update_button_states(PaginationManager.get_total_pages(cstate))
        label = getattr(cstate, "page_info_label", None)
        if label is not None:
            label.config(text=PaginationManager.get_page_info(cstate))


def render_comments(
    list_frame: tk.Frame,
    comments: list,
    win: tk.Toplevel,
    cstate,
    img_refs: list,
    card_img_refs: list,
):
    """Clear and re-render comment cards for the current page.

    The scrollregion is updated automatically via the ``<Configure>`` binding
    set up in ``build_comment_list`` — no manual canvas.configure call needed.

    Args:
        list_frame: The frame inside the canvas where comment cards are rendered.
        comments: Current-page comment dicts to render.
        win: The comments window.
        cstate: CommentsWindowState (for photo info delegation and UI refs).
        img_refs: Window-lifetime image references.
        card_img_refs: Per-render refs; cleared before rebuilding cards.
    """
    for widget in list_frame.winfo_children():
        widget.destroy()
    card_img_refs.clear()

    # Scroll back to top after clearing (page change or reload).
    list_canvas = getattr(cstate, "list_canvas", None)
    if list_canvas is not None:
        list_canvas.yview_moveto(0)

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
                list_frame, comment, win, cstate, img_refs, card_img_refs
            )
