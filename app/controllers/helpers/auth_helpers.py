from app.core.state.session import session


def get_post_login_destination() -> str:
    """
    Determine the view destination after a successful login.

    Routes blocked users to a restricted view, normal users to home.
    This keeps routing decision logic separate from controllers while
    avoiding circular imports in the presentation layer.

    Returns:
        str: 'home_banned' when the user is blocked, otherwise 'home'.
    """
    return "home_banned" if session.is_blocked else "home"
