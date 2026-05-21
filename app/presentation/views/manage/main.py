import tkinter as tk
import tkinter.ttk as ttk

from app.controllers.category_controller import CategoryController
from app.controllers.user_controller import UserController
from app.presentation.styles.button import COMPACT_BTN_STYLE, ICON_CENTER_BTN_STYLE
from app.presentation.styles.colors import colors
from app.presentation.styles.fonts import quickSandBold
from app.presentation.widgets.helpers.button import make_button
from app.presentation.widgets.helpers.images import load_image
from app.presentation.widgets.helpers.input import (
    on_click_outside,
    on_focus_in,
    on_focus_out,
)
from app.presentation.widgets.helpers.ui_dialogs import (
    show_confirmation,
    show_error,
    show_info,
)
from app.presentation.widgets.lists import insert_categories, insert_users
from app.presentation.widgets.window import create_toplevel

addIcon: str = ""
removeIcon: str = ""


def manageWindow():
    """
    Display the management window for admin or user management tasks.

    :return: None
    """

    global addIcon, removeIcon

    # create the window using the reusable helper
    _manageWindow_: tk.Toplevel = create_toplevel(
        title="🛠️ Manage 🛠️",
        width=1349,
        height=678,
        icon_path="app/assets/PhotoShowIcon.ico",
        bg_color=colors["primary-50"],
    )

    # -------------------------------------------------------------------------
    # global variables
    roles: list = ["select role", "unsigned", "regular"]
    status: list = ["select status", "blocked", "unblocked"]
    users: list = UserController.get_manageable_users()
    categories: list = CategoryController.get_categories()

    initialRoleVal: tk.StringVar = tk.StringVar()
    initialStatusVal: tk.StringVar = tk.StringVar()

    initialRoleVal.set(roles[0])
    initialStatusVal.set(status[0])

    # -------------------------------------------------------------------------
    # filter username section
    canvasFilterUsernameIcon: tk.Canvas = tk.Canvas(
        _manageWindow_, height=40, width=46, highlightthickness=0
    )
    canvasFilterUsernameIcon.place(x=10, y=10)
    # load and render filter icon
    filter_photo = load_image(
        "assets/images/UI_Icons/Filter_Icon.png",
        size=(48, 44),
        canvas=canvasFilterUsernameIcon,
        x=0,
        y=0,
    )
    canvasFilterUsernameIcon.image = filter_photo

    filterUsernameLabel: tk.Label = tk.Label(
        _manageWindow_,
        text="Filter by username",
        font=quickSandBold(13),
        bg=colors["primary-50"],
        fg=colors["secondary-500"],
    )

    filterUsernameLabel.place(x=54, y=16)

    filterUsernameInput: tk.Entry = tk.Entry(
        _manageWindow_,
        width=25,
        borderwidth=0,
        font=quickSandBold(12),
        bg=colors["secondary-300"],
        fg=colors["secondary-500"],
        highlightthickness=0,
        cursor="xterm",
    )

    filterUsernameInput.place(x=24, y=56)
    filterUsernameInput.bind(
        "<FocusIn>", lambda event: on_focus_in(event, filterUsernameInput)
    )
    filterUsernameInput.bind(
        "<FocusOut>", lambda event: on_focus_out(event, filterUsernameInput)
    )

    # -------------------------------------------------------------------------
    # filter email section

    canvasFilterEmailIcon: tk.Canvas = tk.Canvas(
        _manageWindow_, height=40, width=46, highlightthickness=0
    )
    canvasFilterEmailIcon.place(x=10, y=94)
    filter_email_photo = load_image(
        "app/assets/images/UI_Icons/Filter_Icon.png",
        size=(48, 44),
        canvas=canvasFilterEmailIcon,
        x=0,
        y=0,
    )
    canvasFilterEmailIcon.image = filter_email_photo

    filterEmailLabel: tk.Label = tk.Label(
        _manageWindow_,
        text="Filter by email",
        font=quickSandBold(13),
        bg=colors["primary-50"],
        fg=colors["secondary-500"],
    )
    filterEmailLabel.place(x=54, y=100)

    filterEmailInput: tk.Entry = tk.Entry(
        _manageWindow_,
        width=25,
        borderwidth=0,
        font=quickSandBold(12),
        bg=colors["secondary-300"],
        fg=colors["secondary-500"],
        highlightthickness=0,
        cursor="xterm",
    )

    filterEmailInput.place(x=24, y=140)
    filterEmailInput.bind(
        "<FocusIn>", lambda event: on_focus_in(event, filterEmailInput)
    )
    filterEmailInput.bind(
        "<FocusOut>", lambda event: on_focus_out(event, filterEmailInput)
    )
    # -------------------------------------------------------------------------
    # change role section

    filterChangeRoleLabel: tk.Label = tk.Label(
        _manageWindow_,
        text="Change role",
        font=quickSandBold(13),
        bg=colors["primary-50"],
        fg=colors["secondary-500"],
    )
    filterChangeRoleLabel.place(x=450, y=20)

    filterChangeRoleDropdown: tk.OptionMenu = tk.OptionMenu(
        _manageWindow_, initialRoleVal, *roles
    )

    filterChangeRoleDropdown.config(
        font=quickSandBold(12),
        bg=colors["secondary-500"],
        fg=colors["primary-50"],
        highlightthickness=0,
        cursor="hand2",
    )

    filterChangeRoleDropdown["menu"].config(
        bg=colors["secondary-500"],
        fg=colors["primary-50"],
        font=quickSandBold(12),
    )

    filterChangeRoleDropdown.place(x=450, y=60)

    # -------------------------------------------------------------------------
    # change status section
    filterChangeStatusLabel: tk.Label = tk.Label(
        _manageWindow_,
        text="Change status",
        font=quickSandBold(13),
        bg=colors["primary-50"],
        fg=colors["secondary-500"],
    )

    filterChangeStatusLabel.place(x=450, y=110)

    filterChangeStatusDropdown: tk.OptionMenu = tk.OptionMenu(
        _manageWindow_, initialStatusVal, *status
    )

    filterChangeStatusDropdown.config(
        font=quickSandBold(12),
        bg=colors["secondary-500"],
        fg=colors["primary-50"],
        highlightthickness=0,
        cursor="hand2",
    )

    filterChangeStatusDropdown["menu"].config(
        bg=colors["secondary-500"],
        fg=colors["primary-50"],
        font=quickSandBold(12),
    )

    filterChangeStatusDropdown.place(x=450, y=150)

    # -------------------------------------------------------------------------
    # filter search button section

    searchUsernameBtn = make_button(
        _manageWindow_,
        "Search",
        width=10,
        height=1,
        **COMPACT_BTN_STYLE,
    )

    searchUsernameBtn.place(x=300, y=52)

    # -------------------------------------------------------------------------
    # filter search email button section
    searchEmailBtn = make_button(
        _manageWindow_,
        "Search",
        width=10,
        height=1,
        **COMPACT_BTN_STYLE,
    )
    searchEmailBtn.place(x=300, y=138)

    # -------------------------------------------------------------------------
    # change role button section
    changeRoleBtn = make_button(
        _manageWindow_,
        "Update",
        width=10,
        height=1,
        **COMPACT_BTN_STYLE,
    )

    changeRoleBtn.place(x=600, y=58)
    # -------------------------------------------------------------------------
    # change status button section
    changeStatusBtn = make_button(
        _manageWindow_,
        "Update",
        width=10,
        height=1,
        **COMPACT_BTN_STYLE,
    )
    changeStatusBtn.place(x=600, y=148)

    # -------------------------------------------------------------------------
    # search category section
    categoryLabel: tk.Label = tk.Label(
        _manageWindow_,
        text="Category",
        font=quickSandBold(13),
        bg=colors["primary-50"],
        fg=colors["secondary-500"],
    )
    categoryLabel.place(x=900, y=20)

    categoryInput: tk.Entry = tk.Entry(
        _manageWindow_,
        width=25,
        borderwidth=0,
        font=quickSandBold(12),
        bg=colors["secondary-300"],
        fg=colors["secondary-500"],
        highlightthickness=0,
        cursor="xterm",
    )

    categoryInput.place(x=900, y=60)
    categoryInput.bind("<FocusIn>", lambda event: on_focus_in(event, categoryInput))
    categoryInput.bind("<FocusOut>", lambda event: on_focus_out(event, categoryInput))
    # -------------------------------------------------------------------------
    # users table section with treeview
    # columns - username, email, role, status
    usersTable: ttk.Treeview = ttk.Treeview(
        _manageWindow_,
        columns=("username", "email", "role", "status"),
        show="headings",
        height=15,
    )

    usersTable.heading("username", text="Username", anchor=tk.CENTER)
    usersTable.heading("email", text="Email", anchor=tk.CENTER)
    usersTable.heading("role", text="Role", anchor=tk.CENTER)
    usersTable.heading("status", text="Status", anchor=tk.CENTER)

    usersTable.column("username", width=200, anchor=tk.CENTER)
    usersTable.column("email", width=200, anchor=tk.CENTER)
    usersTable.column("role", width=150, anchor=tk.CENTER)
    usersTable.column("status", width=150, anchor=tk.CENTER)

    usersTable.place(x=10, y=200)

    # adding a scrollbar to the treeview
    scrollbar: tk.Scrollbar = tk.Scrollbar(
        _manageWindow_, orient="vertical", command=usersTable.yview
    )

    usersTable.configure(yscrollcommand=scrollbar.set)

    scrollbar.place(x=695, y=200, height=328)

    # inserting the users into the treeview
    insert_users(users, usersTable)
    # -------------------------------------------------------------------------
    # categories list section with listbox

    categoriesList: tk.Listbox = tk.Listbox(
        _manageWindow_,
        width=30,
        height=12,
        font=quickSandBold(12),
        highlightthickness=0,
        cursor="hand2",
    )

    # adding a scrollbar to the listbox
    scrollbar: tk.Scrollbar = tk.Scrollbar(
        _manageWindow_, orient="vertical", command=categoriesList.yview
    )

    categoriesList.config(yscrollcommand=scrollbar.set)

    scrollbar.place(x=1190, y=120, height=300)

    categoriesList.place(x=900, y=120)

    addIcon = load_image("app/assets/images/UI_Icons/Add_Icon.png", size=(35, 35))
    removeIcon = load_image("app/assets/images/UI_Icons/Remove_Icon.png", size=(35, 35))

    insert_categories(categories, categoriesList)

    btnAddCategory = make_button(
        _manageWindow_,
        "",
        icon=addIcon,
        width=190,
        height=50,
        **ICON_CENTER_BTN_STYLE,
    )
    btnAddCategory.place(x=950, y=460)

    btnDeleteCategory = make_button(
        _manageWindow_,
        "",
        icon=removeIcon,
        width=190,
        height=50,
        **ICON_CENTER_BTN_STYLE,
    )

    btnDeleteCategory.place(x=950, y=550)

    # -------------------------------------------------------------------------
    # trigger events OnClick

    def _is_valid_email_(email: str) -> bool:
        """Basic email format validation."""
        import re

        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(pattern, email) is not None

    def _filter_users_(event: tk.Event):
        username: str = filterUsernameInput.get()
        email: str = filterEmailInput.get()
        if email and not _is_valid_email_(email):
            show_error(_manageWindow_, "Error", "Please enter a valid email.")
            return
        filtered: list = UserController.filter_users(username, email)
        usersTable.delete(*usersTable.get_children())
        for user in filtered:
            usersTable.insert(
                "",
                "end",
                values=(
                    user["username"],
                    user["email"],
                    user["role"],
                    "Blocked" if user["isBlocked"] else "Not Blocked",
                ),
            )
        filterUsernameInput.delete(0, "end")
        filterEmailInput.delete(0, "end")

    def _change_role_(event: tk.Event):
        if not usersTable.selection():
            show_error(_manageWindow_, "Error", "Please select a user.")
            return
        if initialRoleVal.get() == "select role":
            show_error(_manageWindow_, "Error", "Please select a role.")
            return
        username: str = usersTable.item(usersTable.selection()[0])["values"][0]
        new_role: str = initialRoleVal.get()
        if new_role == usersTable.item(usersTable.selection()[0])["values"][2]:
            show_error(_manageWindow_, "Error", f'"{username}" is already {new_role}.')
            return
        success, msg = UserController.change_user_role(username, new_role)
        if success:
            show_info(_manageWindow_, "Success", msg)
            updated: list = UserController.get_manageable_users()
            usersTable.delete(*usersTable.get_children())
            for user in updated:
                usersTable.insert(
                    "",
                    "end",
                    values=(
                        user["username"],
                        user["email"],
                        user["role"],
                        "Blocked" if user["isBlocked"] else "Not Blocked",
                    ),
                )
        else:
            show_error(_manageWindow_, "Error", msg)

    def _change_status_(event: tk.Event):
        if not usersTable.selection():
            show_error(_manageWindow_, "Error", "Please select a user.")
            return
        if initialStatusVal.get() == "select status":
            show_error(_manageWindow_, "Error", "Please select a status.")
            return
        username: str = usersTable.item(usersTable.selection()[0])["values"][0]
        new_status: str = initialStatusVal.get()
        current_status: str = usersTable.item(usersTable.selection()[0])["values"][3]
        if new_status == "blocked" and current_status == "Blocked":
            show_error(_manageWindow_, "Error", f'"{username}" is already blocked.')
            return
        if new_status == "unblocked" and current_status == "Not Blocked":
            show_error(_manageWindow_, "Error", f'"{username}" is already unblocked.')
            return
        if new_status == "blocked":
            success, msg = UserController.block_user(username)
        else:
            success, msg = UserController.unblock_user(username)
        if success:
            show_info(_manageWindow_, "Success", msg)
            updated: list = UserController.get_manageable_users()
            usersTable.delete(*usersTable.get_children())
            for user in updated:
                usersTable.insert(
                    "",
                    "end",
                    values=(
                        user["username"],
                        user["email"],
                        user["role"],
                        "Blocked" if user["isBlocked"] else "Not Blocked",
                    ),
                )
        else:
            show_error(_manageWindow_, "Error", msg)

    def _add_category_(event: tk.Event):
        success, msg = CategoryController.add_category(categoryInput.get())
        if success:
            show_info(_manageWindow_, "Success", msg)
            categoriesList.insert("end", categoryInput.get())
            categoryInput.delete(0, "end")
        else:
            show_error(_manageWindow_, "Error", msg)

    def _delete_category_(event: tk.Event):
        if not categoriesList.curselection():
            show_info(_manageWindow_, "Warning", "Please select a category to delete.")
            return
        selected: str = categoriesList.get(categoriesList.curselection())
        if not show_confirmation(
            _manageWindow_,
            "Confirm",
            f"Are you sure you want to delete {selected}?",
        ):
            return
        show_info(
            _manageWindow_, "Info", "Delete category feature not implemented yet."
        )

    btnAddCategory.bind("<Button-1>", _add_category_)

    btnDeleteCategory.bind("<Button-1>", _delete_category_)

    searchUsernameBtn.bind("<Button-1>", _filter_users_)

    searchEmailBtn.bind("<Button-1>", _filter_users_)

    changeRoleBtn.bind("<Button-1>", _change_role_)

    changeStatusBtn.bind("<Button-1>", _change_status_)

    _manageWindow_.bind(
        "<Button-1>",
        lambda event: on_click_outside(
            event, _manageWindow_, filterUsernameInput, filterEmailInput, categoryInput
        ),
    )

    _manageWindow_.grab_set()
