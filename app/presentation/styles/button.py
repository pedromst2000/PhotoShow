import tkinter as tk

from app.presentation.styles.colors import colors
from app.presentation.styles.fonts import quickSandBold

# ── Shared base (colors, border, cursor — common to all action buttons) ────────
_BASE: dict = dict(
    bg=colors["accent-300"],
    fg=colors["secondary-500"],
    activebackground=colors["accent-100"],
    activeforeground=colors["secondary-500"],
    borderwidth=0,
    highlightthickness=0,
    cursor="hand2",
    relief=tk.FLAT,
)

# ── Small icon-action button (Add, Edit — panel toolbars) ─────────────────────
ACTION_BTN_STYLE: dict = {
    **_BASE,
    "font": quickSandBold(10),
    "padx": 8,
    "pady": 5,
    "compound": tk.LEFT,
}

# ── Destructive variant — Delete buttons ──────────────────────────────────────
DEL_BTN_STYLE: dict = {
    **ACTION_BTN_STYLE,
    "bg": colors["accent-300"],
    "fg": colors["secondary-500"],
    "activebackground": colors["accent-100"],
    "activeforeground": colors["secondary-500"],
}

# ── Larger primary action button (profile actions, dialogs) ───────────────────
PRIMARY_BTN_STYLE: dict = {
    **_BASE,
    "font": quickSandBold(13),
    "padx": 16,
    "pady": 8,
}

# ── Navigation tab button ─────────────────────────────────────────────────────
NAV_BTN_STYLE: dict = {
    **_BASE,
    "font": quickSandBold(13),
    "padx": 24,
    "pady": 10,
}

# ── Follow / Unfollow inline button ───────────────────────────────────────────
FOLLOW_BTN_STYLE: dict = {
    **_BASE,
    "font": quickSandBold(11),
    "padx": 10,
    "pady": 4,
}

# ── Medium action button (comments, dialogs) ──────────────────────────────────
MEDIUM_BTN_STYLE: dict = {
    **_BASE,
    "font": quickSandBold(12),
    "padx": 16,
    "pady": 8,
}

# ── Tiny card-action button (comment Report / Delete icons) ───────────────────
CARD_ACTION_BTN_STYLE: dict = {
    **_BASE,
    "font": quickSandBold(9),
}

# ── Auth / form submit button (login, register, change-password, banned notice)
AUTH_BTN_STYLE: dict = {
    **_BASE,
    "font": quickSandBold(13),
}

COMPACT_BTN_STYLE: dict = {
    **_BASE,
    "font": quickSandBold(12),
}

ICON_CENTER_BTN_STYLE: dict = {
    **_BASE,
    "font": quickSandBold(15),
    "compound": tk.CENTER,
}
