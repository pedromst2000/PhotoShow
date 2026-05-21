import tkinter as tk
from typing import Callable, Optional

from app.presentation.styles.button import MEDIUM_BTN_STYLE
from app.presentation.styles.colors import colors
from app.presentation.styles.fonts import quickSandBold, quickSandRegular
from app.presentation.widgets.helpers.button import make_button
from app.presentation.widgets.helpers.ui_dialogs import show_error
from app.presentation.widgets.window import create_toplevel


def _validate_and_submit(
    name_var: tk.StringVar,
    dialog: tk.Toplevel,
    on_submit: Optional[Callable[[str], None]],
) -> None:
    """Validate the album name entry and, if valid, close the dialog and invoke *on_submit*."""
    name = name_var.get().strip()
    if not name:
        show_error(dialog, "Validation Error", "Album name cannot be empty.")
        return
    if len(name) > 100:
        show_error(
            dialog, "Validation Error", "Album name is too long (max 100 characters)."
        )
        return
    dialog.destroy()
    if on_submit:
        on_submit(name)


def open_album_dialog(
    parent: tk.Widget,
    mode: str,
    current_name: str = "",
    on_submit: Optional[Callable[[str], None]] = None,
) -> None:
    """Open the shared Add / Edit Album dialog.

    A single lightweight ``Toplevel`` is used for both operations; the
    title, description, and submit-button label are derived from *mode*.

    Args:
        parent: Parent widget used to position the dialog over the caller's
                window (passed to ``grab_set`` for modality).
        mode: ``"add"`` to create a new album or ``"edit"`` to rename the
              currently selected album.
        current_name: Pre-filled album name; used when *mode* is ``"edit"``.
        on_submit: Callable receiving the validated album name string.  Called
                   only on a successful (non-empty) submission.
    """
    _WIN_W = 420
    _WIN_H = 230

    is_edit = mode == "edit"
    title = "Edit Album" if is_edit else "Add Album"
    description = (
        "Enter a new name for the selected album."
        if is_edit
        else "Enter a name for your new album."
    )
    btn_label = "Save Name" if is_edit else "Create Album"

    _BG = colors["primary-50"]
    _FG = colors["secondary-500"]

    dialog: tk.Toplevel = create_toplevel(
        title=f"\U0001f5c2 {title}",
        width=_WIN_W,
        height=_WIN_H,
        icon_path="app/assets/PhotoShowIcon.ico",
        bg_color=_BG,
    )

    # ── Title ─────────────────────────────────────────────────────────────────
    tk.Label(
        dialog,
        text=title,
        font=quickSandBold(18),
        bg=_BG,
        fg=_FG,
    ).place(x=30, y=22)

    # ── Description ───────────────────────────────────────────────────────────
    tk.Label(
        dialog,
        text=description,
        font=quickSandRegular(11),
        bg=_BG,
        fg=_FG,
        wraplength=_WIN_W - 60,
        justify="left",
    ).place(x=30, y=58)

    # ── Name entry ────────────────────────────────────────────────────────────
    tk.Label(
        dialog,
        text="Album name",
        font=quickSandBold(11),
        bg=_BG,
        fg=_FG,
    ).place(x=30, y=100)

    name_var = tk.StringVar(value=current_name)
    entry = tk.Entry(
        dialog,
        textvariable=name_var,
        font=quickSandRegular(12),
        bg="white",
        fg=_FG,
        insertbackground=_FG,
        relief=tk.FLAT,
        highlightthickness=1,
        highlightbackground=colors["secondary-400"],
        highlightcolor=colors["secondary-300"],
        width=32,
    )
    entry.place(x=30, y=125)
    entry.focus_set()

    # ── Submit button ─────────────────────────────────────────────────────────
    submit_btn = make_button(
        dialog,
        btn_label,
        cmd=lambda: _validate_and_submit(name_var, dialog, on_submit),
        **{**MEDIUM_BTN_STYLE, "padx": 18},
    )
    submit_btn.place(x=30, y=165)

    # Allow pressing Enter to submit.
    entry.bind(
        "<Return>",
        lambda _e: _validate_and_submit(name_var, dialog, on_submit),
    )

    dialog.grab_set()
