import tkinter as tk
from typing import Optional

from app.presentation.styles.colors import colors
from app.presentation.styles.fonts import quickSandBold, quickSandRegular
from app.presentation.views.home.contact_admin.helpers import (
    submit_contact_admin,
    validate_contact_inputs,
)
from app.presentation.widgets.helpers.scrollable_text import ScrollableText
from app.presentation.widgets.window import create_toplevel


def open_contact_admin(parent: tk.Tk, event: Optional[tk.Event] = None):
    """Open a modal dialog allowing the user to contact the admin.

    The dialog uses a simple packed layout with consistent spacing and a
    vertical scrollbar attached to the message text area.

    Args:
        parent: Parent window for modality/centering.
        event: Optional triggering event.
    """

    dialog_width, dialog_height = 420, 650
    dialog: tk.Toplevel = create_toplevel(
        title="Contact Admin",
        width=dialog_width,
        height=dialog_height,
        parent=parent,
        bg_color=colors["primary-50"],
    )

    # Main frame with padding to hold all content and ensure consistent spacing from edges
    main_frame = tk.Frame(dialog, bg=colors["primary-50"])
    main_frame.pack(expand=True, fill="both", padx=20, pady=12)

    # Configure grid to allow the message area to expand while keeping other elements sized to content
    main_frame.grid_columnconfigure(0, weight=1)
    main_frame.grid_rowconfigure(5, weight=0)  # scrollable (fixed by height)
    main_frame.grid_rowconfigure(7, weight=1)  # flexible spacer

    header = tk.Label(
        main_frame,
        text="Contact Admin",
        font=quickSandBold(18),
        bg=colors["primary-50"],
        fg=colors["secondary-500"],
    )
    header.grid(row=0, column=0, pady=(0, 10))

    title_label = tk.Label(
        main_frame,
        text="Title",
        font=quickSandBold(12),
        bg=colors["primary-50"],
        fg=colors["secondary-500"],
    )
    title_label.grid(row=1, column=0, pady=(0, 6))

    title_entry: tk.Entry = tk.Entry(
        main_frame,
        width=44,
        borderwidth=0,
        font=quickSandBold(11),
        bg=colors["secondary-300"],
        fg=colors["secondary-500"],
        highlightthickness=0,
        cursor="xterm",
    )
    title_entry.grid(row=2, column=0, pady=(0, 6), sticky="ew")

    title_count = tk.Label(
        main_frame,
        text="0/75",
        font=quickSandRegular(10),
        bg=colors["primary-50"],
        fg=colors["secondary-500"],
    )
    title_count.grid(row=3, column=0, sticky="e", pady=(0, 8))

    message_label = tk.Label(
        main_frame,
        text="Message",
        font=quickSandBold(12),
        bg=colors["primary-50"],
        fg=colors["secondary-500"],
    )
    message_label.grid(row=4, column=0, pady=(0, 6))

    # Message area with ScrollableText helper
    scrollable = ScrollableText(
        main_frame,
        width=44,
        height=12,
        font=quickSandRegular(11),
        bg=colors["secondary-300"],
        fg=colors["secondary-500"],
        wrap="word",
        highlightthickness=0,
        borderwidth=0,
    )
    scrollable.grid(row=5, column=0, sticky="nsew")

    # Message character counter
    message_count = tk.Label(
        main_frame,
        text="0/255",
        font=quickSandRegular(10),
        bg=colors["primary-50"],
        fg=colors["secondary-500"],
    )
    message_count.grid(row=6, column=0, sticky="e", pady=(6, 8))

    # Send button placed near the bottom, centered with consistent spacing
    button_frame = tk.Frame(main_frame, bg=colors["primary-50"])
    # Place button one row lower so it sits closer to the bottom
    button_frame.grid(row=8, column=0, pady=(16, 12))

    send_btn: tk.Button = tk.Button(
        button_frame,
        width=20,
        height=2,
        text="Send Message",
        borderwidth=0,
        font=quickSandBold(12),
        background=colors["accent-300"],
        highlightthickness=0,
        activebackground=colors["accent-100"],
        fg=colors["secondary-500"],
        cursor="hand2",
        command=lambda: submit_contact_admin(dialog, title_entry, scrollable.text),
    )
    send_btn.pack()

    # Focus the title entry for convenience

    title_entry.focus_set()

    # Bind events for real-time validation and submission, and perform an initial validation to set the correct state/colors.
    send_btn.config(state="normal")
    title_entry.bind(
        "<KeyRelease>",
        lambda e: validate_contact_inputs(
            title_entry, scrollable, title_count, message_count, e
        ),
    )
    scrollable.text.bind(
        "<KeyRelease>",
        lambda e: validate_contact_inputs(
            title_entry, scrollable, title_count, message_count, e
        ),
    )
    dialog.bind(
        "<Return>",
        lambda e: submit_contact_admin(dialog, title_entry, scrollable.text, e),
    )
    validate_contact_inputs(title_entry, scrollable, title_count, message_count)
    dialog.grab_set()
