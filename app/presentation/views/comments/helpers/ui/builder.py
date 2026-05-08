import tkinter as tk

from app.core.state.session import session
from app.presentation.styles.colors import colors
from app.presentation.styles.fonts import quickSandBold, quickSandRegular
from app.presentation.views.helpers.ui.modals import open_report_dialog
from app.presentation.widgets.helpers.button import on_enter as button_on_enter
from app.presentation.widgets.helpers.button import on_leave as button_on_leave
from app.presentation.widgets.helpers.images import load_image
from app.presentation.widgets.helpers.scrollable_text import ScrollableText
from app.utils.date_utils import format_timestamp
from app.utils.file_utils import resolve_avatar_path

_WIN_W = 600
_WIN_H = 630
_BG = colors["primary-50"]
_BORDER_CLR = colors["secondary-300"]
_BTN_BG = colors["accent-300"]
_BTN_FG = colors["secondary-500"]
_TEXT_FG = colors["secondary-500"]
_COMMENT_MAX_LEN = 255
_ICON_DIR = "app/assets/images/UI_Icons/"
_AVATAR_SIZE = 28


def build_comment_list(parent: tk.Frame) -> tuple[tk.Canvas, tk.Frame, tk.Frame]:
    """
    Build the scrollable area that will hold comment cards.

    Args:
        parent: The parent frame to attach the comment list to.

    Returns:
        tuple[tk.Canvas, tk.Frame, tk.Frame]: The canvas, the inner frame where comment
        cards should be rendered, and the outer container frame. The caller is responsible
        for packing the container after anchoring the input area to the bottom.
    """
    container = tk.Frame(parent, bg=_BG)
    container.grid_columnconfigure(0, weight=1)
    container.grid_rowconfigure(0, weight=1)

    list_canvas = tk.Canvas(container, bg=_BG, highlightthickness=0, bd=0, height=190)
    scrollbar = tk.Scrollbar(container, orient="vertical", command=list_canvas.yview)
    list_canvas.configure(yscrollcommand=scrollbar.set)

    list_canvas.grid(row=0, column=0, sticky="nsew")
    scrollbar.grid(row=0, column=1, sticky="ns")

    list_frame = tk.Frame(list_canvas, bg=_BG)
    canvas_win = list_canvas.create_window((0, 0), window=list_frame, anchor="nw")

    list_frame.bind(
        "<Configure>",
        lambda e: list_canvas.configure(scrollregion=list_canvas.bbox("all")),
    )
    list_canvas.bind(
        "<Configure>",
        lambda e: list_canvas.itemconfig(canvas_win, width=e.width),
    )
    # Mouse wheel scrolling
    list_canvas.bind(
        "<MouseWheel>",
        lambda e: list_canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"),
    )

    return list_canvas, list_frame, container


def build_input_area(
    parent: tk.Frame,
    win: tk.Toplevel,
    cstate,
    img_refs: list,
    card_img_refs: list,
):
    """
    Build the comment text box and 'Add Comment' button.

    Args:
        parent: The parent frame to attach the input area to.
        win: The top-level window containing the input area.
        cstate: CommentsWindowState (owns list_canvas, list_frame and photo delegation).
        img_refs: List to hold image references for the window lifetime (e.g. photo image, add icon).
        card_img_refs: List to hold image references for comment cards.
    """
    input_frame = tk.Frame(parent, bg=_BG)
    input_frame.pack(side=tk.TOP, fill=tk.X)
    input_frame.grid_columnconfigure(0, weight=1)

    tk.Label(
        input_frame,
        text=f"Write a comment  (max {_COMMENT_MAX_LEN} characters)",
        font=quickSandBold(11),
        bg=_BG,
        fg=_TEXT_FG,
    ).grid(row=0, column=0, sticky="w", pady=(0, 6))

    scrollable = ScrollableText(
        input_frame,
        width=48,
        height=3,
        font=quickSandRegular(11),
        bg=_BORDER_CLR,
        fg=_TEXT_FG,
        wrap="word",
        highlightthickness=0,
        borderwidth=0,
    )
    scrollable.grid(row=1, column=0, sticky="ew", pady=(0, 4))

    char_count = tk.Label(
        input_frame,
        text=f"0/{_COMMENT_MAX_LEN}",
        font=quickSandRegular(9),
        bg=_BG,
        fg=_TEXT_FG,
    )
    char_count.grid(row=2, column=0, sticky="e", pady=(0, 10))

    # Load the add icon once — kept alive via img_refs
    add_icon_ref = load_image(_ICON_DIR + "Add_Icon.png", size=(20, 20))
    img_refs.append(add_icon_ref)

    btn_frame = tk.Frame(input_frame, bg=_BG)
    btn_frame.grid(row=3, column=0, pady=(0, 10))

    add_btn = tk.Button(
        btn_frame,
        text="  Add Comment",
        image=add_icon_ref,
        compound=tk.LEFT,
        font=quickSandBold(12),
        bg=_BTN_BG,
        fg=_BTN_FG,
        activebackground=colors["accent-100"],
        borderwidth=0,
        highlightthickness=0,
        cursor="hand2",
        padx=16,
        pady=8,
        state=tk.DISABLED,
    )
    add_btn.pack()
    add_btn.bind("<Enter>", lambda e: button_on_enter(e, add_btn))
    add_btn.bind("<Leave>", lambda e: button_on_leave(e, add_btn))

    # Late import to avoid circular dependency: interactions.py imports constants from this module.
    from app.presentation.views.comments.helpers.ui.interactions import (
        on_add_comment,
        on_input_change,
    )

    def _on_input_change(event=None):
        """Validate comment input and toggle Add button."""
        on_input_change(scrollable, char_count, add_btn, event)

    def _on_add():
        """Handle Add Comment button click."""
        on_add_comment(
            win, cstate, scrollable, img_refs, card_img_refs, char_count, add_btn
        )

    add_btn.config(command=_on_add)
    scrollable.text.bind("<KeyRelease>", _on_input_change)
    win.bind(
        "<Return>",
        lambda e: _on_add() if add_btn["state"] == tk.NORMAL else None,
    )


def build_comment_card(
    parent: tk.Frame,
    comment: dict,
    win: tk.Toplevel,
    cstate,
    img_refs: list,
    card_img_refs: list,
):
    """
    Build a single comment card.

    Args:
        parent: The parent frame to attach the comment card to.
        comment: The comment data dictionary.
        win: The top-level window containing the comment card.
        cstate: CommentsWindowState (for photo delegation and delete callback).
        img_refs: List to hold image references for the window lifetime.
        card_img_refs: Per-render image refs; cleared and repopulated on each render.
    """
    # Late imports to avoid circular dependency with interactions.py
    from app.presentation.views.comments.helpers.ui.interactions import (
        make_action_button,
        on_delete,
    )

    # Outer border frame (the background IS the border colour)
    border = tk.Frame(parent, bg=_BORDER_CLR)
    border.pack(fill="x", padx=4, pady=(0, 8))

    # Inner card (window background colour — contrast via the surrounding border)
    card = tk.Frame(border, bg=_BG)
    card.pack(fill="both", expand=True, padx=2, pady=2)
    card.grid_columnconfigure(1, weight=1)

    # -- Avatar
    avatar_canvas = tk.Canvas(
        card,
        width=_AVATAR_SIZE,
        height=_AVATAR_SIZE,
        bg=_BG,
        highlightthickness=0,
        bd=0,
    )
    avatar_canvas.grid(row=0, column=0, rowspan=2, padx=(10, 6), pady=10, sticky="n")

    avatar_path = resolve_avatar_path(comment.get("author_avatar"))
    av_photo = load_image(
        avatar_path,
        size=(_AVATAR_SIZE, _AVATAR_SIZE),
        canvas=avatar_canvas,
        x=0,
        y=0,
    )
    card_img_refs.append(av_photo)

    # -- Header (username and published date)
    header = tk.Frame(card, bg=_BG)
    header.grid(row=0, column=1, sticky="ew", padx=(0, 8), pady=(10, 2))

    tk.Label(
        header,
        text=comment.get("author_username", "Unknown"),
        font=quickSandBold(11),
        bg=_BG,
        fg=_TEXT_FG,
        anchor="w",
    ).pack(side=tk.LEFT)

    published_date = format_timestamp(comment.get("publishedDate"))
    tk.Label(
        header,
        text=f"  {published_date}",
        font=quickSandRegular(9),
        bg=_BG,
        fg=_TEXT_FG,
        anchor="w",
    ).pack(side=tk.LEFT, padx=(4, 0))

    # -- Action buttons column
    comment_id = comment.get("id")
    author_id = comment.get("authorId")
    author_role = comment.get("author_role", "regular")
    is_admin = session.is_admin
    current_uid = session.user_id

    actions = tk.Frame(card, bg=_BG)
    actions.grid(row=0, column=2, rowspan=2, padx=(4, 10), pady=10, sticky="ne")

    # Only allow reporting if user is not admin and not the author of the comment
    can_report = not is_admin and author_id != current_uid and author_role != "admin"
    if can_report:
        make_action_button(
            actions,
            "  Report",
            "Report_Icon.png",
            card_img_refs,
            command=lambda cid=comment_id: open_report_dialog(win, comment_id=cid),
        ).pack(side=tk.TOP, pady=(0, 4))

    # Only allow delete if user is admin or the author of the comment
    can_delete = is_admin or author_id == current_uid
    if can_delete:
        make_action_button(
            actions,
            "  Delete",
            "Remove_Icon.png",
            card_img_refs,
            command=lambda cid=comment_id: on_delete(
                cid, win, cstate, img_refs, card_img_refs
            ),
        ).pack(side=tk.TOP)

    # -- Comment body text
    tk.Label(
        card,
        text=comment.get("comment", ""),
        font=quickSandRegular(11),
        bg=_BG,
        fg=_TEXT_FG,
        anchor="w",
        justify="left",
        wraplength=_WIN_W - 150,
    ).grid(row=1, column=1, sticky="ew", padx=(0, 8), pady=(0, 10))


def build_comments_pagination(parent: tk.Frame, cstate) -> None:
    """Build the pagination row for the comments list.

    Delegates to the global ``build_listbox_pagination`` with comments-specific
    colours and a page-changed callback that re-renders the current page of
    comment cards.

    Args:
        parent: Frame into which the pagination row is packed (directly below
                the comment list container).
        cstate: CommentsWindowState whose pagination was initialised by
                ``initialize_comments_pagination``.
    """
    from app.presentation.views.helpers.ui.builder import build_listbox_pagination

    build_listbox_pagination(
        parent,
        cstate,
        on_page_changed=lambda: _on_comments_page_changed(cstate),
        bg=_BG,
        btn_bg=_BTN_BG,
        btn_fg=_BTN_FG,
        text_fg=_TEXT_FG,
    )


def _on_comments_page_changed(cstate) -> None:
    """Re-render the current page of comments after navigation.

    Called by the PaginationUIController's on_page_changed hook. At the point
    this runs, ``cstate.photos`` has already been updated by
    ``_make_page_changed_handler`` in the global listbox_pagination builder.

    Args:
        cstate: CommentsWindowState with updated ``photos`` for the current page.
    """
    from app.presentation.views.comments.helpers.data.comments import render_comments

    render_comments(
        cstate.list_frame,
        cstate.photos,
        cstate.win,
        cstate,
        cstate.img_refs,
        cstate.card_img_refs,
    )
