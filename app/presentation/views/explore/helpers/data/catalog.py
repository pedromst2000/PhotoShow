from app.controllers.explore_controller import ExploreController
from app.core.services.photo_service import PhotoService
from app.presentation.views.explore.helpers.data.pagination import PaginationManager
from app.presentation.views.explore.helpers.data.state import ExploreState
from app.presentation.views.explore.helpers.ui.preview import reset_preview

# Mapping from OptionMenu display label → sort_by key understood by the controller
SORT_OPTIONS = {
    "Most Recent": "date",
    "Most Liked": "likes",
    "Highest Rated": "rating",
    "Most Commented": "comments",
}

MIN_UNSIGNED_LIKES = 1  # minimum likes for unsigned users (show popular content)
MIN_UNSIGNED_COMMENTS = 1  # minimum comments for unsigned users (show engaging content)
MAX_UNSIGNED_PHOTOS = 5  # max photos to display for unsigned users

# Store current filter state for lazy loading
_current_filters = {
    "sort_by": "date",
    "category": "all",
    "author": None,
    "is_unsigned": False,
}

# Cache sorted catalog to avoid reloading on every page navigation
# Key: (sort_by, category, username) tuple; Value: sorted list of all photos
_catalog_cache = {}
_cache_key = None  # Track current cache key for invalidation


def _get_catalog_cache_key(sort_by: str, category: str, username: str = None) -> tuple:
    """
    Generate cache key for sorted catalog.

    Args:
        sort_by: Sorting criterion (e.g., "date", "likes")
        category: Photo category filter (e.g., "nature", "people")
        username: Author filter (optional)
    Returns:
        tuple: Tuple key for caching sorted catalog
    """
    return (sort_by, category, username)


def _get_filtered_photos(
    sort_key: str, category: str, author: str, is_unsigned: bool
) -> list:
    """
    Fetch and filter photos once, with caching.
    For unsigned users, applies engagement filter (3+ likes AND 3+ comments).

    Args:
        sort_key: Sort criterion
        category: Category filter
        author: Author filter
        is_unsigned: Whether to apply unsigned user filters

    Returns:
        List of filtered photos (already sorted)
    """
    global _cache_key

    # Generate cache key for this query
    current_key = _get_catalog_cache_key(sort_key, category, author)

    # Load catalog from cache OR fetch it once and cache
    if _cache_key != current_key or current_key not in _catalog_cache:
        # Cache miss: fetch and sort the full catalog ONCE (expensive operation)
        all_filtered = PhotoService.get_explore_catalog(
            sort_by=sort_key,
            category=category,
            username=author,
            user_id=None,
        )
        _catalog_cache[current_key] = all_filtered
        _cache_key = current_key
    else:
        # Cache hit: reuse sorted catalog WITHOUT reloading
        all_filtered = _catalog_cache[current_key]

    # Apply unsigned user filter if needed
    if is_unsigned:
        # For unsigned users: sort ALL photos by engagement (likes + comments) descending
        # and take only top 5 most liked/commented photos
        all_filtered.sort(
            key=lambda p: (p.get("likes", 0) + p.get("comments", 0)), reverse=True
        )
        all_filtered = all_filtered[:MAX_UNSIGNED_PHOTOS]  # Keep only top 5

    return all_filtered


def _get_page_data(state: ExploreState, page_num: int) -> list:
    """
    Data provider function for lazy loading.
    Fetches a single page from the pre-filtered catalog.

    Args:
        state: ExploreState object
        page_num: Page number (1-based)

    Returns:
        List of photo items for the requested page (10 or fewer)
    """
    # Get filter state from globals
    sort_key = _current_filters["sort_by"]
    category = _current_filters["category"]
    author = _current_filters["author"]
    is_unsigned = _current_filters["is_unsigned"]

    # Get all filtered photos (cached)
    all_filtered = _get_filtered_photos(sort_key, category, author, is_unsigned)

    # Extract just the page slice (no re-sorting, no re-fetching)
    start_idx = (page_num - 1) * state.items_per_page
    end_idx = start_idx + state.items_per_page
    page_items = all_filtered[start_idx:end_idx]

    return page_items


def load_catalog(state: ExploreState):
    """
    Setup lazy-loading pagination for the catalog with cache invalidation.

    Args:
        state (ExploreState): The current state of the Explore view.
    """
    global _cache_key

    # Get filter values from UI
    sort_key = "date"
    if state.sort_var and state.sort_var.get():
        sort_key = SORT_OPTIONS.get(state.sort_var.get(), "date")

    author = None
    if state.author_var:
        val = state.author_var.get().strip()
        author = val if val else None

    category = "all"
    if state.category_var and state.category_var.get():
        cat_val = state.category_var.get().strip()
        category = cat_val if cat_val and cat_val.lower() != "all" else "all"

    # CACHE INVALIDATION: if filters changed, clear cache
    old_filters = _current_filters.copy()

    # Store filter state for data provider
    _current_filters["sort_by"] = sort_key
    _current_filters["category"] = category
    _current_filters["author"] = author
    _current_filters["is_unsigned"] = state.is_unsigned

    # If any filter changed, invalidate the cache
    if old_filters != _current_filters:
        _cache_key = None
        _catalog_cache.clear()

    # All users see 10 items per page, except unsigned users see top 5 only
    effective_items_per_page = MAX_UNSIGNED_PHOTOS if state.is_unsigned else 10

    # Get ACTUAL COUNT of photos (for unsigned: count filtered photos, not all)
    if state.is_unsigned:
        # For unsigned users, fetch actual filtered list to count correctly
        all_filtered = _get_filtered_photos(
            sort_key, category, author, is_unsigned=True
        )
        total_count = len(all_filtered)
    else:
        # For regular/admin users, use the full count
        total_count = PhotoService.count_filtered_photos(
            category=category,
            username=author,
        )

    # Initialize pagination with lazy-loading data provider
    # Pages will be fetched on-demand via _get_page_data (WITH CACHING)
    def page_provider(page_num: int) -> list:
        return _get_page_data(state, page_num)

    # For unsigned users, total_count includes all photos but only top 5 will display
    # This is acceptable since count is just for page calculation
    PaginationManager.initialize_pagination(
        state,
        items_per_page=effective_items_per_page,
        data_provider=page_provider,
        total_items=total_count,
    )

    # Refresh UI through pagination controller if available
    if (
        hasattr(state, "_pagination_ui_controller")
        and state._pagination_ui_controller is not None
    ):
        try:
            state._pagination_ui_controller.refresh_ui()
        except Exception as e:
            print(f"Error refreshing UI: {e}")
            import traceback

            traceback.print_exc()
            reset_preview(state)
    else:
        # Fallback: just show empty message
        reset_preview(state)

    has_active_filters = bool(author) or category != "all"
    empty_message = (
        "No photos match the selected filters"
        if has_active_filters
        else "No photo selected"
    )
    if total_count == 0:
        reset_preview(state, carousel_message=empty_message)


def invalidate_catalog_cache():
    """
    Invalidate the entire catalog cache to force a reload on next pagination.

    Use this after photo deletion or other data mutations to ensure fresh data.
    """
    global _cache_key
    _cache_key = None
    _catalog_cache.clear()


def apply_filters(state: ExploreState):
    """
    Apply active filters and reload catalog.

    Args:
        state (ExploreState): The current state of the Explore view.
    """
    load_catalog(state)


def get_category_options() -> list:
    """
    Get available category options for filter dropdown.

    Returns:
        list: A list of available category options.
    """
    return ExploreController.get_categories()
