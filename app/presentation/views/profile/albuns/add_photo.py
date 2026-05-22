import tkinter as tk
from typing import Optional

from app.controllers.category_controller import CategoryController
from app.presentation.styles.button import COMPACT_BTN_STYLE
from app.presentation.styles.colors import colors
from app.presentation.styles.fonts import quickSandBold, quickSandRegular
from app.presentation.views.helpers.ui.modals.helpers.option_menu import (
    create_option_menu,
)
from app.presentation.views.profile.helpers.ui.photo_upload import (
    handle_photo_submission,
    handle_photo_upload,
)
from app.presentation.widgets.helpers.button import make_button
from app.presentation.widgets.helpers.char_limit import validate_text_char_limit
from app.presentation.widgets.helpers.scrollable_text import ScrollableText
from app.presentation.widgets.window import create_toplevel

_WIN_W = 900
_WIN_H = 720
_MAX_DESCRIPTION = 255


def _on_upload_click(
    win: tk.Toplevel,
    photo_state: dict,
    canvas_preview: tk.Canvas,
    btn_submit: tk.Button,
) -> None:
    """
    Handle the Upload Photo button click: open file dialog, validate, preview, and enable submit.

    Args:
        win (tk.Toplevel): The add photo window.
        photo_state (dict): Photo state container to store file path.
        canvas_preview (tk.Canvas): Canvas widget for preview rendering.
        btn_submit (tk.Button): Submit button to enable after upload.
    """
    if canvas_preview and btn_submit:
        handle_photo_upload(win, photo_state, canvas_preview, btn_submit)


def _on_submit_click(
    win: tk.Toplevel,
    album_id: Optional[int],
    photo_state: dict,
    scrollable_desc: ScrollableText,
    cat_var: tk.StringVar,
    on_created: Optional[callable],  # type: ignore[valid-type]
) -> None:
    """
    Handle the Create Photo button click: validate form, upload photo, show feedback, and trigger callback.

    Args:
        win (tk.Toplevel): The add photo window.
        album_id (Optional[int]): ID of the album for the photo.
        photo_state (dict): Photo state container.
        scrollable_desc (ScrollableText): Description textarea.
        cat_var (tk.StringVar): Category dropdown variable.
        on_created (Optional[callable]): Optional callback after successful creation.
    """
    handle_photo_submission(
        win, album_id, photo_state, scrollable_desc, cat_var, on_created
    )


def open_add_photo_window(
    parent: tk.Widget,
    album_id: Optional[int] = None,
    on_created: Optional[callable] = None,  # type: ignore[valid-type]
) -> None:
    """Open the Add Photo window for uploading a photo to an album.

    Args:
        parent: Parent widget used for window positioning and modality.
        album_id: ID of the album the photo will be added to.
        on_created: Optional callback invoked after successful photo creation.
    """

    _BG = colors["primary-50"]

    win = create_toplevel(
        title="\U0001f4f7 Add Photo",
        width=_WIN_W,
        height=_WIN_H,
        icon_path="app/assets/PhotoShowIcon.ico",
        bg_color=_BG,
    )

    # ── Header ────────────────────────────────────────────────────────────────
    header = tk.Frame(win, bg=_BG)
    header.pack(fill="x", padx=20, pady=(16, 4))

    tk.Label(
        header,
        text="Add Photo",
        font=quickSandBold(22),
        bg=_BG,
        fg=colors["secondary-500"],
    ).pack(anchor="w")

    tk.Label(
        header,
        text="Upload a new photo to your album with description and category.",
        font=quickSandRegular(11),
        bg=_BG,
        fg=colors["secondary-500"],
    ).pack(anchor="w")

    # ── Main content (two columns) ────────────────────────────────────────────
    main_frame = tk.Frame(win, bg=_BG)
    main_frame.pack(fill="both", expand=True, padx=20, pady=(12, 20))

    # ── Left: Form inputs ─────────────────────────────────────────────────────
    left_frame = tk.Frame(main_frame, bg=_BG)
    left_frame.pack(side="left", fill="both", expand=False, padx=(0, 20))

    photo_state: dict = {"path": None}

    # Photo Upload
    tk.Label(
        left_frame,
        text="Photo File",
        font=quickSandBold(12),
        bg=_BG,
        fg=colors["secondary-500"],
    ).pack(anchor="w", pady=(0, 6))

    # Placeholder for canvas and submit button (declared later)
    canvas_preview = None
    btn_submit = None

    btn_upload = make_button(
        left_frame,
        "Upload Photo",
        width=16,
        height=2,
        compound="center",
        command=lambda: _on_upload_click(win, photo_state, canvas_preview, btn_submit),
        **COMPACT_BTN_STYLE,
    )
    btn_upload.pack(pady=(0, 16))

    # Description
    tk.Label(
        left_frame,
        text=f"Description (max {_MAX_DESCRIPTION} chars)",
        font=quickSandBold(12),
        bg=_BG,
        fg=colors["secondary-500"],
    ).pack(anchor="w", pady=(0, 6))

    scrollable_desc = ScrollableText(
        left_frame,
        width=40,
        height=6,
        font=quickSandRegular(11),
        bg=colors["secondary-300"],
        fg=colors["secondary-500"],
        wrap="word",
        highlightthickness=0,
        borderwidth=0,
    )
    scrollable_desc.pack(pady=(0, 4))

    desc_count = tk.Label(
        left_frame,
        text="0/255",
        font=quickSandRegular(10),
        bg=_BG,
        fg=colors["secondary-500"],
    )
    desc_count.pack(anchor="e", pady=(0, 16))

    scrollable_desc.text.bind(
        "<KeyRelease>",
        lambda e: validate_text_char_limit(
            scrollable_desc.text, desc_count, _MAX_DESCRIPTION
        ),
    )

    # Category
    tk.Label(
        left_frame,
        text="Category",
        font=quickSandBold(12),
        bg=_BG,
        fg=colors["secondary-500"],
    ).pack(anchor="w", pady=(0, 6))

    categories = CategoryController.get_all_categories()
    cat_options = [cat.get("category", "") for cat in categories]
    cat_menu, cat_var = create_option_menu(
        left_frame,
        cat_options,
        width=18,
        font_size=11,
    )
    cat_menu.pack(pady=(0, 16))

    # Submit button
    btn_submit = make_button(
        left_frame,
        "Create Photo",
        width=16,
        height=2,
        compound="center",
        state="disabled",
        command=lambda: _on_submit_click(
            win, album_id, photo_state, scrollable_desc, cat_var, on_created
        ),
        **{**COMPACT_BTN_STYLE, "cursor": "arrow"},
    )
    btn_submit.pack()

    photo_state["submit_btn"] = btn_submit

    # ── Right: Preview ────────────────────────────────────────────────────────
    right_frame = tk.Frame(main_frame, bg=colors["secondary-400"])
    right_frame.pack(side="right", fill="both", expand=True)

    preview_header = tk.Frame(right_frame, bg=colors["secondary-400"])
    preview_header.pack(fill="x", padx=15, pady=(10, 8))

    tk.Label(
        preview_header,
        text="Photo Preview",
        font=quickSandBold(14),
        bg=colors["secondary-400"],
        fg=colors["secondary-500"],
    ).pack(anchor="w")

    tk.Label(
        preview_header,
        text="Upload a photo to preview it here",
        font=quickSandRegular(11),
        bg=colors["secondary-400"],
        fg=colors["primary-50"],
    ).pack(anchor="w")

    canvas_preview = tk.Canvas(
        right_frame,
        width=350,
        height=350,
        bg=colors["secondary-500"],
        highlightthickness=0,
        bd=0,
    )
    canvas_preview.pack(padx=10, pady=(0, 12))

    canvas_preview.create_text(
        175,
        175,
        text="\U0001f5bc\nNo photo selected",
        font=quickSandRegular(14),
        fill=colors["primary-50"],
    )

    win.grab_set()
