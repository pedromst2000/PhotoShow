import tkinter as tk

from app.presentation.styles.colors import colors
from app.presentation.styles.fonts import quickSandBold, quickSandRegular
from app.presentation.views.helpers.ui.builder import build_empty_state
from app.presentation.widgets.window import create_toplevel


def reportsWindow() -> None:
    """Display the admin reports window. Currently shows an empty state."""
    win: tk.Toplevel = create_toplevel(
        title="\U0001f6a8 Profile - Reports",
        width=900,
        height=540,
        icon_path="app/assets/PhotoShowIcon.ico",
        bg_color=colors["primary-50"],
    )

    tk.Label(
        win,
        text="Reports",
        font=quickSandBold(22),
        bg=colors["primary-50"],
        fg=colors["secondary-500"],
    ).place(x=40, y=20)

    # TODO: Not yet implemented — the reports list is a placeholder.
    #       Replace this empty state with real report data fetched from the DB,
    #       showing submitted user reports (or a dynamic empty state if there are none).
    tk.Label(
        win,
        text="Review and manage reported content submitted by users.",
        font=quickSandRegular(12),
        bg=colors["primary-50"],
        fg=colors["secondary-500"],
    ).place(x=40, y=60)

    build_empty_state(
        win,
        icon="\U0001f6a8",
        title="No reports to review",
        subtitle="When users submit reports about inappropriate content they will appear here.",
    )

    win.grab_set()
