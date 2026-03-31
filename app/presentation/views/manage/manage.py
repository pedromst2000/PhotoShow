import tkinter as tk
import tkinter.messagebox as messagebox
import tkinter.ttk as ttk

from PIL import Image, ImageTk

from app.controllers.admin_controller import AdminController
from app.presentation.styles.colors import colors
from app.presentation.styles.fonts import quickSandBold
from app.presentation.widgets.button import on_enter as button_on_enter
from app.presentation.widgets.button import on_leave as button_on_leave
from app.presentation.widgets.input import on_click_outside, on_focus_in, on_focus_out
from app.presentation.widgets.lists import insert_categories, insert_users

addIcon: str = ""
removeIcon: str = ""


def manageWindow():
    """
    Display the management window for admin or user management tasks.

    :return: None
    """

    global addIcon, removeIcon

    # open the window
    _manageWindow_: tk.Toplevel = tk.Toplevel()

    # centering the window
    manageWindowWidth: int = 1349  # width of the window
    manageWindowHeight: int = 678  # height of the window

    screenWidth: int = _manageWindow_.winfo_screenwidth()  # width of the screen

    screenHeight: int = _manageWindow_.winfo_screenheight()  # height of the screen

    x: float = (screenWidth / 2) - (manageWindowWidth / 2)  # calculate x position

    y: float = (screenHeight / 2) - (manageWindowHeight / 2)  # calculate y position

    # setting the window size and position
    # %d = integer
    # %dx%d = width x height
    # %d+%d = x position + y position
    _manageWindow_.geometry(
        "%dx%d+%d+%d" % (manageWindowWidth, manageWindowHeight, x, y)
    )
    _manageWindow_.title("🛠️ Manage 🛠️")
    _manageWindow_.iconbitmap("app/assets/PhotoShowIcon.ico")
    _manageWindow_.resizable(0, 0)
    _manageWindow_.config(bg=colors["primary-50"])

    # -------------------------------------------------------------------------
    # global variables
    roles: list = ["select role", "unsigned", "regular"]
    status: list = ["select status", "blocked", "unblocked"]
    users: list = AdminController.get_manageable_users()
    categories: list = AdminController.get_categories()

    initialRoleVal: tk.StringVar = tk.StringVar()
    initialStatusVal: tk.StringVar = tk.StringVar()

    initialRoleVal.set(roles[0])
    initialStatusVal.set(status[0])

    # -------------------------------------------------------------------------
    # filter username section
    filterUsernameIcon: Image.Image = Image.open(
        "assets/images/UI_Icons/Filter_Icon.png"
    )
    filterUsernameIcon = filterUsernameIcon.resize((48, 44))

    canvasFilterUsernameIcon: tk.Canvas = tk.Canvas(
        _manageWindow_, height=40, width=46, highlightthickness=0
    )
    canvasFilterUsernameIcon.place(x=10, y=10)

    canvasFilterUsernameIcon.image = ImageTk.PhotoImage(filterUsernameIcon)

    canvasFilterUsernameIcon.create_image(
        0, 0, anchor=tk.NW, image=canvasFilterUsernameIcon.image
    )

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

    filterEmailIcon: Image.Image = Image.open(
        "app/assets/images/UI_Icons/Filter_Icon.png"
    )
    filterEmailIcon = filterEmailIcon.resize((48, 44))

    canvasFilterEmailIcon: tk.Canvas = tk.Canvas(
        _manageWindow_, height=40, width=46, highlightthickness=0
    )
    canvasFilterEmailIcon.place(x=10, y=94)

    canvasFilterEmailIcon.image = ImageTk.PhotoImage(filterEmailIcon)

    canvasFilterEmailIcon.create_image(
        0, 0, anchor=tk.NW, image=canvasFilterEmailIcon.image
    )

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

    searchUsernameBtn: tk.Button = tk.Button(
        _manageWindow_,
        width=10,
        height=1,
        text="Search",
        master=_manageWindow_,
        borderwidth=10,
        font=quickSandBold(12),
        background=colors["accent-300"],
        bd=0,
        highlightthickness=0,
        activebackground=colors["accent-100"],
        cursor="hand2",
    )

    searchUsernameBtn.place(x=300, y=52)

    searchUsernameBtn.bind(
        "<Enter>", lambda event: button_on_enter(event, searchUsernameBtn)
    )
    searchUsernameBtn.bind(
        "<Leave>", lambda event: button_on_leave(event, searchUsernameBtn)
    )

    # -------------------------------------------------------------------------
    # filter search email button section
    searchEmailBtn: tk.Button = tk.Button(
        _manageWindow_,
        width=10,
        height=1,
        text="Search",
        master=_manageWindow_,
        borderwidth=10,
        font=quickSandBold(12),
        background=colors["accent-300"],
        bd=0,
        highlightthickness=0,
        activebackground=colors["accent-100"],
        cursor="hand2",
    )
    searchEmailBtn.place(x=300, y=138)

    searchEmailBtn.bind("<Enter>", lambda event: button_on_enter(event, searchEmailBtn))
    searchEmailBtn.bind("<Leave>", lambda event: button_on_leave(event, searchEmailBtn))

    # -------------------------------------------------------------------------
    # change role button section
    changeRoleBtn: tk.Button = tk.Button(
        _manageWindow_,
        width=10,
        height=1,
        text="Update",
        master=_manageWindow_,
        borderwidth=10,
        font=quickSandBold(12),
        background=colors["accent-300"],
        bd=0,
        highlightthickness=0,
        activebackground=colors["accent-100"],
        cursor="hand2",
    )

    changeRoleBtn.place(x=600, y=58)

    changeRoleBtn.bind("<Enter>", lambda event: button_on_enter(event, changeRoleBtn))
    changeRoleBtn.bind("<Leave>", lambda event: button_on_leave(event, changeRoleBtn))
    # -------------------------------------------------------------------------
    # change status button section
    changeStatusBtn: tk.Button = tk.Button(
        _manageWindow_,
        width=10,
        height=1,
        text="Update",
        master=_manageWindow_,
        borderwidth=10,
        font=quickSandBold(12),
        background=colors["accent-300"],
        bd=0,
        highlightthickness=0,
        activebackground=colors["accent-100"],
        cursor="hand2",
    )
    changeStatusBtn.place(x=600, y=148)

    changeStatusBtn.bind(
        "<Enter>", lambda event: button_on_enter(event, changeStatusBtn)
    )
    changeStatusBtn.bind(
        "<Leave>", lambda event: button_on_leave(event, changeStatusBtn)
    )

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

    addIcon = ImageTk.PhotoImage(
        Image.open("app/assets/images/UI_Icons/Add_Icon.png").resize((35, 35))
    )
    removeIcon = ImageTk.PhotoImage(
        Image.open("app/assets/images/UI_Icons/Remove_Icon.png").resize((35, 35))
    )

    insert_categories(categories, categoriesList)

    btnAddCategory: tk.Button = tk.Button(
        _manageWindow_,
        width=190,
        height=50,
        master=_manageWindow_,
        borderwidth=10,
        font=quickSandBold(15),
        background=colors["accent-300"],
        highlightthickness=0,
        activebackground=colors["accent-100"],
        cursor="hand2",
        compound="center",
        border=0,
        image=addIcon,
    )
    btnAddCategory.place(x=950, y=460)
    btnAddCategory.bind("<Enter>", lambda event: button_on_enter(event, btnAddCategory))
    btnAddCategory.bind("<Leave>", lambda event: button_on_leave(event, btnAddCategory))

    btnDeleteCategory: tk.Button = tk.Button(
        _manageWindow_,
        width=190,
        height=50,
        master=_manageWindow_,
        borderwidth=10,
        font=quickSandBold(15),
        background=colors["accent-300"],
        highlightthickness=0,
        activebackground=colors["accent-100"],
        cursor="hand2",
        compound="center",
        border=0,
        image=removeIcon,
    )

    btnDeleteCategory.place(x=950, y=550)
    btnDeleteCategory.bind(
        "<Enter>", lambda event: button_on_enter(event, btnDeleteCategory)
    )
    btnDeleteCategory.bind(
        "<Leave>", lambda event: button_on_leave(event, btnDeleteCategory)
    )

    # -------------------------------------------------------------------------
    # trigger events OnClick

    def _filter_users_(event: tk.Event):
        username: str = filterUsernameInput.get()
        email: str = filterEmailInput.get()
        if email and not AdminController.is_valid_email_format(email):
            messagebox.showerror(
                "Error", "Please enter a valid email.", parent=_manageWindow_
            )
            return
        filtered: list = AdminController.filter_users(username, email)
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
            messagebox.showerror(
                "Error", "Please select a user.", parent=_manageWindow_
            )
            return
        if initialRoleVal.get() == "select role":
            messagebox.showerror(
                "Error", "Please select a role.", parent=_manageWindow_
            )
            return
        username: str = usersTable.item(usersTable.selection()[0])["values"][0]
        new_role: str = initialRoleVal.get()
        if new_role == usersTable.item(usersTable.selection()[0])["values"][2]:
            messagebox.showerror(
                "Error", f'"{username}" is already {new_role}.', parent=_manageWindow_
            )
            return
        success, msg = AdminController.change_user_role(username, new_role)
        if success:
            messagebox.showinfo("Success", msg, parent=_manageWindow_)
            updated: list = AdminController.get_manageable_users()
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
            messagebox.showerror("Error", msg, parent=_manageWindow_)

    def _change_status_(event: tk.Event):
        if not usersTable.selection():
            messagebox.showerror(
                "Error", "Please select a user.", parent=_manageWindow_
            )
            return
        if initialStatusVal.get() == "select status":
            messagebox.showerror(
                "Error", "Please select a status.", parent=_manageWindow_
            )
            return
        username: str = usersTable.item(usersTable.selection()[0])["values"][0]
        new_status: str = initialStatusVal.get()
        current_status: str = usersTable.item(usersTable.selection()[0])["values"][3]
        if new_status == "blocked" and current_status == "Blocked":
            messagebox.showerror(
                "Error", f'"{username}" is already blocked.', parent=_manageWindow_
            )
            return
        if new_status == "unblocked" and current_status == "Not Blocked":
            messagebox.showerror(
                "Error", f'"{username}" is already unblocked.', parent=_manageWindow_
            )
            return
        if new_status == "blocked":
            success, msg = AdminController.block_user(username)
        else:
            success, msg = AdminController.unblock_user(username)
        if success:
            messagebox.showinfo("Success", msg, parent=_manageWindow_)
            updated: list = AdminController.get_manageable_users()
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
            messagebox.showerror("Error", msg, parent=_manageWindow_)

    def _add_category_(event: tk.Event):
        success, msg = AdminController.add_category(categoryInput.get())
        if success:
            messagebox.showinfo("Success", msg, parent=_manageWindow_)
            categoriesList.insert("end", categoryInput.get())
            categoryInput.delete(0, "end")
        else:
            messagebox.showerror("Error", msg, parent=_manageWindow_)

    def _delete_category_(event: tk.Event):
        if not categoriesList.curselection():
            messagebox.showwarning(
                "Warning", "Please select a category to delete", parent=_manageWindow_
            )
            return
        selected: str = categoriesList.get(categoriesList.curselection())
        if not messagebox.askyesno(
            "Confirm",
            f"Are you sure you want to delete {selected}?",
            parent=_manageWindow_,
        ):
            return
        success, msg = AdminController.delete_category(selected)
        if success:
            messagebox.showinfo("Success", msg, parent=_manageWindow_)
            categoriesList.delete(categoriesList.curselection())
        else:
            messagebox.showerror("Error", msg, parent=_manageWindow_)

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
