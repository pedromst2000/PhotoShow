import tkinter as tk
from typing import Dict, List, Optional

from PIL import ImageTk


class NotificationState:
    """Holds all mutable references for the Notifications window.

    Widget refs are set by the builder functions and read / mutated
    by the interaction handlers.
    """

    def __init__(self) -> None:
        self.win: Optional[tk.Toplevel] = None

        # ── Data ──────────────────────────────────────────────────────────────
        # Unread enriched notifications (newest first)
        self.notifications: List[dict] = []
        # typeId → type dict (for label lookup)
        self.notification_types: Dict[int, dict] = {}
        self.selected_notification: Optional[dict] = None
        self.selected_index: Optional[int] = None

        # ── Widget refs ───────────────────────────────────────────────────────
        self.listbox_widget = None  # ListboxWidget instance
        self.mark_read_btn: Optional[tk.Button] = None
        self.mark_all_btn: Optional[tk.Button] = None
        self.right_panel: Optional[tk.Frame] = None

        # Detail / placeholder frames (swapped on selection)
        self._placeholder_frame: Optional[tk.Frame] = None
        self._detail_frame: Optional[tk.Frame] = None

        # Labels inside the detail card
        self.detail_avatar_canvas: Optional[tk.Canvas] = None
        self.detail_sender_label: Optional[tk.Label] = None
        self.detail_type_label: Optional[tk.Label] = None
        self.detail_msg_label: Optional[tk.Label] = None
        self.detail_time_label: Optional[tk.Label] = None

        # Rebuilt on every notification selection to match the type's action
        self.detail_actions_frame: Optional[tk.Frame] = None

        # GC guard — keeps the current avatar ImageTk.PhotoImage alive
        self._avatar_img_ref: Optional[ImageTk.PhotoImage] = None
