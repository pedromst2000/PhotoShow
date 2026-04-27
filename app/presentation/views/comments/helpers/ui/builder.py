import tkinter as tk

from app.core.state.session import session
from app.presentation.styles.colors import colors
from app.presentation.styles.fonts import quickSandBold, quickSandRegular
from app.presentation.views.helpers.data.state import ExploreState
from app.presentation.views.helpers.ui.modals import open_report_dialog
from app.presentation.widgets.helpers.button import on_enter as button_on_enter
from app.presentation.widgets.helpers.button import on_leave as button_on_leave
from app.presentation.widgets.helpers.char_limit import validate_text_char_limit
from app.presentation.widgets.helpers.images import load_image
from app.presentation.widgets.helpers.scrollable_text import ScrollableText
from app.utils.date_utils import format_timestamp
from app.utils.file_utils import resolve_avatar_path, resolve_image_path

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


def build_photo_canvas(
    parent: tk.Frame,
    state: ExploreState,
    img_refs: list,
):
    """
    Render the selected photo image at the top of the window.

    Args:
        parent: The parent frame to attach the canvas to.
        state: ExploreState containing selected photo info.
        img_refs: List to hold image references for the window lifetime (e.g. photo image, add icon).
    """
    photo = state.selected_photo
    photo_canvas = tk.Canvas(
        parent,
        width=_WIN_W - 32,
        height=180,
        bg=colors["secondary-400"],
        highlightthickness=0,
        bd=0,
    )
    photo_canvas.pack(side=tk.TOP, fill=tk.X, pady=(0, 16))

    img_path = resolve_image_path(photo.get("image")) if photo else None
    img_ref = None
    if img_path:
        img_ref = load_image(
            img_path,
            size=(_WIN_W - 32, 180),
            canvas=photo_canvas,
            x=0,
            y=0,
        )
        img_refs.append(img_ref)

    if img_ref is None:
        photo_canvas.create_text(
            (_WIN_W - 32) // 2,
            90,
            text="No image available",
            font=quickSandBold(14),
            fill=colors["primary-50"],
        )


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
    state: ExploreState,
    list_canvas: tk.Canvas,
    list_frame: tk.Frame,
    img_refs: list,
    card_img_refs: list,
):
    """
    Build the comment text box and 'Add Comment' button.

    Args:
        parent: The parent frame to attach the input area to.
        win: The top-level window containing the input area.
        state: ExploreState containing selected photo info.
        list_canvas: The canvas containing the comment list.
        list_frame: The frame inside the canvas where comment cards are rendered.
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

    # Closures capture all widget references — no class needed
    def _on_input_change(event=None):
        """Validate input and enable/disable the Add Comment button."""
        validate_text_char_limit(
            scrollable.text, char_count, _COMMENT_MAX_LEN, required=True
        )
        # Button disabled only when text is empty; char-limit is backend-validated
        text = scrollable.text.get("1.0", "end-1c").strip()
        add_btn.config(state=tk.NORMAL if text else tk.DISABLED)

    def _on_add():
        """Handle the Add Comment button action."""
        # Late import to avoid circular dependency with interactions.py
        from app.presentation.views.comments.helpers.ui.interactions import (
            submit_comment,
        )

        submit_comment(
            win,
            state,
            scrollable,
            list_canvas,
            list_frame,
            img_refs,
            card_img_refs,
            _on_input_change,
        )

    add_btn.config(command=_on_add)
    scrollable.text.bind("<KeyRelease>", _on_input_change)
    win.bind("<Return>", lambda e: _on_add() if add_btn["state"] == tk.NORMAL else None)


def build_comment_card(
    parent: tk.Frame,
    comment: dict,
    win: tk.Toplevel,
    state: ExploreState,
    list_canvas: tk.Canvas,
    img_refs: list,
    card_img_refs: list,
):
    """
    Build a single comment card.

    Args:
        parent: The parent frame to attach the comment card to.
        comment: The comment data dictionary.
        win: The top-level window containing the comment card (for context in logging).
        state: ExploreState containing selected photo info (for context in logging).
        list_canvas: The canvas containing the comment list (for scrollregion update on delete).
        img_refs: List to hold image references for the window lifetime (e.g. photo image, add icon).
        card_img_refs: List to hold image references for the comment cards (e.g. avatars, action icons); cleared and repopulated on each render.
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

    # -- Header: username + timestamp inline (matching the reference image)
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

    ts = format_timestamp(comment.get("createdAt"))
    tk.Label(
        header,
        text=f"  {ts}",
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

    can_report = not is_admin and author_id != current_uid and author_role != "admin"
    if can_report:
        make_action_button(
            actions,
            "  Report",
            "Report_Icon.png",
            card_img_refs,
            command=lambda cid=comment_id: open_report_dialog(win, comment_id=cid),
        ).pack(side=tk.TOP, pady=(0, 4))

    can_delete = is_admin or author_id == current_uid
    if can_delete:
        make_action_button(
            actions,
            "  Delete",
            "Remove_Icon.png",
            card_img_refs,
            command=lambda cid=comment_id: on_delete(
                cid, win, state, list_canvas, parent, img_refs, card_img_refs
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
