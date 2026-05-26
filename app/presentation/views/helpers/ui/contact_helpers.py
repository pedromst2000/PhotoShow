import tkinter as tk
from typing import Optional

from app.controllers.contact_controller import ContactController
from app.presentation.widgets.helpers.char_limit import (
    validate_entry_char_limit,
    validate_text_char_limit,
)
from app.presentation.widgets.helpers.ui_dialogs import show_error, show_info


def validate_contact_inputs(
    title_entry: tk.Entry,
    scrollable,
    title_count: tk.Label,
    message_count: tk.Label,
    e: Optional[tk.Event] = None,
) -> None:
    """
    Update character counters and visual feedback for the contact dialog.

    Args:
        title_entry: The Entry widget for the title.
        scrollable: The ScrollableText widget for the message.
        title_count: Label to display the title character count.
        message_count: Label to display the message character count.
        e: Optional event parameter for binding.
    """
    validate_entry_char_limit(title_entry, title_count, 75, required=True)
    validate_text_char_limit(scrollable.text, message_count, 255, required=True)


def submit_contact_admin(
    dialog: tk.Toplevel,
    title_entry: tk.Entry,
    message_text,
    e: Optional[tk.Event] = None,
) -> None:
    """
    Submit the contact admin form.

    Calls the controller, displays success/error messagebox, and closes dialog
    on success.

    Args:
        dialog: The modal dialog window.
        title_entry: The Entry widget containing the title.
        message_text: The ScrollableText widget containing the message.
        e: Optional event parameter for key binding.
    """
    success, msg = ContactController.create(
        title_entry.get(), message_text.get("1.0", "end-1c")
    )

    if success:
        show_info(dialog, "Success", msg)
        dialog.destroy()
    else:
        show_error(dialog, "Error", msg)
