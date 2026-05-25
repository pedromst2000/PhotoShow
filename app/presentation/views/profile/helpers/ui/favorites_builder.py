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
    build_empty_state,
    build_listbox_pagination,
    build_preview_panel,
)
from app.presentation.views.helpers.ui.carousel import (
    listbox_navigate_next,
    listbox_navigate_prev,
)
from app.presentation.views.helpers.ui.preview import reset_preview
from app.presentation.views.profile.helpers.data.favorites_state import FavoritesState
from app.presentation.views.profile.helpers.ui.favorites_interactions import (
    _reset_photo_panel,
    on_fav_album_select,
    on_fav_photo_select,
    on_remove_favorite,
)
from app.presentation.widgets.helpers.button import make_button
from app.presentation.widgets.helpers.images import load_image
from app.presentation.widgets.listbox_widget import ListboxWidget
from app.presentation.widgets.photo_listbox import PhotoListboxWidget

# ── Layout constants ───────────────────────────────────────────────────────────
_WIN_W: int = 1150
_WIN_H: int = 620
_HEADER_H: int = 80
_LEFT_W: int = 240  # Favorites album list panel
_MIDDLE_W: int = 280  # Photo list panel
_RIGHT_W: int = _WIN_W - _LEFT_W - _MIDDLE_W  # Preview panel = 630

_BG = PAGE_BG
_LIST_BG = LIST_BG
_PANEL_BG = PANEL_BG
_BTN_BG = BTN_BG
_BTN_FG = BTN_FG
_HEADER_FG = HEADER_FG
_ICON_DIR = "app/assets/images/UI_Icons/"

_PAG_ROW_H = 34
_ACTION_ROW_H = 38
_NOTICE_H = 36  # Height of the static outdated-list notice row


def _album_label(album: dict) -> str:
    """
    Return the display label for a favorite album row.

    Args:
        album (dict): The album data.

    Returns:
        str: The display label for the album.
    """
    name = album.get("name") or f"Album {album.get('id', '?')}"
    creator = album.get("creator_username")
    if creator:
        return f"{name} \u2014 {creator}"
    return name


# ── Header ─────────────────────────────────────────────────────────────────────


def build_favorites_header(win: tk.Toplevel, state: FavoritesState) -> None:
    """Build the window header with a bold title and subtitle.

    Args:
        win: The favorites profile Toplevel window.
        state: Favorites state (used to adapt subtitle for owner vs. visitor).
    """
    header = tk.Frame(win, bg=_LIST_BG, height=_HEADER_H)
    header.pack(fill="x")
    header.pack_propagate(False)

    title = "My Favorites" if state.is_own else "Favorites"
    tk.Label(
        header,
        text=title,
        font=quickSandBold(16),
        bg=_LIST_BG,
        fg=_HEADER_FG,
        anchor="w",
    ).pack(side="left", padx=(18, 6), pady=(12, 2), anchor="n")

    subtitle = (
        "Albums you have marked as favorites."
        if state.is_own
        else "Browse this user's favorite albums."
    )
    tk.Label(
        header,
        text=subtitle,
        font=quickSandRegular(10),
        bg=_LIST_BG,
        fg=colors["primary-50"],
        anchor="w",
    ).pack(side="left", padx=(0, 10), pady=(18, 2), anchor="n")


# ── Body ───────────────────────────────────────────────────────────────────────


def build_favorites_body(win: tk.Toplevel, state: FavoritesState) -> None:
    """Build the main body frame, routing to empty-state or three-column UI.

    Stores ``state._empty_frame`` and ``state._content_frame`` so that
    interaction handlers can toggle between the two without reopening the window.

    Args:
        win: The favorites profile Toplevel.
        state: Favorites state populated with favorite album data.
    """
    body = tk.Frame(win, bg=_BG)
    body.pack(fill="both", expand=True)
    # Store so that focus-sync handler can call _rebuild_empty_or_content.
    state._body_frame = body  # type: ignore[attr-defined]

    # ── Empty state frame ─────────────────────────────────────────────────────
    empty_frame = tk.Frame(body, bg=_BG)
    state._empty_frame = empty_frame  # type: ignore[attr-defined]

    if state.is_own:
        build_empty_state(
            empty_frame,
            icon="\u2728",
            title="You haven't added any favorites yet",
            subtitle="Browse albums and add them to your favorites to see them here.",
            icon_rely=0.38,
            title_rely=0.52,
            subtitle_rely=0.61,
        )
    else:
        name = state.username or "This user"
        build_empty_state(
            empty_frame,
            icon="\u2728",
            title=f"{name} hasn't added any favorites yet",
            subtitle="Check back later to see their favorite albums.",
            icon_rely=0.38,
            title_rely=0.52,
            subtitle_rely=0.61,
        )

    # ── Content frame (three-column layout) ───────────────────────────────────
    content_frame = tk.Frame(body, bg=_BG)
    state._content_frame = content_frame  # type: ignore[attr-defined]

    _build_left_panel(content_frame, state, body)
    _build_middle_panel(content_frame, state)
    _build_right_panel(content_frame, state)

    # Show the appropriate frame based on whether favorites exist.
    has_favorites = bool(state.all_favorites)
    if has_favorites:
        content_frame.pack(fill="both", expand=True)
    else:
        empty_frame.pack(fill="both", expand=True)


# ── Left panel — favorites album listbox ──────────────────────────────────────


def _build_left_panel(
    body: tk.Frame,
    state: FavoritesState,
    parent_body: tk.Widget,
) -> None:
    """Build the left panel: Remove button + favorites listbox + pagination.

    Args:
        body: Three-column content frame.
        state: Favorites state.
        parent_body: Outer body used as dialog parent for modality.
    """
    left = tk.Frame(body, bg=_LIST_BG, width=_LEFT_W)
    left.pack(side="left", fill="y")
    left.pack_propagate(False)

    # ── Remove from Favorites button (above listbox) ──────────────────────────
    _build_remove_button(left, state, parent_body)

    # ── Static info notice (owner only) ─────────────────────────────────────
    if state.is_own:
        _build_outdated_notice(left)

    # ── Favorites album listbox ─────────────────────────────────────────────────
    listbox_h = (
        _WIN_H - _HEADER_H - _ACTION_ROW_H - _NOTICE_H - _PAG_ROW_H - 18
        if state.is_own
        else _WIN_H - _HEADER_H - _ACTION_ROW_H - _PAG_ROW_H - 18
    )
    album_listbox = ListboxWidget(
        left,
        items=state.album_list_state.photos,
        label_fn=_album_label,
        title="Favorite Albums",
        on_select=lambda idx: on_fav_album_select(idx, state),
        width=_LEFT_W,
        height=listbox_h,
        bg=_LIST_BG,
        fg=colors["primary-50"],
        select_bg=_PANEL_BG,
        select_fg=colors["primary-50"],
    )
    album_listbox.pack(fill="both", expand=True)
    state.album_listbox_widget = album_listbox
    state.album_list_state.listbox_widget = album_listbox  # type: ignore[assignment]

    # ── Pagination row (below listbox) ────────────────────────────────────────
    build_listbox_pagination(
        left,
        state.album_list_state,  # type: ignore[arg-type]
        on_page_changed=lambda: _on_album_page_changed(state),
        bg=_LIST_BG,
        btn_bg=_BTN_BG,
        btn_fg=_BTN_FG,
        text_fg=colors["primary-50"],
    )


def _build_remove_button(
    parent: tk.Frame,
    state: FavoritesState,
    body: tk.Widget,
) -> None:
    """Build the Remove from Favorites button above the album listbox.

    Disabled until an album is selected; shown only when ``is_own`` is True.

    Args:
        parent: The left panel frame.
        state: Favorites state.
        body: Outer body used as dialog/messagebox parent.
    """
    if not state.is_own:
        return

    del_icon = load_image(f"{_ICON_DIR}Remove_Icon.png", size=(16, 16))

    btn_row = tk.Frame(parent, bg=_LIST_BG, height=_ACTION_ROW_H)
    btn_row.pack(fill="x", padx=6, pady=(6, 4))
    btn_row.pack_propagate(False)

    remove_btn = make_button(
        btn_row,
        "  Remove Favorite",
        icon=del_icon,
        cmd=lambda: on_remove_favorite(state, body),
        state=tk.DISABLED,
        **DEL_BTN_STYLE,
    )
    remove_btn.pack(fill="x")
    remove_btn.image = del_icon  # type: ignore[attr-defined]
    state.remove_fav_btn = remove_btn


def _build_outdated_notice(parent: tk.Frame) -> None:
    """Build the static info notice above the album listbox.

    Always visible; informs the user that albums deleted by their owners are
    automatically removed from the favorites list, so some entries may be
    missing.

    Args:
        parent: The left panel frame.
    """
    notice_frame = tk.Frame(parent, bg=colors["danger-500"], height=_NOTICE_H)
    notice_frame.pack(fill="x")
    notice_frame.pack_propagate(False)

    tk.Label(
        notice_frame,
        text="\u26a0  List may be outdated if owners deleted their albums.",
        font=quickSandBold(8),
        bg=colors["danger-500"],
        fg="#FFFFFF",
        wraplength=_LEFT_W - 16,
        justify="left",
        anchor="w",
    ).pack(fill="x", padx=8, pady=6)


def _on_album_page_changed(state: FavoritesState) -> None:
    """Reset album selection and clear photo panel when album page changes."""
    state.selected_album = None
    state.album_list_state.selected_index = None
    _set_remove_btn_state(state, enabled=False)
    _reset_photo_panel(state, "Select an album")


def _set_remove_btn_state(state: FavoritesState, *, enabled: bool) -> None:
    """Enable or disable the Remove button (when one exists).

    Args:
        state: Favorites state carrying the button reference.
        enabled: True to enable, False to disable.
    """
    btn = state.remove_fav_btn
    if btn is not None:
        btn.config(state=tk.NORMAL if enabled else tk.DISABLED)


# ── Middle panel — photo listbox ───────────────────────────────────────────────


def _build_middle_panel(body: tk.Frame, state: FavoritesState) -> None:
    """Build the middle panel: photo listbox + pagination (no action buttons).

    Args:
        body: Three-column content frame.
        state: Favorites state.
    """
    middle = tk.Frame(body, bg=_LIST_BG, width=_MIDDLE_W)
    middle.pack(side="left", fill="y")
    middle.pack_propagate(False)

    # ── Photo listbox (no Add/Delete buttons — read-only window) ─────────────
    listbox_h = _WIN_H - _HEADER_H - _PAG_ROW_H - 8
    photo_listbox = PhotoListboxWidget(
        middle,
        photos=state.photos,
        on_select=lambda idx: on_fav_photo_select(idx, state),
        width=_MIDDLE_W,
        height=listbox_h,
        bg=_LIST_BG,
        fg=colors["primary-50"],
        select_bg=_PANEL_BG,
        select_fg=colors["primary-50"],
    )
    photo_listbox.pack(fill="both", expand=True)
    state.listbox_widget = photo_listbox

    # ── Photo pagination row (below listbox) ──────────────────────────────────
    build_listbox_pagination(
        middle,
        state,
        on_page_changed=lambda: _on_photo_page_changed(state),
        bg=_LIST_BG,
        btn_bg=_BTN_BG,
        btn_fg=_BTN_FG,
        text_fg=colors["primary-50"],
    )

    # Initial placeholder message.
    reset_preview(state, "Select an album")


def _on_photo_page_changed(state: FavoritesState) -> None:
    """Reset photo selection and preview when the photo page changes."""
    reset_preview(state, "Select a photo")


# ── Right panel — preview ──────────────────────────────────────────────────────


def _build_right_panel(body: tk.Frame, state: FavoritesState) -> None:
    """Build the right preview panel (display-only; no action buttons).

    Args:
        body: Three-column content frame.
        state: Favorites state.
    """
    panel_h = _WIN_H - _HEADER_H

    build_preview_panel(
        body,
        state,
        title="Photo Preview",
        subtitle=(
            "Select a favorite album  \u2022  then select a photo  \u2022  "
            "Photo details shown below"
        ),
        show_metadata=True,
        show_buttons=False,
        on_prev=lambda: listbox_navigate_prev(state),
        on_next=lambda: listbox_navigate_next(state),
        # Explicit no-op: prevents the default open_author_profile from being
        # applied, so clicking the avatar/username does nothing in this read-only
        # window (no nested profile navigation).
        on_username_click=lambda: None,
        on_rate=None,
        x_pos=_LEFT_W + _MIDDLE_W,
        width=_RIGHT_W,
        height=panel_h,
    )
