import tkinter as tk
from typing import Optional

from app.controllers.notification_controller import NotificationController
from app.presentation.styles.button import ACTION_BTN_STYLE
from app.presentation.styles.colors import colors
from app.presentation.styles.fonts import quickSandRegular
from app.presentation.styles.theme import PANEL_BG
from app.presentation.views.notifications.helpers.data.formatters import (
    format_notification_message,
    format_time_ago,
    format_time_full,
)
from app.presentation.views.notifications.helpers.data.state import NotificationState
from app.presentation.views.notifications.helpers.ui.avatar import load_avatar_image
from app.presentation.widgets.helpers.button import make_button

# ── Main interaction handlers ─────────────────────────────────────────────────


def on_notification_select(idx: int, state: NotificationState) -> None:
    """Handle listbox selection — populate the detail panel.

    Args:
        idx: Zero-based index of the selected notification in ``state.notifications``.
        state: Notification view state.
    """
    if idx < 0 or idx >= len(state.notifications):
        return
    state.selected_index = idx
    state.selected_notification = state.notifications[idx]

    # Mark as read in DB so the unread count drops for the next blinker poll.
    NotificationController.mark_read(state.selected_notification["id"])

    if state.mark_read_btn:
        state.mark_read_btn.config(state=tk.NORMAL)

    # Swap placeholder → detail
    if state._placeholder_frame:
        state._placeholder_frame.pack_forget()
    if state._detail_frame:
        state._detail_frame.pack(fill="both", expand=True)

    _populate_detail(state)


def on_mark_read(state: NotificationState) -> None:
    """Mark the selected notification as read and remove it from the list view.

    Args:
        state: Notification view state.
    """
    n = state.selected_notification
    if n is None:
        return

    NotificationController.mark_read(n["id"])

    state.notifications = [
        item for item in state.notifications if item["id"] != n["id"]
    ]
    state.selected_notification = None
    state.selected_index = None

    if state.listbox_widget:
        state.listbox_widget.refresh(state.notifications)
    if state.mark_read_btn:
        state.mark_read_btn.config(state=tk.DISABLED)

    # Revert to placeholder
    if state._detail_frame:
        state._detail_frame.pack_forget()
    if state._placeholder_frame:
        state._placeholder_frame.pack(fill="both", expand=True)


def on_mark_all_read(state: NotificationState) -> None:
    """Mark all notifications as read and clear the list view.

    Args:
        state: Notification view state.
    """
    NotificationController.mark_all_read()

    state.notifications = []
    state.selected_notification = None
    state.selected_index = None

    if state.listbox_widget:
        state.listbox_widget.refresh([])
    if state.mark_read_btn:
        state.mark_read_btn.config(state=tk.DISABLED)

    # Revert to placeholder
    if state._detail_frame:
        state._detail_frame.pack_forget()
    if state._placeholder_frame:
        state._placeholder_frame.pack(fill="both", expand=True)


# ── Detail panel helpers ──────────────────────────────────────────────────────


def _populate_detail(state: NotificationState) -> None:
    """Fill all detail-panel widgets from the currently selected notification.

    Args:
        state: Notification view state carrying the selected notification.
    """
    n = state.selected_notification
    if n is None:
        return

    sender = n.get("sender_username", "Unknown")
    type_label = n.get("type_label", "Notification")
    message = format_notification_message(n)
    created_at = n.get("createdAt")
    time_str = (
        f"{format_time_ago(created_at)}  ·  {format_time_full(created_at)}"
        if created_at
        else "—"
    )

    # ── Avatar ──────────────────────────────────────────────────────────────
    canvas = state.detail_avatar_canvas
    if canvas:
        avatar_path: Optional[str] = n.get("sender_avatar")
        img_ref = load_avatar_image(canvas, avatar_path, size=64)
        state._avatar_img_ref = img_ref  # prevent GC

    # ── Text labels ────────────────────────────────────────────────────────
    if state.detail_sender_label:
        state.detail_sender_label.config(text=sender)
    if state.detail_type_label:
        state.detail_type_label.config(text=type_label)
    if state.detail_msg_label:
        state.detail_msg_label.config(text=message)
    if state.detail_time_label:
        state.detail_time_label.config(text=time_str)

    # ── Per-type action(s) ─────────────────────────────────────────────────
    _rebuild_actions(state, n)


def _rebuild_actions(state: NotificationState, n: dict) -> None:
    """Clear and rebuild the actions frame based on the notification type.

    Each type maps to a distinct action:
    - ``comment_on_photo``  → "Open Comments" (opens the photo's comment thread)
    - ``like_photo``        → "Open Photo" (opens photo details)
    - ``album_favorited``   → "Open Album" (opens the favourited album)
    - ``new_follower``      → descriptive label only (no navigation)
    - ``admin_delete_*``    → no action (content is gone)

    Args:
        state: Notification view state carrying the ``detail_actions_frame`` ref.
        n: Enriched notification dict for the currently selected item.
    """
    frame = state.detail_actions_frame
    if frame is None:
        return

    for child in frame.winfo_children():
        child.destroy()

    type_key: str = n.get("type_key", "")
    photo_id: Optional[int] = n.get("photoId")
    album_id: Optional[int] = n.get("albumId")
    sender: str = n.get("sender_username", "")

    if type_key == "comment_on_photo" and photo_id:
        _pid = photo_id
        btn = make_button(
            frame,
            "Open Comments",
            cmd=lambda: _open_comments(_pid),
            **ACTION_BTN_STYLE,
        )
        btn.pack(pady=4)

    elif type_key == "like_photo" and photo_id:
        _pid = photo_id
        btn = make_button(
            frame,
            "Open Photo",
            cmd=lambda: _open_photo(_pid, state),
            **ACTION_BTN_STYLE,
        )
        btn.pack(pady=4)

    elif type_key == "album_favorited" and album_id:
        _aid = album_id
        btn = make_button(
            frame,
            "Open Album",
            cmd=lambda: _open_album(_aid),
            **ACTION_BTN_STYLE,
        )
        btn.pack(pady=4)

    elif type_key == "new_follower":
        tk.Label(
            frame,
            text=f"@{sender} is now following you.",
            font=quickSandRegular(11),
            bg=PANEL_BG,
            fg=colors["primary-50"],
            anchor="center",
        ).pack(pady=4)

    # admin_delete_comment / admin_delete_photo → no action widget (content removed)


# ── Navigation helpers ────────────────────────────────────────────────────────


def _open_comments(photo_id: int) -> None:
    """Open the standard comments window for *photo_id*.

    Args:
        photo_id: The photo whose comment thread to open.
    """
    try:
        from app.controllers.photo_controller import PhotoController
        from app.presentation.views.comments.main import open_comments
        from app.presentation.views.helpers.data.state import BasePhotoState

        photo = PhotoController.get_photo_details(photo_id)
        if photo is None:
            return

        nav_state = BasePhotoState()
        nav_state.photos = [photo]
        nav_state.selected_index = 0
        open_comments(nav_state)
    except Exception as e:
        from app.utils.log_utils import log_exception

        log_exception("notifications._open_comments", e, context={"photo_id": photo_id})


def _open_photo(photo_id: int, notif_state: NotificationState) -> None:
    """Open the standard photo details window for *photo_id*.

    Wires a deletion callback so that when the photo is deleted from inside
    the details window, all related notifications are removed from the
    notification panel in real-time.

    Args:
        photo_id: The photo to display.
        notif_state: The active notification panel state.
    """
    try:
        from app.controllers.photo_controller import PhotoController
        from app.presentation.views.helpers.data.state import BasePhotoState
        from app.presentation.views.photo.main import open_photo_details

        photo = PhotoController.get_photo_details(photo_id)
        if photo is None:
            return

        nav_state = BasePhotoState()
        nav_state.photos = [photo]
        nav_state.selected_index = 0
        nav_state._on_photo_deleted = lambda pid: _clear_photo_notifications(
            pid, notif_state
        )
        open_photo_details(nav_state)
    except Exception as e:
        from app.utils.log_utils import log_exception

        log_exception("notifications._open_photo", e, context={"photo_id": photo_id})


def _clear_photo_notifications(photo_id: int, notif_state: NotificationState) -> None:
    """Remove all in-memory notifications linked to *photo_id* and reset the panel.

    Called after a successful photo deletion from the details window.

    Args:
        photo_id: ID of the deleted photo.
        notif_state: The active notification panel state.
    """
    notif_state.notifications = [
        n for n in notif_state.notifications if n.get("photoId") != photo_id
    ]
    notif_state.selected_notification = None
    notif_state.selected_index = None

    if notif_state.listbox_widget:
        notif_state.listbox_widget.refresh(notif_state.notifications)
    if notif_state.mark_read_btn:
        notif_state.mark_read_btn.config(state=tk.DISABLED)
    if notif_state._detail_frame:
        notif_state._detail_frame.pack_forget()
    if notif_state._placeholder_frame:
        notif_state._placeholder_frame.pack(fill="both", expand=True)


def _open_album(album_id: int) -> None:
    """Open the album window for *album_id*.

    Args:
        album_id: The album to display.
    """
    try:
        from app.presentation.views.album.main import open_album
        from app.presentation.views.helpers.data.state import BasePhotoState

        nav_state = BasePhotoState()
        nav_state.photos = [{"albumId": album_id}]
        nav_state.selected_index = 0
        open_album(nav_state)
    except Exception:
        pass
