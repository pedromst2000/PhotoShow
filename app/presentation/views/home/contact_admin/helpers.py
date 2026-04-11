import tkinter as tk
from tkinter import messagebox
from typing import Optional

from app.controllers.profile_controller import ProfileController
from app.presentation.styles.colors import colors


def validate_contact_inputs(
    title_entry: tk.Entry,
    scrollable,
    title_count: tk.Label,
    message_count: tk.Label,
    e: Optional[tk.Event] = None,
) -> None:
    """
    Update character counters and visual feedback for the contact dialog.
    Validates that fields are required and shows visual feedback for length limits.

    Args:
        title_entry: The Entry widget for the title.
        scrollable: The ScrollableText widget for the message.
        title_count: Label to display the title character count.
        message_count: Label to display the message character count.
        e: Optional event parameter for binding.
    """

    title = title_entry.get().strip()
    message = scrollable.text.get("1.0", "end-1c").strip()
    title_len = len(title)
    message_len = len(message)

    # Update counters
    title_count.config(text=f"{title_len}/75")
    message_count.config(text=f"{message_len}/255")

    # Colors
    default_fg = colors["secondary-500"]
    danger_fg = colors.get("danger-500")
    required_fg = colors.get("required-500")

    # Title validation: red if empty (required) or near limit (>=75)
    if title_len == 0:
        # Required field is empty - show red outline
        title_count.config(fg=required_fg)
        title_entry.config(highlightthickness=2, highlightbackground=required_fg)
    elif title_len > 75:
        # Limit reached - show danger color
        title_count.config(fg=danger_fg)
        title_entry.config(highlightthickness=2, highlightbackground=danger_fg)
    else:
        # Valid state - reset to default colors
        title_count.config(fg=default_fg)
        title_entry.config(highlightthickness=0)

    # Message validation: red if empty (required) or near limit (> 255)
    if message_len == 0:
        # Required field is empty - show red outline
        message_count.config(fg=required_fg)
        try:
            scrollable.text.config(
                highlightthickness=2, highlightbackground=required_fg
            )
        except Exception:
            pass
    elif message_len > 255:
        # Limit reached - show danger color
        message_count.config(fg=danger_fg)
        try:
            scrollable.text.config(highlightthickness=2, highlightbackground=danger_fg)
        except Exception:
            pass
    else:
        # Valid state - reset to default colors
        message_count.config(fg=default_fg)
        try:
            scrollable.text.config(highlightthickness=0)
        except Exception:
            pass


def submit_contact_admin(
    dialog: tk.Toplevel,
    title_entry: tk.Entry,
    message_text,
    e: Optional[tk.Event] = None,
) -> None:
    """
    Submit the contact admin form.
    Calls the controller, displays success/error messagebox, and closes dialog on success.

    Args:
        dialog: The modal dialog window.
        title_entry: The Entry widget containing the title.
        message_text: The ScrollableText widget containing the message.
        e: Optional event parameter for key binding.
    """
    success, msg = ProfileController.contact_admin(
        title_entry.get(), message_text.get("1.0", "end-1c")
    )

    if success:
        messagebox.showinfo("Success", msg, parent=dialog)
        dialog.destroy()
    else:
        messagebox.showerror("Error", msg, parent=dialog)
