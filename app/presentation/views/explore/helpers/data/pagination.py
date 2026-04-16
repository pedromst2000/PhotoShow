from typing import Callable, List

from app.presentation.views.explore.helpers.data.state import ExploreState


class PaginationManager:
    """
    Manages pagination UI state for the explore view using LAZY-LOADING ONLY.

    This class is responsible for:
    - Initializing pagination state in ExploreState
    - Fetching paginated items for the current page via data_provider
    - Navigating between pages (next/prev)
    """

    DEFAULT_ITEMS_PER_PAGE = 10

    @staticmethod
    def initialize_pagination(
        state: ExploreState,
        items_per_page: int = DEFAULT_ITEMS_PER_PAGE,
        data_provider: Callable[[int], List[dict]] = None,
        total_items: int = 0,
    ) -> None:
        """
        Initialize pagination state with lazy-loading.

        Args:
            state: ExploreState object
            items_per_page: Number of items per page (default: 10)
            data_provider: REQUIRED function(page_number) -> list of items for that page
                          Pages are fetched on-demand to avoid loading entire list in memory
            total_items: Total number of items across all pages
        """
        if data_provider is None:
            raise ValueError(
                "PaginationManager requires data_provider - lazy-loading only"
            )

        state.current_page = 1
        state.items_per_page = items_per_page
        state.selected_index = None
        state.data_provider = data_provider
        state.total_items = total_items
        state.photos = []  # Current page items only (populated on-demand)

    @staticmethod
    def get_paginated_items(state: ExploreState) -> list:
        """
        Get items for current page by calling data_provider.

        Args:
            state: ExploreState object

        Returns:
            list: Items for the current page fetched from data_provider
        """
        if state.data_provider is None:
            raise ValueError("data_provider not set - call initialize_pagination first")

        # Always fetch from provider - lazy-loading mode only
        items = state.data_provider(state.current_page)
        state.photos = items  # Update with current page items only
        return items

    @staticmethod
    def get_total_pages(state: ExploreState) -> int:
        """
        Get total number of pages.

        Args:
            state: ExploreState object

        Returns:
            int: Total number of pages based on total_items and items_per_page
        """
        if state.total_items == 0:
            return 1
        return (state.total_items + state.items_per_page - 1) // state.items_per_page

    @staticmethod
    def can_go_next(state: ExploreState) -> bool:
        """Check if next page exists.

        Args:
            state: ExploreState object

        Returns:
            bool: True if next page exists, False otherwise
        """
        return state.current_page < PaginationManager.get_total_pages(state)

    @staticmethod
    def can_go_prev(state: ExploreState) -> bool:
        """Check if previous page exists.

        Args:
            state: ExploreState object

        Returns:
            bool: True if previous page exists, False otherwise
        """
        return state.current_page > 1

    @staticmethod
    def go_to_next_page(state: ExploreState) -> bool:
        """
        Navigate to next page.

        Args:
            state: ExploreState object

        Returns:
            bool: True if navigation succeeded, False otherwise
        """
        if not PaginationManager.can_go_next(state):
            return False
        state.current_page += 1
        state.selected_index = None
        return True

    @staticmethod
    def go_to_prev_page(state: ExploreState) -> bool:
        """
        Navigate to previous page.

        Args:
            state: ExploreState object

        Returns:
            bool: True if navigation succeeded, False otherwise
        """
        if not PaginationManager.can_go_prev(state):
            return False
        state.current_page -= 1
        state.selected_index = None
        return True

    @staticmethod
    def get_page_info(state: ExploreState) -> str:
        """Get human-readable page info (e.g., 'Page 1/10').

        Args:
            state: ExploreState object

        Returns:
            str: Human-readable page info
        """
        total = PaginationManager.get_total_pages(state)
        return f"Page {state.current_page}/{total}"
