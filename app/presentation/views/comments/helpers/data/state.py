from app.presentation.views.helpers.data.state import BasePhotoState


class CommentsWindowState(BasePhotoState):
    """
    Pagination and UI state for the comments window.

    Wraps the parent view's state (ExploreState, AlbumState, etc.) so that:

    * ``selected_photo`` delegates to the parent — the comments window never
      owns which photo is selected, the calling view does.
    * ``comments_label`` delegates to the parent — keeps the explore/album
      panel counter in sync when comments are added or deleted.
    * All pagination fields (``current_page``, ``items_per_page``,
      ``data_provider``, ``total_items``, ``photos``, pagination buttons, …)
      are owned by this instance and managed by PaginationManager /
      PaginationUIController like any other paginated view.
    * ``list_canvas``, ``list_frame``, ``win``, ``img_refs``, and
      ``card_img_refs`` are stored here so that on_page_changed callbacks and
      load_and_render can access them without extra parameters.

    Args:
        parent_state: The state object from the calling view.
    """

    def __init__(self, parent_state: BasePhotoState) -> None:
        # Store parent BEFORE super().__init__() so that property setters
        # that fire during __init__ (e.g. comments_label = None) can safely
        # delegate without raising AttributeError.
        self._parent_state = parent_state
        super().__init__()

        # UI refs populated by open_comments after widgets are built.
        self.list_canvas = None
        self.list_frame = None
        self.img_refs: list = []
        self.card_img_refs: list = []

    # ------------------------------------------------------------------
    # Delegated properties
    # ------------------------------------------------------------------

    @property
    def selected_photo(self):
        """Delegate to the parent state - the photo being commented on."""
        return self._parent_state.selected_photo

    @property
    def comments_label(self):
        """Read the parent panel's comment-count label."""
        return self._parent_state.comments_label

    @comments_label.setter
    def comments_label(self, val) -> None:
        """Route label updates to the parent panel.

        ``None`` assignments (emitted by ``BasePhotoState.__init__``) are
        silently ignored so the parent's already-configured label is not
        overwritten during our own ``__init__``.
        """
        if val is not None:
            self._parent_state.comments_label = val
