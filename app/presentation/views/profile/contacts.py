import tkinter as tk

from app.controllers.admin_controller import AdminController
from app.presentation.styles.colors import colors
from app.presentation.styles.fonts import quickSandBold, quickSandRegular
from app.presentation.widgets.lists import insert_contacts


def contactsWindow():
    """
    This function is used to display the admin contacts of banned users window.
    """
    # open the window
    _contactsWindow_: tk.Toplevel = tk.Toplevel()

    # centering the window
    contactsWindowWidth: int = 1000  # width of the window
    contactsWindowHeight: int = 595  # height of the window

    screenWidth: int = _contactsWindow_.winfo_screenwidth()  # width of the screen

    screenHeight: int = _contactsWindow_.winfo_screenheight()  # height of the screen

    x: float = (screenWidth / 2) - (contactsWindowWidth / 2)  # calculate x position

    y: float = (screenHeight / 2) - (contactsWindowHeight / 2)  # calculate y position

    # setting the window size and position
    # %d = integer
    # %dx%d = width x height
    # %d+%d = x position + y position
    _contactsWindow_.geometry(
        "%dx%d+%d+%d" % (contactsWindowWidth, contactsWindowHeight, x, y)
    )
    _contactsWindow_.title("👤 Profile - Contacts 👥")
    _contactsWindow_.iconbitmap("app/assets/PhotoShowIcon.ico")
    _contactsWindow_.resizable(0, 0)
    _contactsWindow_.config(bg=colors["primary-50"])

    # ----------------------  Labels ---------------------------
    contactsLabel: tk.Label = tk.Label(
        _contactsWindow_,
        text="Contacts",
        font=quickSandBold(22),
        bg=colors["primary-50"],
        fg=colors["secondary-500"],
    )

    contactsLabel.place(x=40, y=15)

    listContactsLabel: tk.Label = tk.Label(
        _contactsWindow_,
        text="Select a contact to see more details of the banned user",
        font=quickSandRegular(12),
        bg=colors["primary-50"],
        fg=colors["secondary-500"],
    )

    listContactsLabel.place(x=40, y=60)
    # ----------------------Contacts List ----------------------
    contacts: list = AdminController.get_contacts()

    listUsers: tk.Listbox = tk.Listbox(
        _contactsWindow_,
        width=20,
        height=10,
        font=quickSandRegular(12),
        bg=colors["secondary-500"],
        fg=colors["primary-50"],
    )

    listUsers.place(x=40, y=100)

    listUsersScrollbar: tk.Scrollbar = tk.Scrollbar(
        _contactsWindow_,
        orient="vertical",
        command=listUsers.yview,
        bg=colors["secondary-500"],
        troughcolor=colors["secondary-500"],
    )

    listUsersScrollbar.place(x=242, y=100, height=252)

    listUsers.configure(yscrollcommand=listUsersScrollbar.set)

    insert_contacts(contacts, listUsers)
    # ----------------------  Preview Message ----------------------------
    previewMessageLabel: tk.Label = tk.Label(
        _contactsWindow_,
        text="Preview Message",
        font=quickSandBold(18),
        bg=colors["primary-50"],
        fg=colors["secondary-500"],
    )

    previewMessageLabel.place(x=550, y=15)

    previewMessageTitle: tk.Label = tk.Label(
        _contactsWindow_,
        text="Title",
        font=quickSandBold(12),
        bg=colors["primary-50"],
        fg=colors["secondary-500"],
    )

    previewMessageTitle.place(x=550, y=60)

    previewMessageMessage: tk.Label = tk.Label(
        _contactsWindow_,
        text="Message",
        font=quickSandBold(12),
        bg=colors["primary-50"],
        fg=colors["secondary-500"],
    )

    previewMessageMessage.place(x=550, y=140)

    previewMessage: tk.Text = tk.Text(
        _contactsWindow_,
        width=40,
        height=10,
        font=quickSandRegular(12),
        bg=colors["secondary-400"],
        fg=colors["primary-50"],
    )

    previewMessage.place(x=550, y=180)

    previewTitleContent: tk.Label = tk.Label(
        _contactsWindow_,
        text="",
        font=quickSandRegular(12),
        bg=colors["primary-50"],
        fg=colors["secondary-500"],
    )

    previewTitleContent.place(x=550, y=90)

    previewMessage.configure(state="disabled")

    def _preview_message_(event: tk.Event):
        if not listUsers.curselection():
            previewTitleContent.configure(text="Select a contact to preview the title")
            previewMessage.configure(state="normal")
            previewMessage.delete("1.0", "end")
            previewMessage.insert("end", "Select a contact to preview the message")
            previewMessage.configure(state="disabled")
            return
        contact: dict = contacts[listUsers.curselection()[0]]
        previewTitleContent.configure(text=contact["title"])
        previewMessage.configure(state="normal")
        previewMessage.delete("1.0", "end")
        previewMessage.insert("end", contact["message"])
        previewMessage.configure(state="disabled")

    # --------------------- -Events------------------------------------------------
    # event when opening the window
    _contactsWindow_.bind("<FocusIn>", _preview_message_)
    listUsers.bind("<<ListboxSelect>>", _preview_message_)

    _contactsWindow_.grab_set()
