import tkinter as tk
from typing import Callable, List, Optional

from app.presentation.styles.colors import colors
from app.presentation.widgets.listbox_widget import ListboxWidget


def _photo_label(photo: dict) -> str:
    """Generate a display label for a photo dict.

    Returns:
        str: "Photo {id} — {description[:30]}…"
    """
    desc = (photo.get("description") or "").strip()
    truncated = desc[:30] + ("…" if len(desc) > 30 else "")
    return f"Photo {photo.get('id', '?')} \u2014 {truncated}"


class PhotoListboxWidget(ListboxWidget):
    """
    Scrollable listbox for displaying a list of photos.

    Thin subclass of ``ListboxWidget`` that fixes the photo-specific label
    format ("Photo {id} — {desc[:30]}") and the "Album Photos" section title.
    All generic behaviour (refresh, pagination sync, empty state) is inherited.
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
            parent: The parent widget.
            photos: A list of photo dictionaries.
            on_select: Callback invoked with the local index on selection.
            selected_photo_id: ID of the photo to pre-select.
            width: Widget width in pixels.
            height: Widget height in pixels.
            bg: Background colour.
            fg: Foreground colour.
            select_bg: Background colour for the selected row.
            select_fg: Foreground colour for the selected row.
        """
        super().__init__(
            parent,
            items=photos,
            label_fn=_photo_label,
            title="Album Photos",
            on_select=on_select,
            selected_item_id=selected_photo_id,
            id_key="id",
            width=width,
            height=height,
            bg=bg,
            fg=fg,
            select_bg=select_bg,
            select_fg=select_fg,
        )

    def refresh(
        self,
        photos: List[dict],
        selected_photo_id: Optional[int] = None,
    ) -> None:
        """Replace the current photo list and rebuild the widget.

        Args:
            photos: New list of photo dictionaries.
            selected_photo_id: Optional ID to pre-select after refresh.
        """
        super().refresh(photos, selected_item_id=selected_photo_id)
