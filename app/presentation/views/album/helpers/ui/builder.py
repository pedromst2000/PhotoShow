import tkinter as tk
from typing import Optional

from app.presentation.styles.colors import colors
from app.presentation.styles.fonts import quickSandBold, quickSandRegularUnderline
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
from app.presentation.widgets.helpers.button import on_enter as button_on_enter
from app.presentation.widgets.helpers.button import on_leave as button_on_leave
from app.presentation.widgets.helpers.images import load_image
from app.presentation.widgets.photo_listbox import PhotoListboxWidget

# ── Layout constants ──────────────────────────────────────────────────────────
_WIN_W = 1100
_WIN_H = 620
_HEADER_H = 70
_LEFT_W = 280
_BG = colors["primary-50"]
_PANEL_BG = colors["secondary-300"]
_LIST_BG = colors["secondary-500"]
_BTN_BG = colors["accent-300"]
_BTN_FG = colors["secondary-500"]
_HEADER_FG = colors["primary-50"]
_ICON_DIR = "app/assets/images/UI_Icons/"


def build_header(win: tk.Toplevel, state: AlbumState) -> None:
    """Build the album header row: album name, author link, and category badge.

    Args:
        win: The album toplevel window.
        state: Album view state containing album, creator, and avg_category.
    """
    album = state.album or {}
    creator = state.creator or {}

    header = tk.Frame(win, bg=_LIST_BG, height=_HEADER_H)
    header.pack(fill="x")
    header.pack_propagate(False)

    # Album name
    album_name = album.get("name", "Album")
    tk.Label(
        header,
        text=album_name,
        font=quickSandBold(16),
        bg=_LIST_BG,
        fg=_HEADER_FG,
        anchor="w",
    ).pack(side="left", padx=(18, 10), pady=10)

    # Divider
    tk.Label(
        header,
        text="|",
        font=quickSandBold(14),
        bg=_LIST_BG,
        fg=_PANEL_BG,
    ).pack(side="left", pady=10)

    # Author person-icon
    try:
        icon_canvas = tk.Canvas(
            header,
            width=24,
            height=24,
            bg=_LIST_BG,
            highlightthickness=0,
        )
        icon_canvas.pack(side="left", padx=(10, 4), pady=10)
        img = load_image(
            f"{_ICON_DIR}Username_Icon.png",
            size=(24, 24),
            canvas=icon_canvas,
            x=0,
            y=0,
        )
        icon_canvas.image = img  # type: ignore[attr-defined]
    except Exception:
        pass

    # Clickable username label
    username = creator.get("username", "Unknown")
    username_lbl = tk.Label(
        header,
        text=username,
        font=quickSandRegularUnderline(11),
        bg=_LIST_BG,
        fg=_HEADER_FG,
        cursor="hand2",
    )
    username_lbl.pack(side="left", padx=(0, 14), pady=10)
    username_lbl.bind(  # type: ignore[misc]
        "<Button-1>", lambda _e: open_author_profile(state)
    )

    # Category badge (only when an avg category is available)
    if state.avg_category:
        cat_frame = tk.Frame(header, bg=_BTN_BG, padx=8, pady=4)
        cat_frame.pack(side="left", pady=10)
        state.header_category_lbl = tk.Label(
            cat_frame,
            text=state.avg_category,
            font=quickSandBold(10),
            bg=_BTN_BG,
            fg=_BTN_FG,
        )
        state.header_category_lbl.pack()


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
    fav_btn = tk.Button(
        left,
        text=fav_label,
        image=fav_icon_ref,
        compound=tk.LEFT,
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
        command=lambda: handle_toggle_favorite(state, body),
    )
    fav_btn.pack(fill="x", padx=10, pady=(4, 10))
    fav_btn.image = fav_icon_ref  # type: ignore[attr-defined]
    fav_btn.bind("<Enter>", lambda e: button_on_enter(e, fav_btn))
    fav_btn.bind("<Leave>", lambda e: button_on_leave(e, fav_btn))
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
            "  \u2022  Click the username to view the author's profile"
        ),
        on_prev=lambda: album_navigate_prev(state),
        on_next=lambda: album_navigate_next(state),
        on_username_click=lambda: open_author_profile(state),
        on_rate=lambda v: handle_rate(state, v, body),
        x_pos=_LEFT_W,
        width=_WIN_W - _LEFT_W,
        height=panel_h,
    )
