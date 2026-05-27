import tkinter as tk
from typing import Any, Callable, Optional

from app.presentation.styles.colors import colors
from app.presentation.styles.fonts import quickSandBold, quickSandRegular
from app.presentation.styles.theme import HEADER_FG, LIST_BG, PAGE_BG, PANEL_BG
from app.presentation.views.helpers.ui.builder.empty_state import build_empty_state


def build_admin_window_header(
    win: tk.Toplevel,
    *,
    title: str,
    subtitle: str = "",
    height: int = 80,
    bg: Optional[str] = None,
) -> None:
    """Build a standard bold-title + optional subtitle header bar.

    Used by all admin-style windows (Contacts, Reports, Albums-profile,
    Favorites, Album detail).  When *subtitle* is empty or omitted the
    title label is centred vertically with balanced padding instead.

    Args:
        win: The Toplevel window to attach the header to.
        title: Bold heading text (e.g. "Contacts", "Reports").
        subtitle: Smaller descriptive text shown to the right of the title.
                  Pass an empty string (default) to render title-only.
        height: Fixed header height in pixels (default 80).
        bg: Background colour (defaults to the ``LIST_BG`` theme constant).
    """
    _bg = bg or LIST_BG
    header = tk.Frame(win, bg=_bg, height=height)
    header.pack(fill="x")
    header.pack_propagate(False)

    title_pady = (12, 2) if subtitle else 10
    tk.Label(
        header,
        text=title,
        font=quickSandBold(16),
        bg=_bg,
        fg=HEADER_FG,
        anchor="w",
    ).pack(side="left", padx=(18, 6), pady=title_pady, anchor="n")

    if subtitle:
        tk.Label(
            header,
            text=subtitle,
            font=quickSandRegular(10),
            bg=_bg,
            fg=colors["primary-50"],
            anchor="w",
        ).pack(side="left", padx=(0, 10), pady=(18, 2), anchor="n")


def build_detail_placeholder(
    parent: tk.Frame,
    state: Any,
    *,
    icon: str,
    title: str,
    subtitle: str,
    bg: Optional[str] = None,
) -> None:
    """Build the "nothing selected" placeholder inside a detail panel.

    Creates a centred emoji + heading + description and stores the frame on
    ``state._placeholder_frame`` so interaction handlers can swap it for the
    detail frame later.

    Args:
        parent: Right-column frame to attach the placeholder to.
        state: View state; ``_placeholder_frame`` is set here.
        icon: Unicode emoji / character shown as a large glyph.
        title: Bold heading text.
        subtitle: Smaller hint text.
        bg: Background colour (defaults to ``PANEL_BG``).
    """
    _bg = bg or PANEL_BG
    placeholder = tk.Frame(parent, bg=_bg)
    placeholder.pack(fill="both", expand=True)
    state._placeholder_frame = placeholder

    tk.Label(
        placeholder,
        text=icon,
        font=quickSandBold(42),
        bg=_bg,
        fg=colors["secondary-400"],
    ).place(relx=0.5, rely=0.40, anchor=tk.CENTER)

    tk.Label(
        placeholder,
        text=title,
        font=quickSandBold(14),
        bg=_bg,
        fg=colors["secondary-500"],
    ).place(relx=0.5, rely=0.52, anchor=tk.CENTER)

    tk.Label(
        placeholder,
        text=subtitle,
        font=quickSandRegular(10),
        bg=_bg,
        fg=colors["secondary-400"],
    ).place(relx=0.5, rely=0.60, anchor=tk.CENTER)


def build_two_column_frames(
    parent: tk.Frame,
    left_w: int,
    *,
    list_bg: Optional[str] = None,
    panel_bg: Optional[str] = None,
) -> tuple[tk.Frame, tk.Frame]:
    """Create and pack the left and right column frames side-by-side.

    Both frames are packed into *parent* immediately so callers only need to
    populate them.

    Args:
        parent: Content frame that will contain both columns.
        left_w: Fixed pixel width of the left column.
        list_bg: Background colour for the left column (defaults to ``LIST_BG``).
        panel_bg: Background colour for the right column (defaults to ``PANEL_BG``).

    Returns:
        tuple[tk.Frame, tk.Frame]: ``(left, right)`` column frames.
    """
    _list_bg = list_bg or LIST_BG
    _panel_bg = panel_bg or PANEL_BG

    left = tk.Frame(parent, bg=_list_bg, width=left_w)
    left.pack(side="left", fill="y")
    left.pack_propagate(False)

    right = tk.Frame(parent, bg=_panel_bg)
    right.pack(side="left", fill="both", expand=True)

    return left, right


def build_admin_window_body(
    win: tk.Toplevel,
    state: Any,
    *,
    has_items: bool,
    empty_icon: str,
    empty_title: str,
    empty_subtitle: str,
    icon_rely: float = 0.38,
    title_rely: float = 0.52,
    subtitle_rely: float = 0.61,
    empty_btn_text: Optional[str] = None,
    empty_btn_cmd: Optional[Callable] = None,
    btn_rely: float = 0.76,
    bg: Optional[str] = None,
    build_content: Callable[[tk.Frame, tk.Frame], None],
) -> None:
    """Build the main body, toggling between empty-state and content layout.

    Sets up the body frame, empty-state frame, and content frame, then shows
    whichever is appropriate for the current data state.  Both frames are
    stored on *state* so ``toggle_empty_content_state`` can swap them later.

    *build_content* receives ``(content_frame, body)`` and is responsible for
    populating the content frame with whatever layout the window needs (two-
    column, three-column, etc.).

    Args:
        win: The Toplevel window to attach the body to.
        state: View state; ``_empty_frame``, ``_content_frame``, and
               ``_body_frame`` are set here.
        has_items: Whether the data source currently has any items to display.
        empty_icon: Unicode emoji shown in the empty state.
        empty_title: Bold heading text for the empty state.
        empty_subtitle: Descriptive text for the empty state.
        icon_rely: Relative Y position for the empty-state icon.
        title_rely: Relative Y position for the empty-state title.
        subtitle_rely: Relative Y position for the empty-state subtitle.
        empty_btn_text: Optional CTA button label for the empty state.
        empty_btn_cmd: Callback for the empty-state button.
        btn_rely: Relative Y position for the empty-state button.
        bg: Background colour for all frames (defaults to ``PAGE_BG``).
        build_content: Callable invoked when *has_items* is True, responsible
                       for populating *content_frame*.
    """
    _bg = bg or PAGE_BG
    body = tk.Frame(win, bg=_bg)
    body.pack(fill="both", expand=True)
    state._body_frame = body  # retained for dialog-parent access (e.g. favorites)

    # ── Empty state ───────────────────────────────────────────────────────────
    empty_frame = tk.Frame(body, bg=_bg)
    state._empty_frame = empty_frame
    build_empty_state(
        empty_frame,
        icon=empty_icon,
        title=empty_title,
        subtitle=empty_subtitle,
        btn_text=empty_btn_text,
        btn_cmd=empty_btn_cmd,
        icon_rely=icon_rely,
        title_rely=title_rely,
        subtitle_rely=subtitle_rely,
        btn_rely=btn_rely,
    )

    # ── Content frame ─────────────────────────────────────────────────────────
    content_frame = tk.Frame(body, bg=_bg)
    state._content_frame = content_frame

    if has_items:
        content_frame.pack(fill="both", expand=True)
        build_content(content_frame, body)
    else:
        empty_frame.pack(fill="both", expand=True)
