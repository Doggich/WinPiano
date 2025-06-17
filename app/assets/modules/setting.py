import os
import tkinter as tk
from tkinter import ttk, messagebox, colorchooser

# UI configuration constants
BG_COLOR = "#2D2D2D"
WHITE_KEY_COLOR = "#F8F9FA"
BLACK_KEY_COLOR = "#2B2B2B"
ACTIVE_WHITE_COLOR = "#E2E6EA"
ACTIVE_BLACK_COLOR = "#404040"
FONT_FAMILY = "Consolas"
FONT_SIZE = 12


class SettingsWindow(tk.Toplevel):
    """Window for application settings configuration."""

    def __init__(self, parent):
        """Initialize settings window and UI components."""
        super().__init__(parent)
        self.parent = parent
        self.title("WinPiano Settings")
        self.geometry("485x250")
        self.configure(bg=BG_COLOR)
        self.resizable(False, False)

        # Base directory for asset paths
        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))

        # self.set_icon()  # Icon setup currently disabled
        self.setup_styles()
        self.create_widgets()

        # Configure window modality
        self.transient(self.parent)
        self.grab_set()
        self.parent.wait_window(self)

    # def set_icon(self):
    #     """Set window icon (currently disabled)."""
    #     try:
    #         icon_path = os.path.abspath(os.path.join(self.BASE_DIR, "./../icon/piano_rec.ico"))
    #         self.iconbitmap(icon_path)
    #     except Exception as e:
    #         messagebox.showerror("Error", f"Failed to load icon: {str(e)}")

    def setup_styles(self):
        """Configure custom styles for UI elements."""
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Main frame styling
        self.style.configure('Settings.TFrame', background=BG_COLOR)

        # Label styling
        self.style.configure('Settings.TLabel',
                             background=BG_COLOR,
                             foreground=WHITE_KEY_COLOR,
                             font=(FONT_FAMILY, FONT_SIZE + 2, 'bold'))

        # Button styling
        self.style.configure('Settings.TButton',
                             font=(FONT_FAMILY, FONT_SIZE),
                             background=BLACK_KEY_COLOR,
                             foreground=WHITE_KEY_COLOR,
                             borderwidth=2,
                             relief='raised')

        # Interactive button states
        self.style.map('Settings.TButton',
                       background=[('active', ACTIVE_WHITE_COLOR),
                                   ('pressed', ACTIVE_BLACK_COLOR)],
                       foreground=[('active', 'black'),
                                   ('pressed', 'white')])

    def create_widgets(self):
        """Create and arrange UI components."""
        main_frame = ttk.Frame(self, style='Settings.TFrame')
        main_frame.pack(pady=20, padx=20, fill='both', expand=True)

        # Window title
        ttk.Label(
            main_frame,
            text="Application Settings",
            style='Settings.TLabel'
        ).grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Configuration buttons
        settings_options = [
            ("Color Theme", self.select_color_theme),
            ("System Sound", self.sndvol)
        ]

        # Create and place buttons
        for row, (text, command) in enumerate(settings_options, start=1):
            btn = ttk.Button(
                main_frame,
                text=text,
                command=command,
                style='Settings.TButton'
            )
            btn.grid(row=row, column=0, columnspan=2, pady=5, padx=20, sticky='ew')

        # Information label
        info_label = ttk.Label(
            main_frame,
            text="* Changes require application restart",
            style='Settings.TLabel'
        )
        info_label.grid(row=4, column=0, columnspan=2, pady=(15, 0))

    def sndvol(self) -> None:
        """Open system volume mixer with error handling."""
        messagebox.showinfo(
            title="WinPiano",
            message="Use system volume mixer to adjust sound levels."
        )
        try:
            os.system("sndvol")  # Windows-specific command
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open volume mixer: {str(e)}")

    def select_color_theme(self) -> None:
        """Open color picker and display restart notification."""
        color = colorchooser.askcolor(
            initialcolor=BG_COLOR,
            title="Select Theme Color",
            parent=self
        )[1]

        if color:
            messagebox.showinfo(
                "WinPiano",
                "Theme color updated. Please restart the application to apply changes."
            )


def settings_notes(parent) -> None:
    """Launch the settings configuration window."""
    SettingsWindow(parent)
