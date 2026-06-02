import tkinter as tk

from app.presentation.styles.button import ACTION_BTN_STYLE
from app.presentation.styles.colors import colors
from app.presentation.styles.fonts import quickSandBold, quickSandRegular
from app.presentation.styles.theme import LIST_BG, PAGE_BG, PANEL_BG
from app.presentation.views.helpers.ui.builder.admin_panel import (
    build_admin_window_header,
    build_detail_placeholder,
)
from app.presentation.views.notifications.helpers.data.formatters import (
    notification_row_label,
)
from app.presentation.views.notifications.helpers.data.state import NotificationState
from app.presentation.views.notifications.helpers.ui.avatar import build_avatar_canvas
from app.presentation.views.notifications.helpers.ui.interactions import (
    on_notification_select,
)
from app.presentation.widgets.helpers.button import make_button
from app.presentation.widgets.helpers.images import load_image
from app.presentation.widgets.listbox_widget import ListboxWidget

# ── Layout constants ──────────────────────────────────────────────────────────
_HEADER_H: int = 70
_LEFT_W: int = 340
_LISTBOX_H: int = 460
_BTN_BAR_H: int = 50
_ICON_DIR: str = "app/assets/images/UI_Icons/"


# ── Public builders ───────────────────────────────────────────────────────────


def build_notification_header(win: tk.Toplevel, state: NotificationState) -> None:
    """Build the header bar with title and subtitle.

    Args:
        win: The Notifications Toplevel window.
        state: Notification view state (reserved for future use).
    """
    build_admin_window_header(
        win,
        title="🔔 Notifications",
        subtitle="Your recent unread activity.",
        height=_HEADER_H,
    )


def build_notification_body(win: tk.Toplevel, state: NotificationState) -> None:
    """Build the body: left list panel + right detail panel.

    Args:
        win: The Notifications Toplevel window.
        state: Notification view state holding runtime refs and widget handles.
    """
    body = tk.Frame(win, bg=PAGE_BG)
    body.pack(fill="both", expand=True)

    _build_left_panel(body, state)
    _build_right_panel(body, state)


# ── Private helpers ───────────────────────────────────────────────────────────


def _build_left_panel(body: tk.Frame, state: NotificationState) -> None:
    """Build the left panel: scrollable notification list + action buttons.

    Args:
        body: The outer body frame.
        state: Notification view state.
    """
    left = tk.Frame(body, bg=LIST_BG, width=_LEFT_W)
    left.pack(side="left", fill="y")
    left.pack_propagate(False)

    lbw = ListboxWidget(
        parent=left,
        items=state.notifications,
        label_fn=lambda n: notification_row_label(n),
        title="Unread Notifications",
        on_select=lambda idx: on_notification_select(idx, state),
        id_key="id",
        width=_LEFT_W,
        height=_LISTBOX_H,
    )
    lbw.pack(fill="x")
    state.listbox_widget = lbw

    # ── Button bar ─────────────────────────────────────────────────────────
    btn_bar = tk.Frame(left, bg=LIST_BG, height=_BTN_BAR_H)
    btn_bar.pack(fill="x", pady=(8, 8))
    btn_bar.pack_propagate(False)

    remove_icon = load_image(f"{_ICON_DIR}Remove_Icon.png", size=(14, 14))

    mark_read_btn = make_button(
        btn_bar,
        "  Mark as Read",
        cmd=None,
        icon=remove_icon,
        state=tk.DISABLED,
        **ACTION_BTN_STYLE,
    )
    mark_read_btn.pack(side="left", padx=(14, 4))
    mark_read_btn.image = remove_icon  # type: ignore[attr-defined]
    state.mark_read_btn = mark_read_btn

    mark_all_btn = make_button(
        btn_bar,
        "  Mark All Read",
        cmd=None,
        **ACTION_BTN_STYLE,
    )
    mark_all_btn.pack(side="left", padx=(4, 14))
    state.mark_all_btn = mark_all_btn


def _build_right_panel(body: tk.Frame, state: NotificationState) -> None:
    """Build the right panel: placeholder + hidden detail card.

    The detail card is revealed and populated when a notification is selected.

    Args:
        body: The outer body frame.
        state: Notification view state.
    """
    right = tk.Frame(body, bg=PANEL_BG)
    right.pack(side="left", fill="both", expand=True)
    state.right_panel = right

    # Placeholder (visible by default)
    build_detail_placeholder(
        right,
        state,
        icon="🔔",
        title="No notification selected",
        subtitle="Click a notification on the left to view details",
        bg=PANEL_BG,
    )

    # Detail card (hidden until a notification is selected)
    detail = tk.Frame(right, bg=PANEL_BG)
    state._detail_frame = detail

    # ── Avatar ─────────────────────────────────────────────────────────────
    avatar_canvas = build_avatar_canvas(detail, size=64, bg=PANEL_BG)
    avatar_canvas.pack(pady=(28, 6))
    state.detail_avatar_canvas = avatar_canvas

    # ── Sender name ────────────────────────────────────────────────────────
    sender_lbl = tk.Label(
        detail,
        text="",
        font=quickSandBold(13),
        bg=PANEL_BG,
        fg=colors["primary-50"],
        anchor="center",
    )
    sender_lbl.pack()
    state.detail_sender_label = sender_lbl

    # Divider
    tk.Frame(detail, bg=colors["secondary-400"], height=1).pack(
        fill="x", padx=30, pady=(10, 10)
    )

    # ── Type label ─────────────────────────────────────────────────────────
    type_lbl = tk.Label(
        detail,
        text="",
        font=quickSandBold(12),
        bg=PANEL_BG,
        fg=colors["accent-300"],
        wraplength=420,
        anchor="center",
        justify="center",
    )
    type_lbl.pack(padx=20)
    state.detail_type_label = type_lbl

    # ── Message ────────────────────────────────────────────────────────────
    msg_lbl = tk.Label(
        detail,
        text="",
        font=quickSandRegular(12),
        bg=PANEL_BG,
        fg=colors["primary-50"],
        wraplength=420,
        anchor="center",
        justify="center",
    )
    msg_lbl.pack(padx=20, pady=(10, 4))
    state.detail_msg_label = msg_lbl

    # ── Timestamp ──────────────────────────────────────────────────────────
    time_lbl = tk.Label(
        detail,
        text="",
        font=quickSandBold(12),
        bg=PANEL_BG,
        fg=colors["secondary-400"],
        anchor="center",
    )
    time_lbl.pack(pady=(4, 14))
    state.detail_time_label = time_lbl

    # Divider
    tk.Frame(detail, bg=colors["secondary-400"], height=1).pack(
        fill="x", padx=30, pady=(0, 14)
    )

    # ── Actions frame (rebuilt on every notification selection) ────────────
    actions_frame = tk.Frame(detail, bg=PANEL_BG)
    actions_frame.pack()
    state.detail_actions_frame = actions_frame
