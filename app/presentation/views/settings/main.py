import tkinter as tk

from app.presentation.styles.colors import colors
from app.presentation.widgets.window import create_toplevel

# Todo - Change the size of the window


def settingsWindow():
    """
    Display the settings window for user preferences and configuration.

    :return: None
    """
    # create the window using the reusable helper
    _settingsWindow_: tk.Toplevel = create_toplevel(
        title="⚙️ Settings ⚙️",
        width=573,
        height=580,
        icon_path="app/assets/PhotoShowIcon.ico",
        bg_color=colors["primary-50"],
    )

    _settingsWindow_.grab_set()
