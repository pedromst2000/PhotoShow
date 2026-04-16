import tkinter as tk
from tkinter import messagebox


def show_limited_access(
    parent: tk.Tk, feature_message: str = "", title: str = "Limited Access"
):
    """
    Show a standard 'Limited Access' info dialog for unsigned users.

    Args:
        parent (tk.Tk): The parent window for the messagebox.
        feature_message (str, optional): A custom message about the limited feature. Defaults to "".
        title (str, optional): The title of the messagebox. Defaults to "Limited Access".
    """

    base = "Your account is pending approval by the administrator.\n\n"

    feature_text = (feature_message or "").strip()
    trailing = "until your account is approved."

    if feature_text:
        if feature_text.endswith(trailing):
            message = f"{base}{feature_text}"
        else:
            message = f"{base}{feature_text} {trailing}"
    else:
        message = f"{base}Interactions are disabled {trailing}"

    messagebox.showinfo(title, message, parent=parent)


def show_info(parent: tk.Tk, title: str, message: str):
    """
    Show an info dialog attached to `parent`.

    Args:
        parent (tk.Tk): The parent window for the messagebox.
        title (str): The title of the messagebox.
        message (str): The message to display in the messagebox.
    """

    messagebox.showinfo(title, message, parent=parent)


def show_error(parent: tk.Tk, title: str, message: str):
    """
    Show an error dialog attached to `parent`.

    Args:
        parent (tk.Tk): The parent window for the messagebox.
        title (str): The title of the messagebox.
        message (str): The error message to display in the messagebox.
    """

    messagebox.showerror(title, message, parent=parent)


def show_onboarding(parent: tk.Tk):
    """
    Show a standard onboarding info dialog for new users after successful login.

    Args:
        parent (tk.Tk): The parent window for the messagebox.
    """

    title = "Welcome to PhotoShow!"
    message = (
        "Where every pixel tells a tale, you can now enjoy your time with us.\n\n"
        "Let's take a look at our features:\n\n"
        "  - \U0001f310 Explore: Explore the world of photos with other users\n\n"
        "  - \U0001f464 Profile: Edit your profile and view your photos and albums\n\n"
        "  - \U0001f514 Notifications: Stay updated with news through notifications\n\n"
        "  - \U0001f4c8 Dashboard: Check your dashboard for statistics"
    )
    messagebox.showinfo(title, message, parent=parent)


def show_confirmation(parent: tk.Tk, title: str, message: str) -> bool:
    """
    Show a confirmation dialog with Yes/No buttons.

    Reusable confirmation dialog for all yes/no actions across the project.

    Args:
        parent (tk.Tk): The parent window for the messagebox.
        title (str): The title of the messagebox.
        message (str): The confirmation message to display.

    Returns:
        bool: True if user clicked Yes, False if clicked No.
    """
    return messagebox.askyesno(title, message, parent=parent)
