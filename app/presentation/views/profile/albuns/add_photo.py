import tkinter as tk
from typing import Optional

from app.presentation.styles.colors import colors
from app.presentation.styles.fonts import quickSandBold, quickSandRegular
from app.presentation.widgets.window import create_toplevel

_WIN_W = 560
_WIN_H = 480


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
    header = tk.Frame(win, bg=colors["secondary-500"], height=70)
    header.pack(fill="x")
    header.pack_propagate(False)

    tk.Label(
        header,
        text="Add Photo",
        font=quickSandBold(18),
        bg=colors["secondary-500"],
        fg=colors["primary-50"],
        anchor="w",
    ).pack(side="left", padx=20, pady=(14, 4), anchor="n")

    tk.Label(
        header,
        text="Upload a new photo to your album.",
        font=quickSandRegular(10),
        bg=colors["secondary-500"],
        fg=colors["primary-50"],
        anchor="w",
    ).pack(side="left", padx=(0, 10), pady=(22, 4), anchor="n")

    # ── Body (stub — hardcoded placeholder) ───────────────────────────────────
    body = tk.Frame(win, bg=_BG)
    body.pack(fill="both", expand=True)

    tk.Label(
        body,
        text="\U0001f6a7",
        font=quickSandBold(48),
        bg=_BG,
        fg=colors["secondary-400"],
    ).place(relx=0.5, rely=0.30, anchor=tk.CENTER)

    tk.Label(
        body,
        text="Photo Upload Form",
        font=quickSandBold(20),
        bg=_BG,
        fg=colors["secondary-500"],
    ).place(relx=0.5, rely=0.50, anchor=tk.CENTER)

    tk.Label(
        body,
        text="This feature is coming soon.\nSelect a photo file, add a description and choose a category.",
        font=quickSandRegular(12),
        bg=_BG,
        fg=colors["secondary-400"],
        justify="center",
    ).place(relx=0.5, rely=0.63, anchor=tk.CENTER)

    # Hardcoded metadata preview (open tab placeholder).
    meta_frame = tk.Frame(body, bg=colors["secondary-500"], padx=16, pady=10)
    meta_frame.place(relx=0.5, rely=0.84, anchor=tk.CENTER, width=400)

    tk.Label(
        meta_frame,
        text=f"Album ID: {album_id or 'N/A'}   \u2022   Accepted: JPG, PNG   \u2022   Max size: 5 MB",
        font=quickSandRegular(10),
        bg=colors["secondary-500"],
        fg=colors["primary-50"],
    ).pack()

    win.grab_set()
