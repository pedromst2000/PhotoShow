import tkinter as tk
from typing import Optional

from PIL import ImageTk

from app.presentation.styles.colors import colors
from app.presentation.styles.fonts import quickSandBold
from app.presentation.views.auth.login import loginWindow
from app.presentation.widgets.helpers.button import on_enter, on_leave
from app.presentation.widgets.window import create_main_window
from app.utils.image_utils import load_image


class main:
    """
    The main class is responsible for creating and managing the main window of the application, including the background, logo, slogan, and sign-in button.
    It initializes the main window and sets up the user interface elements.
    """

    window: Optional[tk.Tk] = None
    canvas: Optional[tk.Canvas] = None
    mainImage: Optional[ImageTk.PhotoImage] = None
    logoImage: Optional[ImageTk.PhotoImage] = None
    sloganText: Optional[int] = None
    signInButton: Optional[tk.Button] = None

    def __init__(
        self,
        window: Optional[tk.Tk] = None,
        canvas: Optional[tk.Canvas] = None,
        mainImage: Optional[ImageTk.PhotoImage] = None,
        logoImage: Optional[ImageTk.PhotoImage] = None,
        sloganText: Optional[int] = None,
        signInButton: Optional[tk.Button] = None,
    ) -> None:
        """
        This class is used to display the main window.

        Args:
            window (Tk, optional): The main application window.
            canvas (Canvas, optional): The canvas to place widgets on.
            mainImage (ImageTk.PhotoImage, optional): The background image for the main window.
            logoImage (ImageTk.PhotoImage, optional): The logo image to display.
            sloganText (Canvas.create_text, optional): The text widget for the slogan.
            signInButton (Button, optional): The button widget for signing in.

        """

        self.window = window
        self.canvas = canvas
        self.mainImage = mainImage
        self.logoImage = logoImage
        self.sloganText = sloganText
        self.signInButton = signInButton

        # methods

    def _main_(self):
        """
        This method is used to create the main window.

        """
        self.window = create_main_window(
            title="PhotoShow",
            width=1350,
            height=700,
            icon_path="app/assets/PhotoShowIcon.ico",
        )

        # canvas
        self.canvas = tk.Canvas(self.window, width=1350, height=700)
        self.canvas.place(x=0, y=0)

        # Background
        self._main_image = load_image(
            "app/assets/images/main_background.png", (1350, 700)
        )
        self.canvas.create_image(0, 0, image=self._main_image, anchor=tk.NW)

        # Logo
        self._logo_image = load_image("app/assets/images/Logo.png", (600, 200))
        self.canvas.create_image(390, 50, image=self._logo_image, anchor=tk.NW)

        # Slogan
        self.slogan_text = self.canvas.create_text(
            550,
            300,
            text="Every Pixel Tells a Tale",
            font=quickSandBold(25),
            fill=colors["accent-500"],
            anchor=tk.NW,
        )

        # Sign-in button
        self.signInButton = tk.Button(
            master=self.canvas,
            width=18,
            height=2,
            text="Sign In",
            borderwidth=10,
            font=quickSandBold(16),
            background=colors["accent-300"],
            bd=0,
            highlightthickness=0,
            activebackground=colors["accent-100"],
            cursor="hand2",
        )
        self.signInButton.place(x=600, y=500)
        self.signInButton.bind(
            "<Button-1>", lambda event: loginWindow(event, self.window)
        )
        self.signInButton.bind(
            "<Enter>", lambda event: on_enter(event, self.signInButton)
        )
        self.signInButton.bind(
            "<Leave>", lambda event: on_leave(event, self.signInButton)
        )

        # Keep references to images on the instance to avoid garbage collection (garbage collection can cause images to disappear from the UI if not referenced)
        self._images = (self._main_image, self._logo_image)

        self.window.mainloop()


if __name__ == "__main__":
    # Imports are placed here to avoid circular import issues and unnecessary side effects
    # when this file is imported elsewhere (e.g., for testing or as a module).
    import sys

    from app.core.db.engine import check_db, init_db
    from app.core.db.reset import reset_db

    if "--resetDB" in sys.argv:
        # ── Reset: wipe database and re-seed from CSV files ──────────────────
        # WARNING: all existing data (photos, users, albums, etc.) will be lost.
        init_db()
        reset_db()
        # Do NOT launch the app after a reset — exit cleanly.
        sys.exit(0)

    if "--restoreDB" in sys.argv:
        # ── Restore: re-populate the database from a backup folder ───────────
        # Usage:  python main.py --restoreDB
        #         python main.py --restoreDB backups/20260320_002126
        # If no path is given, the latest folder inside backups/ is used.
        from app.core.db.restore import restore_db_from_backup

        _idx = sys.argv.index("--restoreDB")
        _backup_path = (
            sys.argv[_idx + 1]
            if _idx + 1 < len(sys.argv) and not sys.argv[_idx + 1].startswith("--")
            else None
        )
        restore_db_from_backup(_backup_path)
        sys.exit(0)

    # ── Normal startup ───────────────────────────────────────────────────────
    init_db()  # Ensure tables exist (no-op if already created)
    ok, message = check_db()  # Check DB health before launching the app
    if not ok:
        import tkinter.messagebox as mb

        _root = tk.Tk()
        _root.withdraw()
        mb.showerror(
            "Database Error",
            f"Cannot start PhotoShow:\n\n{message}\n\nRun: python main.py --resetDB to reset the database (WARNING: all data will be lost).",
        )
        _root.destroy()
        sys.exit(1)
    main()._main_()  # Launch the main application window
