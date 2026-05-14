import tkinter as tk

from app.presentation.styles.colors import colors
from app.presentation.styles.fonts import quickSandBold, quickSandRegular
from app.presentation.widgets.window import create_toplevel

_WIN_W = 600
_WIN_H = 420


def openCreateAlbum() -> None:
    """
    Open the Create Album window.

    Currently a placeholder — full album creation UI (name input, category
    selection, photo upload) is planned.
    """
    win: tk.Toplevel = create_toplevel(
        title="📷 Create Album",
        width=_WIN_W,
        height=_WIN_H,
        icon_path="app/assets/PhotoShowIcon.ico",
        bg_color=colors["primary-50"],
    )

    # ── Header ────────────────────────────────────────────────────────
    tk.Label(
        win,
        text="Create Album",
        font=quickSandBold(22),
        bg=colors["primary-50"],
        fg=colors["secondary-500"],
    ).place(x=40, y=20)

    tk.Label(
        win,
        text="Give your album a name, choose a category, and add photos.",
        font=quickSandRegular(12),
        bg=colors["primary-50"],
        fg=colors["secondary-500"],
    ).place(x=40, y=60)

    # ── Placeholder notice ────────────────────────────────────────────
    tk.Label(
        win,
        text="🚧",
        font=quickSandBold(48),
        bg=colors["primary-50"],
        fg=colors["secondary-400"],
    ).place(relx=0.5, rely=0.45, anchor=tk.CENTER)

    tk.Label(
        win,
        text="Coming Soon",
        font=quickSandBold(18),
        bg=colors["primary-50"],
        fg=colors["secondary-500"],
    ).place(relx=0.5, rely=0.62, anchor=tk.CENTER)

    tk.Label(
        win,
        text="Album creation will be available in a future update.",
        font=quickSandRegular(12),
        bg=colors["primary-50"],
        fg=colors["secondary-400"],
    ).place(relx=0.5, rely=0.72, anchor=tk.CENTER)

    win.grab_set()
