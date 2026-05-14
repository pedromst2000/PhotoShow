import tkinter as tk
from typing import Optional

from app.presentation.styles.colors import colors
from app.presentation.styles.fonts import quickSandBold
from app.presentation.styles.theme import (
    BTN_BG,
    BTN_FG,
    HEADER_FG,
    LIST_BG,
    PAGE_BG,
    PANEL_BG,
)
from app.presentation.views.album.helpers.data.state import AlbumState
from app.presentation.views.album.helpers.ui.interactions import (
    album_navigate_next,
    album_navigate_prev,
    handle_toggle_favorite,
    on_photo_select,
)
from app.presentation.views.helpers.ui.builder import (
    build_listbox_pagination,
    build_preview_panel,
)
from app.presentation.views.helpers.ui.interactions import handle_rate
from app.presentation.views.helpers.ui.preview import reset_preview
from app.presentation.views.profile.author import open_author_profile
from app.presentation.widgets.helpers.button import make_button
from app.presentation.widgets.helpers.images import load_image
from app.presentation.widgets.photo_listbox import PhotoListboxWidget

# ── Layout constants ──────────────────────────────────────────────────────────
_WIN_W = 1100
_WIN_H = 620
_HEADER_H = 70
_LEFT_W = 280
_BG = PAGE_BG
_PANEL_BG = PANEL_BG
_LIST_BG = LIST_BG
_BTN_BG = BTN_BG
_BTN_FG = BTN_FG
_HEADER_FG = HEADER_FG
_ICON_DIR = "app/assets/images/UI_Icons/"


def build_header(win: tk.Toplevel, state: AlbumState) -> None:
    """Build the album header row: album name only.

    Args:
        win: The album toplevel window.
        state: Album view state containing album data.
    """
    album = state.album or {}

    header = tk.Frame(win, bg=_LIST_BG, height=_HEADER_H)
    header.pack(fill="x")
    header.pack_propagate(False)

    album_name = album.get("name", "Album")
    tk.Label(
        header,
        text=album_name,
        font=quickSandBold(16),
        bg=_LIST_BG,
        fg=_HEADER_FG,
        anchor="w",
    ).pack(side="left", padx=(18, 10), pady=10)


def build_body(
    win: tk.Toplevel,
    state: AlbumState,
    default_photo_id: Optional[int] = None,
) -> None:
    """Build the main body containing the photo listbox and preview panel.

    Args:
        win: The album toplevel window.
        state: Album view state.
        default_photo_id: Photo ID to pre-select in the listbox.
    """
    body = tk.Frame(win, bg=_BG)
    body.pack(fill="both", expand=True)

    _build_left_panel(body, state, default_photo_id)
    _build_preview_panel(body, state)


def _build_left_panel(
    body: tk.Frame,
    state: AlbumState,
    default_photo_id: Optional[int],
) -> None:
    """Build the left panel: photo listbox + Add-to-Favorites button."""
    left = tk.Frame(body, bg=_LIST_BG, width=_LEFT_W)
    left.pack(side="left", fill="y")
    left.pack_propagate(False)

    # Listbox (shrunk slightly to make room for the pagination row)
    _PAG_ROW_H = 34
    listbox_h = (
        _WIN_H - _HEADER_H - 56 - _PAG_ROW_H
    )  # reserve room for fav btn + pagination
    photo_listbox = PhotoListboxWidget(
        left,
        photos=state.photos,
        on_select=lambda idx: on_photo_select(idx, state),
        selected_photo_id=default_photo_id,
        width=_LEFT_W,
        height=listbox_h,
        bg=_LIST_BG,
        fg=colors["primary-50"],
        select_bg=_PANEL_BG,
        select_fg=colors["primary-50"],
    )
    photo_listbox.pack(fill="both", expand=True)
    state.listbox_widget = photo_listbox

    if not state.photos:
        reset_preview(state, "No photos in this album")

    # ── Listbox pagination row ────────────────────────────────────────
    build_listbox_pagination(
        left,
        state,
        on_page_changed=lambda: reset_preview(state, "Select a photo"),
        bg=_LIST_BG,
        btn_bg=_BTN_BG,
        btn_fg=_BTN_FG,
        text_fg=colors["primary-50"],
    )

    # ── Favorite button (matches Add-Comment button style) ────────────
    fav_label = (
        "  \u2605 Remove from Favorites"
        if state.is_favorite
        else "  \u2606 Add to Favorites"
    )
    fav_icon_ref = load_image(
        f"{_ICON_DIR}Favorite_Icon.png",
        size=(20, 20),
    )
    fav_btn = make_button(
        left,
        fav_label,
        icon=fav_icon_ref,
        cmd=lambda: handle_toggle_favorite(state, body),
        font=quickSandBold(12),
        bg=_BTN_BG,
        fg=_BTN_FG,
        activebackground=colors["accent-500"],
        activeforeground=_BTN_FG,
        borderwidth=0,
        highlightthickness=0,
        cursor="hand2",
        padx=16,
        pady=8,
    )
    fav_btn.pack(fill="x", padx=10, pady=(4, 10))
    fav_btn.image = fav_icon_ref  # type: ignore[attr-defined]
    state.favorite_btn = fav_btn


def _build_preview_panel(body: tk.Frame, state: AlbumState) -> None:
    """Build the right preview panel via the global build_preview_panel helper."""
    panel_h = _WIN_H - _HEADER_H

    build_preview_panel(
        body,
        state,
        title="Album Preview",
        subtitle=(
            "Select a photo on the left"
            "  \u2022  Click the username to view the author's profile \u2022  Hover over the stars to rate the photo"
        ),
        show_buttons=False,
        on_prev=lambda: album_navigate_prev(state),
        on_next=lambda: album_navigate_next(state),
        on_username_click=lambda: open_author_profile(state),
        on_rate=lambda v: handle_rate(state, v, body),
        x_pos=_LEFT_W,
        width=_WIN_W - _LEFT_W,
        height=panel_h,
    )
