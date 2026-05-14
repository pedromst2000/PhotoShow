import tkinter as tk
from typing import Optional

from app.presentation.styles.colors import colors
from app.presentation.styles.fonts import quickSandBold, quickSandRegular
from app.presentation.views.helpers.ui.contact_helpers import (
    submit_contact_admin,
    validate_contact_inputs,
)
from app.presentation.widgets.helpers.button import make_button
from app.presentation.widgets.helpers.scrollable_text import ScrollableText
from app.presentation.widgets.window import create_toplevel


class ContactAdminModal:
    """
    Modal dialog for contacting the admin.

    Encapsulates all dialog state and event handling with no nested functions.
    Delegates validation and submission to contact_helpers.
    """

    def __init__(self, parent: tk.Widget) -> None:
        self.parent = parent

        self._win: Optional[tk.Toplevel] = None
        self._title_entry: Optional[tk.Entry] = None
        self._title_count: Optional[tk.Label] = None
        self._scrollable: Optional[ScrollableText] = None
        self._message_count: Optional[tk.Label] = None
        self._submit_btn: Optional[tk.Button] = None

    def open(self) -> None:
        self._win = create_toplevel(
            title="Contact Admin",
            width=420,
            height=650,
            parent=self.parent,
            bg_color=colors["primary-50"],
        )
        self._build_ui()
        self._win.grab_set()

    def _build_ui(self) -> None:
        assert (
            self._win is not None
        )  # for mypy, all UI-building methods should only be called after open()
        main_frame = tk.Frame(self._win, bg=colors["primary-50"])
        main_frame.pack(expand=True, fill="both", padx=20, pady=12)

        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(5, weight=0)  # scrollable (fixed by height)
        main_frame.grid_rowconfigure(7, weight=1)  # flexible spacer

        tk.Label(
            main_frame,
            text="Contact Admin",
            font=quickSandBold(18),
            bg=colors["primary-50"],
            fg=colors["secondary-500"],
        ).grid(row=0, column=0, pady=(0, 10))

        tk.Label(
            main_frame,
            text="Title",
            font=quickSandBold(12),
            bg=colors["primary-50"],
            fg=colors["secondary-500"],
        ).grid(row=1, column=0, pady=(0, 6))

        self._title_entry = tk.Entry(
            main_frame,
            width=44,
            borderwidth=0,
            font=quickSandBold(11),
            bg=colors["secondary-300"],
            fg=colors["secondary-500"],
            highlightthickness=0,
            cursor="xterm",
        )
        self._title_entry.grid(row=2, column=0, pady=(0, 6), sticky="ew")

        self._title_count = tk.Label(
            main_frame,
            text="0/75",
            font=quickSandRegular(10),
            bg=colors["primary-50"],
            fg=colors["secondary-500"],
        )
        self._title_count.grid(row=3, column=0, sticky="e", pady=(0, 8))

        tk.Label(
            main_frame,
            text="Message",
            font=quickSandBold(12),
            bg=colors["primary-50"],
            fg=colors["secondary-500"],
        ).grid(row=4, column=0, pady=(0, 6))

        self._scrollable = ScrollableText(
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
        self._scrollable.grid(row=5, column=0, sticky="nsew")

        self._message_count = tk.Label(
            main_frame,
            text="0/255",
            font=quickSandRegular(10),
            bg=colors["primary-50"],
            fg=colors["secondary-500"],
        )
        self._message_count.grid(row=6, column=0, sticky="e", pady=(6, 8))

        button_frame = tk.Frame(main_frame, bg=colors["primary-50"])
        button_frame.grid(row=8, column=0, pady=(16, 12))

        self._submit_btn = make_button(
            button_frame,
            "Send Message",
            cmd=self.on_submit,
            width=20,
            height=2,
            borderwidth=0,
            font=quickSandBold(12),
            background=colors["accent-300"],
            highlightthickness=0,
            activebackground=colors["accent-100"],
            fg=colors["secondary-500"],
            cursor="hand2",
        )
        self._submit_btn.pack()

        self._title_entry.focus_set()
        self._title_entry.bind("<KeyRelease>", self.on_input_change)
        self._scrollable.text.bind("<KeyRelease>", self.on_input_change)
        self._win.bind("<Return>", lambda e: self.on_submit())

        self.on_input_change()

    def on_input_change(self, event=None) -> None:
        assert (
            self._title_entry is not None
        )  # for mypy, all input-handling methods should only be called after open()
        assert self._scrollable is not None
        assert self._title_count is not None
        assert self._message_count is not None
        validate_contact_inputs(
            self._title_entry,
            self._scrollable,
            self._title_count,
            self._message_count,
        )

    def on_submit(self) -> None:
        assert (
            self._win is not None
        )  # for mypy, all submission-handling methods should only be called after open()
        assert self._title_entry is not None
        assert self._scrollable is not None
        submit_contact_admin(self._win, self._title_entry, self._scrollable.text)
