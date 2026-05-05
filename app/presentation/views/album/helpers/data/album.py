from typing import Optional

from app.controllers.album_controller import AlbumController
from app.presentation.views.album.helpers.data.state import AlbumState
from app.presentation.views.helpers.data.pagination import PaginationManager
from app.utils.log_utils import log_exception

_ITEMS_PER_PAGE = 10


def load_album_data(
    state: AlbumState, album_id: int, default_photo_id: Optional[int] = None
) -> bool:
    """Populate *state* with enriched album data from the controller.

    Photos are captured in a closure (not stored on *state*) to match the
    catalog's no-persistent-state-cache pattern — only the current page slice
    lives in ``state.photos`` at any given time.

    Args:
        state: The AlbumState instance to populate.
        album_id: ID of the album to load.
        default_photo_id: Optional photo ID to pre-select in the listbox.
            The correct page is automatically navigated to if the photo is
            not on the first page.

    Returns:
        True if data loaded successfully, False otherwise.
    """
    try:
        details = AlbumController.get_album_details(album_id)
        if details is None:
            return False

        state.album = details["album"]
        state.creator = details["creator"]
        state.avg_category = details["avg_category"]
        state.is_favorite = details["is_favorite"]

        # Capture photos in a closure — never written back to state directly.
        all_photos = details["photos"]

        def page_provider(page_num: int) -> list:
            start = (page_num - 1) * _ITEMS_PER_PAGE
            return all_photos[start : start + _ITEMS_PER_PAGE]

        PaginationManager.initialize_pagination(
            state,
            items_per_page=_ITEMS_PER_PAGE,
            data_provider=page_provider,
            total_items=len(all_photos),
        )

        if all_photos:
            # Navigate to the page that contains default_photo_id (if given).
            target_page = 1
            local_index = 0
            if default_photo_id is not None:
                for global_idx, p in enumerate(all_photos):
                    if p.get("id") == default_photo_id:
                        target_page = (global_idx // _ITEMS_PER_PAGE) + 1
                        local_index = global_idx % _ITEMS_PER_PAGE
                        break
            state.current_page = target_page
            state.photos = PaginationManager.get_paginated_items(state)
            state.selected_index = local_index

        return True
    except Exception as e:
        log_exception("album.load_album_data", e, context={"album_id": album_id})
        return False
