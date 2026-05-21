import tkinter as tk
from tkinter import ttk
from typing import Callable, List, Optional

from app.presentation.styles.colors import colors
from app.presentation.styles.fonts import quickSandBold, quickSandRegular


class ListboxWidget(tk.Frame):
    """
    Generic reusable scrollable listbox for displaying a list of dict items.

    Each entry label is produced by a caller-supplied *label_fn*.  Supports
    pre-selection by item ID, an empty state, and a selection callback.

    Intended to be reused for photos, albums, favorites, and any other
    list views across the project.
    """

    _EMPTY_TEXT = "No items to display"

    def __init__(
        self,
        parent: tk.Widget,
        items: List[dict],
        label_fn: Callable[[dict], str],
        title: str = "",
        on_select: Optional[Callable[[int], None]] = None,
        selected_item_id: Optional[int] = None,
        id_key: str = "id",
        width: int = 260,
        height: int = 460,
        bg: str = colors["secondary-500"],
        fg: str = colors["primary-50"],
        select_bg: str = colors["secondary-300"],
        select_fg: str = colors["primary-50"],
    ):
        """
        Initialize the ListboxWidget.

        Args:
            parent: The parent widget.
            items: A list of item dictionaries to display.
            label_fn: Callable receiving a single item dict and returning the
                      display string for that row.
            title: Optional section title rendered above the listbox.
            on_select: Callback invoked with the *local page* index when an
                       item is selected.
            selected_item_id: ID of the item to pre-select (matched via
                              ``item[id_key]``).
            id_key: Dict key used for ID comparison (default: ``"id"``).
            width: Widget width in pixels.
            height: Widget height in pixels.
            bg: Background colour.
            fg: Foreground (text) colour.
            select_bg: Background colour for the selected row.
            select_fg: Foreground colour for the selected row.
        """
        super().__init__(parent, bg=bg, width=width, height=height)
        self.pack_propagate(False)

        self._items = items
        self._label_fn = label_fn
        self._title = title
        self._on_select = on_select
        self._id_key = id_key
        self._bg = bg
        self._fg = fg
        self._select_bg = select_bg
        self._select_fg = select_fg
        self._is_empty = not bool(items)

        self._listbox: Optional[tk.Listbox] = None

        self._build(selected_item_id)

    # ── Public API ────────────────────────────────────────────────────────────

    def refresh(
        self,
        items: List[dict],
        selected_item_id: Optional[int] = None,
    ) -> None:
        """Replace the current item list and rebuild the widget contents.

        Args:
            items: New list of item dictionaries to display.
            selected_item_id: Optional ID to pre-select after refresh.
        """
        self._items = items
        self._is_empty = not bool(items)
        for widget in self.winfo_children():
            widget.destroy()
        self._listbox = None
        self._build(selected_item_id)

    def select_index(self, idx: int) -> None:
        """Programmatically select a row by its local index.

        Args:
            idx: Zero-based index within the current page items.
        """
        if self._listbox is None or self._is_empty:
            return
        if 0 <= idx < len(self._items):
            self._listbox.selection_clear(0, "end")
            self._listbox.selection_set(idx)
            self._listbox.see(idx)

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _build(self, selected_item_id: Optional[int]) -> None:
        """Build (or rebuild) the listbox interior."""
        if self._title:
            tk.Label(
                self,
                text=self._title,
                font=quickSandBold(11),
                bg=self._bg,
                fg=self._fg,
                anchor="w",
            ).pack(anchor="w", padx=10, pady=(10, 4))

        list_frame = tk.Frame(self, bg=self._bg)
        list_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical")
        scrollbar.pack(side=tk.RIGHT, fill="y")

        self._listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            bg=self._bg,
            fg=self._fg,
            selectbackground=self._select_bg,
            selectforeground=self._select_fg,
            font=quickSandRegular(10),
            relief=tk.FLAT,
            borderwidth=0,
            highlightthickness=0,
            activestyle="none",
            exportselection=False,
        )
        self._listbox.pack(side=tk.LEFT, fill="both", expand=True)
        scrollbar.config(command=self._listbox.yview)

        if self._is_empty:
            self._listbox.insert("end", self._EMPTY_TEXT)
            self._listbox.config(state="disabled")
        else:
            for item in self._items:
                self._listbox.insert("end", self._label_fn(item))

            self._listbox.bind(  # type: ignore[misc]
                "<<ListboxSelect>>", self._on_listbox_select
            )

            if selected_item_id is not None:
                for idx, item in enumerate(self._items):
                    if item.get(self._id_key) == selected_item_id:
                        self._listbox.selection_clear(0, "end")
                        self._listbox.selection_set(idx)
                        self._listbox.see(idx)
                        break

    def _on_listbox_select(self, _event: tk.Event) -> None:  # type: ignore[type-arg]
        """Handle item selection in the listbox."""
        if self._is_empty or self._on_select is None or self._listbox is None:
            return
        sel = self._listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        if 0 <= idx < len(self._items):
            self._on_select(idx)
