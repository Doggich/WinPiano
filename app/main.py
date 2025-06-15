import os
import tkinter as tk
from tkinter import ttk, messagebox
import winsound
import threading
from app.assets.modules.creator import creator_notes
from app.assets.modules.setting import settings_notes

BG_COLOR = "#2D2D2D"
WHITE_KEY_COLOR = "#F8F9FA"
BLACK_KEY_COLOR = "#2B2B2B"
ACTIVE_WHITE_COLOR = "#E2E6EA"
ACTIVE_BLACK_COLOR = "#404040"
FONT_FAMILY = "Consolas"
FONT_SIZE = 12

KEY_BINDINGS = {
    'a': 'C',
    'w': 'C#',
    's': 'D',
    'e': 'D#',
    'd': 'E',
    'f': 'F',
    't': 'F#',
    'g': 'G',
    'y': 'G#',
    'h': 'A',
    'u': 'A#',
    'j': 'B'
}

MODES = [
    "Субконтр", "Контр", "Большая",
    "Малая", "Первая", "Вторая",
    "Третья", "Четвертая", "Пятая",
    "Шестая", "Седьмая"
]

WHITE_NOTES = [("C", 0), ("D", 2), ("E", 4), ("F", 5), ("G", 7), ("A", 9), ("B", 11)]
BLACK_NOTES = [("C#", 1), ("D#", 3), ("F#", 6), ("G#", 8), ("A#", 10)]

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
    def __init__(self, root):
        self.root = root
        self.mode = 4
        self.root.title("WinPiano: Play mode")
        self.root.geometry("635x320")
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(False, False)

        self.setup_icon()
        self.create_widgets()
        self.bind_events()

    def setup_icon(self):
        try:
            abs_path = os.path.abspath("app/assets/icon/piano.ico")
            self.root.iconbitmap(abs_path)
        except Exception as e:
            print(f"Ошибка загрузки иконки: {e}")

    def create_widgets(self):
        self.setup_styles()
        self.create_keys_frame()
        self.create_control_frame()

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')

        self.style.configure('TCombobox',
                             fieldbackground=BLACK_KEY_COLOR,
                             foreground='white',
                             font=(FONT_FAMILY, FONT_SIZE))

        self.style.map('TCombobox',
                       fieldbackground=[('readonly', BLACK_KEY_COLOR)],
                       foreground=[('readonly', 'white')])

        self.btn_style = ttk.Style()
        self.btn_style.configure('Control.TButton',
                                 padding=6,
                                 font=(FONT_FAMILY, FONT_SIZE, 'bold'),
                                 borderwidth=2,
                                 relief='raised')

        self.btn_style.map('Control.TButton',
                           background=[('active', '#F4E7E1'),
                                       ('pressed', ACTIVE_BLACK_COLOR)],
                           foreground=[('active', 'black'),
                                       ('pressed', 'white')],
                           relief=[('pressed', 'sunken'),
                                   ('!pressed', 'raised')])

    def create_keys_frame(self):
        self.keys_frame = ttk.Frame(self.root)
        self.keys_frame.grid(row=0, column=0, columnspan=12, pady=(20, 10), padx=20)

        for note, col in WHITE_NOTES:
            self.create_key(note, col, 'white')

        for note, col in BLACK_NOTES:
            self.create_key(note, col, 'black')

    def create_key(self, note, col, key_type):
        if key_type == 'white':
            btn = tk.Button(self.keys_frame,
                            text=note,
                            bg=WHITE_KEY_COLOR,
                            fg=BLACK_KEY_COLOR,
                            activebackground=ACTIVE_WHITE_COLOR,
                            font=(FONT_FAMILY, FONT_SIZE, 'bold'),
                            borderwidth=1,
                            relief='raised',
                            width=6,
                            height=10)
            btn.grid(row=0, column=col, sticky='nsew')
        else:
            btn = tk.Button(self.keys_frame,
                            text=note,
                            bg=BLACK_KEY_COLOR,
                            fg=WHITE_KEY_COLOR,
                            activebackground=ACTIVE_BLACK_COLOR,
                            font=(FONT_FAMILY, FONT_SIZE - 1, 'bold'),
                            borderwidth=0,
                            relief='raised',
                            width=3,
                            height=6)
            btn.grid(row=0, column=col, sticky='n', pady=(0, 50))

        btn.configure(command=lambda n=note: self.play_note(n))

    def create_control_frame(self):
        self.control_frame = ttk.Frame(self.root)
        self.control_frame.grid(row=1, column=0, columnspan=12, pady=20, sticky='ew')

        self.combobox = ttk.Combobox(self.control_frame,
                                     values=MODES,
                                     state="readonly",
                                     width=15)
        self.combobox.current(self.mode)
        self.combobox.pack(side='left', padx=20)

        self.settings_btn = ttk.Button(self.control_frame,
                                       text="Настройки",
                                       command=lambda: settings_notes(self.root),
                                       style='Control.TButton')
        self.settings_btn.pack(side='right', padx=20)

        self.editor_btn = ttk.Button(self.control_frame,
                                     text="Редактор",
                                     command=lambda: creator_notes(self.root),
                                     style='Control.TButton')
        self.editor_btn.pack(side='right', padx=10)

    def bind_events(self):
        self.root.bind("<KeyPress>", self.handle_key_press)
        self.combobox.bind("<<ComboboxSelected>>", self.select_mode)
        self.root.bind('<Left>', lambda e: self.combobox.set(MODES[max(self.mode - 1, 0)]))
        self.root.bind('<Right>', lambda e: self.combobox.set(MODES[min(self.mode + 1, 10)]))

    @staticmethod
    def play_sound(frequency: int, duration: int):
        try:
            winsound.Beep(frequency, duration)
        except RuntimeError as e:
            messagebox.showerror("Ошибка", f"Невозможно воспроизвести звук: {str(e)}")

    def play_note(self, note_name: str, note_duration: int = 300):
        note_name = note_name.upper()
        if note_name not in FREQUENCIES:
            return

        try:
            freq = FREQUENCIES[note_name][self.mode]
        except IndexError:
            messagebox.showerror("Ошибка", "Недопустимая октава")
            return

        thread = threading.Thread(
            target=self.play_sound,
            args=(freq, note_duration),
            daemon=True
        )
        thread.start()

    def select_mode(self, event):
        self.mode = MODES.index(self.combobox.get())

    def handle_key_press(self, event):
        key = event.char.lower()
        if key in KEY_BINDINGS:
            self.play_note(KEY_BINDINGS[key])


def main():
    root = tk.Tk()
    app = PianoApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
