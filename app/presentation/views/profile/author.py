from app.presentation.views.helpers.data.state import BasePhotoState
from app.presentation.views.profile.main import profileWindow


def open_author_profile(state: BasePhotoState) -> None:
    """
    Open the profile window of the photo's author.

    Delegates to ``profileWindow`` with the author's user_id.  If the author
    is the currently authenticated user their full management profile is shown;
    otherwise a visitor view (Albums + Favorites only) is displayed.

    Args:
        state: Any state that exposes ``selected_photo`` with a ``user_id`` key.
    """
    photo = state.selected_photo
    if photo is None:
        return
    author_id = photo.get("owner_id")
    profileWindow(user_id=author_id)
