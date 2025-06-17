import os
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
import winsound
import json
import re
from collections import deque

# UI configuration constants
BG_COLOR = "#2D2D2D"
WHITE_KEY_COLOR = "#F8F9FA"
BLACK_KEY_COLOR = "#2B2B2B"
ACTIVE_COLOR = "#404040"
FONT_FAMILY = "Consolas"
FONT_SIZE = 12
HOTKEY_BG = "#1E1E1E"
HINT_COLOR = "#6C757D"

# Example content templates
EXAMPLE_NOTES = """{
    1: (261, 500),
    2: (293, 500),
    3: (329, 500),
    4: (349, 500),
    5: (392, 500),
    6: (440, 500),
    7: (494, 500)
}"""

JSON_EXAMPLE = """{
    "notes": {
        "1": [261, 500],
        "2": [293, 500]
    }
}"""


class NotesEditor(tk.Toplevel):
    """Window for creating and editing musical note sequences."""

    def __init__(self, master):
        """Initialize the notes editor window."""
        super().__init__(master)
        self.master = master
        self.transient(self.master)
        self.grab_set()

        # Window configuration
        self.title("WinPiano: Creator mode")
        self.geometry("650x450")
        self.configure(bg=BG_COLOR)
        self.resizable(False, False)

        # History tracking for undo/redo
        self.history = deque(maxlen=100)
        self.redo_stack = []

        # Initialize UI components
        self.setup_styles()
        self.create_widgets()
        self.setup_menu()
        self.create_statusbar()
        self.setup_text_validation()
        self.setup_syntax_highlighting()
    def setup_styles(self):
        """Configure custom styles for UI elements."""
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Frame styling
        self.style.configure('Editor.TFrame', background=BG_COLOR)

        # Button styling
        self.style.configure('Editor.TButton',
                             font=(FONT_FAMILY, FONT_SIZE),
                             background=BLACK_KEY_COLOR,
                             foreground=WHITE_KEY_COLOR,
                             borderwidth=2,
                             relief='raised')

        # Interactive button states
        self.style.map('Editor.TButton',
                       background=[('active', WHITE_KEY_COLOR),
                                   ('pressed', ACTIVE_COLOR)],
                       foreground=[('active', 'black'),
                                   ('pressed', 'white')])

        # Text editor styling
        self.style.configure('Editor.TScrolledText',
                             background=WHITE_KEY_COLOR,
                             foreground=BLACK_KEY_COLOR,
                             insertbackground=BLACK_KEY_COLOR,
                             borderwidth=2)

    def create_widgets(self):
        """Create and arrange primary UI components."""
        main_frame = ttk.Frame(self, style='Editor.TFrame')
        main_frame.pack(pady=20, padx=20, fill='both', expand=True)

        # Text editor area
        self.txt_editor = scrolledtext.ScrolledText(
            main_frame,
            width=50,
            height=15,
            font=(FONT_FAMILY, FONT_SIZE),
            bg=WHITE_KEY_COLOR,
            fg=BLACK_KEY_COLOR,
            insertwidth=2,
            padx=10,
            pady=10
        )
        self.txt_editor.grid(row=0, column=0, columnspan=4, pady=(0, 15))
        self.txt_editor.insert("1.0", EXAMPLE_NOTES)

        # Control buttons
        buttons = [
            ("Format", self.format_action),
            ("Save", self.save_file),
            ("Open", self.open_file),
            ("Play", self.play_action)
        ]

        for i, (text, cmd) in enumerate(buttons):
            btn = ttk.Button(
                main_frame,
                text=text,
                command=cmd,
                style='Editor.TButton'
            )
            btn.grid(row=1, column=i, padx=5, sticky='ew')

    def setup_menu(self):
        """Create context menu and bind keyboard shortcuts."""
        self.menu = tk.Menu(self, tearoff=0, bg=BLACK_KEY_COLOR, fg=WHITE_KEY_COLOR)
        self.menu.add_command(label="Undo Ctrl+Z", command=self.undo)
        self.menu.add_command(label="Redo Ctrl+Y", command=self.redo)
        self.txt_editor.bind("<Button-3>", self.show_context_menu)

        # Keyboard shortcuts binding
        shortcuts = [
            ("Control-s", self.save_file),
            ("Control-o", self.open_file),
            ("Control-f", self.format_action),
            ("Control-p", self.play_action),
            ("Control-z", self.undo),
            ("Control-y", self.redo)
        ]
        for key, cmd in shortcuts:
            self.bind_all(f"<{key}>", lambda e, c=cmd: c())

    def create_statusbar(self):
        """Create status bar with usage hints."""
        self.status = ttk.Label(
            self,
            style='Status.TLabel',
            text="Ctrl+S: Save | Ctrl+O: Open | Ctrl+F: Format | Ctrl+P: Play"
        )
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

        self.style.configure('Status.TLabel',
                             background=HOTKEY_BG,
                             foreground=HINT_COLOR,
                             font=(FONT_FAMILY, 9))

    def setup_text_validation(self):
        """Configure input validation and change tracking."""
        self.txt_editor.bind('<KeyRelease>', self.on_text_changed)

        # Allowed input characters
        valid_keys = [
            '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
            '(', ')', '{', '}', '[', ']', ':', ',', '.', ' ',
            '\t', '\n', '"', "'"
        ]

        def validate_input(event):
            """Validate user input to only allow specific characters."""
            if event.keysym in ('BackSpace', 'Delete', 'Left', 'Right'):
                return
            if event.char not in valid_keys and len(event.char) > 0:
                self.bell()
                return "break"

        self.txt_editor.bind('<KeyPress>', validate_input)

    def setup_syntax_highlighting(self):
        """Configure syntax highlighting rules."""
        self.txt_editor.tag_configure("number", foreground="#4EC9B0")
        self.txt_editor.tag_configure("structure", foreground="#569CD6")
        self.txt_editor.tag_configure("error", background="#FFB6C1")
        self.txt_editor.bind('<KeyRelease>', self.highlight_syntax)

    def setup_syntax_highlighting(self):
        """Configure syntax highlighting rules."""
        self.txt_editor.tag_configure("number", foreground="#4EC9B0")  # Numbers
        self.txt_editor.tag_configure("structure", foreground="#569CD6")  # Syntax symbols
        self.txt_editor.tag_configure("string", foreground="#CE9178")  # Strings
        self.txt_editor.tag_configure("key", foreground="#DCDCAA")  # Dictionary keys
        self.txt_editor.tag_configure("error", background="#FFB6C1")  # Error highlighting
        self.txt_editor.bind('<KeyRelease>', self.highlight_syntax)

    def highlight_syntax(self, event=None):
        """Apply syntax highlighting to text content."""
        text = self.txt_editor.get("1.0", "end-1c")

        # Clear existing tags
        for tag in ["number", "structure", "string", "key", "error"]:
            self.txt_editor.tag_remove(tag, "1.0", tk.END)

        # Highlighting patterns in priority order
        patterns = [
            (r'(".*?"|\'.*?\')', "string"),  # String literals
            (r'\b\d+\b', "number"),  # Numbers
            (r'\b([A-Za-z_]\w*)(?=\s*:)', "key"),  # Dictionary keys
            (r'[{}()[$$,:]', "structure"),  # Syntax symbols
        ]

        # Apply highlighting for each pattern
        for pattern, tag in patterns:
            start = "1.0"
            while True:
                match = self.txt_editor.search(pattern, start, tk.END,
                                               regexp=True, count=tk.Text.Count.VISIBLE)
                if not match:
                    break
                end = f"{match}+{self.txt_editor.count(tk.INSERT, match, 'end', 'chars')[0]}c"
                self.txt_editor.tag_add(tag, match, end)
                start = end

    def on_text_changed(self, event=None):
        """Track text changes for undo/redo functionality."""
        current_content = self.txt_editor.get("1.0", tk.END)
        if self.history and self.history[-1] == current_content:
            return

        self.history.append(current_content)
        self.redo_stack.clear()

    def undo(self):
        """Revert to previous text state."""
        if len(self.history) > 1:
            self.redo_stack.append(self.history.pop())
            self.txt_editor.delete("1.0", tk.END)
            self.txt_editor.insert("1.0", self.history[-1])

    def redo(self):
        """Restore next text state from redo stack."""
        if self.redo_stack:
            content = self.redo_stack.pop()
            self.history.append(content)
            self.txt_editor.delete("1.0", tk.END)
            self.txt_editor.insert("1.0", content)

    def show_context_menu(self, event):
        """Display right-click context menu."""
        try:
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()

    def format_notes(self, notes_str: str) -> dict:
        """Parse and validate notes from text input."""
        try:
            cleaned_str = notes_str.strip().replace('\t', '    ')
            notes_dict = eval(cleaned_str)

            if not isinstance(notes_dict, dict):
                raise ValueError("Notes must be in dictionary format")

            formatted = {}
            for k, v in notes_dict.items():
                # Validate key type
                try:
                    key = int(k)
                except ValueError:
                    raise ValueError(f"Invalid key: {k}")

                # Validate value structure
                if not isinstance(v, (tuple, list)) or len(v) != 2:
                    raise ValueError(f"Invalid format for note {k}")

                # Validate frequency and duration values
                try:
                    freq = int(v[0])
                    duration = int(v[1])
                except (ValueError, TypeError):
                    raise ValueError(f"Invalid values for note {k}")

                # Validate frequency range
                if not 37 <= freq <= 32767:
                    raise ValueError(f"Frequency {freq}Hz out of range (37-32767)")

                formatted[key] = (freq, duration)

            return formatted

        except Exception as e:
            self.highlight_error(e)
            messagebox.showerror("Error", f"Format error: {str(e)}")
            return {}

    def highlight_error(self, exception):
        """Highlight problematic lines in the editor."""
        match = re.search(r'(\d+)$', str(exception))
        if match:
            line_no = int(match.group())
            start = f"{line_no}.0"
            end = f"{line_no}.end"
            self.txt_editor.tag_add("error", start, end)
            self.txt_editor.see(start)

    @staticmethod
    def play_notes(notes_dict: dict) -> None:
        """Play notes using system beep sounds."""
        def play_in_thread():
            try:
                for key in sorted(notes_dict.keys()):
                    freq, duration = notes_dict[key]
                    winsound.Beep(freq, duration)
            except RuntimeError as e:
                messagebox.showerror("Error", f"Sound error: {str(e)}")
            except Exception as e:
                messagebox.showerror("Error", f"Playback error: {str(e)}")

        threading.Thread(target=play_in_thread, daemon=True).start()

    def format_action(self):
        """Format and validate the text input."""
        try:
            content = self.txt_editor.get("1.0", tk.END)
            formatted = self.format_notes(content)

            if formatted:
                # Generate formatted text output
                original_order = list(formatted.keys())
                max_key_len = max(len(str(k)) for k in original_order)

                entries = []
                for k in original_order:
                    v = formatted[k]
                    key_str = str(k).rjust(max_key_len)
                    entry = f"    {key_str}: ({v[0]:>5}, {v[1]:>4})"
                    entries.append(entry)

                formatted_text = "{\n" + ",\n".join(entries) + "\n}"
                self.txt_editor.delete("1.0", tk.END)
                self.txt_editor.insert("1.0", formatted_text)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def save_file(self):
        """Save notes to file in text or JSON format."""
        filepath = filedialog.asksaveasfilename(
            title="Save File",
            filetypes=[
                ("Text Files", "*.txt"),
                ("JSON Files", "*.json"),
                ("All Files", "*.*")
            ],
            defaultextension=".txt"
        )
        if filepath:
            try:
                content = self.txt_editor.get("1.0", tk.END)
                if filepath.endswith('.json'):
                    notes = self.format_notes(content)
                    with open(filepath, 'w', encoding='utf-8') as file:
                        json.dump({"notes": notes}, file, indent=4)
                else:
                    with open(filepath, 'w', encoding='utf-8') as file:
                        file.write(content.expandtabs(4))
            except Exception as e:
                messagebox.showerror("Error", f"Save error: {str(e)}")

    def open_file(self):
        """Open and load notes from file."""
        filepath = filedialog.askopenfilename(
            title="Open File",
            filetypes=[
                ("Text Files", "*.txt"),
                ("JSON Files", "*.json"),
                ("All Files", "*.*")
            ]
        )
        if filepath:
            try:
                with open(filepath, "r", encoding="utf-8") as file:
                    if filepath.endswith('.json'):
                        data = json.load(file)
                        content = "{\n"
                        for k, v in data['notes'].items():
                            content += f"    {k}: ({v[0]}, {v[1]}),\n"
                        content += "}"
                    else:
                        content = file.read()

                    self.txt_editor.delete("1.0", tk.END)
                    self.txt_editor.insert("1.0", content)
                    self.format_action()

            except Exception as e:
                messagebox.showerror("Error", f"Load error: {str(e)}")

    def play_action(self):
        """Trigger note playback."""
        content = self.txt_editor.get("1.0", tk.END)
        notes = self.format_notes(content)
        if notes:
            self.play_notes(notes)


def creator_notes(master):
    """Launch the notes editor window."""
    NotesEditor(master)
