import os
import tkinter as tk
from tkinter import ttk, messagebox
import winsound
import threading
from app.assets.modules.creator import creator_notes
from app.assets.modules.setting import settings_notes

# Constants for UI configuration
BG_COLOR = "#2D2D2D"
WHITE_KEY_COLOR = "#F8F9FA"
BLACK_KEY_COLOR = "#2B2B2B"
ACTIVE_WHITE_COLOR = "#E2E6EA"
ACTIVE_BLACK_COLOR = "#404040"
FONT_FAMILY = "Consolas"
FONT_SIZE = 12
ICON_PATH = "app/assets/icon/piano.ico"

# Key bindings for keyboard input
KEY_BINDINGS = {
    'a': 'C', 'w': 'C#', 's': 'D', 'e': 'D#',
    'd': 'E', 'f': 'F', 't': 'F#', 'g': 'G',
    'y': 'G#', 'h': 'A', 'u': 'A#', 'j': 'B'
}

# Octave modes available in the application
MODES = [
    "Субконтр", "Контр", "Большая", "Малая", "Первая",
    "Вторая", "Третья", "Четвертая", "Пятая", "Шестая", "Седьмая"
]

# Note positions for white and black keys on the piano UI
WHITE_NOTES = [("C", 0), ("D", 2), ("E", 4), ("F", 5), ("G", 7), ("A", 9), ("B", 11)]
BLACK_NOTES = [("C#", 1), ("D#", 3), ("F#", 6), ("G#", 8), ("A#", 10)]

# Predefined frequencies for each note across different octaves
FREQUENCIES = {
    "C": [16, 32, 65, 131, 262, 523, 1046, 2093, 4186, 8372, 16744],
    "C#": [17, 34, 69, 138, 277, 554, 1109, 2217, 4435, 8870, 17739],
    "D": [18, 37, 74, 148, 293, 587, 1175, 2349, 4698, 9397, 18794],
    "D#": [19, 39, 78, 156, 311, 622, 1244, 2489, 4978, 9956, 19912],
    "E": [20, 41, 82, 165, 330, 659, 1318, 2637, 5274, 10548, 21096],
    "F": [22, 44, 87, 175, 349, 698, 1397, 2794, 5588, 11175, 22350],
    "F#": [23, 46, 92, 185, 370, 739, 1480, 2960, 5020, 11840, 23680],
    "G": [24, 49, 98, 196, 392, 784, 1568, 3136, 6272, 12544, 25088],
    "G#": [26, 52, 104, 207, 415, 831, 1661, 3322, 6644, 13290, 26579],
    "A": [27, 55, 110, 220, 440, 880, 1760, 3520, 7040, 14080, 28160],
    "A#": [29, 68, 116, 233, 466, 932, 1864, 3729, 7458, 14916, 29833],
    "B": [30, 62, 123, 246, 494, 988, 1975, 3951, 7902, 15804, 31608]
}


class PianoApp:
    """Main class for the virtual piano application."""

    def __init__(self, root):
        """Initialize the main application window and components."""
        self.root = root
        self.mode = 4  # Default octave (Первая/First)
        self.initialize_window()
        # self.setup_icon()  # Currently commented out due to potential path issues
        self.create_widgets()
        self.bind_events()

    def initialize_window(self):
        """Configure main window properties."""
        self.root.title("WinPiano: Play mode")
        self.root.geometry("635x320")
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(False, False)

    # def setup_icon(self):
    #     """Set application icon (currently not in use)."""
    #     try:
    #         abs_path = os.path.abspath(ICON_PATH)
    #         self.root.iconbitmap(abs_path)
    #     except Exception as e:
    #         messagebox.showerror("Icon Error", f"Failed to load icon:\n{str(e)}")

    def create_widgets(self):
        """Create all UI components."""
        self.setup_styles()
        self.create_keys_frame()
        self.create_control_panel()

    def setup_styles(self):
        """Configure custom widget styles."""
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Combobox styling
        self.style.configure('TCombobox',
                             fieldbackground=BLACK_KEY_COLOR,
                             foreground='white',
                             font=(FONT_FAMILY, FONT_SIZE))
        self.style.map('TCombobox',
                       fieldbackground=[('readonly', BLACK_KEY_COLOR)],
                       foreground=[('readonly', 'white')])

        # Control buttons styling
        self.btn_style = ttk.Style()
        self.btn_style.configure('Control.TButton',
                                 padding=6,
                                 font=(FONT_FAMILY, FONT_SIZE, 'bold'),
                                 borderwidth=2,
                                 relief='raised')
        self.btn_style.map('Control.TButton',
                           background=[('active', '#F4E7E1'), ('pressed', ACTIVE_BLACK_COLOR)],
                           foreground=[('active', 'black'), ('pressed', 'white')],
                           relief=[('pressed', 'sunken'), ('!pressed', 'raised')])

    def create_keys_frame(self):
        """Create the piano keys interface."""
        self.keys_frame = ttk.Frame(self.root)
        self.keys_frame.grid(row=0, column=0, columnspan=12, pady=(20, 10), padx=20)

        # Create white keys
        for note, col in WHITE_NOTES:
            self.create_white_key(note, col)

        # Create black keys
        for note, col in BLACK_NOTES:
            self.create_black_key(note, col)

    def create_white_key(self, note, column):
        """Create a single white piano key."""
        btn = tk.Button(
            self.keys_frame,
            text=note,
            bg=WHITE_KEY_COLOR,
            fg=BLACK_KEY_COLOR,
            activebackground=ACTIVE_WHITE_COLOR,
            font=(FONT_FAMILY, FONT_SIZE, 'bold'),
            borderwidth=1,
            relief='raised',
            width=6,
            height=10
        )
        btn.grid(row=0, column=column, sticky='nsew')
        btn.configure(command=lambda n=note: self.play_note(n))

    def create_black_key(self, note, column):
        """Create a single black piano key."""
        btn = tk.Button(
            self.keys_frame,
            text=note,
            bg=BLACK_KEY_COLOR,
            fg=WHITE_KEY_COLOR,
            activebackground=ACTIVE_BLACK_COLOR,
            font=(FONT_FAMILY, FONT_SIZE - 1, 'bold'),
            borderwidth=0,
            relief='raised',
            width=3,
            height=6
        )
        btn.grid(row=0, column=column, sticky='n', pady=(0, 50))
        btn.configure(command=lambda n=note: self.play_note(n))

    def create_control_panel(self):
        """Create the bottom control panel."""
        self.control_frame = ttk.Frame(self.root)
        self.control_frame.grid(row=1, column=0, columnspan=12, pady=20, sticky='ew')

        # Octave selection combobox
        self.octave_combobox = ttk.Combobox(
            self.control_frame,
            values=MODES,
            state="readonly",
            width=15
        )
        self.octave_combobox.current(self.mode)
        self.octave_combobox.pack(side='left', padx=20)

        # Control buttons
        self.create_control_buttons()

    def create_control_buttons(self):
        """Create settings and editor buttons."""
        self.settings_btn = ttk.Button(
            self.control_frame,
            text="Settings",
            command=lambda: settings_notes(self.root),
            style='Control.TButton'
        )
        self.settings_btn.pack(side='right', padx=20)

        self.editor_btn = ttk.Button(
            self.control_frame,
            text="Editor",
            command=lambda: creator_notes(self.root),
            style='Control.TButton'
        )
        self.editor_btn.pack(side='right', padx=10)

    def bind_events(self):
        """Bind keyboard and UI events."""
        self.root.bind("<KeyPress>", self.handle_key_press)
        self.octave_combobox.bind("<<ComboboxSelected>>", self.select_octave)
        self.root.bind('<Up>', self.prev_octave)
        self.root.bind('<Down>', self.next_octave)

    @staticmethod
    def play_sound(frequency: int, duration: int = 300):
        """Play sound using winsound in a separate thread."""

        def sound_thread():
            try:
                winsound.Beep(frequency, duration)
            except RuntimeError as e:
                messagebox.showerror("Sound Error", f"Failed to play sound:\n{str(e)}")

        threading.Thread(target=sound_thread, daemon=True).start()

    def play_note(self, note_name: str):
        """Play note based on current octave."""
        note_name = note_name.upper()
        try:
            freq = FREQUENCIES[note_name][self.mode]
        except (KeyError, IndexError) as e:
            messagebox.showerror("Note Error", f"Invalid note or octave:\n{str(e)}")
            return
        self.play_sound(freq)

    def select_octave(self, event):
        """Handle octave selection from combobox."""
        self.mode = MODES.index(self.octave_combobox.get())

    def prev_octave(self, event):
        """Switch to previous octave using up arrow key."""
        new_index = max(self.mode - 1, 0)
        self.octave_combobox.set(MODES[new_index])
        self.mode = new_index

    def next_octave(self, event):
        """Switch to next octave using down arrow key."""
        new_index = min(self.mode + 1, len(MODES) - 1)
        self.octave_combobox.set(MODES[new_index])
        self.mode = new_index

    def handle_key_press(self, event):
        """Handle keyboard input for note playing."""
        if event.char and event.char.lower() in KEY_BINDINGS:
            self.play_note(KEY_BINDINGS[event.char.lower()])


def main():
    """Entry point for the application."""
    root = tk.Tk()
    PianoApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
