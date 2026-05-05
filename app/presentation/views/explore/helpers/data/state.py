import tkinter as tk
from typing import Optional

from app.presentation.views.helpers.data.state import BasePhotoState


class ExploreState(BasePhotoState):
    """
    Runtime state for the Explore view.

    Extends BasePhotoState with explore-specific filter-bar variables
    (author, category, sort) that are not needed by album or profile views.
    """

    def __init__(self) -> None:
        super().__init__()

        # Filter-bar tkinter vars (Explore-only)
        self.sort_var: Optional[tk.StringVar] = None
        self.author_var: Optional[tk.StringVar] = None
        self.category_var: Optional[tk.StringVar] = None
