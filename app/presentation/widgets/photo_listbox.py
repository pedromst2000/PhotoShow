import tkinter as tk
from tkinter import ttk
from typing import Callable, List, Optional

from app.presentation.styles.colors import colors
from app.presentation.styles.fonts import quickSandBold, quickSandRegular


class PhotoListboxWidget(tk.Frame):
    """
    Reusable scrollable listbox for displaying a list of photos.

    Each entry shows "Photo {id} — {description[:30]}".
    Supports pre-selection by photo ID, empty state, and a selection callback.
    Intended to be reused in album details, profile, and other views.
    """

    _EMPTY_TEXT = "No photos to display"

    def __init__(
        self,
        parent: tk.Widget,
        photos: List[dict],
        on_select: Optional[Callable[[int], None]] = None,
        selected_photo_id: Optional[int] = None,
        width: int = 260,
        height: int = 460,
        bg: str = colors["secondary-500"],
        fg: str = colors["primary-50"],
        select_bg: str = colors["secondary-300"],
        select_fg: str = colors["primary-50"],
    ):
        """
        Initialize the PhotoListboxWidget.

        Args:
            parent (tk.Widget): The parent widget.
            photos (List[dict]): A list of photo dictionaries.
            on_select (Optional[Callable[[int], None]], optional): Callback for photo selection. Defaults to None.
            selected_photo_id (Optional[int], optional): The ID of the photo to be pre-selected. Defaults to None.
            width (int, optional): The width of the widget. Defaults to 260.
            height (int, optional): The height of the widget. Defaults to 460.
            bg (str, optional): Background color. Defaults to colors["secondary-500"].
            fg (str, optional): Foreground color. Defaults to colors["primary-50"].
            select_bg (str, optional): Background color for selected item. Defaults to colors["secondary-300"].
            select_fg (str, optional): Foreground color for selected item. Defaults to colors["primary-50"].
        """

        super().__init__(parent, bg=bg, width=width, height=height)
        self.pack_propagate(False)

        self._photos = photos
        self._on_select = on_select
        self._bg = bg
        self._fg = fg
        self._select_bg = select_bg
        self._select_fg = select_fg
        self._is_empty = not bool(photos)

        self._listbox: Optional[tk.Listbox] = None

        self._build(selected_photo_id)

    def refresh(
        self,
        photos: List[dict],
        selected_photo_id: Optional[int] = None,
    ):
        """
        Replace the current photo list and rebuild the widget contents.

        Args:
            photos (List[dict]): New list of photo dictionaries to display.
            selected_photo_id (Optional[int], optional): The ID of the photo to be pre-selected after refresh. Defaults to None.
        """
        self._photos = photos
        self._is_empty = not bool(photos)
        for widget in self.winfo_children():
            widget.destroy()
        self._listbox = None
        self._build(selected_photo_id)

    @staticmethod
    def _photo_label(photo: dict) -> str:
        """
        Generate a display label for a photo dictionary.

        Args:
            photo (dict): A dictionary representing a photo, expected to have 'id' and 'description' keys.

        Returns:
            str: A formatted string like "Photo {id} — {description[:30]}".
        """
        desc = (photo.get("description") or "").strip()
        truncated = desc[:30] + ("…" if len(desc) > 30 else "")
        return f"Photo {photo.get('id', '?')} — {truncated}"

    def _build(self, selected_photo_id: Optional[int]):
        """
        Build the photo listbox widget.

        Args:
            selected_photo_id (Optional[int]): The ID of the photo to be pre-selected. Defaults to None.
        """
        title_lbl = tk.Label(
            self,
            text="Album Photos",
            font=quickSandBold(11),
            bg=self._bg,
            fg=self._fg,
            anchor="w",
        )
        title_lbl.pack(anchor="w", padx=10, pady=(10, 4))

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
        )
        self._listbox.pack(side=tk.LEFT, fill="both", expand=True)
        scrollbar.config(command=self._listbox.yview)

        if self._is_empty:
            self._listbox.insert("end", self._EMPTY_TEXT)
            self._listbox.config(state="disabled")
        else:
            for photo in self._photos:
                self._listbox.insert("end", self._photo_label(photo))

            self._listbox.bind(  # type: ignore[misc]
                "<<ListboxSelect>>", self._on_listbox_select
            )

            # Pre-select by photo id
            if selected_photo_id is not None:
                for idx, photo in enumerate(self._photos):
                    if photo.get("id") == selected_photo_id:
                        self._listbox.selection_clear(0, "end")
                        self._listbox.selection_set(idx)
                        self._listbox.see(idx)
                        break

    def _on_listbox_select(self, _event: tk.Event):  # type: ignore[type-arg]
        """
        Handle the event when a photo is selected in the listbox.

        Args:
            _event (tk.Event): The event object (not used).
        """
        if self._is_empty or self._on_select is None or self._listbox is None:
            return
        sel = self._listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        if 0 <= idx < len(self._photos):
            self._on_select(idx)
