import tkinter as tk
from typing import Optional

from app.controllers.category_controller import CategoryController
from app.controllers.user_controller import UserController
from app.presentation.views.manage.helpers.data.manage_data import (
    filter_users,
    refresh_categories_list,
    refresh_tree,
)
from app.presentation.views.manage.helpers.data.manage_state import ManageState
from app.presentation.widgets.helpers.ui_dialogs import (
    show_confirmation,
    show_error,
    show_info,
)

# ── Internal helpers ──────────────────────────────────────────────────────────


def _get_parent(state: ManageState) -> tk.Toplevel:
    """Return the Toplevel window as the dialog parent.

    Args:
        state: Manage state carrying ``win``.

    Returns:
        tk.Toplevel: The manage window.
    """
    assert state.win is not None
    return state.win


def _selected_tree_user(state: ManageState) -> Optional[str]:
    """Return the username of the currently selected Treeview row, or None.

    Args:
        state: Manage state.

    Returns:
        str or None: The selected username.
    """
    return state.selected_username


# ── Users — filter ────────────────────────────────────────────────────────────


def on_filter_users(state: ManageState) -> None:
    """Apply username/email/role/status filters and refresh the Treeview.

    Args:
        state: Manage state.
    """
    users = filter_users(state)
    refresh_tree(state, users)


# ── Users — treeview selection ────────────────────────────────────────────────


def on_tree_select(state: ManageState) -> None:
    """Handle a Treeview row selection, recording the chosen username.

    Args:
        state: Manage state.
    """
    tree = state.tree
    if tree is None:
        return
    selection = tree.selection()
    if not selection:
        state.selected_username = None
        return
    values = tree.item(selection[0])["values"]
    state.selected_username = str(values[0]) if values else None


# ── Users — apply role / status change ───────────────────────────────────────


def on_apply_user_action(state: ManageState) -> None:
    """Apply role and/or status change to the currently selected user.

        Validates that a user is selected and that at least one of role/status is chosen.  Then calls the appropriate controller methods and shows a summary
        dialog with the results.  Finally refreshes the Treeview with the current filters to reflect any changes.

    Args:
        state: Manage state.
    """
    parent = _get_parent(state)
    username = _selected_tree_user(state)
    if not username:
        show_info(parent, "Manage Users", "Please select a user from the list first.")
        return

    role = state.change_role_var.get()
    status = state.status_var.get()
    role_selected = role not in ("Select Role", "")
    status_selected = status not in ("Select Status", "")

    if not role_selected and not status_selected:
        show_info(
            parent,
            "Manage Users",
            "Please select a role or status to apply for the selected user.",
        )
        return

    errors: list[str] = []

    if role_selected:
        success, msg = UserController.change_user_role(username, role)
        if not success:
            errors.append(f"Role: {msg}")

    if status_selected:
        if status == "block":
            success, msg = UserController.block_user(username)
        else:  # "unblock"
            success, msg = UserController.unblock_user(username)
        if not success:
            errors.append(f"Status: {msg}")

    if errors:
        show_error(parent, "Manage Users", "\n".join(errors))
    else:
        show_info(parent, "Manage Users", f'Changes applied to "{username}".')
        # Refresh tree with current filters
        users = filter_users(state)
        refresh_tree(state, users)


# ── Categories — listbox selection ────────────────────────────────────────────


def on_category_select(idx: int, state: ManageState) -> None:
    """Handle category selection in the listbox.

    Stores the selected category ID and name on state, and pre-fills the
    category name entry with the selected category so the admin can edit it.

    Args:
        idx: Local index of the selected item in ``state.all_categories``.
        state: Manage state.
    """
    if not (0 <= idx < len(state.all_categories)):
        return
    cat = state.all_categories[idx]
    state.selected_category_id = cat.get("id")
    state.selected_category_name = cat.get("category", "")
    state.category_input_var.set(state.selected_category_name)


# ── Categories — add ──────────────────────────────────────────────────────────


def on_add_category(state: ManageState) -> None:
    """Add a new category using the value in the category name entry.

    Validates that the name is non-empty before calling the controller.
    On success refreshes the categories listbox and clears the entry.

    Args:
        state: Manage state.
    """
    parent = _get_parent(state)
    name = state.category_input_var.get().strip()
    if not name:
        show_error(parent, "Add Category", "Please enter a category name.")
        return

    success, msg = CategoryController.add_category(name)
    if success:
        show_info(parent, "Add Category", msg)
        state.category_input_var.set("")
        state.selected_category_id = None
        state.selected_category_name = None
        refresh_categories_list(state)
    else:
        show_error(parent, "Add Category", msg)


# ── Categories — edit ─────────────────────────────────────────────────────────


def on_edit_category(state: ManageState) -> None:
    """Edit the currently selected category with the value in the name entry.

    Validates that:
    - A category is selected from the listbox.
    - The new name is non-empty.
    - The admin confirms the action.

    On success refreshes the listbox and clears the entry.

    Args:
        state: Manage state.
    """
    parent = _get_parent(state)

    if state.selected_category_id is None:
        show_info(
            parent, "Edit Category", "Please select a category from the list first."
        )
        return

    new_name = state.category_input_var.get().strip()
    if not new_name:
        show_error(parent, "Edit Category", "Please enter a new category name.")
        return

    old_name = state.selected_category_name or "this category"
    confirmed = show_confirmation(
        parent,
        "Edit Category",
        f'Rename "{old_name}" to "{new_name}"?',
    )
    if not confirmed:
        return

    success, msg = CategoryController.update_category(
        state.selected_category_id, new_name
    )
    if success:
        show_info(parent, "Edit Category", msg)
        state.category_input_var.set("")
        state.selected_category_id = None
        state.selected_category_name = None
        refresh_categories_list(state)
    else:
        show_error(parent, "Edit Category", msg)
