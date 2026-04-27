import tkinter as tk

from app.controllers.comment_controller import CommentController
from app.presentation.styles.colors import colors
from app.presentation.styles.fonts import quickSandBold
from app.presentation.views.comments.helpers.data.comments import load_and_render
from app.presentation.views.comments.helpers.ui.builder import (
    _BTN_BG,
    _BTN_FG,
    _ICON_DIR,
)
from app.presentation.views.helpers.data.state import ExploreState
from app.presentation.widgets.helpers.button import on_enter as button_on_enter
from app.presentation.widgets.helpers.button import on_leave as button_on_leave
from app.presentation.widgets.helpers.images import load_image
from app.presentation.widgets.helpers.scrollable_text import ScrollableText
from app.presentation.widgets.helpers.ui_dialogs import show_confirmation, show_error


def make_action_button(
    parent: tk.Frame,
    text: str,
    icon_name: str,
    card_img_refs: list,
    command,
) -> tk.Button:
    """Create a small icon-labelled action button (Report or Delete)."""
    icon_ref = load_image(_ICON_DIR + icon_name, size=(14, 14))
    card_img_refs.append(icon_ref)

    btn = tk.Button(
        parent,
        text=text,
        image=icon_ref,
        compound=tk.LEFT,
        font=quickSandBold(9),
        bg=_BTN_BG,
        fg=_BTN_FG,
        activebackground=colors["accent-100"],
        borderwidth=0,
        highlightthickness=0,
        cursor="hand2",
        command=command,
    )
    btn.bind("<Enter>", lambda e, b=btn: button_on_enter(e, b))  # type: ignore[misc]
    btn.bind("<Leave>", lambda e, b=btn: button_on_leave(e, b))  # type: ignore[misc]
    return btn


def submit_comment(
    win: tk.Toplevel,
    state: ExploreState,
    scrollable: ScrollableText,
    list_canvas: tk.Canvas,
    list_frame: tk.Frame,
    img_refs: list,
    card_img_refs: list,
    on_input_change,
) -> None:
    """Handle the Add Comment button action."""
    photo = state.selected_photo
    if photo is None:
        return

    text = scrollable.text.get("1.0", "end-1c")
    success, message, _ = CommentController.add_comment(photo.get("id"), text)

    if success:
        scrollable.text.delete("1.0", tk.END)
        on_input_change()
        load_and_render(state, list_canvas, list_frame, win, img_refs, card_img_refs)
        # Keep explore preview panel count in sync
        photo["comments"] = photo.get("comments", 0) + 1
        if state.comments_label:
            state.comments_label.config(text=str(photo["comments"]))
    else:
        show_error(win, "Error", message)


def on_delete(
    comment_id: int,
    win: tk.Toplevel,
    state: ExploreState,
    list_canvas: tk.Canvas,
    list_frame: tk.Frame,
    img_refs: list,
    card_img_refs: list,
) -> None:
    """Confirm and delete a comment, then refresh the list and explore counters."""
    confirmed = show_confirmation(
        win,
        "Delete Comment",
        "Are you sure you want to delete this comment?\n\nThis action cannot be undone.",
    )
    if not confirmed:
        return

    success, message = CommentController.delete_comment(comment_id)
    if success:
        load_and_render(state, list_canvas, list_frame, win, img_refs, card_img_refs)
        photo = state.selected_photo
        if photo is not None:
            photo["comments"] = max(0, photo.get("comments", 1) - 1)
            if state.comments_label:
                state.comments_label.config(text=str(photo["comments"]))
    else:
        show_error(win, "Error", message)
