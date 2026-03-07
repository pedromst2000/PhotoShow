import tkinter as tk
import tkinter.ttk as ttk
from tkinter import Canvas, Entry, Button, NW, CENTER, messagebox, Scrollbar
from PIL import ImageTk, Image
from styles.colors import colors
from styles.fonts import quickSandBold
from models.users import (
    get_users_list,
    change_role,
    block_user,
    unblock_user,
    filter_users,
)
from models.categories import (
    get_categories,
    add_category,
    delete_category,
)
from utils.widgets.input import on_focus_in, on_focus_out, on_click_outside
from utils.widgets.button import (
    on_enter as button_on_enter,
    on_leave as button_on_leave,
)
from utils.manage.manage import (
    insert_users,
    insert_categories,
    filteringUsersList,
    changingRole,
    changingStatus,
    addCategory,
    deleteCategory,
)
from utils.authentication.authentication import checkEmail


addIcon = ""
removeIcon = ""


def manageWindow():
    """
    Display the management window for admin or user management tasks.

    :return: None
    """
    """
    This function is used to display the manage window.
    """
    global addIcon, removeIcon

    # open the window
    _manageWindow_ = tk.Toplevel()

    # centering the window
    manageWindowWidth = 1349  # width of the window
    manageWindowHeight = 678  # height of the window

    screenWidth = _manageWindow_.winfo_screenwidth()  # width of the screen

    screenHeight = _manageWindow_.winfo_screenheight()  # height of the screen

    x = (screenWidth / 2) - (manageWindowWidth / 2)  # calculate x position

    y = (screenHeight / 2) - (manageWindowHeight / 2)  # calculate y position

    # setting the window size and position
    # %d = integer
    # %dx%d = width x height
    # %d+%d = x position + y position
    _manageWindow_.geometry(
        "%dx%d+%d+%d" % (manageWindowWidth, manageWindowHeight, x, y)
    )
    _manageWindow_.title("🛠️ Manage 🛠️")
    _manageWindow_.iconbitmap("assets/PhotoShowIcon.ico")
    _manageWindow_.resizable(0, 0)
    _manageWindow_.config(bg=colors["primary-50"])

    # -------------------------------------------------------------------------
    # global variables
    roles = ["select role", "unsigned", "regular"]
    status = ["select status", "blocked", "unblocked"]
    users = get_users_list()
    categories = get_categories()

    initialRoleVal = tk.StringVar()
    initialStatusVal = tk.StringVar()

    initialRoleVal.set(roles[0])
    initialStatusVal.set(status[0])

    # -------------------------------------------------------------------------
    # filter username section
    filterUsernameIcon = Image.open("assets/images/UI_Icons/Filter_Icon.png")
    filterUsernameIcon = filterUsernameIcon.resize((48, 44))

    canvasFilterUsernameIcon = Canvas(
        _manageWindow_, height=40, width=46, highlightthickness=0
    )
    canvasFilterUsernameIcon.place(x=10, y=10)

    canvasFilterUsernameIcon.image = ImageTk.PhotoImage(filterUsernameIcon)

    canvasFilterUsernameIcon.create_image(
        0, 0, anchor=NW, image=canvasFilterUsernameIcon.image
    )

    filterUsernameLabel = tk.Label(
        _manageWindow_,
        text="Filter by username",
        font=quickSandBold(13),
        bg=colors["primary-50"],
        fg=colors["secondary-500"],
    )

    filterUsernameLabel.place(x=54, y=16)

    filterUsernameInput = Entry(
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
    filterUsernameInput.bind("<FocusIn>", lambda e: on_focus_in(e, filterUsernameInput))
    filterUsernameInput.bind(
        "<FocusOut>", lambda e: on_focus_out(e, filterUsernameInput)
    )

    # -------------------------------------------------------------------------
    # filter email section

    filterEmailIcon = Image.open("assets/images/UI_Icons/Filter_Icon.png")
    filterEmailIcon = filterEmailIcon.resize((48, 44))

    canvasFilterEmailIcon = Canvas(
        _manageWindow_, height=40, width=46, highlightthickness=0
    )
    canvasFilterEmailIcon.place(x=10, y=94)

    canvasFilterEmailIcon.image = ImageTk.PhotoImage(filterEmailIcon)

    canvasFilterEmailIcon.create_image(
        0, 0, anchor=NW, image=canvasFilterEmailIcon.image
    )

    filterEmailLabel = tk.Label(
        _manageWindow_,
        text="Filter by email",
        font=quickSandBold(13),
        bg=colors["primary-50"],
        fg=colors["secondary-500"],
    )
    filterEmailLabel.place(x=54, y=100)

    filterEmailInput = Entry(
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
    filterEmailInput.bind("<FocusIn>", lambda e: on_focus_in(e, filterEmailInput))
    filterEmailInput.bind("<FocusOut>", lambda e: on_focus_out(e, filterEmailInput))
    # -------------------------------------------------------------------------
    # change role section

    filterChangeRoleLabel = tk.Label(
        _manageWindow_,
        text="Change role",
        font=quickSandBold(13),
        bg=colors["primary-50"],
        fg=colors["secondary-500"],
    )
    filterChangeRoleLabel.place(x=450, y=20)

    filterChangeRoleDropdown = tk.OptionMenu(_manageWindow_, initialRoleVal, *roles)

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
    filterChangeStatusLabel = tk.Label(
        _manageWindow_,
        text="Change status",
        font=quickSandBold(13),
        bg=colors["primary-50"],
        fg=colors["secondary-500"],
    )

    filterChangeStatusLabel.place(x=450, y=110)

    filterChangeStatusDropdown = tk.OptionMenu(
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

    searchUsernameBtn = Button(
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

    searchUsernameBtn.bind("<Enter>", lambda e: button_on_enter(e, searchUsernameBtn))
    searchUsernameBtn.bind("<Leave>", lambda e: button_on_leave(e, searchUsernameBtn))

    # -------------------------------------------------------------------------
    # filter search email button section
    searchEmailBtn = Button(
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

    searchEmailBtn.bind("<Enter>", lambda e: button_on_enter(e, searchEmailBtn))
    searchEmailBtn.bind("<Leave>", lambda e: button_on_leave(e, searchEmailBtn))

    # -------------------------------------------------------------------------
    # change role button section
    changeRoleBtn = Button(
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

    changeRoleBtn.bind("<Enter>", lambda e: button_on_enter(e, changeRoleBtn))
    changeRoleBtn.bind("<Leave>", lambda e: button_on_leave(e, changeRoleBtn))
    # -------------------------------------------------------------------------
    # change status button section
    changeStatusBtn = Button(
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

    changeStatusBtn.bind("<Enter>", lambda e: button_on_enter(e, changeStatusBtn))
    changeStatusBtn.bind("<Leave>", lambda e: button_on_leave(e, changeStatusBtn))

    # -------------------------------------------------------------------------
    # search category section
    categoryLabel = tk.Label(
        _manageWindow_,
        text="Category",
        font=quickSandBold(13),
        bg=colors["primary-50"],
        fg=colors["secondary-500"],
    )
    categoryLabel.place(x=900, y=20)

    categoryInput = Entry(
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
    categoryInput.bind("<FocusIn>", lambda e: on_focus_in(e, categoryInput))
    categoryInput.bind("<FocusOut>", lambda e: on_focus_out(e, categoryInput))
    # -------------------------------------------------------------------------
    # users table section with treeview
    # columns - username, email, role, status
    usersTable = ttk.Treeview(
        _manageWindow_,
        columns=("username", "email", "role", "status"),
        show="headings",
        height=15,
    )

    usersTable.heading("username", text="Username", anchor=CENTER)
    usersTable.heading("email", text="Email", anchor=CENTER)
    usersTable.heading("role", text="Role", anchor=CENTER)
    usersTable.heading("status", text="Status", anchor=CENTER)

    usersTable.column("username", width=200, anchor=CENTER)
    usersTable.column("email", width=200, anchor=CENTER)
    usersTable.column("role", width=150, anchor=CENTER)
    usersTable.column("status", width=150, anchor=CENTER)

    usersTable.place(x=10, y=200)

    # adding a scrollbar to the treeview
    scrollbar = Scrollbar(_manageWindow_, orient="vertical", command=usersTable.yview)

    usersTable.configure(yscrollcommand=scrollbar.set)

    scrollbar.place(x=695, y=200, height=328)

    # inserting the users into the treeview
    insert_users(users, usersTable)
    # -------------------------------------------------------------------------
    # categories list section with listbox

    categoriesList = tk.Listbox(
        _manageWindow_,
        width=30,
        height=12,
        font=quickSandBold(12),
        highlightthickness=0,
        cursor="hand2",
    )

    # adding a scrollbar to the listbox
    scrollbar = Scrollbar(
        _manageWindow_, orient="vertical", command=categoriesList.yview
    )

    categoriesList.config(yscrollcommand=scrollbar.set)

    scrollbar.place(x=1190, y=120, height=300)

    categoriesList.place(x=900, y=120)

    addIcon = ImageTk.PhotoImage(
        Image.open("assets/images/UI_Icons/Add_Icon.png").resize((35, 35))
    )
    removeIcon = ImageTk.PhotoImage(
        Image.open("assets/images/UI_Icons/Remove_Icon.png").resize((35, 35))
    )

    insert_categories(categories, categoriesList)

    btnAddCategory = Button(
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
    btnAddCategory.bind("<Enter>", lambda e: button_on_enter(e, btnAddCategory))
    btnAddCategory.bind("<Leave>", lambda e: button_on_leave(e, btnAddCategory))

    btnDeleteCategory = Button(
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
    btnDeleteCategory.bind("<Enter>", lambda e: button_on_enter(e, btnDeleteCategory))
    btnDeleteCategory.bind("<Leave>", lambda e: button_on_leave(e, btnDeleteCategory))

    # -------------------------------------------------------------------------
    # trigger events OnClick

    btnAddCategory.bind(
        "<Button-1>",
        lambda e: addCategory(
            categoryInput, categoriesList, add_category, messagebox, _manageWindow_
        ),
    )

    btnDeleteCategory.bind(
        "<Button-1>",
        lambda e: deleteCategory(
            categoriesList, delete_category, messagebox, _manageWindow_
        ),
    )

    searchUsernameBtn.bind(
        "<Button-1>",
        lambda e: filteringUsersList(
            filterUsernameInput,
            filterEmailInput,
            usersTable,
            filter_users,
            checkEmail,
            messagebox,
            _manageWindow_,
        ),
    )

    searchEmailBtn.bind(
        "<Button-1>",
        lambda e: filteringUsersList(
            filterUsernameInput,
            filterEmailInput,
            usersTable,
            filter_users,
            checkEmail,
            messagebox,
            _manageWindow_,
        ),
    )

    changeRoleBtn.bind(
        "<Button-1>",
        lambda e: changingRole(
            usersTable,
            initialRoleVal,
            change_role,
            get_users_list,
            messagebox,
            _manageWindow_,
        ),
    )

    changeStatusBtn.bind(
        "<Button-1>",
        lambda e: changingStatus(
            usersTable,
            initialStatusVal,
            block_user,
            unblock_user,
            get_users_list,
            messagebox,
            _manageWindow_,
        ),
    )

    _manageWindow_.bind(
        "<Button-1>",
        lambda e: on_click_outside(
            e, _manageWindow_, filterUsernameInput, filterEmailInput, categoryInput
        ),
    )

    _manageWindow_.grab_set()
