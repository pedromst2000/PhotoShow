import tkinter as tk

from app.presentation.styles.colors import colors
from app.presentation.widgets.window import create_toplevel

# Todo - Change the size of the window


def notificationsWindow():
    """
    This function is used to display the notifications window.
    """

    # create the window using the reusable helper
    _notificationsWindow_: tk.Toplevel = create_toplevel(
        title="🔔 Notifications 🔔",
        width=573,
        height=580,
        icon_path="app/assets/PhotoShowIcon.ico",
        bg_color=colors["primary-50"],
    )

    _notificationsWindow_.grab_set()
