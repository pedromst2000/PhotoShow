import tkinter as tk
import tkinter.ttk as ttk

from PIL import Image, ImageTk


def insert_users(users: list[dict], usersTable: ttk.Treeview):
    """
    Insert user data into a Treeview widget.

    Args:
        users (list[dict]): A list of user dictionaries, each containing 'username', 'email', 'role', and 'isBlocked' keys.
        usersTable (ttk.Treeview): The Treeview widget to insert user data into.

    """
    for user in users:
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


def insert_categories(categories: list[str], categoriesList: tk.Listbox):
    """
    Insert categories into a Listbox widget.

    Args:
        categories (list[str]): A list of category names to insert.
        categoriesList (tk.Listbox): The Listbox widget to insert category names into.

    """
    for category in categories:
        categoriesList.insert("end", category)


def insert_albuns(albuns: list[dict], albunsListbox: tk.Listbox):
    """
    Insert album names into a Listbox widget.

    Args:
        albuns (list[dict]): A list of album dictionaries, each containing a 'name' key.
        albunsListbox (tk.Listbox): The Listbox widget to insert album names into.

    """
    if len(albuns) == 0:
        albunsListbox.insert("end", "No albums available.")

    for album in albuns:
        albunsListbox.insert("end", album["name"])


def insert_favorite_albuns(
    favorite_albuns: list[dict], favoriteAlbunsListbox: tk.Listbox
):
    """
    Insert favorite album names into a Listbox widget.

    Args:
        favorite_albuns (list[dict]): A list of favorite album dictionaries, each containing a 'name' key.
        favoriteAlbunsListbox (tk.Listbox): The Listbox widget to insert favorite album names into.
    """
    if len(favorite_albuns) == 0:
        favoriteAlbunsListbox.insert("end", "No favorite albums available.")

    for album in favorite_albuns:
        favoriteAlbunsListbox.insert("end", album["name"])


def insert_contacts(contacts: list[dict], contactsListbox: tk.Listbox):
    """
    Insert contact usernames into a Listbox widget.

    Args:
        contacts (list[dict]): A list of contact dictionaries, each containing a 'username' key.
        contactsListbox (tk.Listbox): The Listbox widget to insert contact usernames into.
    """
    if len(contacts) == 0:
        contactsListbox.insert("end", "No contacts available.")

    for contact in contacts:
        contactsListbox.insert("end", contact["username"])


def previewSelectedPhoto(
    event: tk.Event,
    listAlbumPhotos: tk.Listbox,
    canvasPreviewImage: tk.Canvas,
    placeholderImage: ImageTk.PhotoImage,
):
    """
    Preview the selected photo in a Canvas widget.

    Args:
        event (tk.Event): The event object from the Listbox selection.
        listAlbumPhotos (tk.Listbox): The Listbox widget containing photo names.
        canvasPreviewImage (tk.Canvas): The Canvas widget to display the photo preview.
        placeholderImage (ImageTk.PhotoImage): The placeholder image (no photo selected).

    """
    if listAlbumPhotos.curselection():
        photoName: str = listAlbumPhotos.get(listAlbumPhotos.curselection())
        currentSelectedImage: ImageTk.PhotoImage = ImageTk.PhotoImage(
            Image.open(f"{photoName}").resize((295, 245))
        )
        canvasPreviewImage.create_image(0, 0, image=currentSelectedImage, anchor=tk.NW)
        canvasPreviewImage.image = currentSelectedImage
    else:
        canvasPreviewImage.create_image(0, 0, image=placeholderImage, anchor=tk.NW)
