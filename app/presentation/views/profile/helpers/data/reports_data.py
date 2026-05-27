from app.controllers.report_controller import ReportController
from app.presentation.views.helpers.data.pagination_helpers import (
    init_list_pagination,
    refresh_listbox_ui,
)
from app.presentation.views.helpers.ui.builder import toggle_empty_content_state
from app.presentation.views.profile.helpers.data.reports_state import ReportsState
from app.utils.log_utils import log_exception

_REPORTS_PER_PAGE = 8


def load_reports(state: ReportsState) -> bool:
    """
    Load all enriched reports into *state* and initialise pagination.

    Populates ``all_reports``, ``filtered_reports``, and ``reason_labels``,
    then sets up the pagination state for the first page.

    Args:
        state: The ``ReportsState`` instance to populate.

    Returns:
        bool: True on success, False on unexpected error.
    """
    try:
        reports = ReportController.get_all_enriched()
        labels = ReportController.get_reason_labels()

        state.all_reports = reports
        state.filtered_reports = reports
        state.reason_labels = labels

        init_list_pagination(state, reports, _REPORTS_PER_PAGE)
        return True
    except Exception as e:
        log_exception("reports.load_reports", e)
        return False


def apply_report_filters(state: ReportsState) -> None:
    """
    Filter ``all_reports`` by the current type and reason selections and
    reinitialise pagination for the filtered result.

    Resets the current selection and hides the detail panel so the UI stays
    consistent after a filter change.

    Args:
        state: Reports view state carrying the filter ``StringVar``\\ s.
    """
    filtered = state.all_reports

    type_filter = state.type_var.get() if state.type_var else "All"
    reason_filter = state.reason_var.get() if state.reason_var else "All"

    if type_filter != "All":
        filtered = [r for r in filtered if r["type"] == type_filter.lower()]

    if reason_filter != "All":
        filtered = [r for r in filtered if r["reason"] == reason_filter]

    state.filtered_reports = filtered
    init_list_pagination(state, filtered, _REPORTS_PER_PAGE)
    refresh_listbox_ui(state)

    # Reset selection and detail panel.
    state.selected_report = None
    state.selected_index = None

    btn = getattr(state, "remove_btn", None)
    if btn is not None:
        btn.config(state="disabled")

    detail = getattr(state, "_detail_frame", None)
    placeholder = getattr(state, "_placeholder_frame", None)
    if detail is not None:
        detail.pack_forget()
    if placeholder is not None:
        placeholder.pack(fill="both", expand=True)

    toggle_empty_content_state(state, has_items=bool(filtered))


def refresh_reports_list(state: ReportsState) -> None:
    """
    Reload all reports from the controller and re-apply the current filters.

    Used after removing a report or deleting content so the listbox reflects
    the current DB state without reopening the window.

    Args:
        state: The ``ReportsState`` instance to refresh.
    """
    try:
        reports = ReportController.get_all_enriched()
        state.all_reports = reports
        apply_report_filters(state)
    except Exception as e:
        log_exception("reports.refresh_reports_list", e)
