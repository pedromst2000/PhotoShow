import tkinter as tk
import tkinter.messagebox as messagebox

from PIL import Image, ImageTk

from app.controllers.album_controller import AlbumController
from app.controllers.photo_controller import PhotoController
from app.core.state.session import session
from app.presentation.styles.colors import colors
from app.presentation.styles.fonts import quickSandBold, quickSandRegular
from app.presentation.widgets.button import on_enter as button_on_enter
from app.presentation.widgets.button import on_leave as button_on_leave
from app.presentation.widgets.lists import insert_favorite_albuns, previewSelectedPhoto

# global variables
arrowRightIcon = ""
placeholderImage = ""
currentSelectedImage = ""
selectedAlbum = ""
current_index = 0


def favoritesProfileWindow():
    """
    This function is used to display favorites profile window.
    """
    global arrowRightIcon, placeholderImage

    # open the window
    _favoritesProfileWindow_: tk.Toplevel = tk.Toplevel()

    userID: int = session.user_id

    # centering the window
    favoritesProfileWindowWidth: int = 1070  # width of the window
    favoritesProfileWindowHeight: int = 595  # height of the window

    screenWidth: int = (
        _favoritesProfileWindow_.winfo_screenwidth()
    )  # width of the screen

    screenHeight: int = (
        _favoritesProfileWindow_.winfo_screenheight()
    )  # height of the screen

    x: float = (screenWidth / 2) - (
        favoritesProfileWindowWidth / 2
    )  # calculate x position

    y: float = (screenHeight / 2) - (
        favoritesProfileWindowHeight / 2
    )  # calculate y position

    # setting the window size and position
    # %d = integer
    # %dx%d = width x height
    # %d+%d = x position + y position
    _favoritesProfileWindow_.geometry(
        "%dx%d+%d+%d"
        % (favoritesProfileWindowWidth, favoritesProfileWindowHeight, x, y)
    )
    _favoritesProfileWindow_.title("👤 Profile - Favorites ✨")
    _favoritesProfileWindow_.iconbitmap("app/assets/PhotoShowIcon.ico")
    _favoritesProfileWindow_.resizable(0, 0)
    _favoritesProfileWindow_.config(bg=colors["primary-50"])

    # ---------------------------- Labels ---------------------------------

    yourFavoriteLabel: tk.Label = tk.Label(
        _favoritesProfileWindow_,
        text="Your favorite albums",
        font=quickSandBold(20),
        bg=colors["primary-50"],
        fg=colors["secondary-500"],
    )

    yourFavoriteLabel.place(x=50, y=10)

    selectFavoriteLabel: tk.Label = tk.Label(
        _favoritesProfileWindow_,
        text="Select a favorite album to see the available photos",
        font=quickSandRegular(12),
        bg=colors["primary-50"],
        fg=colors["secondary-500"],
    )

    selectFavoriteLabel.place(x=50, y=50)

    previewPhotosLabel: tk.Label = tk.Label(
        _favoritesProfileWindow_,
        text="Preview photos",
        font=quickSandBold(16),
        bg=colors["primary-50"],
        fg=colors["secondary-500"],
    )

    previewPhotosLabel.place(x=790, y=70)

    # ---------------------------- Buttons ----------------------------------------------

    arrowRightIcon = ImageTk.PhotoImage(
        Image.open("app/assets/images/UI_Icons/arrow_right.png").resize((35, 35))
    )

    btnSelectFavoriteAlbum: tk.Button = tk.Button(
        width=78,
        height=50,
        master=_favoritesProfileWindow_,
        image=arrowRightIcon,
        borderwidth=10,
        font=quickSandBold(16),
        background=colors["accent-300"],
        bd=0,
        highlightthickness=0,
        command=tk.CENTER,
        cursor="hand2",
    )

    btnSelectFavoriteAlbum.place(x=320, y=210)

    btnPrevImage: tk.Button = tk.Button(
        width=4,
        height=1,
        master=_favoritesProfileWindow_,
        text="<",
        font=quickSandBold(20),
        background=colors["accent-300"],
        bd=0,
        highlightthickness=0,
        command=tk.CENTER,
        cursor="hand2",
    )

    btnPrevImage.place(x=720, y=380)

    btnNextImage: tk.Button = tk.Button(
        width=4,
        height=1,
        master=_favoritesProfileWindow_,
        text=">",
        font=quickSandBold(20),
        background=colors["accent-300"],
        bd=0,
        highlightthickness=0,
        command=tk.CENTER,
        cursor="hand2",
    )

    btnNextImage.place(x=950, y=380)

    # ---------------------------- Favorites List Albuns ---------------------------------

    favoritesAlbunsListbox: tk.Listbox = tk.Listbox(
        _favoritesProfileWindow_,
        width=22,
        height=10,
        font=quickSandRegular(12),
        bg=colors["secondary-500"],
        fg=colors["primary-50"],
        highlightthickness=0,
        borderwidth=0,
    )

    # change the selected background color
    favoritesAlbunsListbox["selectbackground"] = colors["secondary-300"]

    favoritesAlbunsListbox.place(x=50, y=120)

    favoritesAlbunsScrollbar: tk.Scrollbar = tk.Scrollbar(
        _favoritesProfileWindow_,
        orient="vertical",
        command=favoritesAlbunsListbox.yview,
    )

    favoritesAlbunsScrollbar.place(x=270, y=120, height=250)

    favoritesAlbunsListbox.configure(yscrollcommand=favoritesAlbunsScrollbar.set)

    insert_favorite_albuns(
        AlbumController.get_favorite_albums(userID), favoritesAlbunsListbox
    )
    # -------------------------------------- Photos List ------------------------------------------

    photosListbox: tk.Listbox = tk.Listbox(
        _favoritesProfileWindow_,
        width=22,
        height=10,
        font=quickSandRegular(12),
        bg=colors["secondary-500"],
        fg=colors["primary-50"],
        highlightthickness=0,
        borderwidth=0,
    )

    # change the selected background color
    photosListbox["selectbackground"] = colors["secondary-300"]

    photosVScrollbar: tk.Scrollbar = tk.Scrollbar(
        _favoritesProfileWindow_,
        orient="vertical",
        command=photosListbox.yview,
    )

    photosHScrollbar: tk.Scrollbar = tk.Scrollbar(
        _favoritesProfileWindow_,
        orient="horizontal",
        command=photosListbox.xview,
    )

    photosVScrollbar.place(x=650, y=120, height=250)
    photosHScrollbar.place(x=430, y=370, width=220)

    photosListbox.config(yscrollcommand=photosVScrollbar.set)
    photosListbox.config(xscrollcommand=photosHScrollbar.set)

    photosListbox.place(x=430, y=120)

    # -------------------------------------- Preview Photos --------------------------------------

    placeholderImage = ImageTk.PhotoImage(
        Image.open("app/assets/images/photos_gallery/placeholder_image.png").resize(
            (295, 245)
        )
    )

    containerCanvas: tk.Frame = tk.Frame(
        _favoritesProfileWindow_,
        width=300,
        height=250,
        relief="sunken",
        border=3,
        bg=colors["secondary-300"],
    )

    containerCanvas.place(x=720, y=120)

    canvasPreviewImage: tk.Canvas = tk.Canvas(
        _favoritesProfileWindow_,
        width=295,
        height=245,
        highlightthickness=0,
        borderwidth=0,
    )

    canvasPreviewImage.place(x=722, y=122)

    canvasPreviewImage.create_image(0, 0, image=placeholderImage, anchor=tk.NW)

    # ----------------------------------Navigation Images--------------------------------------
    def showImage(index: int):
        """
        Helper function to display the image at the given index.

        Args:
            index (int): The index of the image to display.
        """
        if 0 <= index < photosListbox.size():
            photoName = photosListbox.get(index)
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
        if len(photosListbox.curselection()) > 0:
            current_index = (current_index + 1) % photosListbox.size()
            if current_index < photosListbox.size():
                photosListbox.selection_clear(0, tk.END)
                photosListbox.selection_set(current_index)
                showImage(current_index)
        else:
            messagebox.showerror(
                "Error",
                "You need to select an image to view the next one.",
                parent=_favoritesProfileWindow_,
            )

    def prevImage(event: tk.Event):
        """
        This function is used to preview the previous image.

        Args:
            event (tk.Event): The event object from the button click.
        """
        global current_index
        if len(photosListbox.curselection()) > 0:
            current_index = (current_index - 1) % photosListbox.size()
            if current_index >= 0:
                photosListbox.selection_clear(0, tk.END)
                photosListbox.selection_set(current_index)
                showImage(current_index)
        else:
            messagebox.showerror(
                "Error",
                "You need to select an image to view the previous one.",
                parent=_favoritesProfileWindow_,
            )

    # ---------------------------- Events -------------------------------------------------------
    btnSelectFavoriteAlbum.bind(
        "<Enter>",
        lambda event: button_on_enter(event, btnSelectFavoriteAlbum),
    )

    btnSelectFavoriteAlbum.bind(
        "<Leave>",
        lambda event: button_on_leave(event, btnSelectFavoriteAlbum),
    )

    btnPrevImage.bind(
        "<Enter>",
        lambda event: button_on_enter(event, btnPrevImage),
    )

    btnPrevImage.bind(
        "<Leave>",
        lambda event: button_on_leave(event, btnPrevImage),
    )

    btnNextImage.bind(
        "<Enter>",
        lambda event: button_on_enter(event, btnNextImage),
    )

    btnNextImage.bind(
        "<Leave>",
        lambda event: button_on_leave(event, btnNextImage),
    )

    def _select_favorite_album_(event: tk.Event):
        if not favoritesAlbunsListbox.curselection():
            return messagebox.showerror(
                "Error",
                "You need to select an album to view the available photos.",
                parent=_favoritesProfileWindow_,
            )
        selected: str = favoritesAlbunsListbox.get(
            favoritesAlbunsListbox.curselection()
        )
        photosListbox.delete(0, "end")
        fav_albums = AlbumController.get_favorite_albums(userID)
        match = next((a for a in fav_albums if a["name"] == selected), None)
        if match:
            for photo in PhotoController.get_photos_by_album(match["albumId"]):
                photosListbox.insert("end", photo["image"])
        if photosListbox.size() == 0:
            photosListbox.insert("end", "No photos to display.")

    btnSelectFavoriteAlbum.bind("<Button-1>", _select_favorite_album_)

    photosListbox.bind(
        "<<ListboxSelect>>",
        lambda event: previewSelectedPhoto(
            event, photosListbox, canvasPreviewImage, placeholderImage
        ),
    )

    btnPrevImage.bind("<Button-1>", lambda event: prevImage(event))
    btnNextImage.bind("<Button-1>", lambda event: nextImage(event))

    _favoritesProfileWindow_.grab_set()
