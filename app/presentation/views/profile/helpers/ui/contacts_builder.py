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
    build_admin_window_body,
    build_admin_window_header,
    build_detail_placeholder,
    build_listbox_pagination,
    build_two_column_frames,
)
from app.presentation.views.helpers.ui.page_change import on_detail_page_changed
from app.presentation.views.profile.helpers.data.contacts_state import ContactsState
from app.presentation.views.profile.helpers.ui.contacts_interactions import (
    on_contact_select,
    on_resolve_contact,
)
from app.presentation.widgets.helpers.button import make_button
from app.presentation.widgets.helpers.images import load_image
from app.presentation.widgets.listbox_widget import ListboxWidget

# ── Layout constants ───────────────────────────────────────────────────────────
_WIN_W: int = 950
_WIN_H: int = 560
_HEADER_H: int = 80
_LEFT_W: int = 290  # Contact list panel
_RIGHT_W: int = _WIN_W - _LEFT_W  # Detail preview panel

_BG = PAGE_BG
_LIST_BG = LIST_BG
_PANEL_BG = PANEL_BG
_BTN_BG = BTN_BG
_BTN_FG = BTN_FG
_HEADER_FG = HEADER_FG
_ICON_DIR = "app/assets/images/UI_Icons/"

_PAG_ROW_H = 34
_ACTION_ROW_H = 38


def _contact_label(contact: dict) -> str:
    """Return the display label for a contact row.

    Args:
        contact: The contact data dict (must include ``username`` and ``title``).

    Returns:
        str: Display label in the form ``"{username} \u2014 {title}"``.
    """
    username = contact.get("username", "Unknown")
    title = contact.get("title", "Untitled")
    return f"{username} \u2014 {title}"


# ── Header ─────────────────────────────────────────────────────────────────────


def build_contacts_header(win: tk.Toplevel, state: ContactsState) -> None:
    """Build the window header with a bold title and descriptive subtitle.

    Args:
        win: The contacts Toplevel window.
        state: Contacts state (currently unused; reserved for future adaptation).
    """
    build_admin_window_header(
        win,
        title="Contacts",
        subtitle="Messages sent by users \u2014 select one to preview and resolve.",
    )


# ── Body ───────────────────────────────────────────────────────────────────────


def build_contacts_body(win: tk.Toplevel, state: ContactsState) -> None:
    """Build the main body, routing to the empty-state or two-column content UI.

    Stores ``state._empty_frame`` and ``state._content_frame`` so that
    interaction handlers can toggle between the two after resolving contacts.

    Args:
        win: The contacts Toplevel window.
        state: Contacts state with ``all_contacts`` already populated.
    """

    def _build_content(content_frame: tk.Frame, body: tk.Frame) -> None:
        left, right = build_two_column_frames(content_frame, _LEFT_W)
        _build_left_panel(left, state, body)
        _build_right_panel(right, state)

    build_admin_window_body(
        win,
        state,
        has_items=bool(state.all_contacts),
        empty_icon="\U0001f4ec",
        empty_title="No contact messages",
        empty_subtitle="Messages sent by users will appear here for review.",
        icon_rely=0.38,
        title_rely=0.52,
        subtitle_rely=0.61,
        build_content=_build_content,
    )


# ── Left panel ─────────────────────────────────────────────────────────────────


def _build_left_panel(left: tk.Frame, state: ContactsState, body: tk.Widget) -> None:
    """Build the left column: Resolve button + contacts listbox + pagination.

    Args:
        left: The left-column frame.
        state: Contacts state.
        body: Parent widget used to anchor dialogs in resolve callbacks.
    """
    _build_resolve_button(left, state, body)

    # Listbox height = available height minus header, action row, pagination row.
    listbox_h = _WIN_H - _HEADER_H - _ACTION_ROW_H - _PAG_ROW_H

    listbox = ListboxWidget(
        left,
        items=state.photos,
        label_fn=_contact_label,
        title="Contact Messages",
        on_select=lambda idx: on_contact_select(idx, state),
        width=_LEFT_W,
        height=listbox_h,
        bg=_LIST_BG,
        fg=colors["primary-50"],
        select_bg=_PANEL_BG,
        select_fg=colors["primary-50"],
    )
    listbox.pack(fill="x")
    state.listbox_widget = listbox

    build_listbox_pagination(
        left,
        state,
        on_page_changed=lambda: on_detail_page_changed(
            state, selected_attr="selected_contact", btn_attr="resolve_btn"
        ),
        bg=_LIST_BG,
        btn_bg=_BTN_BG,
        btn_fg=_BTN_FG,
        text_fg=colors["primary-50"],
    )


def _build_resolve_button(
    parent: tk.Frame, state: ContactsState, body: tk.Widget
) -> None:
    """Build the "Mark as Resolved" action button row.

    The button is initially disabled until the user selects a contact.

    Args:
        parent: The left-column frame.
        state: Contacts state; ``resolve_btn`` is set here.
        body: Parent widget used to anchor dialogs.
    """
    action_row = tk.Frame(parent, bg=_LIST_BG, height=_ACTION_ROW_H)
    action_row.pack(fill="x", padx=6, pady=(6, 4))
    action_row.pack_propagate(False)

    icon = load_image(f"{_ICON_DIR}Remove_Icon.png", size=(16, 16))

    btn = make_button(
        action_row,
        text="  Mark as Resolved",
        cmd=lambda: on_resolve_contact(state, body),
        icon=icon,
        **DEL_BTN_STYLE,
    )
    btn.config(state=tk.DISABLED)
    btn.pack(fill="x")

    btn.image = icon  # type: ignore[attr-defined]
    state.resolve_btn = btn


# ── Right panel ────────────────────────────────────────────────────────────────


def _build_right_panel(right: tk.Frame, state: ContactsState) -> None:
    """Build the contact detail preview panel on the right column.

    Displays a placeholder when no contact is selected and the full detail
    (author, title, message) once the user selects a contact.

    This is a non-reusable helper function; all widget refs are stored on
    *state* so ``contacts_interactions`` can update them without rebuilding.

    Args:
        right: The right-column frame.
        state: Contacts state; widget refs are set on this object.
    """
    build_detail_placeholder(
        right,
        state,
        icon="\U0001f4cb",
        title="Select a message to preview",
        subtitle="Click a contact from the list on the left.",
    )

    # ── Detail view (hidden until a contact is selected) ──────────────────────
    detail = tk.Frame(right, bg=_PANEL_BG)
    state._detail_frame = detail
    # (Not packed yet — revealed by _update_detail_panel)

    _build_detail_fields(detail, state)


def _build_detail_fields(detail: tk.Frame, state: ContactsState) -> None:
    """Populate the detail frame with labelled fields for author, title, message.

    Stores widget references on *state* so interaction handlers can update
    content without rebuilding the UI.

    Args:
        detail: The detail frame (child of the right panel).
        state: Contacts state; label refs are stored here.
    """
    pad_x = 24
    pad_top = 20

    # ── Section title ─────────────────────────────────────────────────────────
    tk.Label(
        detail,
        text="Contact Details",
        font=quickSandBold(16),
        bg=_PANEL_BG,
        fg=_HEADER_FG,
        anchor="w",
    ).pack(anchor="w", padx=pad_x, pady=(pad_top, 12))

    tk.Frame(detail, bg=colors["secondary-400"], height=1).pack(
        fill="x", padx=pad_x, pady=(0, 14)
    )

    # ── Author ────────────────────────────────────────────────────────────────
    _field_row(detail, label="From:", pad_x=pad_x)
    author_lbl = tk.Label(
        detail,
        text="",
        font=quickSandBold(13),
        bg=_PANEL_BG,
        fg=_HEADER_FG,
        anchor="w",
    )
    author_lbl.pack(anchor="w", padx=(pad_x + 8, pad_x), pady=(0, 10))
    state._author_label = author_lbl

    # ── Title ─────────────────────────────────────────────────────────────────
    _field_row(detail, label="Subject:", pad_x=pad_x)
    title_lbl = tk.Label(
        detail,
        text="",
        font=quickSandBold(13),
        bg=_PANEL_BG,
        fg=_HEADER_FG,
        anchor="w",
        wraplength=_RIGHT_W - pad_x * 2 - 12,
        justify="left",
    )
    title_lbl.pack(anchor="w", padx=(pad_x + 8, pad_x), pady=(0, 10))
    state._title_label = title_lbl

    # ── Message ───────────────────────────────────────────────────────────────
    _field_row(detail, label="Message:", pad_x=pad_x)

    msg_frame = tk.Frame(detail, bg=_PANEL_BG)
    msg_frame.pack(fill="both", expand=True, padx=pad_x, pady=(0, pad_top))

    msg_text = tk.Text(
        msg_frame,
        font=quickSandRegular(11),
        bg=colors["secondary-300"],
        fg=_HEADER_FG,
        relief="flat",
        borderwidth=0,
        highlightthickness=0,
        wrap="word",
        state=tk.DISABLED,
        padx=10,
        pady=8,
    )
    msg_text.pack(fill="both", expand=True)
    state._message_text = msg_text


def _field_row(parent: tk.Widget, *, label: str, pad_x: int) -> None:
    """Render a small muted field-name label (e.g. "From:", "Subject:").

    Args:
        parent: Parent widget to pack into.
        label: The field label text.
        pad_x: Horizontal padding.
    """
    tk.Label(
        parent,
        text=label,
        font=quickSandBold(10),
        bg=_PANEL_BG,
        fg=colors["secondary-400"],
        anchor="w",
    ).pack(anchor="w", padx=pad_x, pady=(0, 2))
