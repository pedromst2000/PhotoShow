import tkinter as tk

from app.controllers.user_controller import UserController
from app.presentation.styles.colors import colors
from app.presentation.styles.fonts import quickSandBold, quickSandRegular
from app.presentation.widgets.lists import insert_contacts
from app.presentation.widgets.window import create_toplevel


def contactsWindow():
    """
    This function is used to display the admin contacts of banned users window.
    """
    # create the window using the reusable helper
    _contactsWindow_: tk.Toplevel = create_toplevel(
        title="👤 Profile - Contacts 👥",
        width=1000,
        height=595,
        icon_path="app/assets/PhotoShowIcon.ico",
        bg_color=colors["primary-50"],
    )

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
    contacts: list = UserController.get_contacts()

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
