from app.controllers.category_controller import CategoryController
from app.controllers.user_controller import UserController
from app.presentation.views.helpers.data.pagination import PaginationManager
from app.presentation.views.manage.helpers.data.manage_state import ManageState
from app.utils.log_utils import log_exception


def load_users(state: ManageState) -> bool:
    """
    Load all manageable users (non-admin) into *state* and set up pagination.

    Args:
        state: The ``ManageState`` instance to populate.

    Returns:
        bool: True on success, False on unexpected error.
    """
    try:
        users = UserController.get_manageable_users()
        state.all_users = users
        _init_user_pagination(state, users)
        return True
    except Exception as e:
        log_exception("manage.load_users", e)
        return False


def _init_user_pagination(state: ManageState, users: list) -> None:
    """Configure PaginationManager so TreeviewWidget can page through users."""

    def data_provider(page: int) -> list:
        start = (page - 1) * state.items_per_page
        return state.all_users[start : start + state.items_per_page]

    PaginationManager.initialize_pagination(
        state,
        items_per_page=state.items_per_page,
        data_provider=data_provider,
        total_items=len(users),
    )


def load_categories(state: ManageState) -> bool:
    """
    Load all categories into *state*.

    Args:
        state: The ``ManageState`` instance to populate.

    Returns:
        bool: True on success, False on unexpected error.
    """
    try:
        state.all_categories = CategoryController.get_all_categories()
        return True
    except Exception as e:
        log_exception("manage.load_categories", e)
        return False


def refresh_tree(state: ManageState, users: list) -> None:
    """
    Re-populate the users Treeview with a new list (re-paginates from page 1).

    Updates ``state.all_users`` and delegates rendering to the
    ``PaginationUIController`` created by ``TreeviewWidget``.

    Args:
        state: The ``ManageState`` instance.
        users: List of user dicts to display.
    """
    state.all_users = users
    state.total_items = len(users)
    state.current_page = 1
    state.selected_username = None
    ctrl = state._pagination_ui_controller
    if ctrl is not None:
        ctrl.refresh_ui()


def refresh_categories_list(state: ManageState) -> None:
    """
    Reload categories from the controller and refresh the ListboxWidget.

    Args:
        state: The ``ManageState`` instance.
    """
    try:
        state.all_categories = CategoryController.get_all_categories()
        state.selected_category_id = None
        state.selected_category_name = None
        if state.categories_listbox is not None:
            state.categories_listbox.refresh(state.all_categories)
    except Exception as e:
        log_exception("manage.refresh_categories_list", e)


def filter_users(state: ManageState) -> list:
    """
    Build and return a filtered user list based on the current filter vars.

    Filters by username, email, and role.  Status is an action-only field
    (block / unblock) and is deliberately excluded from filtering.

    Args:
        state: The ``ManageState`` instance.

    Returns:
        list: Filtered list of user dicts.
    """
    username = state.username_var.get().strip()
    email = state.email_var.get().strip()
    role = state.role_var.get()

    # Sentinel "All Roles" means no role filter
    role = "" if role in ("All Roles", "") else role

    return UserController.filter_users(username, email, role, "")
