import os
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
import winsound

BG_COLOR = "#2D2D2D"
WHITE_KEY_COLOR = "#F8F9FA"
BLACK_KEY_COLOR = "#2B2B2B"
ACTIVE_COLOR = "#404040"
FONT_FAMILY = "Consolas"
FONT_SIZE = 12

EXAMPLE_NOTES = """{
    1: (261, 500), 
    2: (293, 500), 
    3: (329, 500),
    4: (349, 500), 
    5: (392, 500), 
    6: (440, 500),
    7: (494, 500)
}"""


class NotesEditor(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.transient(self.master)
        self.grab_set()

        self.title("WinPiano: Creator mode")
        self.geometry("600x400")
        self.configure(bg=BG_COLOR)
        self.resizable(False, False)

        # self.set_icon()
        self.setup_styles()
        self.create_widgets()

    # def set_icon(self):
    #     try:
    #         icon_path = os.path.abspath("../icon/piano_rec.ico")
    #         self.iconbitmap(icon_path)
    #     except Exception as e:
    #         messagebox.showerror("Ошибка", f"Не удалось загрузить иконку: {str(e)}")

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Стиль фрейма
        self.style.configure('Editor.TFrame', background=BG_COLOR)

        # Стиль кнопок
        self.style.configure('Editor.TButton',
                             font=(FONT_FAMILY, FONT_SIZE),
                             background=BLACK_KEY_COLOR,
                             foreground=WHITE_KEY_COLOR,
                             borderwidth=2,
                             relief='raised')

        self.style.map('Editor.TButton',
                       background=[('active', WHITE_KEY_COLOR),
                                   ('pressed', ACTIVE_COLOR)],
                       foreground=[('active', 'black'),
                                   ('pressed', 'white')])

        self.style.configure('Editor.TScrolledText',
                             background=WHITE_KEY_COLOR,
                             foreground=BLACK_KEY_COLOR,
                             insertbackground=BLACK_KEY_COLOR,
                             borderwidth=2)

    def create_widgets(self):
        main_frame = ttk.Frame(self, style='Editor.TFrame')
        main_frame.pack(pady=20, padx=20, fill='both', expand=True)

        self.txt_editor = scrolledtext.ScrolledText(
            main_frame,
            width=50,
            height=15,
            font=(FONT_FAMILY, FONT_SIZE),
            bg=WHITE_KEY_COLOR,
            fg=BLACK_KEY_COLOR
        )
        self.txt_editor.grid(row=0, column=0, columnspan=4, pady=(0, 15))
        self.txt_editor.insert("1.0", EXAMPLE_NOTES)

        buttons = [
            ("Форматировать", self.format_action),
            ("Сохранить", self.save_file),
            ("Открыть", self.open_file),
            ("Воспроизвести", self.play_action)
        ]

        for i, (text, cmd) in enumerate(buttons):
            btn = ttk.Button(
                main_frame,
                text=text,
                command=cmd,
                style='Editor.TButton'
            )
            btn.grid(row=1, column=i, padx=5, sticky='ew')

    def format_notes(self, notes_str: str) -> dict:
        try:
            notes_dict = eval(notes_str.strip())
            if not isinstance(notes_dict, dict):
                raise ValueError("Ноты должны быть представлены в виде словаря")

            formatted = {}
            for k, v in notes_dict.items():
                key = int(k)

                if not (isinstance(v, (tuple, list)) and len(v) == 2):
                    raise ValueError(f"Неправильный формат для ноты {k}")

                freq = int(v[0])
                duration = int(v[1])

                if not 37 <= freq <= 32767:
                    raise ValueError(f"Частота {freq} Гц вне допустимого диапазона (37-32767)")

                formatted[key] = (freq, duration)

            return formatted

        except Exception as e:
            messagebox.showerror("Ошибка", f"Некорректный формат нот: {str(e)}")
            return {}

    @staticmethod
    def play_notes(notes_dict: dict) -> None:

        def play_in_thread():
            try:
                for key in sorted(notes_dict.keys()):
                    freq, duration = notes_dict[key]
                    winsound.Beep(freq, duration)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка воспроизведения: {str(e)}")

        threading.Thread(target=play_in_thread, daemon=True).start()

    def format_action(self):
        content = self.txt_editor.get("1.0", tk.END)
        formatted = self.format_notes(content)
        if formatted:
            self.txt_editor.delete("1.0", tk.END)
            self.txt_editor.insert("1.0", "{\n" + ",\n".join(
                f"    {k}: {v}" for k, v in formatted.items()
            ) + "\n}")

    def save_file(self):
        filepath = filedialog.asksaveasfilename(
            title="Сохранить файл",
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")],
            defaultextension=".txt"
        )
        if filepath:
            try:
                with open(filepath, "w") as file:
                    file.write(self.txt_editor.get("1.0", tk.END))
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка сохранения: {str(e)}")

    def open_file(self):
        filepath = filedialog.askopenfilename(
            title="Открыть файл",
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
        )
        if filepath:
            try:
                with open(filepath, "r") as file:
                    self.txt_editor.delete("1.0", tk.END)
                    self.txt_editor.insert("1.0", file.read())
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка загрузки: {str(e)}")

    def play_action(self):
        content = self.txt_editor.get("1.0", tk.END)
        notes = self.format_notes(content)
        if notes:
            self.play_notes(notes)


def creator_notes(master):
    """Функция для создания экземпляра редактора"""
    NotesEditor(master)
