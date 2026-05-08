import tkinter as tk
from typing import Callable, Optional

from app.presentation.styles.colors import colors


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

    _ctrl = PaginationUIController(
        state,
        on_page_changed=_make_page_changed_handler(state, on_page_changed),
    )
    state._pagination_ui_controller = _ctrl

    # Apply initial button enabled/disabled state.
    _ctrl._update_button_states(PaginationManager.get_total_pages(state))


def _make_page_changed_handler(state, on_page_changed: Optional[Callable]):
    """Return a no-arg callable that refreshes the listbox on a page change.

    Extracted from build_listbox_pagination to avoid a nested function definition.

    Args:
        state: BasePhotoState subclass whose listbox_widget will be refreshed.
        on_page_changed: Optional extra callback supplied by the view.
    """
    from app.presentation.views.helpers.data.pagination import PaginationManager

    def _handler():
        """Refresh the listbox to show the new page's items, then call the view's on_page_changed."""
        state.photos = PaginationManager.get_paginated_items(state)
        state.selected_index = 0
        listbox = getattr(state, "listbox_widget", None)
        if listbox is not None:
            listbox.refresh(state.photos)
        if on_page_changed is not None:
            on_page_changed()

    return _handler
