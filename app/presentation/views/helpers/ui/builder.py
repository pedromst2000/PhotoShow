import tkinter as tk
from typing import Callable, List, Optional

from app.presentation.styles.colors import colors
from app.presentation.views.helpers.ui.carousel import navigate_next, navigate_prev
from app.presentation.views.helpers.ui.interactions import handle_like, handle_rate
from app.presentation.widgets.preview_panel import PreviewPanelWidget

# Shared colour defaults - same across Explore, Album Details, Profile.
_DEFAULT_PANEL_BG = colors["secondary-300"]
_DEFAULT_BTN_BG = colors["accent-300"]
_DEFAULT_BTN_FG = colors["secondary-500"]
_DEFAULT_CANVAS_BG = colors["secondary-400"]


def build_preview_panel(
    parent: tk.Frame,
    state,
    *,
    title: str = "Preview",
    subtitle: Optional[str] = None,
    show_metadata: bool = True,
    on_prev=None,
    on_next=None,
    on_username_click=None,
    on_rate=None,
    extra_buttons: Optional[List[dict]] = None,
    x_pos: int = 545,
    width: int = 755,
    height: int = 674,
    panel_bg: Optional[str] = None,
    btn_bg: Optional[str] = None,
    btn_fg: Optional[str] = None,
    canvas_bg: Optional[str] = None,
) -> None:
    """
    Instantiate a PreviewPanelWidget with the supplied configuration.

    Centralises all PreviewPanelWidget creation so every view (Explore,
    Album, Profile, ...) shares the same construction path.

    Standard buttons (like, details, comments, report) are built automatically
    from *state* and *parent* - no need to repeat them in callers.  Pass
    ``extra_buttons`` only for view-specific actions (e.g. "See Album" in
    Explore).  Extra buttons are inserted between the "See Comments" and
    "Report Photo" buttons.

    Callback defaults (on_prev, on_next, on_username_click, on_rate) are
    supplied from standard helpers so callers only override when the view
    needs non-default behaviour (e.g. album listbox navigation).

    Args:
        parent: Parent frame (doubles as the ``body`` context for dialogs).
        state: Shared state object (BasePhotoState or any subclass).
        title: Panel heading text.
        subtitle: Optional secondary heading shown below the title.
        show_metadata: Whether to render the avatar/username/stars row.
        on_prev: Callback for "previous photo". Default: navigate_prev(state).
        on_next: Callback for "next photo". Default: navigate_next(state).
        on_username_click: Callback when username is clicked.
                           Default: open_author_profile(state).
        on_rate: Callback receiving chosen star value (int).
                 Default: handle_rate(state, v, parent).
        extra_buttons: Optional list of extra button config dicts inserted
                       between "See Comments" and "Report Photo".
        x_pos: X position of the panel within *parent*.
        width: Panel pixel width.
        height: Panel pixel height.
        panel_bg: Background colour override (default: secondary-300).
        btn_bg: Button background colour override (default: accent-300).
        btn_fg: Button foreground colour override (default: secondary-500).
        canvas_bg: Photo canvas background colour override (default: secondary-400).
    """
    # Lazy cross-view imports - avoids circular dependencies at module load time.
    from app.presentation.views.comments.main import open_comments
    from app.presentation.views.helpers.ui.modals import open_report_dialog
    from app.presentation.views.photo.main import open_photo_details
    from app.presentation.views.profile.author import open_author_profile

    # Resolve callable defaults
    if on_prev is None:
        on_prev = lambda: navigate_prev(state)  # noqa: E731
    if on_next is None:
        on_next = lambda: navigate_next(state)  # noqa: E731
    if on_username_click is None:
        on_username_click = lambda: open_author_profile(state)  # noqa: E731
    if on_rate is None:
        on_rate = lambda v: handle_rate(state, v, parent)  # noqa: E731

    # Standard buttons present in every preview panel.
    # extra_buttons (view-specific) are slotted between comments and report.
    buttons: List[dict] = [
        {
            "name": "like_btn",
            "label": "  Add Like",
            "icon": "Like_Icon_V2.png",
            "unlike_icon": "Unlike_Icon_V2.png",
            "command": lambda: handle_like(state, parent),
        },
        {
            "name": "details_btn",
            "label": "  See Details",
            "icon": "Eye_Icon_V2.png",
            "command": lambda: open_photo_details(state),
        },
        {
            "name": "comments_btn",
            "label": "  See Comments",
            "icon": "Comment_Icon_V2.png",
            "command": lambda: open_comments(state),
        },
        *(extra_buttons or []),
        {
            "name": "report_btn",
            "label": "  Report Photo",
            "icon": "Report_Icon.png",
            "command": lambda: open_report_dialog(
                parent,
                photo_id=(
                    state.selected_photo.get("id") if state.selected_photo else None
                ),
            ),
        },
    ]

    PreviewPanelWidget(
        parent,
        state,
        title=title,
        subtitle=subtitle,
        show_metadata=show_metadata,
        on_prev=on_prev,
        on_next=on_next,
        on_username_click=on_username_click,
        on_rate=on_rate,
        buttons=buttons,
        x_pos=x_pos,
        width=width,
        height=height,
        panel_bg=panel_bg or _DEFAULT_PANEL_BG,
        btn_bg=btn_bg or _DEFAULT_BTN_BG,
        btn_fg=btn_fg or _DEFAULT_BTN_FG,
        canvas_bg=canvas_bg or _DEFAULT_CANVAS_BG,
    )


def build_listbox_pagination(
    parent: tk.Frame,
    state,
    on_page_changed: Optional[Callable] = None,
    bg: str = colors["secondary-500"],
    btn_bg: str = colors["accent-300"],
    btn_fg: str = colors["secondary-500"],
    text_fg: str = colors["primary-50"],
) -> None:
    """Build a pagination row (← Prev / page-info / Next →) for any PhotoListboxWidget view.

    Wires a PaginationUIController to *state* and stores ``prev_page_btn``,
    ``next_page_btn``, and ``page_info_label`` on *state* so the controller
    can manage button states and the label text automatically.

    On every page change the function automatically:

    1. Fetches the new page via ``PaginationManager.get_paginated_items``.
    2. Resets ``state.selected_index`` to 0.
    3. Calls ``state.listbox_widget.refresh(state.photos)`` when the widget exists.
    4. Invokes the caller-supplied *on_page_changed* for any view-specific logic
       (e.g. resetting the preview panel).

    Args:
        parent: Frame into which the pagination row is packed.
        state: Any BasePhotoState subclass initialised via
               PaginationManager.initialize_pagination.
        on_page_changed: Optional no-arg callback for extra view-specific logic.
        bg: Row background colour. Default: secondary-500.
        btn_bg: Prev/Next button background colour. Default: accent-300.
        btn_fg: Prev/Next button foreground colour. Default: secondary-500.
        text_fg: Page-info label foreground colour. Default: primary-50.
    """
    # Lazy imports to avoid circular dependency chains at module load time.
    from app.controllers.ui.pagination_controller import PaginationUIController
    from app.presentation.styles.fonts import quickSandBold, quickSandRegular
    from app.presentation.views.helpers.data.pagination import PaginationManager

    pag_frame = tk.Frame(parent, bg=bg, height=34)
    pag_frame.pack(fill="x", padx=6, pady=(2, 4))
    pag_frame.pack_propagate(False)

    _btn_kw = dict(
        font=quickSandBold(9),
        bg=btn_bg,
        fg=btn_fg,
        activebackground=colors["accent-500"],
        activeforeground=btn_fg,
        borderwidth=0,
        highlightthickness=0,
        cursor="hand2",
        padx=8,
        pady=4,
    )

    prev_btn = tk.Button(
        pag_frame,
        text="\u2190 Prev",
        command=lambda: _ctrl.go_to_prev_page(),
        **_btn_kw,
    )
    prev_btn.pack(side="left")

    page_lbl = tk.Label(
        pag_frame,
        text=PaginationManager.get_page_info(state),
        font=quickSandRegular(9),
        bg=bg,
        fg=text_fg,
    )
    page_lbl.pack(side="left", expand=True)

    next_btn = tk.Button(
        pag_frame,
        text="Next \u2192",
        command=lambda: _ctrl.go_to_next_page(),
        **_btn_kw,
    )
    next_btn.pack(side="right")

    # Store refs so PaginationUIController can update them on page change.
    state.prev_page_btn = prev_btn
    state.next_page_btn = next_btn
    state.page_info_label = page_lbl

    def _internal_on_page_changed() -> None:
        state.photos = PaginationManager.get_paginated_items(state)
        state.selected_index = 0
        listbox = getattr(state, "listbox_widget", None)
        if listbox is not None:
            listbox.refresh(state.photos)
        if on_page_changed is not None:
            on_page_changed()

    _ctrl = PaginationUIController(state, on_page_changed=_internal_on_page_changed)
    state._pagination_ui_controller = _ctrl

    # Apply initial button enabled/disabled state.
    _ctrl._update_button_states(PaginationManager.get_total_pages(state))
