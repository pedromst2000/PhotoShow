import tkinter as tk
from styles.colors import colors

# Todo - Change the size of the window


def settingsWindow():
    """
    Display the settings window for user preferences and configuration.

    :return: None
    """
    """
    This function is used to display the settings window.
    """

    # open the window
    _settingsWindow_ = tk.Toplevel()

    # centering the window
    settingsWindowWidth = 573  # width of the window
    settingsWindowHeight = 580  # height of the window

    screenWidth = _settingsWindow_.winfo_screenwidth()  # width of the screen

    screenHeight = _settingsWindow_.winfo_screenheight()  # height of the screen

    x = (screenWidth / 2) - (settingsWindowWidth / 2)  # calculate x position

    y = (screenHeight / 2) - (settingsWindowHeight / 2)  # calculate y position

    # setting the window size and position
    # %d = integer
    # %dx%d = width x height
    # %d+%d = x position + y position
    _settingsWindow_.geometry(
        "%dx%d+%d+%d" % (settingsWindowWidth, settingsWindowHeight, x, y)
    )
    _settingsWindow_.title("⚙️ Settings ⚙️")
    _settingsWindow_.iconbitmap("assets/PhotoShowIcon.ico")
    _settingsWindow_.resizable(0, 0)
    _settingsWindow_.config(bg=colors["primary-50"])

    _settingsWindow_.grab_set()
