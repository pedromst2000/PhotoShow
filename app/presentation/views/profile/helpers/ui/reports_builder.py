import tkinter as tk

from app.presentation.styles.button import DEL_BTN_STYLE
from app.presentation.styles.colors import colors
from app.presentation.styles.fonts import quickSandBold, quickSandRegular
from app.presentation.styles.theme import (
    BTN_BG,
    BTN_FG,
    HEADER_FG,
    LIST_BG,
    PAGE_BG,
    PANEL_BG,
)
from app.presentation.views.helpers.ui.builder import (
    build_admin_window_body,
    build_admin_window_header,
    build_detail_placeholder,
    build_listbox_pagination,
    build_two_column_frames,
)
from app.presentation.views.helpers.ui.page_change import on_detail_page_changed
from app.presentation.views.profile.helpers.data.reports_data import (
    apply_report_filters,
)
from app.presentation.views.profile.helpers.data.reports_state import ReportsState
from app.presentation.views.profile.helpers.ui.reports_interactions import (
    on_delete_content,
    on_remove_report,
    on_report_select,
)
from app.presentation.widgets.filter_bar import build_option_filter
from app.presentation.widgets.helpers.button import make_button
from app.presentation.widgets.helpers.images import load_image
from app.presentation.widgets.listbox_widget import ListboxWidget

# ── Layout constants ──────────────────────────────────────────────────────────
_WIN_W: int = 950
_WIN_H: int = 660
_HEADER_H: int = 80
_LEFT_W: int = 290
_RIGHT_W: int = _WIN_W - _LEFT_W

_BG = PAGE_BG
_LIST_BG = LIST_BG
_PANEL_BG = PANEL_BG
_BTN_BG = BTN_BG
_BTN_FG = BTN_FG
_HEADER_FG = HEADER_FG
_ICON_DIR = "app/assets/images/UI_Icons/"

_FILTER_ROW_H: int = 32  # height per filter row (Type + Reason = 2 rows)
_PAG_ROW_H: int = 34
_ACTION_ROW_H: int = 38
_LISTBOX_H: int = _WIN_H - _HEADER_H - (_FILTER_ROW_H * 2) - _ACTION_ROW_H - _PAG_ROW_H


def _report_label(report: dict) -> str:
    """Return the display label for a report row.

    Args:
        report: The enriched report dict (must include ``type``, ``photo_id``,
                ``comment_id``, and ``reason``).

    Returns:
        str: Label in the form ``"Photo Report \u2014 Photo #<id> \u2014 <reason>"``
             or the equivalent for a comment report.
    """
    report_type = report.get("type", "photo")
    reason = report.get("reason", "Unknown")
    if report_type == "photo":
        content_id = report.get("photo_id", "?")
        return f"Photo Report \u2014 Photo #{content_id} \u2014 {reason}"
    content_id = report.get("comment_id", "?")
    return f"Comment Report \u2014 Comment #{content_id} \u2014 {reason}"


# ── Header ────────────────────────────────────────────────────────────────────


def build_reports_header(win: tk.Toplevel, state: ReportsState) -> None:
    """Build the window header with a bold title and descriptive subtitle.

    Args:
        win: The reports Toplevel window.
        state: Reports state (reserved for future adaptation).
    """
    build_admin_window_header(
        win,
        title="Reports",
        subtitle="User-submitted reports \u2014 select one to preview, remove, or delete the content.",
    )


# ── Body ──────────────────────────────────────────────────────────────────────


def build_reports_body(win: tk.Toplevel, state: ReportsState) -> None:
    """Build the main body, routing to the empty-state or two-column content UI.

    Stores ``state._empty_frame`` and ``state._content_frame`` so that
    interaction handlers can toggle between the two after removing reports.

    Args:
        win: The reports Toplevel window.
        state: Reports state with ``all_reports`` and ``filtered_reports``
               already populated by ``load_reports``.
    """

    def _build_content(content_frame: tk.Frame, body: tk.Frame) -> None:
        left, right = build_two_column_frames(content_frame, _LEFT_W)
        _build_left_panel(left, state, body)
        _build_right_panel(right, state, body)

    build_admin_window_body(
        win,
        state,
        has_items=bool(state.all_reports),
        empty_icon="\U0001f6a8",
        empty_title="No reports",
        empty_subtitle="Reports submitted by users will appear here for review.",
        icon_rely=0.38,
        title_rely=0.52,
        subtitle_rely=0.61,
        build_content=_build_content,
    )


# ── Left panel ────────────────────────────────────────────────────────────────


def _build_left_panel(left: tk.Frame, state: ReportsState, body: tk.Widget) -> None:
    """Build the left column: filters + Remove button + listbox + pagination.

    Args:
        left: The left-column frame.
        state: Reports state.
        body: Parent widget used to anchor dialogs in action callbacks.
    """
    _build_filter_rows(left, state)
    _build_remove_button(left, state, body)

    listbox = ListboxWidget(
        left,
        items=state.photos,
        label_fn=_report_label,
        title="Reports",
        on_select=lambda idx: on_report_select(idx, state),
        width=_LEFT_W,
        height=_LISTBOX_H,
        bg=_LIST_BG,
        fg=colors["primary-50"],
        select_bg=_PANEL_BG,
        select_fg=colors["primary-50"],
    )
    listbox.pack(fill="x")
    state.listbox_widget = listbox

    build_listbox_pagination(
        left,
        state,
        on_page_changed=lambda: on_detail_page_changed(
            state, selected_attr="selected_report", btn_attr="remove_btn"
        ),
        bg=_LIST_BG,
        btn_bg=_BTN_BG,
        btn_fg=_BTN_FG,
        text_fg=colors["primary-50"],
    )


def _build_filter_rows(parent: tk.Frame, state: ReportsState) -> None:
    """Build the Type and Reason filter dropdown rows for the left panel.

    Each filter row uses the shared ``build_option_filter`` helper so that
    the OptionMenu styling is consistent with other admin windows.

    Args:
        parent: The left-column frame to append the filter rows to.
        state: Reports state; ``type_var`` and ``reason_var`` are set here.
    """
    # ── Type filter ───────────────────────────────────────────────────────────
    type_row = tk.Frame(parent, bg=_LIST_BG, height=_FILTER_ROW_H)
    type_row.pack(fill="x", padx=6, pady=(6, 2))
    type_row.pack_propagate(False)

    tk.Label(
        type_row,
        text="Type",
        font=quickSandBold(10),
        bg=_LIST_BG,
        fg=colors["primary-50"],
        width=7,
        anchor="w",
    ).pack(side="left", padx=(0, 4))

    type_var = tk.StringVar(value="All")
    state.type_var = type_var

    type_menu = build_option_filter(
        type_row,
        type_var,
        ["All", "Photo", "Comment"],
        lambda: apply_report_filters(state),
        width=10,
    )
    type_menu.pack(side="left", fill="x", expand=True)

    # ── Reason filter ─────────────────────────────────────────────────────────
    reason_row = tk.Frame(parent, bg=_LIST_BG, height=_FILTER_ROW_H)
    reason_row.pack(fill="x", padx=6, pady=(0, 2))
    reason_row.pack_propagate(False)

    tk.Label(
        reason_row,
        text="Reason",
        font=quickSandBold(10),
        bg=_LIST_BG,
        fg=colors["primary-50"],
        width=7,
        anchor="w",
    ).pack(side="left", padx=(0, 4))

    reason_var = tk.StringVar(value="All")
    state.reason_var = reason_var

    reason_options = ["All"] + (state.reason_labels or [])
    reason_menu = build_option_filter(
        reason_row,
        reason_var,
        reason_options,
        lambda: apply_report_filters(state),
        width=10,
    )
    reason_menu.pack(side="left", fill="x", expand=True)


def _build_remove_button(
    parent: tk.Frame, state: ReportsState, body: tk.Widget
) -> None:
    """Build the "Remove Report" action button row.

    The button is initially disabled until the user selects a report.
    Removing a report deletes only the report record; the content is kept.

    Args:
        parent: The left-column frame.
        state: Reports state; ``remove_btn`` is set here.
        body: Parent widget used to anchor dialogs.
    """
    action_row = tk.Frame(parent, bg=_LIST_BG, height=_ACTION_ROW_H)
    action_row.pack(fill="x", padx=6, pady=(0, 4))
    action_row.pack_propagate(False)

    icon = load_image(f"{_ICON_DIR}Remove_Icon.png", size=(16, 16))

    btn = make_button(
        action_row,
        text="  Remove Report",
        cmd=lambda: on_remove_report(state, body),
        icon=icon,
        **DEL_BTN_STYLE,
    )
    btn.config(state=tk.DISABLED)
    btn.pack(fill="x")

    btn.image = icon  # type: ignore[attr-defined]
    state.remove_btn = btn


# ── Right panel ───────────────────────────────────────────────────────────────


def _build_right_panel(right: tk.Frame, state: ReportsState, body: tk.Widget) -> None:
    """Build the report detail preview panel on the right column.

    Shows a placeholder when no report is selected and the full detail
    (type, reason, content, creator, optional description, delete button)
    once the user makes a selection.

    Args:
        right: The right-column frame.
        state: Reports state; widget refs are set on this object.
        body: Parent widget used to anchor dialogs in delete callbacks.
    """
    build_detail_placeholder(
        right,
        state,
        icon="\U0001f6a8",
        title="Select a report to preview",
        subtitle="Click a report from the list on the left.",
    )

    # ── Detail view (hidden until a report is selected) ───────────────────────
    detail = tk.Frame(right, bg=_PANEL_BG)
    state._detail_frame = detail
    # (Not packed yet — revealed by _update_detail_panel in interactions)

    _build_detail_fields(detail, state, body)


def _build_detail_fields(
    detail: tk.Frame, state: ReportsState, body: tk.Widget
) -> None:
    """Populate the detail frame with labelled fields for the selected report.

    Stores widget references on *state* so interaction handlers can update
    content without rebuilding the UI.

    Args:
        detail: The detail frame (child of the right panel).
        state: Reports state; widget refs are stored here.
        body: Parent widget passed to the Delete Content button callback.
    """
    pad_x = 24
    pad_top = 20

    # ── Section title ─────────────────────────────────────────────────────────
    tk.Label(
        detail,
        text="Report Details",
        font=quickSandBold(16),
        bg=_PANEL_BG,
        fg=_HEADER_FG,
        anchor="w",
    ).pack(anchor="w", padx=pad_x, pady=(pad_top, 12))

    tk.Frame(detail, bg=colors["secondary-400"], height=1).pack(
        fill="x", padx=pad_x, pady=(0, 14)
    )

    # ── Type ──────────────────────────────────────────────────────────────────
    _field_label(detail, label="Type:", pad_x=pad_x)
    type_lbl = tk.Label(
        detail,
        text="",
        font=quickSandBold(13),
        bg=_PANEL_BG,
        fg=_HEADER_FG,
        anchor="w",
    )
    type_lbl.pack(anchor="w", padx=(pad_x + 8, pad_x), pady=(0, 10))
    state._type_label = type_lbl

    # ── Reason ────────────────────────────────────────────────────────────────
    _field_label(detail, label="Reason:", pad_x=pad_x)
    reason_lbl = tk.Label(
        detail,
        text="",
        font=quickSandBold(13),
        bg=_PANEL_BG,
        fg=_HEADER_FG,
        anchor="w",
        wraplength=_RIGHT_W - pad_x * 2 - 12,
        justify="left",
    )
    reason_lbl.pack(anchor="w", padx=(pad_x + 8, pad_x), pady=(0, 10))
    state._reason_label = reason_lbl

    # ── Reported content ──────────────────────────────────────────────────────

    content_frame = tk.Frame(detail, bg=_PANEL_BG)
    content_frame.pack(fill="x", padx=pad_x, pady=(0, 10))

    # Comment text — shown only for comment reports.
    content_text = tk.Text(
        content_frame,
        font=quickSandRegular(11),
        bg=colors["secondary-300"],
        fg=_HEADER_FG,
        relief="flat",
        borderwidth=0,
        highlightthickness=0,
        wrap="word",
        state=tk.DISABLED,
        height=4,
        padx=10,
        pady=6,
    )
    state._content_text = content_text
    # Not packed yet — _update_detail_panel shows the correct widget.

    # Photo preview canvas — shown only for photo reports.
    photo_canvas = tk.Canvas(
        content_frame,
        width=_RIGHT_W - pad_x * 2,
        height=160,
        bg=colors["secondary-300"],
        highlightthickness=0,
        bd=0,
    )
    state._content_photo_canvas = photo_canvas
    # Not packed yet — _update_detail_panel shows the correct widget.

    # ── Content creator (avatar + username, no label text) ────────────────────
    creator_row = tk.Frame(detail, bg=_PANEL_BG)
    creator_row.pack(anchor="w", padx=pad_x, pady=(0, 10))

    avatar_canvas = tk.Canvas(
        creator_row, width=28, height=28, bg=_PANEL_BG, highlightthickness=0, bd=0
    )
    avatar_canvas.pack(side="left", padx=(0, 6))
    state._creator_avatar_canvas = avatar_canvas

    username_lbl = tk.Label(
        creator_row,
        text="",
        font=quickSandBold(12),
        bg=_PANEL_BG,
        fg=_HEADER_FG,
        anchor="w",
    )
    username_lbl.pack(side="left")
    state._creator_username_label = username_lbl

    # ── Optional reporter description (shown only when reason is "Other") ──────
    desc_frame = tk.Frame(detail, bg=_PANEL_BG)
    # Not packed yet — revealed by _update_detail_panel when applicable.
    state._description_frame = desc_frame

    _field_label(desc_frame, label="Reporter Note:", pad_x=0)
    desc_label = tk.Label(
        desc_frame,
        text="",
        font=quickSandRegular(11),
        bg=_PANEL_BG,
        fg=_HEADER_FG,
        anchor="w",
        justify="left",
        wraplength=_RIGHT_W - pad_x * 2 - 12,
    )
    desc_label.pack(fill="x", pady=(0, 4))
    state._description_label = desc_label

    # ── Delete Content button ─────────────────────────────────────────────────
    icon = load_image(f"{_ICON_DIR}Remove_Icon.png", size=(16, 16))
    del_btn = make_button(
        detail,
        text="  Delete Photo",
        cmd=lambda: on_delete_content(state, body),
        icon=icon,
        **DEL_BTN_STYLE,
    )
    del_btn.pack(anchor="w", padx=pad_x, pady=(4, pad_top))
    del_btn.image = icon  # type: ignore[attr-defined]
    state._delete_btn = del_btn


def _field_label(parent: tk.Widget, *, label: str, pad_x: int) -> None:
    """Render a small muted field-name label (e.g. "Type:", "Reason:").

    Args:
        parent: Parent widget to pack into.
        label: The field label text.
        pad_x: Horizontal padding.
    """
    tk.Label(
        parent,
        text=label,
        font=quickSandBold(10),
        bg=_PANEL_BG,
        fg=colors["secondary-400"],
        anchor="w",
    ).pack(anchor="w", padx=pad_x, pady=(0, 2))
