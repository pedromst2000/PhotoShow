from typing import Optional

from app.core.state.session import session
from app.presentation.views.profile.helpers.data.favorites_data import (
    load_user_favorites,
)
from app.presentation.views.profile.helpers.data.favorites_state import FavoritesState
from app.presentation.views.profile.helpers.ui.favorites_builder import (
    _WIN_H,
    _WIN_W,
    build_favorites_body,
    build_favorites_header,
)
from app.presentation.views.profile.helpers.ui.favorites_interactions import (
    sync_favorites_on_focus,
)
from app.presentation.widgets.window import create_toplevel


def favoritesProfileWindow(
    is_own: bool = True,
    username: Optional[str] = None,
    user_id: Optional[int] = None,
) -> None:
    """Display the Favorites Albums profile window.

    Shows a three-column layout (favorites list | photo list | preview) when
    the profile owner has favorites, or a contextual empty state otherwise.

    Args:
        is_own: True when the logged-in user is viewing their own favorites.
        username: Display name of the profile owner (used in visitor messages
                  when ``is_own`` is False).
        user_id: ID of the profile owner.  Defaults to the session user when
                 ``is_own`` is True and *user_id* is not supplied.
    """
    effective_user_id: Optional[int] = user_id
    if effective_user_id is None and is_own:
        effective_user_id = session.user_id

    title_suffix = f" \u2014 {username}" if (username and not is_own) else ""
    win = create_toplevel(
        title=f"\u2728 Favorites{title_suffix}",
        width=_WIN_W,
        height=_WIN_H,
        icon_path="app/assets/PhotoShowIcon.ico",
        bg_color="white",
    )

    state = FavoritesState()
    state.win = win
    state.is_own = is_own
    state.username = username
    state.user_id = effective_user_id

    load_user_favorites(state)

    build_favorites_header(win, state)
    build_favorites_body(win, state)

    # Refresh the favorites list whenever the window regains focus so that
    # changes made in other windows (e.g. toggling a favorite from the album
    # details window) are automatically reflected.  A 250 ms debounce prevents
    # redundant DB queries when multiple <FocusIn> events fire in rapid succession.
    _after_id: list = [None]

    def _on_focus(e) -> None:  # type: ignore[type-arg]
        # Only sync when the OS activates this window (e.g. after an album-details
        # window closes).  <FocusIn> bubbles up from child widgets too, so we
        # filter those out: if the focus stayed inside this Toplevel we skip.
        try:
            if e.widget.winfo_toplevel() is win:
                return
        except Exception:
            pass
        if _after_id[0] is not None:
            win.after_cancel(_after_id[0])
        _after_id[0] = win.after(250, lambda: sync_favorites_on_focus(state))

    win.bind("<FocusIn>", _on_focus)

    win.grab_set()
