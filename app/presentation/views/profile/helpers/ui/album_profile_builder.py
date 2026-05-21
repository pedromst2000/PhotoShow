import tkinter as tk

from app.presentation.styles.button import ACTION_BTN_STYLE, DEL_BTN_STYLE
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
from app.presentation.views.profile.helpers.data.album_profile_state import (
    AlbumProfileState,
)
from app.presentation.views.profile.helpers.ui.album_profile_interactions import (
    _reset_photo_panel,
    _set_album_btns_state,
    on_add_album,
    on_add_photo,
    on_album_select,
    on_delete_album,
    on_delete_photo,
    on_edit_album,
    on_photo_select,
)
from app.presentation.widgets.helpers.button import make_button
from app.presentation.widgets.helpers.images import load_image
from app.presentation.widgets.listbox_widget import ListboxWidget
from app.presentation.widgets.photo_listbox import PhotoListboxWidget

# ── Layout constants ───────────────────────────────────────────────────────────
_WIN_W: int = 1150
_WIN_H: int = 620
_HEADER_H: int = 80
_LEFT_W: int = 240  # Album list panel
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


def _album_label(album: dict) -> str:
    """Return the display label for an album row."""
    return album.get("name") or f"Album {album.get('id', '?')}"


# ── Header ─────────────────────────────────────────────────────────────────────


def build_albums_header(win: tk.Toplevel, state: AlbumProfileState) -> None:
    """Build the window header with a bold title and subtitle.

    Args:
        win: The albums profile Toplevel window.
        state: Album profile state (used to conditionally show owner info).
    """
    header = tk.Frame(win, bg=_LIST_BG, height=_HEADER_H)
    header.pack(fill="x")
    header.pack_propagate(False)

    title = "My Albums" if state.is_own else "Albums"
    tk.Label(
        header,
        text=title,
        font=quickSandBold(16),
        bg=_LIST_BG,
        fg=_HEADER_FG,
        anchor="w",
    ).pack(side="left", padx=(18, 6), pady=(12, 2), anchor="n")

    subtitle = (
        "Create and manage your photo albums."
        if state.is_own
        else "Browse this user's photo albums."
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


def build_albums_body(
    win: tk.Toplevel,
    state: AlbumProfileState,
) -> None:
    """Build the main body frame, routing to empty-state or three-column UI.

    Stores ``state._empty_frame`` and ``state._content_frame`` so that
    interaction handlers can toggle between the two without reopening the window.

    Args:
        win: The albums profile Toplevel.
        state: Album profile state populated with album/photo data.
    """
    body = tk.Frame(win, bg=_BG)
    body.pack(fill="both", expand=True)

    # ── Empty state frame ─────────────────────────────────────────────────────
    empty_frame = tk.Frame(body, bg=_BG)
    state._empty_frame = empty_frame  # type: ignore[attr-defined]

    if state.is_own:
        build_empty_state(
            empty_frame,
            icon="\U0001f4f7",
            title="You don't have any albums yet",
            subtitle="Create your first album to start sharing your photos!",
            btn_text="  Add Album",
            btn_cmd=lambda: on_add_album(state, body),
            icon_rely=0.38,
            title_rely=0.52,
            subtitle_rely=0.61,
            btn_rely=0.73,
        )
    else:
        build_empty_state(
            empty_frame,
            icon="\U0001f4f7",
            title="This user doesn't have any albums yet",
            subtitle="Check back later to see their albums.",
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

    # Show the appropriate frame based on whether albums exist.
    has_albums = bool(state.all_albums)
    if has_albums:
        content_frame.pack(fill="both", expand=True)
    else:
        empty_frame.pack(fill="both", expand=True)


# ── Left panel — album listbox ─────────────────────────────────────────────────


def _build_left_panel(
    body: tk.Frame,
    state: AlbumProfileState,
    parent_body: tk.Widget,
) -> None:
    """Build the left panel: album management buttons + album listbox + pagination.

    Args:
        body: Three-column content frame.
        state: Album profile state.
        parent_body: Outer body used as dialog parent for modality.
    """
    left = tk.Frame(body, bg=_LIST_BG, width=_LEFT_W)
    left.pack(side="left", fill="y")
    left.pack_propagate(False)

    # ── Album management buttons (above listbox) ──────────────────────────────
    _build_album_action_buttons(left, state, parent_body)

    # ── Album listbox ─────────────────────────────────────────────────────────
    listbox_h = _WIN_H - _HEADER_H - _ACTION_ROW_H * 3 - _PAG_ROW_H - 12
    album_listbox = ListboxWidget(
        left,
        items=state.album_list_state.photos,
        label_fn=_album_label,
        title="Albums",
        on_select=lambda idx: on_album_select(idx, state),
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


def _build_album_action_buttons(
    parent: tk.Frame,
    state: AlbumProfileState,
    body: tk.Widget,
) -> None:
    """Build Add / Edit / Delete album buttons above the album listbox.

    Edit and Delete are initially disabled until an album is selected.

    Args:
        parent: The left panel frame.
        state: Album profile state.
        body: Outer body used as dialog/messagebox parent.
    """
    if not state.is_own:
        return

    # Load icons once; store on state to prevent GC.
    add_icon = load_image(f"{_ICON_DIR}Add_Icon.png", size=(16, 16))
    edit_icon = load_image(f"{_ICON_DIR}Edit_Icon.png", size=(16, 16))
    del_icon = load_image(f"{_ICON_DIR}Remove_Icon.png", size=(16, 16))

    btn_row1 = tk.Frame(parent, bg=_LIST_BG, height=_ACTION_ROW_H)
    btn_row1.pack(fill="x", padx=6, pady=(6, 2))
    btn_row1.pack_propagate(False)

    add_btn = make_button(
        btn_row1,
        "  Add Album",
        icon=add_icon,
        cmd=lambda: on_add_album(state, body),
        **ACTION_BTN_STYLE,
    )
    add_btn.pack(fill="x")
    add_btn.image = add_icon  # type: ignore[attr-defined]

    btn_row2 = tk.Frame(parent, bg=_LIST_BG, height=_ACTION_ROW_H)
    btn_row2.pack(fill="x", padx=6, pady=(0, 2))
    btn_row2.pack_propagate(False)

    edit_btn = make_button(
        btn_row2,
        "  Edit Name",
        icon=edit_icon,
        cmd=lambda: on_edit_album(state, body),
        state=tk.DISABLED,
        **ACTION_BTN_STYLE,
    )
    edit_btn.pack(fill="x")
    edit_btn.image = edit_icon  # type: ignore[attr-defined]
    state.edit_album_btn = edit_btn

    btn_row3 = tk.Frame(parent, bg=_LIST_BG, height=_ACTION_ROW_H)
    btn_row3.pack(fill="x", padx=6, pady=(0, 4))
    btn_row3.pack_propagate(False)

    del_btn = make_button(
        btn_row3,
        "  Delete Album",
        icon=del_icon,
        cmd=lambda: on_delete_album(state, body),
        state=tk.DISABLED,
        **DEL_BTN_STYLE,
    )
    del_btn.pack(fill="x")
    del_btn.image = del_icon  # type: ignore[attr-defined]
    state.delete_album_btn = del_btn


def _on_album_page_changed(state: AlbumProfileState) -> None:
    """Reset album selection and clear photo panel when page changes."""
    state.selected_album = None
    state.album_list_state.selected_index = None
    _set_album_btns_state(state, enabled=False)
    _reset_photo_panel(state, "Select an album")


# ── Middle panel — photo listbox ───────────────────────────────────────────────


def _build_middle_panel(body: tk.Frame, state: AlbumProfileState) -> None:
    """Build the middle panel: delete-photo button + photo listbox + pagination.

    Args:
        body: Three-column content frame.
        state: Album profile state.
    """
    middle = tk.Frame(body, bg=_LIST_BG, width=_MIDDLE_W)
    middle.pack(side="left", fill="y")
    middle.pack_propagate(False)

    # ── Add Photo + Delete Photo buttons (above listbox) ─────────────────────
    if state.is_own:
        add_photo_icon = load_image(f"{_ICON_DIR}Add_Icon.png", size=(16, 16))
        del_photo_icon = load_image(f"{_ICON_DIR}Remove_Icon.png", size=(16, 16))

        btn_row_add = tk.Frame(middle, bg=_LIST_BG, height=_ACTION_ROW_H)
        btn_row_add.pack(fill="x", padx=6, pady=(6, 2))
        btn_row_add.pack_propagate(False)

        add_photo_btn = make_button(
            btn_row_add,
            "  Add Photo",
            icon=add_photo_icon,
            cmd=lambda: on_add_photo(state, middle),
            **ACTION_BTN_STYLE,
        )
        add_photo_btn.pack(fill="x")
        add_photo_btn.image = add_photo_icon  # type: ignore[attr-defined]

        btn_row = tk.Frame(middle, bg=_LIST_BG, height=_ACTION_ROW_H)
        btn_row.pack(fill="x", padx=6, pady=(0, 4))
        btn_row.pack_propagate(False)

        del_photo_btn = make_button(
            btn_row,
            "  Delete Photo",
            icon=del_photo_icon,
            cmd=lambda: on_delete_photo(state, middle),
            state=tk.DISABLED,
            **DEL_BTN_STYLE,
        )
        del_photo_btn.pack(fill="x")
        del_photo_btn.image = del_photo_icon  # type: ignore[attr-defined]
        state.delete_photo_btn = del_photo_btn

    # ── Photo listbox ─────────────────────────────────────────────────────────
    extra_h = ((_ACTION_ROW_H + 6) * 2 + 10) if state.is_own else 0
    listbox_h = _WIN_H - _HEADER_H - extra_h - _PAG_ROW_H - 8
    photo_listbox = PhotoListboxWidget(
        middle,
        photos=state.photos,
        on_select=lambda idx: on_photo_select(idx, state),
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

    # Initial empty state message.
    reset_preview(state, "Select an album")


def _on_photo_page_changed(state: AlbumProfileState) -> None:
    """Reset photo selection and preview when the photo page changes."""
    reset_preview(state, "Select a photo")
    if state.delete_photo_btn is not None:
        state.delete_photo_btn.config(state=tk.DISABLED)


# ── Right panel — preview ──────────────────────────────────────────────────────


def _build_right_panel(body: tk.Frame, state: AlbumProfileState) -> None:
    """Build the right preview panel (metadata-only, no action buttons).

    Args:
        body: Three-column content frame.
        state: Album profile state.
    """
    panel_h = _WIN_H - _HEADER_H

    build_preview_panel(
        body,
        state,
        title="Photo Preview",
        subtitle=(
            "Select an album  \u2022  then select a photo  \u2022  "
            "Hover over the stars to rate"
        ),
        show_metadata=True,
        show_buttons=False,
        on_prev=lambda: listbox_navigate_prev(state),
        on_next=lambda: listbox_navigate_next(state),
        on_username_click=None,
        on_rate=None,
        x_pos=_LEFT_W + _MIDDLE_W,
        width=_RIGHT_W,
        height=panel_h,
    )
