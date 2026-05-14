import tkinter as tk
from typing import Optional, cast  # for mypy narrow types

from app.controllers.report_controller import ReportController
from app.presentation.styles.colors import colors
from app.presentation.styles.fonts import quickSandBold, quickSandRegular
from app.presentation.views.helpers.ui.modals.helpers.option_menu import (
    create_option_menu,
)
from app.presentation.widgets.helpers.button import make_button
from app.presentation.widgets.helpers.char_limit import validate_text_char_limit
from app.presentation.widgets.helpers.scrollable_text import ScrollableText
from app.presentation.widgets.helpers.ui_dialogs import show_error, show_info
from app.presentation.widgets.window import create_toplevel


class ReportModal:
    """
    Modal dialog for reporting a photo or comment.
    """

    def __init__(
        self,
        parent: tk.Widget,
        photo_id: Optional[int] = None,
        comment_id: Optional[int] = None,
    ) -> None:
        """
        Initialize the report modal.

        Args:
            parent: The parent widget to attach the modal to.
            photo_id: The ID of the photo being reported (if applicable).
            comment_id: The ID of the comment being reported (if applicable).
        """

        self.parent = parent
        self.photo_id = photo_id
        self.comment_id = comment_id
        self.is_photo = photo_id is not None
        self.target_id = photo_id if self.is_photo else comment_id
        self.content_type = "Photo" if self.is_photo else "Comment"

        self._win: Optional[tk.Toplevel] = None
        self._reason_var: Optional[tk.StringVar] = None
        self._submit_btn: Optional[tk.Button] = None
        self._desc_label: Optional[tk.Label] = None
        self._scrollable: Optional[ScrollableText] = None
        self._desc_count: Optional[tk.Label] = None

    def open(self) -> None:
        """Open the report modal dialog."""

        if ReportController.check_already_reported(
            photo_id=self.photo_id, comment_id=self.comment_id
        ):
            show_error(
                self.parent,
                "Already Reported",
                "You have already reported this content.",
            )
            return

        reason_labels = ReportController.get_reason_labels()
        self._dropdown_options = ["Select an option"] + reason_labels

        self._win = create_toplevel(
            title=f"\u26a0 Report {self.content_type}",
            width=420,
            height=520,
            icon_path="app/assets/PhotoShowIcon.ico",
            bg_color=colors["primary-50"],
        )
        self._build_ui()
        self._win.grab_set()

    def _build_ui(self) -> None:
        """Build the UI components for the report modal."""
        # assert self._win is not None
        main_frame = tk.Frame(self._win, bg=colors["primary-50"])
        main_frame.pack(expand=True, fill="both", padx=20, pady=16)
        main_frame.grid_columnconfigure(0, weight=1)

        # Title (centered)
        tk.Label(
            main_frame,
            text=f"Report {self.content_type}",
            font=quickSandBold(18),
            bg=colors["primary-50"],
            fg=colors["secondary-500"],
            anchor="center",
        ).grid(row=0, column=0, sticky="ew", pady=(0, 16))

        # Instruction label with clear message about "Other"
        tk.Label(
            main_frame,
            text=(
                "Select a reason for review and to take the appropriate action.\n"
                "If you select 'Other', please provide details about the issue.\n"
                "Your report will be sent for admin review."
            ),
            font=quickSandRegular(10),
            bg=colors["primary-50"],
            fg=colors["secondary-500"],
            justify=tk.CENTER,
            wraplength=360,
        ).grid(row=1, column=0, sticky="ew", pady=(0, 16))

        # Reason dropdown (centered)
        reason_menu, self._reason_var = create_option_menu(
            main_frame,
            self._dropdown_options,
            width=18,
            font_size=10,
            on_change=lambda _: self.on_reason_change(),
        )
        reason_menu.grid(row=2, column=0, pady=(0, 16))

        # Description frame (shown only when "Other" is selected)
        desc_frame = tk.Frame(main_frame, bg=colors["primary-50"])
        desc_frame.grid(row=3, column=0, sticky="ew", pady=(0, 16))
        desc_frame.grid_columnconfigure(0, weight=1)

        self._desc_label = tk.Label(
            desc_frame,
            text="Message (max 255 chars)",
            font=quickSandBold(12),
            bg=colors["primary-50"],
            fg=colors["secondary-500"],
        )

        self._scrollable = ScrollableText(
            desc_frame,
            width=44,
            height=6,
            font=quickSandRegular(11),
            bg=colors["secondary-300"],
            fg=colors["secondary-500"],
            wrap="word",
            highlightthickness=0,
            borderwidth=0,
        )

        self._desc_count = tk.Label(
            desc_frame,
            text="0/255",
            font=quickSandRegular(10),
            bg=colors["primary-50"],
            fg=colors["secondary-500"],
        )

        # Submit button (centered)
        self._submit_btn = make_button(
            main_frame,
            "Submit",
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
            state=tk.DISABLED,
        )
        self._submit_btn.grid(row=4, column=0, pady=(0, 0))

        self._scrollable.text.bind("<KeyRelease>", self.on_description_change)
        # Cast to narrow type for mypy
        win = cast(tk.Toplevel, self._win)
        submit_btn = cast(tk.Button, self._submit_btn)
        win.bind(
            "<Return>",
            lambda e: (self.on_submit() if submit_btn["state"] == tk.NORMAL else None),
        )

    def on_reason_change(self) -> None:
        """Handle changes in the selected reason."""
        assert self._reason_var is not None
        assert self._submit_btn is not None
        assert self._win is not None
        assert self._desc_label is not None
        assert self._scrollable is not None
        assert self._desc_count is not None
        selected = self._reason_var.get()
        is_valid = selected != "Select an option"
        self._submit_btn.config(state=tk.NORMAL if is_valid else tk.DISABLED)

        if selected == "Other":
            self._win.geometry("420x550")
            self._desc_label.grid(row=0, column=0, sticky="w", pady=(0, 8))
            self._scrollable.grid(row=1, column=0, sticky="ew", pady=(0, 8))
            self._desc_count.grid(row=2, column=0, sticky="e")
            validate_text_char_limit(
                self._scrollable.text, self._desc_count, 255, required=True
            )
        else:
            self._desc_label.grid_remove()
            self._scrollable.grid_remove()
            self._desc_count.grid_remove()
            self._win.geometry("420x520")

    def on_description_change(self, event=None) -> None:
        """Handle changes in the description text."""
        assert self._scrollable is not None
        assert self._desc_count is not None
        validate_text_char_limit(
            self._scrollable.text, self._desc_count, 255, required=True
        )

    def on_submit(self) -> None:
        """Handle the submission of the report."""
        assert self._reason_var is not None
        assert self._scrollable is not None
        assert self._win is not None
        reason = self._reason_var.get().strip()
        if reason == "Select an option" or not reason:
            show_error(self._win, "Error", "Please select a reason.")
            return

        description = None
        if reason == "Other":
            description = self._scrollable.text.get("1.0", "end-1c").strip() or None

        if self.is_photo:
            success, msg = ReportController.report_photo(
                self.target_id, reason, description
            )
        else:
            success, msg = ReportController.report_comment(
                self.target_id, reason, description
            )

        if success:
            show_info(self._win, "Report Submitted", msg)
            self._win.destroy()
        else:
            show_error(self._win, "Error", msg)
