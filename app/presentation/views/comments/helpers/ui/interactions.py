import tkinter as tk

from app.controllers.comment_controller import CommentController
from app.presentation.styles.colors import colors
from app.presentation.styles.fonts import quickSandBold
from app.presentation.views.comments.helpers.data.comments import load_and_render
from app.presentation.views.comments.helpers.ui.builder import (
    _BTN_BG,
    _BTN_FG,
    _COMMENT_MAX_LEN,
    _ICON_DIR,
)
from app.presentation.widgets.helpers.button import on_enter as button_on_enter
from app.presentation.widgets.helpers.button import on_leave as button_on_leave
from app.presentation.widgets.helpers.char_limit import validate_text_char_limit
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
    """
    Create a small icon-labelled action button (Report or Delete).

    Args:
        parent: The parent frame to attach the button to.
        text: The button text label.
        icon_name: Filename of the button icon (in _ICON_DIR).
        card_img_refs: List to hold image references for the comment card lifetime.
        command: The function to call when the button is clicked.
    Returns:
        tk.Button: The created button widget.
    """
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
    cstate,
    scrollable: ScrollableText,
    img_refs: list,
    card_img_refs: list,
    on_input_change,
):
    """Handle the Add Comment button action.

    Args:
        win: The top-level comments window.
        cstate: CommentsWindowState (owns selected_photo delegation and UI refs).
        scrollable: The comment text input widget.
        img_refs: Window-lifetime image references.
        card_img_refs: Per-render image references for comment cards.
        on_input_change: Callback to re-validate the input after submission.
    """
    photo = cstate.selected_photo
    if photo is None:
        return

    text = scrollable.text.get("1.0", "end-1c")
    success, message, _ = CommentController.add_comment(photo.get("id"), text)

    if success:
        scrollable.text.delete("1.0", tk.END)
        on_input_change()
        load_and_render(cstate, win, img_refs, card_img_refs)
        # Keep parent panel comment counter in sync.
        photo["comments"] = photo.get("comments", 0) + 1
        if cstate.comments_label:
            cstate.comments_label.config(text=str(photo["comments"]))
    else:
        show_error(win, "Error", message)


def on_delete(
    comment_id: int,
    win: tk.Toplevel,
    cstate,
    img_refs: list,
    card_img_refs: list,
):
    """Confirm and delete a comment, then refresh the list and parent counters.

    Args:
        comment_id: ID of the comment to delete.
        win: The top-level comments window.
        cstate: CommentsWindowState (owns selected_photo delegation and UI refs).
        img_refs: Window-lifetime image references.
        card_img_refs: Per-render image references for comment cards.
    """
    confirmed = show_confirmation(
        win,
        "Delete Comment",
        "Are you sure you want to delete this comment?\n\nThis action cannot be undone.",
    )
    if not confirmed:
        return

    success, message = CommentController.delete_comment(comment_id)
    if success:
        load_and_render(cstate, win, img_refs, card_img_refs)
        photo = cstate.selected_photo
        if photo is not None:
            photo["comments"] = max(0, photo.get("comments", 1) - 1)
            if cstate.comments_label:
                cstate.comments_label.config(text=str(photo["comments"]))
    else:
        show_error(win, "Error", message)


def on_input_change(
    scrollable: ScrollableText,
    char_count: tk.Label,
    add_btn: tk.Button,
    event=None,
):
    """
    Validate the comment input and enable/disable the Add Comment button.

    Args:
        scrollable: The scrollable text widget containing the comment.
        char_count: Label showing current character count.
        add_btn: The Add Comment button to enable or disable.
        event: Optional Tkinter event (ignored; present for ``bind`` compatibility).
    """
    validate_text_char_limit(
        scrollable.text, char_count, _COMMENT_MAX_LEN, required=True
    )
    text = scrollable.text.get("1.0", "end-1c").strip()
    add_btn.config(state=tk.NORMAL if text else tk.DISABLED)


def on_add_comment(
    win: tk.Toplevel,
    cstate,
    scrollable: ScrollableText,
    img_refs: list,
    card_img_refs: list,
    char_count: tk.Label,
    add_btn: tk.Button,
):
    """Handle the Add Comment button click.

    Args:
        win: The top-level comments window.
        cstate: CommentsWindowState (owns selected_photo delegation and UI refs).
        scrollable: The comment text input widget.
        img_refs: Window-lifetime image references.
        card_img_refs: Per-render image references for comment cards.
        char_count: Character-count label to reset after submission.
        add_btn: Add Comment button (passed to on_input_change to re-validate).
    """
    submit_comment(
        win,
        cstate,
        scrollable,
        img_refs,
        card_img_refs,
        lambda: on_input_change(scrollable, char_count, add_btn),
    )
