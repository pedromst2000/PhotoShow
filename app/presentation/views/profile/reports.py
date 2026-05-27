from app.presentation.styles.theme import LIST_BG
from app.presentation.views.profile.helpers.data.reports_data import load_reports
from app.presentation.views.profile.helpers.data.reports_state import ReportsState
from app.presentation.views.profile.helpers.ui.reports_builder import (
    _WIN_H,
    _WIN_W,
    build_reports_body,
    build_reports_header,
)
from app.presentation.widgets.window import create_toplevel


def reportsWindow() -> None:
    """Display the admin reports window.

    This window is only accessible to admin users and shows all reports
    submitted by users about photos or comments.
    """
    win = create_toplevel(
        title="\U0001f6a8 Reports",
        width=_WIN_W,
        height=_WIN_H,
        icon_path="app/assets/PhotoShowIcon.ico",
        bg_color=LIST_BG,
    )

    state = ReportsState()
    state.win = win

    load_reports(state)
    build_reports_header(win, state)
    build_reports_body(win, state)

    win.grab_set()
