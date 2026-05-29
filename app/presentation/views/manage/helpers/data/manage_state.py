import tkinter as tk
import tkinter.ttk as ttk
from typing import List, Optional


class ManageState:
    """
    Runtime state for the admin Manage window.

    Holds all widget references and data needed by the builder and
    interaction handlers.  Widget refs are set by the builder during
    construction and updated by interactions in response to user actions.

    Attribute overview
    ------------------
    win                     The Toplevel window.

    Data
    ----
    all_users               Full list of manageable user dicts (non-admin).
    all_categories          Full list of category dicts (id + category).

    Filter / action vars (tkinter StringVars)
    -----------------------------------------
    username_var            Bound to the username filter entry.
    email_var               Bound to the email filter entry.
    role_var                Bound to the role filter OptionMenu.
    change_role_var         Bound to the "Set Role" action OptionMenu.
    status_var              Bound to the "Set Status" action OptionMenu.

    Selection state
    ---------------
    selected_username       Username of the currently selected treeview row.
    selected_category_id    ID of the currently selected category in the listbox.
    selected_category_name  Name of the currently selected category.

    Widget refs (users left panel)
    -------------------------------
    tree                    ttk.Treeview showing users (set by TreeviewWidget).
    filter_btn              Search/filter button (set by FilterBarWidget).
    apply_btn               Apply role/status change button (set by FilterBarWidget).
    page_info_label         Pagination label (set by TreeviewWidget).
    prev_page_btn           Previous-page button (set by TreeviewWidget).
    next_page_btn           Next-page button (set by TreeviewWidget).

    Widget refs (categories right panel)
    -------------------------------------
    category_entry          tk.Entry for category name input.
    add_category_btn        "Add Category" button.
    edit_category_btn       "Edit Category" button.
    categories_listbox      ListboxWidget showing available categories.
    """

    def __init__(self) -> None:
        # ── Window ────────────────────────────────────────────────────────────
        self.win: Optional[tk.Toplevel] = None

        # ── Data ──────────────────────────────────────────────────────────────
        self.all_users: List[dict] = []
        self.all_categories: List[dict] = []

        # ── Filter / action vars ──────────────────────────────────────────────
        self.username_var: tk.StringVar = tk.StringVar()
        self.email_var: tk.StringVar = tk.StringVar()
        self.role_var: tk.StringVar = tk.StringVar(value="All Roles")
        self.change_role_var: tk.StringVar = tk.StringVar(value="Select Role")
        self.status_var: tk.StringVar = tk.StringVar(value="Select Status")
        self.category_input_var: tk.StringVar = tk.StringVar()

        # ── Selection state ───────────────────────────────────────────────────
        self.selected_username: Optional[str] = None
        self.selected_category_id: Optional[int] = None
        self.selected_category_name: Optional[str] = None

        # ── TreeviewWidget / PaginationUIController required attributes ───────
        self.tree: Optional[ttk.Treeview] = None
        self.current_page: int = 1
        self.items_per_page: int = 15
        self.total_items: int = 0
        self.selected_index: Optional[int] = None
        self.photos: list = []
        self.data_provider = None
        self._tree_id_to_global_idx: dict = {}
        self._pagination_ui_controller = None
        self.page_info_label: Optional[tk.Label] = None
        self.prev_page_btn: Optional[tk.Button] = None
        self.next_page_btn: Optional[tk.Button] = None

        # ── Users panel widget refs ───────────────────────────────────────────
        self.filter_btn: Optional[tk.Button] = None
        self.apply_btn: Optional[tk.Button] = None

        # ── Categories panel widget refs ──────────────────────────────────────
        self.category_entry: Optional[tk.Entry] = None
        self.add_category_btn: Optional[tk.Button] = None
        self.edit_category_btn: Optional[tk.Button] = None
        self.categories_listbox = None  # ListboxWidget ref
