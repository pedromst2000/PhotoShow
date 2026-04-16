import tkinter as tk

from app.presentation.styles.colors import colors
from app.presentation.widgets.window import create_toplevel

# Todo - Change the size of the window


def dashboardWindow():
    """
    Display the main dashboard window of the application.
    """

    # create the window using the reusable helper
    _dashboardWindow_: tk.Toplevel = create_toplevel(
        title="📈 Dashboard 📈",
        width=573,
        height=580,
        icon_path="app/assets/PhotoShowIcon.ico",
        bg_color=colors["primary-50"],
    )

    _dashboardWindow_.grab_set()
