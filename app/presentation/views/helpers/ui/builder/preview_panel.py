import tkinter as tk
from typing import List, Optional

from app.presentation.styles.theme import BTN_BG, BTN_FG, CANVAS_BG, PANEL_BG
from app.presentation.views.helpers.ui.carousel import navigate_next, navigate_prev
from app.presentation.views.helpers.ui.interactions import handle_like, handle_rate
from app.presentation.widgets.preview_panel import PreviewPanelWidget

# Shared colour defaults - same across Explore, Album Details, Profile.
_DEFAULT_PANEL_BG = PANEL_BG
_DEFAULT_BTN_BG = BTN_BG
_DEFAULT_BTN_FG = BTN_FG
_DEFAULT_CANVAS_BG = CANVAS_BG


def build_preview_panel(
    parent: tk.Frame,
    state,
    *,
    title: str = "Preview",
    subtitle: Optional[str] = None,
    show_metadata: bool = True,
    show_buttons: bool = True,
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

    Args:
        parent: Parent frame (doubles as the ``body`` context for dialogs).
        state: Shared state object (BasePhotoState or any subclass).
        title: Panel heading text.
        subtitle: Optional secondary heading shown below the title.
        show_metadata: Whether to render the avatar/username/stars row.
        show_buttons: When False, no action buttons are rendered (e.g. album preview).
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
    from app.presentation.views.helpers.ui.modals import open_report_dialog
    from app.presentation.views.photo.main import open_photo_details
    from app.presentation.views.profile.author import open_author_profile

    if on_prev is None:
        on_prev = lambda: navigate_prev(state)  # noqa: E731
    if on_next is None:
        on_next = lambda: navigate_next(state)  # noqa: E731
    if on_username_click is None:
        on_username_click = lambda: open_author_profile(state)  # noqa: E731
    # Only apply the default rate handler when the panel has action buttons.
    # Passing on_rate=None with show_buttons=False signals a display-only panel.
    if on_rate is None and show_buttons:
        on_rate = lambda v: handle_rate(state, v, parent)  # noqa: E731

    # Standard buttons present in every preview panel.
    # extra_buttons (view-specific) are slotted between details and report.
    if show_buttons:
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
    else:
        buttons = []

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
