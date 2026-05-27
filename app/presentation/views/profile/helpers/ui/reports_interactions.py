import tkinter as tk

from app.controllers.comment_controller import CommentController
from app.controllers.photo_controller import PhotoController
from app.controllers.report_controller import ReportController
from app.presentation.styles.colors import colors
from app.presentation.styles.fonts import quickSandBold
from app.presentation.views.helpers.ui.builder import toggle_empty_content_state
from app.presentation.views.profile.helpers.data.reports_data import (
    refresh_reports_list,
)
from app.presentation.views.profile.helpers.data.reports_state import ReportsState
from app.presentation.widgets.helpers.images import load_image
from app.presentation.widgets.helpers.ui_dialogs import (
    show_confirmation,
    show_error,
    show_info,
)
from app.utils.file_utils import resolve_avatar_path, resolve_image_path

# ── Internal helpers ──────────────────────────────────────────────────────────


def _set_remove_btn_state(state: ReportsState, *, enabled: bool) -> None:
    """Enable or disable the Remove Report button.

    Args:
        state: Reports state carrying the button reference.
        enabled: True to enable, False to disable.
    """
    btn = state.remove_btn
    if btn is not None:
        btn.config(state=tk.NORMAL if enabled else tk.DISABLED)


def _reset_detail_panel(state: ReportsState) -> None:
    """Hide the detail frame and show the selection placeholder.

    Args:
        state: Reports state carrying the panel widget references.
    """
    detail = state._detail_frame
    placeholder = state._placeholder_frame
    if detail is not None:
        detail.pack_forget()
    if placeholder is not None:
        placeholder.pack(fill="both", expand=True)


def _show_type_and_reason(state: ReportsState, report: dict, report_type: str) -> None:
    """
    Update the Type and Reason labels for the selected report.

    Args:
    state: Reports state carrying the label references.
    report: The selected report dict containing 'type' and 'reason' keys.
    report_type: The type of the report, either "photo" or "comment".
    """
    type_label = "Photo Report" if report_type == "photo" else "Comment Report"
    if state._type_label is not None:
        state._type_label.config(text=type_label)
    if state._reason_label is not None:
        state._reason_label.config(text=report.get("reason", "—"))


def _update_delete_btn(state: ReportsState, report_type: str) -> None:
    """
    Set the delete button label to match the report type.

    Args:
        state: Reports state carrying the button reference.
        report_type: The type of the report, either "photo" or "comment".
    """
    if state._delete_btn is None:
        return
    text = "  Delete Photo" if report_type == "photo" else "  Delete Comment"
    state._delete_btn.config(text=text)


def _show_content(state: ReportsState, report: dict, report_type: str) -> None:
    """Show the photo canvas or comment text widget based on the report type."""
    content_text = state._content_text
    canvas = state._content_photo_canvas

    if report_type == "photo":
        if content_text is not None:
            content_text.pack_forget()
        if canvas is not None:
            canvas.pack(fill="x")
            canvas.delete("all")
            canvas_w = int(canvas.cget("width"))
            canvas_h = int(canvas.cget("height"))
            resolved = resolve_image_path(report.get("photo_path") or "")
            if resolved:
                img = load_image(
                    resolved, size=(canvas_w, canvas_h), canvas=canvas, x=0, y=0
                )
                canvas.image = img  # type: ignore[attr-defined]
            else:
                canvas.create_text(
                    canvas_w // 2,
                    canvas_h // 2,
                    text="No image available",
                    font=quickSandBold(12),
                    fill=colors["primary-50"],
                )
    else:
        if canvas is not None:
            canvas.pack_forget()
        if content_text is not None:
            content_text.pack(fill="x")
            content_text.config(state=tk.NORMAL)
            content_text.delete("1.0", tk.END)
            content_text.insert("1.0", report.get("content", ""))
            content_text.config(state=tk.DISABLED)


def _show_creator(state: ReportsState, report: dict) -> None:
    """Load the creator's avatar and display their username.

    Args:
        state: Reports state carrying the avatar canvas and username label references.
        report: The selected report dict containing 'content_creator' and 'creator_avatar' keys.
    """
    if state._creator_username_label is not None:
        state._creator_username_label.config(
            text=report.get("content_creator", "Unknown")
        )
    if state._creator_avatar_canvas is not None:
        avatar_path = resolve_avatar_path(report.get("creator_avatar"))
        state._creator_avatar_canvas.delete("all")
        img = load_image(
            avatar_path, size=(28, 28), canvas=state._creator_avatar_canvas, x=0, y=0
        )
        state._creator_avatar_canvas.image = img  # type: ignore[attr-defined]


def _show_description(state: ReportsState, report: dict) -> None:
    """Show the reporter note only when the reason is 'Other' and a description exists.

    Args:
        state: Reports state carrying the description frame and label references.
        report: The selected report dict containing 'reason' and 'description' keys.
    """
    desc_frame = state._description_frame
    if desc_frame is None:
        return
    description = report.get("description") or ""
    if report.get("reason") == "Other" and description.strip():
        if state._description_label is not None:
            state._description_label.config(text=description)
        desc_frame.pack(fill="x", padx=12, pady=(0, 8))
    else:
        desc_frame.pack_forget()


def _update_detail_panel(state: ReportsState) -> None:
    """Populate and reveal the detail panel for the selected report.

    Args:
        state: Reports state carrying the detail panel references.
    """
    report = state.selected_report
    if report is None:
        return

    report_type = report.get("type", "photo")

    _show_type_and_reason(state, report, report_type)
    _update_delete_btn(state, report_type)

    _show_content(state, report, report_type)
    _show_creator(state, report)
    _show_description(state, report)

    if state._placeholder_frame is not None:
        state._placeholder_frame.pack_forget()
    if state._detail_frame is not None:
        state._detail_frame.pack(fill="both", expand=True)


# ── Report selection ──────────────────────────────────────────────────────────


def on_report_select(idx: int, state: ReportsState) -> None:
    """Handle selection of a report in the left listbox.

    Updates the detail panel on the right to show the selected report's
    type, reason, content, and creator.

    Args:
        idx: Local page index of the selected report.
        state: Reports view state.
    """
    reports_on_page = state.photos
    if not (0 <= idx < len(reports_on_page)):
        return

    state.selected_index = idx
    state.selected_report = reports_on_page[idx]

    _set_remove_btn_state(state, enabled=True)
    _update_detail_panel(state)


# ── Remove report ─────────────────────────────────────────────────────────────


def on_remove_report(state: ReportsState, body: tk.Widget) -> None:
    """Remove the selected report record, leaving the reported content intact.

    Prompts the admin for confirmation before permanently deleting the
    report from the database and refreshing the listbox.

    Args:
        state: Reports view state.
        body: Parent widget used for confirmation / info dialogs.
    """
    if state.selected_report is None:
        show_info(body, "Remove Report", "Please select a report first.")
        return

    report_id = state.selected_report.get("id")
    reason = state.selected_report.get("reason", "this report")

    confirmed = show_confirmation(
        body,
        "Remove Report",
        f'Remove the report "{reason}"?\n\nThe reported content will NOT be deleted.',
    )
    if not confirmed:
        return

    success, msg = ReportController.resolve_report(report_id)
    if success:
        state.selected_report = None
        state.selected_index = None
        _set_remove_btn_state(state, enabled=False)
        _reset_detail_panel(state)
        refresh_reports_list(state)
        toggle_empty_content_state(state, has_items=bool(state.filtered_reports))
        show_info(body, "Remove Report", "Report removed successfully.")
    else:
        show_error(body, "Remove Report", msg)


# ── Delete content ────────────────────────────────────────────────────────────


def on_delete_content(state: ReportsState, body: tk.Widget) -> None:
    """Delete the reported content (photo or comment).

    The corresponding report (and any other reports for the same content)
    are removed automatically via the database cascade.

    Prompts the admin for confirmation before permanently deleting the
    content.

    Args:
        state: Reports view state.
        body: Parent widget used for confirmation / info dialogs.
    """
    if state.selected_report is None:
        show_info(body, "Delete Content", "Please select a report first.")
        return

    report = state.selected_report
    report_type = report.get("type", "photo")
    creator = report.get("content_creator", "Unknown")

    confirmed = show_confirmation(
        body,
        "Delete Content",
        (
            f'Permanently delete this {report_type} by "{creator}"?\n\n'
            "All reports for this content will also be removed."
        ),
    )
    if not confirmed:
        return

    if report_type == "photo":
        photo_id = report.get("photo_id")
        success, msg = PhotoController.delete_photo(photo_id)
    else:
        comment_id = report.get("comment_id")
        success, msg = CommentController.delete_comment(comment_id)

    if success:
        state.selected_report = None
        state.selected_index = None
        _set_remove_btn_state(state, enabled=False)
        _reset_detail_panel(state)
        refresh_reports_list(state)
        toggle_empty_content_state(state, has_items=bool(state.filtered_reports))
        show_info(body, "Delete Content", "Content deleted successfully.")
    else:
        show_error(body, "Delete Content", msg)
