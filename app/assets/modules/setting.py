import os
import tkinter as tk
from tkinter import ttk, messagebox, colorchooser

BG_COLOR = "#2D2D2D"
WHITE_KEY_COLOR = "#F8F9FA"
BLACK_KEY_COLOR = "#2B2B2B"
ACTIVE_WHITE_COLOR = "#E2E6EA"
ACTIVE_BLACK_COLOR = "#404040"
FONT_FAMILY = "Consolas"
FONT_SIZE = 12


class SettingsWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Настройки WinPiano")
        self.geometry("485x250")
        self.configure(bg=BG_COLOR)
        self.resizable(False, False)

        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))

        # self.set_icon()
        self.setup_styles()
        self.create_widgets()

        self.transient(self.parent)
        self.grab_set()
        self.parent.wait_window(self)

    # def set_icon(self):
    #     try:
    #         open()
    #         icon_path = os.path.abspath(os.path.join(self.BASE_DIR, "./../icon/piano_rec.ico"))
    #         self.iconbitmap(icon_path)
    #     except Exception as e:
    #         messagebox.showerror("Ошибка", f"Не удалось загрузить иконку: {str(e)}")

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Стиль фрейма
        self.style.configure('Settings.TFrame', background=BG_COLOR)

        # Стиль заголовков
        self.style.configure('Settings.TLabel',
                             background=BG_COLOR,
                             foreground=WHITE_KEY_COLOR,
                             font=(FONT_FAMILY, FONT_SIZE + 2, 'bold'))

        # Стиль кнопок
        self.style.configure('Settings.TButton',
                             font=(FONT_FAMILY, FONT_SIZE),
                             background=BLACK_KEY_COLOR,
                             foreground=WHITE_KEY_COLOR,
                             borderwidth=2,
                             relief='raised')

        self.style.map('Settings.TButton',
                       background=[('active', ACTIVE_WHITE_COLOR),
                                   ('pressed', ACTIVE_BLACK_COLOR)],
                       foreground=[('active', 'black'),
                                   ('pressed', 'white')])

    def create_widgets(self):
        main_frame = ttk.Frame(self, style='Settings.TFrame')
        main_frame.pack(pady=20, padx=20, fill='both', expand=True)

        ttk.Label(
            main_frame,
            text="Настройки приложения",
            style='Settings.TLabel'
        ).grid(row=0, column=0, columnspan=2, pady=(0, 20))

        buttons = [
            ("Цветовая схема", self.select_color_theme),
            ("Системный звук", self.sndvol)
        ]

        for i, (text, command) in enumerate(buttons, start=1):
            btn = ttk.Button(
                main_frame,
                text=text,
                command=command,
                style='Settings.TButton'
            )
            btn.grid(row=i, column=0, columnspan=2, pady=5, padx=20, sticky='ew')

        info_label = ttk.Label(
            main_frame,
            text="* Изменения требуют перезапуска приложения",
            style='Settings.TLabel'
        )
        info_label.grid(row=4, column=0, columnspan=2, pady=(15, 0))

    def sndvol(self) -> None:
        messagebox.showinfo(
            title="WinPiano",
            message="Для изменения громкости используйте системный микшер."
        )
        try:
            os.system("sndvol")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть микшер громкости: {str(e)}")

    def select_color_theme(self) -> None:
        color = colorchooser.askcolor(
            initialcolor=BG_COLOR,
            title="Выберите цвет темы",
            parent=self
        )[1]

        if color:
            messagebox.showinfo(
                "WinPiano",
                "Цвет темы изменён. Для применения изменений перезапустите приложение."
            )


def settings_notes(parent) -> None:
    SettingsWindow(parent)
