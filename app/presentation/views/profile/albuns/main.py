from typing import Optional

from app.core.state.session import session
from app.presentation.views.profile.helpers.data.album_profile_data import (
    load_user_albums,
)
from app.presentation.views.profile.helpers.data.album_profile_state import (
    AlbumProfileState,
)
from app.presentation.views.profile.helpers.ui.album_profile_builder import (
    _WIN_H,
    _WIN_W,
    build_albums_body,
    build_albums_header,
)
from app.presentation.widgets.window import create_toplevel


def albunsProfileWindow(
    is_own: bool = True,
    username: Optional[str] = None,
    user_id: Optional[int] = None,
) -> None:
    """Display the Albums profile window.

    Shows a three-column layout (album list | photo list | preview) when the
    profile owner has albums, or a contextual empty state otherwise.

    Args:
        is_own: True when the logged-in user is viewing their own albums.
        username: Display name of the profile owner (used in window title /
                  visitor messages when ``is_own`` is False).
        user_id: ID of the profile owner.  Defaults to the session user when
                 ``is_own`` is True and *user_id* is not supplied.
    """
    effective_user_id: Optional[int] = user_id
    if effective_user_id is None and is_own:
        effective_user_id = session.user_id

    title_suffix = f" \u2014 {username}" if (username and not is_own) else ""
    win = create_toplevel(
        title=f"\U0001f5c2 Albums{title_suffix}",
        width=_WIN_W,
        height=_WIN_H,
        icon_path="app/assets/PhotoShowIcon.ico",
        bg_color="white",
    )

    state = AlbumProfileState()
    state.win = win
    state.is_own = is_own
    state.user_id = effective_user_id

    load_user_albums(state)

    build_albums_header(win, state)
    build_albums_body(win, state)

    win.grab_set()
