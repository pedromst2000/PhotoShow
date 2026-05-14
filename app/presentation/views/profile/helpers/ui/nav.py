import tkinter as tk

from app.presentation.styles.colors import colors
from app.presentation.styles.fonts import quickSandBold
from app.presentation.widgets.helpers.button import make_button


def build_profile_nav(
    window: tk.Toplevel,
    *,
    banner_height: int,
    nav_height: int,
    win_width: int,
    show_albuns: bool,
    show_favorites: bool,
    show_contacts: bool,
    show_reports: bool,
    own_profile: bool,
    username: str,
) -> None:
    """Build and place the horizontal navigation bar below the profile banner.

    Args:
        window: The profile Toplevel window.
        banner_height: Pixel height of the banner section.
        nav_height: Pixel height of the navigation bar.
        win_width: Full pixel width of the window.
        show_albuns: Whether to include the Albums button.
        show_favorites: Whether to include the Favorites button.
        show_contacts: Whether to include the Contacts button (admin only).
        show_reports: Whether to include the Reports button (admin only).
        own_profile: True when displaying the current user's own profile.
        username: Username of the profile owner (forwarded to sub-windows).
    """
    nav_frame = tk.Frame(window, bg=colors["accent-300"], height=nav_height)
    nav_frame.place(x=0, y=banner_height, width=win_width, height=nav_height)
    nav_frame.pack_propagate(False)

    _btn_style = dict(
        font=quickSandBold(13),
        bg=colors["accent-300"],
        fg=colors["secondary-500"],
        activebackground=colors["accent-100"],
        activeforeground=colors["secondary-500"],
        borderwidth=0,
        highlightthickness=0,
        cursor="hand2",
        padx=24,
        pady=10,
        relief=tk.FLAT,
    )

    def _make_nav_btn(text: str, cmd) -> None:
        make_button(nav_frame, text, cmd=cmd, **_btn_style).pack(side=tk.LEFT)

    if show_albuns:
        from app.presentation.views.profile.albuns import albunsProfileWindow

        _make_nav_btn(
            "Albums",
            lambda: albunsProfileWindow(is_own=own_profile, username=username),
        )

    if show_favorites:
        from app.presentation.views.profile.favorites import favoritesProfileWindow

        _make_nav_btn(
            "Favorites",
            lambda: favoritesProfileWindow(is_own=own_profile, username=username),
        )

    if show_contacts:
        from app.presentation.views.profile.contacts import contactsWindow

        _make_nav_btn("Contacts", lambda: contactsWindow())

    if show_reports:
        from app.presentation.views.profile.reports import reportsWindow

        _make_nav_btn("Reports", lambda: reportsWindow())
