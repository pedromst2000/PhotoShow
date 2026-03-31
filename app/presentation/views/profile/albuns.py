import tkinter as tk
import tkinter.messagebox as messagebox
from typing import Optional

from PIL import Image, ImageTk

from app.controllers.album_controller import AlbumController
from app.controllers.photo_controller import PhotoController
from app.core.state.session import session
from app.presentation.styles.colors import colors
from app.presentation.styles.fonts import quickSandBold, quickSandRegular
from app.presentation.widgets.button import on_enter as button_on_enter
from app.presentation.widgets.button import on_leave as button_on_leave
from app.presentation.widgets.input import on_click_outside, on_focus_in, on_focus_out
from app.presentation.widgets.lists import insert_albuns, previewSelectedPhoto

# global variables
arrowRightIcon = ""
placeholderImage = ""
currentSelectedImage = ""
selectedAlbum = ""
editIcon = ""
addIcon = ""
current_index = 0


def albunsProfileWindow():
    """
    This function is used to display albuns profile window.
    """

    global arrowRightIcon, placeholderImage, editIcon, addIcon

    # open the window
    _albunsProfileWindow_: tk.Toplevel = tk.Toplevel()

    userID: int = session.user_id

    # centering the window
    albunsProfileWindowWidth: int = 1100  # width of the window
    albunsProfileWindowHeight: int = 595  # height of the window

    screenWidth: int = _albunsProfileWindow_.winfo_screenwidth()  # width of the screen

    screenHeight: int = (
        _albunsProfileWindow_.winfo_screenheight()
    )  # height of the screen

    x: float = (screenWidth / 2) - (
        albunsProfileWindowWidth / 2
    )  # calculate x position

    y: float = (screenHeight / 2) - (
        albunsProfileWindowHeight / 2
    )  # calculate y position

    # setting the window size and position
    # %d = integer
    # %dx%d = width x height
    # %d+%d = x position + y position
    _albunsProfileWindow_.geometry(
        "%dx%d+%d+%d" % (albunsProfileWindowWidth, albunsProfileWindowHeight, x, y)
    )
    _albunsProfileWindow_.title("👤 Profile - Albuns 📷🖼️")
    _albunsProfileWindow_.iconbitmap("app/assets/PhotoShowIcon.ico")
    _albunsProfileWindow_.resizable(0, 0)
    _albunsProfileWindow_.config(bg=colors["primary-50"])
    # ---------------------------------Labels---------------------------------

    selectLabel: tk.Label = tk.Label(
        _albunsProfileWindow_,
        text="Select an album to view the available photos",
        font=quickSandBold(12),
        bg=colors["primary-50"],
        fg=colors["secondary-500"],
    )

    selectLabel.place(x=20, y=20)

    previewLabel: tk.Label = tk.Label(
        _albunsProfileWindow_,
        text="Preview Photos",
        font=quickSandBold(16),
        bg=colors["primary-50"],
        fg=colors["secondary-500"],
    )

    previewLabel.place(x=790, y=20)

    editAlbumNameLabel: tk.Label = tk.Label(
        _albunsProfileWindow_,
        text="Edit Album Name",
        font=quickSandBold(13),
        bg=colors["primary-50"],
        fg=colors["secondary-500"],
    )

    editAlbumNameLabel.place(x=20, y=326)

    addAlbumLabel: tk.Label = tk.Label(
        _albunsProfileWindow_,
        text="Add Album",
        font=quickSandBold(13),
        bg=colors["primary-50"],
        fg=colors["secondary-500"],
    )

    addAlbumLabel.place(x=20, y=446)

    # --------------------------------Albuns List--------------------------------
    albunsListbox: tk.Listbox = tk.Listbox(
        _albunsProfileWindow_,
        width=22,
        height=10,
        font=quickSandRegular(12),
        bg=colors["secondary-500"],
        fg=colors["primary-50"],
        highlightthickness=0,
        borderwidth=0,
    )

    # change the selected background color
    albunsListbox["selectbackground"] = colors["secondary-300"]

    albunsListbox.place(x=25, y=60)

    albunsScrollbar: tk.Scrollbar = tk.Scrollbar(
        _albunsProfileWindow_,
        orient="vertical",
        command=albunsListbox.yview,
    )

    albunsScrollbar.place(x=240, y=60, height=250)

    insert_albuns(AlbumController.get_user_albums(userID), albunsListbox)

    albunsListbox.config(yscrollcommand=albunsScrollbar.set)

    arrowRightIcon = ImageTk.PhotoImage(
        Image.open("app/assets/images/UI_Icons/arrow_right.png").resize((35, 35))
    )
    # ---------------------------------Buttons--------------------------------------

    # TODO: will not show the add album button for a visitor user (Nice to have)
    # TODO: will not show the edit album button for a visitor user (Nice to have)
    # TODO: will not show the remove photo button for a visitor user (Nice to have)
    # TODO: Willl not show the labels of the inputs for a visitor user (Nice to have)
    # TODO: Will not show the inputs for a visitor user (Nice to have)
    # TODO: The favorite button will only show for a visitor user (Nice to have)

    btnSelectAlbum: tk.Button = tk.Button(
        width=78,
        height=50,
        master=_albunsProfileWindow_,
        image=arrowRightIcon,
        borderwidth=10,
        font=quickSandBold(16),
        background=colors["accent-300"],
        bd=0,
        highlightthickness=0,
        command=tk.CENTER,
        cursor="hand2",
    )

    btnSelectAlbum.place(x=280, y=200)

    btnPrevImage: tk.Button = tk.Button(
        width=4,
        height=1,
        master=_albunsProfileWindow_,
        text="<",
        font=quickSandBold(20),
        background=colors["accent-300"],
        bd=0,
        highlightthickness=0,
        command=tk.CENTER,
        cursor="hand2",
    )

    btnPrevImage.place(x=720, y=350)

    btnNextImage: tk.Button = tk.Button(
        width=4,
        height=1,
        master=_albunsProfileWindow_,
        text=">",
        font=quickSandBold(20),
        background=colors["accent-300"],
        bd=0,
        highlightthickness=0,
        command=tk.CENTER,
        cursor="hand2",
    )

    btnNextImage.place(x=950, y=350)

    editIcon = ImageTk.PhotoImage(
        Image.open("app/assets/images/UI_Icons/Edit_ICON.png").resize((25, 25))
    )

    btnEditAlbum: tk.Button = tk.Button(
        width=200,
        height=40,
        master=_albunsProfileWindow_,
        borderwidth=10,
        font=quickSandBold(15),
        background=colors["accent-300"],
        highlightthickness=0,
        activebackground=colors["accent-100"],
        cursor="hand2",
        compound="center",
        border=0,
        image=editIcon,
    )

    # place under the input
    btnEditAlbum.place(x=25, y=400)

    addIcon = ImageTk.PhotoImage(
        Image.open("app/assets/images/UI_Icons/Add_Icon.png").resize((35, 35))
    )

    btnAddAlbum: tk.Button = tk.Button(
        width=200,
        height=40,
        master=_albunsProfileWindow_,
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

    btnAddAlbum.place(x=25, y=520)

    btnDeletePhoto: tk.Button = tk.Button(
        width=16,
        height=1,
        master=_albunsProfileWindow_,
        text="Delete Photo",
        borderwidth=10,
        font=quickSandBold(12),
        fg=colors["secondary-500"],
        background=colors["accent-300"],
        highlightthickness=0,
        activebackground=colors["accent-100"],
        cursor="hand2",
        compound="center",
        border=0,
    )

    btnDeletePhoto.place(x=400, y=480)

    btnAddFavorite: tk.Button = tk.Button(
        width=22,
        height=2,
        master=_albunsProfileWindow_,
        text="Add to Favorite albums",
        borderwidth=10,
        font=quickSandBold(12),
        fg=colors["secondary-500"],
        background=colors["accent-300"],
        highlightthickness=0,
        activebackground=colors["accent-100"],
        cursor="hand2",
        compound="center",
        border=0,
    )

    # btnAddFavorite.place(x=25, y=340)

    # --------------------------------Photos List-----------------------------------

    placeholderImage = ImageTk.PhotoImage(
        Image.open("app/assets/images/photos_gallery/placeholder_image.png").resize(
            (295, 245)
        )
    )

    listAlbumPhotos: tk.Listbox = tk.Listbox(
        _albunsProfileWindow_,
        width=22,
        height=15,
        font=quickSandRegular(12),
        bg=colors["secondary-500"],
        fg=colors["primary-50"],
        highlightthickness=0,
        borderwidth=0,
    )

    listAlbumPhotos["selectbackground"] = colors["secondary-300"]
    listAlbumPhotos.place(x=380, y=60)

    photosVScrollbar: tk.Scrollbar = tk.Scrollbar(
        _albunsProfileWindow_,
        orient="vertical",
        command=listAlbumPhotos.yview,
    )

    photosHScrollbar: tk.Scrollbar = tk.Scrollbar(
        _albunsProfileWindow_,
        orient="horizontal",
        command=listAlbumPhotos.xview,
    )

    photosVScrollbar.place(x=595, y=60, height=375)
    photosHScrollbar.place(x=380, y=435, width=215)

    listAlbumPhotos.config(yscrollcommand=photosVScrollbar.set)
    listAlbumPhotos.config(xscrollcommand=photosHScrollbar.set)

    # ---------------------------------NAVIGATION IMAGES---------------------------------

    containerCanvas: tk.Frame = tk.Frame(
        _albunsProfileWindow_,
        width=300,
        height=250,
        relief="sunken",
        border=3,
        bg=colors["secondary-300"],
    )

    containerCanvas.place(x=720, y=80)

    canvasPreviewImage: tk.Canvas = tk.Canvas(
        _albunsProfileWindow_,
        width=295,
        height=245,
        highlightthickness=0,
        borderwidth=0,
    )

    canvasPreviewImage.place(x=722, y=82)

    canvasPreviewImage.create_image(0, 0, image=placeholderImage, anchor=tk.NW)

    def showImage(index: int):
        """
        Helper function to display the image at the given index.

        Args:
            index (int): The index of the image to display.
        """
        if 0 <= index < listAlbumPhotos.size():
            photoName = listAlbumPhotos.get(index)
            currentSelectedImage = ImageTk.PhotoImage(
                Image.open(f"{photoName}").resize((295, 245))
            )
            canvasPreviewImage.create_image(
                0, 0, image=currentSelectedImage, anchor=tk.NW
            )
            canvasPreviewImage.image = currentSelectedImage

    def nextImage(event: tk.Event):
        """
        This function is used to preview the next image.

        Args:
            event (tk.Event): The event object from the button click.
        """
        global current_index
        if len(listAlbumPhotos.curselection()) > 0:
            current_index = (current_index + 1) % listAlbumPhotos.size()
            if current_index < listAlbumPhotos.size():
                listAlbumPhotos.selection_clear(0, tk.END)
                listAlbumPhotos.selection_set(current_index)
                showImage(current_index)
        else:
            tk.messagebox.showerror(
                "Error",
                "You need to select an image to view the next one.",
                parent=_albunsProfileWindow_,
            )

    def prevImage(event: tk.Event):
        """
        This function is used to preview the previous image.

        Args:
            event (tk.Event): The event object from the button click.
        """
        global current_index
        if len(listAlbumPhotos.curselection()) > 0:
            current_index = (current_index - 1) % listAlbumPhotos.size()
            if current_index >= 0:
                listAlbumPhotos.selection_clear(0, tk.END)
                listAlbumPhotos.selection_set(current_index)
                showImage(current_index)
        else:
            tk.messagebox.showerror(
                "Error",
                "You need to select an image to view the previous one.",
                parent=_albunsProfileWindow_,
            )

    # ---------------------------------INPUTS---------------------------------
    editAlbumInput: tk.Entry = tk.Entry(
        _albunsProfileWindow_,
        width=20,
        font=quickSandBold(12),
        bg=colors["secondary-300"],
        fg=colors["primary-50"],
        highlightthickness=0,
        borderwidth=0,
    )

    editAlbumInput.place(x=25, y=360)

    addAlbumInput: tk.Entry = tk.Entry(
        _albunsProfileWindow_,
        width=20,
        font=quickSandBold(12),
        bg=colors["secondary-300"],
        fg=colors["primary-50"],
        highlightthickness=0,
        borderwidth=0,
        cursor="xterm",
    )

    addAlbumInput.place(x=25, y=480)

    # ---------------------------------Events---------------------------------
    listAlbumPhotos.bind(
        "<<ListboxSelect>>",
        lambda event: previewSelectedPhoto(
            event, listAlbumPhotos, canvasPreviewImage, placeholderImage
        ),
    )

    def _select_album_(event: tk.Event):
        if not albunsListbox.curselection():
            return messagebox.showerror(
                "Error",
                "You need to select an album to view the available photos.",
                parent=_albunsProfileWindow_,
            )
        album_name: str = albunsListbox.get(albunsListbox.curselection())
        album_id: Optional[int] = AlbumController.get_album_id_by_name(
            album_name, userID
        )
        listAlbumPhotos.delete(0, "end")
        if album_id is not None:
            for photo in PhotoController.get_photos_by_album(album_id):
                listAlbumPhotos.insert("end", photo["image"])
        if listAlbumPhotos.size() == 0:
            listAlbumPhotos.insert("end", "No photos to display.")

    btnSelectAlbum.bind("<Button-1>", _select_album_)
    btnSelectAlbum.bind("<Enter>", lambda event: button_on_enter(event, btnSelectAlbum))
    btnSelectAlbum.bind("<Leave>", lambda event: button_on_leave(event, btnSelectAlbum))
    btnPrevImage.bind("<Enter>", lambda event: button_on_enter(event, btnPrevImage))
    btnPrevImage.bind("<Leave>", lambda event: button_on_leave(event, btnPrevImage))
    btnNextImage.bind("<Enter>", lambda event: button_on_enter(event, btnNextImage))
    btnNextImage.bind("<Leave>", lambda event: button_on_leave(event, btnNextImage))
    btnAddAlbum.bind("<Enter>", lambda event: button_on_enter(event, btnAddAlbum))
    btnAddAlbum.bind("<Leave>", lambda event: button_on_leave(event, btnAddAlbum))

    def _add_album_(event: tk.Event):
        name: str = addAlbumInput.get()
        if not name:
            return messagebox.showerror(
                "Error",
                "You need to type the album name.",
                parent=_albunsProfileWindow_,
            )
        if AlbumController.album_name_exists(name):
            return messagebox.showerror(
                "Error", "This album name already exists.", parent=_albunsProfileWindow_
            )
        AlbumController.create_album(name)
        addAlbumInput.delete(0, tk.END)
        albunsListbox.delete(0, "end")
        for album in AlbumController.get_user_albums(userID):
            albunsListbox.insert("end", album["name"])
        messagebox.showinfo(
            "Success", "The album was successfully added.", parent=_albunsProfileWindow_
        )

    btnAddAlbum.bind("<Button-1>", _add_album_)
    btnEditAlbum.bind("<Enter>", lambda event: button_on_enter(event, btnEditAlbum))
    btnEditAlbum.bind("<Leave>", lambda event: button_on_leave(event, btnEditAlbum))
    btnDeletePhoto.bind("<Enter>", lambda event: button_on_enter(event, btnDeletePhoto))
    btnDeletePhoto.bind("<Leave>", lambda event: button_on_leave(event, btnDeletePhoto))

    def _remove_photo_(event: tk.Event):
        if not listAlbumPhotos.curselection():
            return messagebox.showerror(
                "Error",
                "You need to select a photo to remove.",
                parent=_albunsProfileWindow_,
            )
        selected_image: str = listAlbumPhotos.get(listAlbumPhotos.curselection())
        all_photos: list = PhotoController.get_all_photos()
        matches = [p["id"] for p in all_photos if p["image"] == selected_image]
        if not matches:
            return messagebox.showerror(
                "Error", "Photo not found.", parent=_albunsProfileWindow_
            )
        photo_id: int = matches[0]
        if not messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this photo?",
            parent=_albunsProfileWindow_,
        ):
            return
        PhotoController.delete_photo(photo_id)
        messagebox.showinfo(
            "Success",
            "The photo was successfully deleted.",
            parent=_albunsProfileWindow_,
        )
        listAlbumPhotos.delete(listAlbumPhotos.curselection())
        if listAlbumPhotos.size() == 0:
            listAlbumPhotos.insert("end", "No photos to display.")
        canvasPreviewImage.create_image(0, 0, image=placeholderImage, anchor=tk.NW)

    btnDeletePhoto.bind("<Button-1>", _remove_photo_)
    btnPrevImage.bind("<Button-1>", lambda event: prevImage(event))
    btnNextImage.bind("<Button-1>", lambda event: nextImage(event))
    editAlbumInput.bind("<FocusIn>", lambda event: on_focus_in(event, editAlbumInput))
    editAlbumInput.bind("<FocusOut>", lambda event: on_focus_out(event, editAlbumInput))
    addAlbumInput.bind("<FocusIn>", lambda event: on_focus_in(event, addAlbumInput))
    addAlbumInput.bind("<FocusOut>", lambda event: on_focus_out(event, addAlbumInput))

    def _edit_album_name_(event: tk.Event):
        if not albunsListbox.curselection():
            return messagebox.showerror(
                "Error",
                "You need to select an album to edit the name.",
                parent=_albunsProfileWindow_,
            )
        new_name: str = editAlbumInput.get()
        if not new_name:
            return messagebox.showerror(
                "Error",
                "You need to type the new album name.",
                parent=_albunsProfileWindow_,
            )
        current_name: str = albunsListbox.get(albunsListbox.curselection())
        if new_name.lower() == current_name.lower():
            return messagebox.showerror(
                "Error",
                "You need to type a different name.",
                parent=_albunsProfileWindow_,
            )
        if AlbumController.album_name_exists(new_name):
            return messagebox.showerror(
                "Error", "This album name already exists.", parent=_albunsProfileWindow_
            )
        album_id: Optional[int] = AlbumController.get_album_id_by_name(
            current_name, userID
        )
        if album_id is None:
            return messagebox.showerror(
                "Error", "Album not found.", parent=_albunsProfileWindow_
            )
        AlbumController.rename_album(album_id, new_name)
        editAlbumInput.delete(0, tk.END)
        albunsListbox.delete(0, "end")
        for album in AlbumController.get_user_albums(userID):
            albunsListbox.insert("end", album["name"])
        messagebox.showinfo(
            "Success",
            "The album name was successfully changed.",
            parent=_albunsProfileWindow_,
        )

    btnEditAlbum.bind("<Button-1>", _edit_album_name_)
    btnAddFavorite.bind("<Enter>", lambda event: button_on_enter(event, btnAddFavorite))
    btnAddFavorite.bind("<Leave>", lambda event: button_on_leave(event, btnAddFavorite))
    _albunsProfileWindow_.bind(
        "<Button-1>",
        lambda event: on_click_outside(
            event, _albunsProfileWindow_, editAlbumInput, addAlbumInput
        ),
    )

    _albunsProfileWindow_.grab_set()
