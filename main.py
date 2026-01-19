import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from tkinter import font as tkfont
from datetime import datetime
import json
import os
import re

try:
    import keyboard
except ImportError:
    keyboard = None

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
HELP_DIR = os.path.join(BASE_DIR, "help")

CONFIG_PATH = os.path.join(DATA_DIR, "config.json")
BINDS_PATH = os.path.join(DATA_DIR, "binds.json")
PHRASES_PATH = os.path.join(DATA_DIR, "phrases.json")
AUTOFIX_PATH = os.path.join(DATA_DIR, "autofix.json")
PROFILES_PATH = os.path.join(DATA_DIR, "profiles.json")
LOG_PATH = os.path.join(DATA_DIR, "log.txt")

NAV_BUTTONS = [
    "Переменные",
    "Профили",
    "Импорт / Экспорт",
    "Информация",
    "Настройки",
]

EXTRA_SCREENS = [
    "Команды",
    "Фразы",
    "Автоисправление",
]

INFO_BUTTONS = [
    ("Журнал изменений", "changelog.txt"),
    ("Подсказки", "hints.txt"),
    ("Телепорты", "teleport.txt"),
    ("Новости", "tips.txt"),
]

THEME = {
    "bg": "#1a0f12",
    "panel": "#1a0f12",
    "card": "#1a0f12",
    "card_alt": "#1a0f12",
    "button": "#2a151b",
    "input": "#140a0e",
    "border": "#2a151b",
    "fg": "#f2e8ea",
    "muted": "#c9b5b9",
    "accent": "#c7323b",
    "accent_alt": "#3a161c",
    "header_from": "#1a0f12",
    "header_to": "#1a0f12",
}

FONT_FAMILY = "Segoe UI"
BASE_FONT_SIZE = 11
TITLE_FONT_SIZE = 16
SECTION_FONT_SIZE = 12
HEADER_FONT_SIZE = 18
SMALL_FONT_SIZE = 10
NAV_WIDTH = 230


def ensure_json_file(path, default_data):
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(default_data, f, ensure_ascii=False, indent=2)


def load_json(path, default_data):
    if not os.path.exists(path):
        return default_data
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return default_data


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def ensure_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(HELP_DIR, exist_ok=True)

    for _, name in INFO_BUTTONS:
        path = os.path.join(HELP_DIR, name)
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                f.write(name.upper())

    ensure_json_file(CONFIG_PATH, {})
    ensure_json_file(BINDS_PATH, [])
    ensure_json_file(PHRASES_PATH, [])
    ensure_json_file(AUTOFIX_PATH, {"layout": [], "custom": []})
    ensure_json_file(PROFILES_PATH, ["default"])
    if not os.path.exists(LOG_PATH):
        with open(LOG_PATH, "w", encoding="utf-8") as f:
            f.write("")


def load_config():
    return load_json(CONFIG_PATH, {})


def save_config(cfg):
    save_json(CONFIG_PATH, cfg)


def style_entry(widget):
    widget.configure(
        bg=THEME["input"],
        fg=THEME["fg"],
        insertbackground=THEME["fg"],
        relief="flat",
        highlightthickness=2,
        highlightbackground=THEME["border"],
        highlightcolor=THEME["accent"],
    )
    widget.configure(highlightbackground=THEME["border"])
    try:
        widget.configure(font=(FONT_FAMILY, BASE_FONT_SIZE))
    except tk.TclError:
        pass


def style_listbox(widget):
    widget.configure(
        bg=THEME["input"],
        fg=THEME["fg"],
        selectbackground=THEME["accent"],
        selectforeground=THEME["fg"],
        relief="flat",
        highlightthickness=2,
        highlightbackground=THEME["border"],
        activestyle="none",
    )
    try:
        widget.configure(font=(FONT_FAMILY, BASE_FONT_SIZE))
    except tk.TclError:
        pass


def style_text(widget):
    widget.configure(
        bg=THEME["input"],
        fg=THEME["fg"],
        insertbackground=THEME["fg"],
        relief="flat",
        highlightthickness=2,
        highlightbackground=THEME["border"],
        highlightcolor=THEME["accent"],
    )
    try:
        widget.configure(font=(FONT_FAMILY, BASE_FONT_SIZE))
    except tk.TclError:
        pass


RU_TO_EN = {
    "й": "q",
    "ц": "w",
    "у": "e",
    "к": "r",
    "е": "t",
    "н": "y",
    "г": "u",
    "ш": "i",
    "щ": "o",
    "з": "p",
    "х": "[",
    "ъ": "]",
    "ф": "a",
    "ы": "s",
    "в": "d",
    "а": "f",
    "п": "g",
    "р": "h",
    "о": "j",
    "л": "k",
    "д": "l",
    "ж": ";",
    "э": "'",
    "я": "z",
    "ч": "x",
    "с": "c",
    "м": "v",
    "и": "b",
    "т": "n",
    "ь": "m",
    "б": ",",
    "ю": ".",
    "ё": "`",
}
RU_TO_EN.update({k.upper(): v.upper() for k, v in RU_TO_EN.items()})


def ru_to_en(text):
    return "".join(RU_TO_EN.get(ch, ch) for ch in text)


def hex_to_rgb(value):
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def blend(color_a, color_b, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(color_a, color_b))


class RoundedButton(ttk.Button):
    def __init__(
        self,
        parent,
        text,
        command,
        bg,
        fg,
        hover_bg,
        active_bg,
        canvas_bg,
        font=None,
        padding=(12, 8),
        radius=12,
        expand_x=False,
        height=None,
        width=None,
    ):
        self._style = ttk.Style(parent)
        self._style_name = f"App{hex(id(self))}.TButton"
        self._font = font or tkfont.Font(family=FONT_FAMILY, size=BASE_FONT_SIZE)
        self._configure_style(bg, fg, hover_bg, active_bg, padding)
        super().__init__(parent, text=text, command=command, style=self._style_name, width=width)

    def _configure_style(self, bg, fg, hover_bg, active_bg, padding):
        self._style.configure(
            self._style_name,
            background=bg,
            foreground=fg,
            padding=padding,
            borderwidth=0,
            focusthickness=0,
            relief="flat",
            font=self._font,
        )
        self._style.map(
            self._style_name,
            background=[("active", hover_bg), ("pressed", active_bg)],
            foreground=[("active", fg), ("pressed", fg)],
        )

    def set_colors(self, bg, hover_bg, active_bg, fg=None):
        if fg is None:
            fg = self._style.lookup(self._style_name, "foreground")
        padding = self._style.lookup(self._style_name, "padding")
        self._configure_style(bg, fg, hover_bg, active_bg, padding)

    def set_command(self, command):
        self.configure(command=command)


class ToggleSwitch(tk.Canvas):
    def __init__(self, parent, value=False, command=None, width=46, height=24, radius=12):
        try:
            canvas_bg = parent.cget("bg")
        except tk.TclError:
            canvas_bg = THEME["bg"]
        super().__init__(parent, width=width, height=height, highlightthickness=0, bd=0, bg=canvas_bg)
        self._value = bool(value)
        self._command = command
        self._width = width
        self._height = height
        self._radius = radius
        self._draw()
        self.bind("<Button-1>", self._toggle)

    def _rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [
            x1 + r,
            y1,
            x2 - r,
            y1,
            x2,
            y1,
            x2,
            y1 + r,
            x2,
            y2 - r,
            x2,
            y2,
            x2 - r,
            y2,
            x1 + r,
            y2,
            x1,
            y2,
            x1,
            y2 - r,
            x1,
            y1 + r,
            x1,
            y1,
        ]
        return self.create_polygon(points, smooth=True, **kwargs)

    def _draw(self):
        self.delete("all")
        bg = THEME["accent"] if self._value else THEME["button"]
        knob = THEME["fg"] if self._value else THEME["muted"]
        self._rounded_rect(0, 0, self._width, self._height, self._radius, fill=bg, outline="")
        knob_radius = (self._height - 6) / 2
        if self._value:
            cx = self._width - self._height / 2
        else:
            cx = self._height / 2
        cy = self._height / 2
        self.create_oval(
            cx - knob_radius,
            cy - knob_radius,
            cx + knob_radius,
            cy + knob_radius,
            fill=knob,
            outline="",
        )

    def _toggle(self, _event=None):
        self._value = not self._value
        self._draw()
        if self._command:
            self._command(self._value)

    def get(self):
        return self._value

    def set(self, value):
        self._value = bool(value)
        self._draw()


class BinderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MajesticRP Binder")
        self.root.geometry("1080x720")
        self.root.configure(bg=THEME["bg"])
        self.root.resizable(False, False)

        self.config = load_config()
        self.config.setdefault("auto_alias_ru", True)
        self.config.setdefault("auto_update_info", True)
        self.config.setdefault("binder_enabled", True)
        save_config(self.config)
        self.setup_style()
        self.build_ui()
        self._setup_binder_listener()

    def _content_button_chars(self, font, padding):
        char_width = font.measure("0") if font else 7
        target_px = NAV_WIDTH
        pad_px = (padding[0] * 2) if padding else 0
        width_px = max(60, target_px - pad_px)
        return max(10, int(width_px / max(1, char_width)))

    def pack_content_button(self, button, pady=4):
        button.pack(anchor="w", pady=pady)
        return button

    def _setup_binder_listener(self):
        self._binder_buffer = ""
        self._binder_max_len = 64
        self._binder_sending = False
        self._binder_map = {}
        if not self.config.get("binder_enabled", True):
            return
        if keyboard is None:
            messagebox.showwarning(
                "Binder",
                "Не найден модуль keyboard.\nУстановите: pip install keyboard",
            )
            return
        self._reload_binder_map()
        keyboard.hook(self._on_binder_key)
        keyboard.on_press_key("enter", self._on_binder_enter, suppress=True)

    def _reload_binder_map(self):
        items = []
        items.extend(load_json(BINDS_PATH, []))
        items.extend(load_json(PHRASES_PATH, []))
        mapping = {}
        for item in items:
            trigger = item.get("trigger")
            if not trigger:
                continue
            text = self.bind_get_text(item)
            if not text:
                continue
            mapping[trigger] = {
                "text": text,
                "cursor_back": int(item.get("cursor_back") or 0),
            }
        self._binder_map = dict(sorted(mapping.items(), key=lambda kv: len(kv[0]), reverse=True))

    def _on_binder_key(self, event):
        if self._binder_sending or event.event_type != "down":
            return
        key = event.name
        if key == "backspace":
            self._binder_buffer = self._binder_buffer[:-1]
            return
        if key == "space":
            self._binder_buffer += " "
        elif len(key) == 1:
            self._binder_buffer += key
        elif key in ("tab",):
            self._binder_buffer += "\t"
        if len(self._binder_buffer) > self._binder_max_len:
            self._binder_buffer = self._binder_buffer[-self._binder_max_len :]

    def _on_binder_enter(self, _event):
        if self._binder_sending:
            return
        match = None
        for trigger, payload in self._binder_map.items():
            if self._binder_buffer.endswith(trigger):
                match = (trigger, payload)
                break
        if match:
            trigger, payload = match
            self._binder_sending = True
            try:
                for _ in range(len(trigger)):
                    keyboard.send("backspace")
                text = self._expand_binder_text(payload["text"])
                self._send_binder_text(text)
                if payload["cursor_back"]:
                    for _ in range(payload["cursor_back"]):
                        keyboard.send("left")
                if "{enter}" not in payload["text"].lower():
                    keyboard.send("enter")
            finally:
                self._binder_sending = False
            self._binder_buffer = ""
            return
        self._binder_sending = True
        try:
            keyboard.send("enter")
        finally:
            self._binder_sending = False
        self._binder_buffer = ""

    def _expand_binder_text(self, text):
        variables = self.config.get("variables", {})
        replacements = {
            "qdis": self.config.get("discord_me", ""),
            "gadis": self.config.get("discord_ga", ""),
            "zgadis": self.config.get("discord_zga", ""),
        }
        def repl(match):
            key = match.group(1)
            if key in replacements:
                return replacements[key]
            return str(variables.get(key, match.group(0)))
        return re.sub(r"%([^%]+)%", repl, text)

    def _send_binder_text(self, text):
        parts = re.split(r"(\{[^}]+\})", text)
        for part in parts:
            if not part:
                continue
            if part.startswith("{") and part.endswith("}"):
                key = part[1:-1].strip()
                if key:
                    keyboard.send(key.lower())
            else:
                keyboard.write(part)

    def _show_variables_form(self, clear=False):
        if not getattr(self, "variables_form_visible", False):
            self.variables_form.pack(fill="x", pady=(0, 10))
            self.variables_form_visible = True
        if clear:
            self.var_key.delete(0, tk.END)
            self.var_value.delete(0, tk.END)
        self.var_key.focus_set()

    def _toggle_variables_list(self):
        if self.variables_list_visible:
            self.variables_list.pack_forget()
            self.variables_list_visible = False
        else:
            self.variables_list.pack(fill="y")
            self.variables_list_visible = True

    def setup_style(self):
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("TFrame", background=THEME["bg"])
        style.configure("Nav.TFrame", background=THEME["panel"])
        style.configure("NavInner.TFrame", background=THEME["panel"])
        style.configure("Card.TFrame", background=THEME["card"], borderwidth=0, relief="flat")
        style.configure("CardBody.TFrame", background=THEME["card"], borderwidth=0, relief="flat")
        style.configure("Subcard.TFrame", background=THEME["card_alt"], borderwidth=0, relief="flat")

        style.configure(
            "TLabel",
            background=THEME["bg"],
            foreground=THEME["fg"],
            font=(FONT_FAMILY, BASE_FONT_SIZE),
        )
        style.configure("Muted.TLabel", background=THEME["bg"], foreground=THEME["muted"])
        style.configure("Card.TLabel", background=THEME["card"], foreground=THEME["fg"])
        style.configure("CardMuted.TLabel", background=THEME["card"], foreground=THEME["muted"])
        style.configure("Subcard.TLabel", background=THEME["card_alt"], foreground=THEME["fg"])
        style.configure(
            "NavTitle.TLabel",
            background=THEME["panel"],
            foreground=THEME["muted"],
            font=(FONT_FAMILY, BASE_FONT_SIZE, "bold"),
        )
        style.configure(
            "ScreenTitle.TLabel",
            background=THEME["bg"],
            foreground=THEME["fg"],
            font=(FONT_FAMILY, TITLE_FONT_SIZE, "bold"),
        )
        style.configure(
            "Section.TLabel",
            background=THEME["card"],
            foreground=THEME["fg"],
            font=(FONT_FAMILY, SECTION_FONT_SIZE, "bold"),
        )

        style.configure(
            "TButton",
            background=THEME["button"],
            foreground=THEME["fg"],
            borderwidth=0,
            focusthickness=0,
            padding=(12, 7),
            font=(FONT_FAMILY, BASE_FONT_SIZE),
        )
        style.map(
            "TButton",
            background=[("active", THEME["accent"]), ("pressed", THEME["accent"])],
            foreground=[("active", THEME["fg"]), ("pressed", THEME["fg"])],
        )
        style.configure(
            "Nav.TButton",
            background=THEME["button"],
            foreground=THEME["fg"],
            borderwidth=0,
            focusthickness=0,
            padding=(14, 9),
            anchor="w",
            font=(FONT_FAMILY, BASE_FONT_SIZE),
        )
        style.map(
            "Nav.TButton",
            background=[("active", THEME["accent"]), ("pressed", THEME["accent"])],
            foreground=[("active", THEME["fg"]), ("pressed", THEME["fg"])],
        )
        style.configure(
            "NavActive.TButton",
            background=THEME["accent_alt"],
            foreground=THEME["fg"],
            borderwidth=0,
            focusthickness=0,
            padding=(14, 9),
            anchor="w",
            font=(FONT_FAMILY, BASE_FONT_SIZE),
        )
        style.map(
            "NavActive.TButton",
            background=[("active", THEME["accent"]), ("pressed", THEME["accent"])],
            foreground=[("active", THEME["fg"]), ("pressed", THEME["fg"])],
        )
        style.configure("Switcher.TButton", padding=(10, 4), font=(FONT_FAMILY, BASE_FONT_SIZE))
        style.configure(
            "SwitcherActive.TButton",
            background=THEME["accent_alt"],
            foreground=THEME["fg"],
            borderwidth=0,
            focusthickness=0,
            padding=(10, 4),
            font=(FONT_FAMILY, BASE_FONT_SIZE),
        )
        style.map(
            "SwitcherActive.TButton",
            background=[("active", THEME["accent"]), ("pressed", THEME["accent"])],
            foreground=[("active", THEME["fg"]), ("pressed", THEME["fg"])],
        )
        style.configure(
            "Muted.TCheckbutton",
            background=THEME["bg"],
            foreground=THEME["muted"],
            font=(FONT_FAMILY, SMALL_FONT_SIZE),
        )
        style.map(
            "Muted.TCheckbutton",
            foreground=[("active", THEME["fg"]), ("selected", THEME["fg"])],
        )

    def build_ui(self):
        header = tk.Canvas(self.root, height=72, highlightthickness=0, bd=0, bg=THEME["bg"])
        header.pack(fill="x")
        self.header_canvas = header
        self.draw_header()
        self.root.bind("<Configure>", self.on_resize)

        main = ttk.Frame(self.root)
        main.pack(fill="both", expand=True, padx=12, pady=12)
        main.columnconfigure(1, weight=1)
        main.rowconfigure(0, weight=1)

        nav = ttk.Frame(main, width=NAV_WIDTH, style="Nav.TFrame")
        nav.grid(row=0, column=0, sticky="ns", padx=(0, 12))

        nav_inner = ttk.Frame(nav, style="NavInner.TFrame", padding=(12, 16))
        nav_inner.pack(fill="both", expand=True)

        ttk.Label(nav_inner, text="НАВИГАЦИЯ", style="NavTitle.TLabel").pack(anchor="w", pady=(0, 8))

        self.nav_buttons = {}
        for name in NAV_BUTTONS:
            btn = self.create_button(
                nav_inner,
                text=name,
                command=lambda n=name: self.show_screen(n),
                kind="nav",
                expand_x=True,
            )
            btn.pack(fill="x", pady=4)
            self.nav_buttons[name] = btn

        self.content = ttk.Frame(main)
        self.content.grid(row=0, column=1, sticky="nsew")

        self.create_screens()
        self.build_commands_screen()
        self.build_phrases_screen()
        self.build_autofix_screen()
        self.build_variables_screen()
        self.build_profiles_screen()
        self.build_import_export_screen()
        self.build_info_screen()
        self.build_settings_screen()

        self.show_screen("Команды")
        self.update_info_files()
        self.root.bind_all("<Control-f>", self.focus_search)

    def on_resize(self, _event):
        if hasattr(self, "header_canvas"):
            self._schedule_header_redraw(_event)

    def draw_header(self):
        canvas = self.header_canvas
        self._header_resize_after = None
        canvas.delete("all")
        width = self.root.winfo_width() or 1080
        height = int(canvas["height"])
        color_a = hex_to_rgb(THEME["header_from"])
        color_b = hex_to_rgb(THEME["header_to"])
        steps = max(1, height)
        for i in range(steps):
            t = i / max(1, steps - 1)
            color = rgb_to_hex(blend(color_a, color_b, t))
            canvas.create_rectangle(0, i, width, i + 1, outline="", fill=color)
        canvas.create_text(
            16,
            height // 2,
            text="MajesticRP Binder",
            anchor="w",
            fill=THEME["fg"],
            font=(FONT_FAMILY, HEADER_FONT_SIZE, "bold"),
        )
        canvas.create_text(
            width - 16,
            height // 2,
            text="Admin Toolkit",
            anchor="e",
            fill=THEME["muted"],
            font=(FONT_FAMILY, BASE_FONT_SIZE),
        )

    def _schedule_header_redraw(self, event=None):
        if event is not None and event.widget is not self.root:
            return False
        width = event.width if event is not None else self.root.winfo_width()
        height = event.height if event is not None else self.root.winfo_height()
        size = (width, height)
        if getattr(self, "_header_last_size", None) == size:
            return True
        self._header_last_size = size
        if getattr(self, "_header_resize_after", None):
            self.root.after_cancel(self._header_resize_after)
        self._header_resize_after = self.root.after(60, self.draw_header)
        return True

    def create_screens(self):
        self.screens = {}
        for name in NAV_BUTTONS + EXTRA_SCREENS:
            frame = ttk.Frame(self.content)
            frame.grid(row=0, column=0, sticky="nsew")
            self.screens[name] = frame

    def show_screen(self, name):
        self.screens[name].tkraise()
        for key, btn in self.nav_buttons.items():
            if key == name:
                btn.set_colors(THEME["accent_alt"], THEME["accent"], THEME["accent"])
            else:
                btn.set_colors(THEME["button"], THEME["accent_alt"], THEME["accent"])
        self.update_manage_switcher(name)
        self.active_screen = name

    def build_screen_shell(self, screen_name, title, subtitle=None):
        parent = self.screens[screen_name]
        header = ttk.Frame(parent)
        header.pack(fill="x", padx=16, pady=(10, 6))

        ttk.Label(header, text=title, style="ScreenTitle.TLabel").pack(anchor="w")
        if subtitle:
            ttk.Label(header, text=subtitle, style="Muted.TLabel").pack(anchor="w", pady=(2, 0))

        card = ttk.Frame(parent, style="Card.TFrame", padding=12)
        card.pack(fill="both", expand=True, padx=16, pady=(0, 14))
        return card

    def add_section_header(self, parent, text):
        ttk.Label(parent, text=text, style="Section.TLabel").pack(anchor="w", pady=(0, 6))

    def add_manage_switcher(self, parent):
        switcher = ttk.Frame(parent, style="CardBody.TFrame")
        switcher.pack(fill="x", pady=(0, 10))
        btn_commands = self.create_button(
            switcher,
            text="Команды",
            command=lambda: self.show_screen("Команды"),
            kind="switcher",
        )
        btn_commands.pack(side="left", padx=(0, 6))
        btn_phrases = self.create_button(
            switcher,
            text="Фразы",
            command=lambda: self.show_screen("Фразы"),
            kind="switcher",
        )
        btn_phrases.pack(side="left", padx=(0, 6))
        btn_autofix = self.create_button(
            switcher,
            text="Автоисправление",
            command=lambda: self.show_screen("Автоисправление"),
            kind="switcher",
        )
        btn_autofix.pack(side="left")
        self.manage_switcher = {
            "Команды": btn_commands,
            "Фразы": btn_phrases,
            "Автоисправление": btn_autofix,
        }

    def update_manage_switcher(self, active_name):
        if not hasattr(self, "manage_switcher"):
            return
        for name, btn in self.manage_switcher.items():
            if name == active_name:
                btn.set_colors(THEME["accent_alt"], THEME["accent"], THEME["accent"])
            else:
                btn.set_colors(THEME["button"], THEME["accent_alt"], THEME["accent"])

    def create_button(self, parent, text, command, kind="default", expand_x=False):
        if kind == "nav":
            bg = THEME["button"]
            hover = THEME["accent_alt"]
            active = THEME["accent"]
            canvas_bg = THEME["panel"]
            padding = (14, 9)
            radius = 999
            font = tkfont.Font(family=FONT_FAMILY, size=BASE_FONT_SIZE)
            width = None
        elif kind == "nav_active":
            bg = THEME["accent_alt"]
            hover = THEME["accent"]
            active = THEME["accent"]
            canvas_bg = THEME["panel"]
            padding = (14, 9)
            radius = 999
            font = tkfont.Font(family=FONT_FAMILY, size=BASE_FONT_SIZE)
            width = None
        elif kind == "switcher":
            bg = THEME["button"]
            hover = THEME["accent_alt"]
            active = THEME["accent"]
            canvas_bg = THEME["bg"]
            padding = (12, 6)
            radius = 999
            font = tkfont.Font(family=FONT_FAMILY, size=BASE_FONT_SIZE)
            width = None
        elif kind == "primary":
            bg = THEME["accent"]
            hover = THEME["accent"]
            active = THEME["accent"]
            canvas_bg = THEME["bg"]
            padding = (12, 7)
            radius = 999
            font = tkfont.Font(family=FONT_FAMILY, size=BASE_FONT_SIZE, weight="bold")
            width = None
        else:
            bg = THEME["button"]
            hover = THEME["accent_alt"]
            active = THEME["accent"]
            canvas_bg = THEME["bg"]
            padding = (12, 7)
            radius = 999
            font = tkfont.Font(family=FONT_FAMILY, size=BASE_FONT_SIZE)
            width = None

        if expand_x and kind not in ("nav", "nav_active"):
            width = self._content_button_chars(font, padding)

        return RoundedButton(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg=THEME["fg"],
            hover_bg=hover,
            active_bg=active,
            canvas_bg=canvas_bg,
            font=font,
            padding=padding,
            radius=radius,
            expand_x=expand_x,
            width=width,
        )

    def load_list(self, path):
        data = load_json(path, [])
        return data if isinstance(data, list) else []

    def load_dict(self, path, default_data):
        data = load_json(path, default_data)
        return data if isinstance(data, dict) else default_data

    def bind_get_text(self, item):
        if isinstance(item, dict):
            return item.get("text") or item.get("response") or ""
        return ""

    def bind_set_text(self, item, value):
        if "response" in item and "text" not in item:
            item["response"] = value
            return
        item["text"] = value
        if "response" in item:
            item["response"] = value

    def maybe_add_alias(self, data_list, trigger, text, cursor_back, label):
        if not self.config.get("auto_alias_ru", True):
            return False
        alias = ru_to_en(trigger)
        if alias == trigger:
            return False
        if any(item.get("trigger") == alias for item in data_list):
            return False
        alias_item = {"trigger": alias, "text": text}
        if cursor_back:
            alias_item["cursor_back"] = cursor_back
        data_list.append(alias_item)
        self.append_log("Добавлено", f"{label} (алиас): {alias} -> {text}")
        return True

    def append_log(self, action, details):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{ts}] {action}: {details}\n"
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(line)

    def should_update_info(self):
        return self.config.get("auto_update_info", True)

    def format_info_line(self, item):
        trigger = item.get("trigger", "")
        text = item.get("text", "")
        cursor = item.get("cursor_back", 0)
        suffix = f" (cursor_back={cursor})" if cursor else ""
        return f"{trigger} -> {text}{suffix}"

    def write_info_file(self, filename, lines, title=None):
        path = os.path.join(HELP_DIR, filename)
        body = "\n".join(lines).strip()
        if title:
            content = f"{title}\n{body}\n" if body else f"{title}\n"
        else:
            content = f"{body}\n" if body else ""
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    def update_info_files(self):
        if not self.should_update_info():
            return
        def unique_by_trigger(items):
            seen = set()
            result = []
            for item in items:
                trigger = item.get("trigger", "")
                if trigger in seen:
                    continue
                seen.add(trigger)
                result.append(item)
            return result

        commands_items = unique_by_trigger(self.commands_data)
        phrases_items = unique_by_trigger(self.phrases_data)

        teleports_items = []
        commands_for_hints = []
        for item in commands_items:
            text = item.get("text", "").strip().lower()
            if text.startswith("/ctp"):
                teleports_items.append(item)
            else:
                commands_for_hints.append(item)

        used_triggers = {item.get("trigger", "") for item in commands_for_hints}
        phrases_for_hints = []
        for item in phrases_items:
            trigger = item.get("trigger", "")
            if trigger in used_triggers:
                continue
            used_triggers.add(trigger)
            phrases_for_hints.append(item)

        commands_lines = [self.format_info_line(item) for item in commands_for_hints]
        phrases_lines = [self.format_info_line(item) for item in phrases_for_hints]
        autofix_lines = []
        for key, label in (("layout", "Раскладка"), ("custom", "Пользовательские")):
            for item in self.autofix_data.get(key, []):
                autofix_lines.append(f'{label}: {item.get("from", "")} -> {item.get("to", "")}')

        variables_lines = []
        for key in sorted(self.variables.keys()) if hasattr(self, "variables") else []:
            variables_lines.append(f"{key} = {self.variables.get(key)}")

        profiles_lines = list(self.profiles_data) if hasattr(self, "profiles_data") else []

        hint_blocks = []
        if commands_lines:
            hint_blocks.append("Команды")
            hint_blocks.extend(commands_lines)
            hint_blocks.append("")
        if phrases_lines:
            hint_blocks.append("Фразы")
            hint_blocks.extend(phrases_lines)
            hint_blocks.append("")
        if autofix_lines:
            hint_blocks.append("Автоисправление")
            hint_blocks.extend(autofix_lines)
            hint_blocks.append("")
        if variables_lines:
            hint_blocks.append("Переменные")
            hint_blocks.extend(variables_lines)
            hint_blocks.append("")
        if profiles_lines:
            hint_blocks.append("Профили")
            hint_blocks.extend(profiles_lines)
            hint_blocks.append("")

        self.write_info_file("hints.txt", hint_blocks)

        teleports = [self.format_info_line(item) for item in teleports_items]
        self.write_info_file("teleport.txt", teleports, title="Телепорты")

    def open_log_window(self):
        win = tk.Toplevel(self.root)
        win.title("Log")
        win.geometry("640x460")
        win.configure(bg=THEME["bg"])

        text = tk.Text(win, wrap="word")
        text.pack(fill="both", expand=True, padx=10, pady=10)
        style_text(text)

        try:
            with open(LOG_PATH, "r", encoding="utf-8") as f:
                text.insert("1.0", f.read())
        except FileNotFoundError:
            text.insert("1.0", "Log пуст.")

        text.config(state="disabled")

    def build_info_screen(self):
        card = self.build_screen_shell(
            "Информация",
            "Информация",
            "Справка и полезные материалы (открываются в отдельном окне).",
        )

        for title, filename in INFO_BUTTONS:
            path = os.path.join(HELP_DIR, filename)
            btn = self.create_button(
                card,
                text=title,
                command=lambda t=title, p=path: self.open_text_window(t, p),
                expand_x=True,
            )
            self.pack_content_button(btn, pady=4)

    def open_text_window(self, title, path):
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry("620x460")
        win.configure(bg=THEME["bg"])

        text = tk.Text(win, wrap="word")
        text.pack(fill="both", expand=True, padx=10, pady=10)
        style_text(text)

        try:
            with open(path, "r", encoding="utf-8") as f:
                text.insert("1.0", f.read())
        except FileNotFoundError:
            text.insert("1.0", "Файл не найден")

        text.config(state="disabled")

    def build_commands_screen(self):
        self.commands_data = self.load_list(BINDS_PATH)
        self.commands_ui = self.build_bind_editor(
            screen_name="Команды",
            title="Команды",
            subtitle="Редактор триггеров и ответов.",
            data_path=BINDS_PATH,
            data_ref="commands_data",
        )
        self.refresh_bind_list(self.commands_ui, self.commands_data)

    def build_phrases_screen(self):
        self.phrases_data = self.load_list(PHRASES_PATH)
        self.phrases_ui = self.build_bind_editor(
            screen_name="Фразы",
            title="Фразы",
            subtitle="RP-фразы и шаблоны общения.",
            data_path=PHRASES_PATH,
            data_ref="phrases_data",
        )
        self.refresh_bind_list(self.phrases_ui, self.phrases_data)

    def build_bind_editor(self, screen_name, title, subtitle, data_path, data_ref):
        card = self.build_screen_shell(screen_name, title, subtitle)
        self.add_manage_switcher(card)

        main = ttk.Frame(card, style="CardBody.TFrame")
        main.pack(fill="both", expand=True)

        list_panel = ttk.Frame(main, style="CardBody.TFrame")
        list_panel.pack(side="left", fill="y", padx=(0, 12))

        search_row = ttk.Frame(list_panel, style="CardBody.TFrame")
        search_row.pack(fill="x", pady=(0, 8))

        search_entry = tk.Entry(search_row)
        search_entry.pack(side="left", fill="x", expand=True)
        style_entry(search_entry)

        reset_btn = self.create_button(
            search_row,
            text="Сброс",
            command=None,
            kind="switcher",
        )
        reset_btn.pack(side="left", padx=(6, 0))

        listbox = tk.Listbox(main, width=26)
        listbox.pack(in_=list_panel, fill="y")
        style_listbox(listbox)

        right = ttk.Frame(main, style="CardBody.TFrame")
        right.pack(fill="both", expand=True)

        ttk.Label(right, text="Триггер", style="Card.TLabel").pack(anchor="w")
        trigger_entry = tk.Entry(right)
        trigger_entry.pack(fill="x", pady=(2, 10))
        style_entry(trigger_entry)

        ttk.Label(right, text="Текст", style="Card.TLabel").pack(anchor="w")
        text_entry = tk.Text(right, height=8)
        text_entry.pack(fill="both", expand=True)
        style_text(text_entry)

        ttk.Label(right, text="Сдвиг курсора", style="Card.TLabel").pack(anchor="w", pady=(10, 0))
        cursor_entry = tk.Entry(right)
        cursor_entry.pack(fill="x", pady=(2, 10))
        style_entry(cursor_entry)
        ttk.Label(
            right,
            text="Число шагов назад после вставки текста",
            style="CardMuted.TLabel",
        ).pack(anchor="w", pady=(0, 10))

        btns = ttk.Frame(right, style="CardBody.TFrame")
        btns.pack(pady=10)

        ui = {
            "listbox": listbox,
            "trigger": trigger_entry,
            "text": text_entry,
            "cursor": cursor_entry,
            "search": search_entry,
            "reset": reset_btn,
            "index_map": [],
            "path": data_path,
            "data_ref": data_ref,
            "label": title,
        }
        if not hasattr(self, "search_entries"):
            self.search_entries = {}
        self.search_entries[screen_name] = search_entry

        self.create_button(btns, text="Добавить", command=lambda: self.bind_add(ui)).pack(
            side="left", padx=4
        )
        self.create_button(btns, text="Изменить", command=lambda: self.bind_update(ui)).pack(
            side="left", padx=4
        )
        self.create_button(btns, text="Удалить", command=lambda: self.bind_delete(ui)).pack(
            side="left", padx=4
        )

        listbox.bind("<<ListboxSelect>>", lambda e: self.bind_on_select(ui))
        search_entry.bind("<KeyRelease>", lambda e: self.apply_bind_filter(ui))
        reset_btn.set_command(lambda: self.clear_bind_filter(ui))
        return ui

    def focus_search(self, _event=None):
        screen = getattr(self, "active_screen", None)
        if not screen or not hasattr(self, "search_entries"):
            return
        entry = self.search_entries.get(screen)
        if not entry:
            return
        entry.focus_set()
        entry.selection_range(0, tk.END)

    def refresh_bind_list(self, ui, data_list):
        query = ui["search"].get().strip().lower() if ui.get("search") else ""
        ui["listbox"].delete(0, tk.END)
        ui["index_map"] = []
        for idx, item in enumerate(data_list):
            trigger = item.get("trigger", "") if isinstance(item, dict) else ""
            text_value = self.bind_get_text(item).lower()
            if query and query not in trigger.lower() and query not in text_value:
                continue
            label = trigger if trigger else "<без триггера>"
            ui["listbox"].insert(tk.END, label)
            ui["index_map"].append(idx)

    def apply_bind_filter(self, ui):
        data_list = getattr(self, ui["data_ref"])
        self.refresh_bind_list(ui, data_list)

    def clear_bind_filter(self, ui):
        ui["search"].delete(0, tk.END)
        data_list = getattr(self, ui["data_ref"])
        self.refresh_bind_list(ui, data_list)

    def get_selected_index(self, ui):
        selection = ui["listbox"].curselection()
        if not selection:
            return None
        idx = selection[0]
        if idx >= len(ui["index_map"]):
            return None
        return ui["index_map"][idx]

    def bind_on_select(self, ui):
        idx = self.get_selected_index(ui)
        if idx is None:
            return
        data_list = getattr(self, ui["data_ref"])
        if idx >= len(data_list):
            return
        item = data_list[idx]
        ui["trigger"].delete(0, tk.END)
        ui["trigger"].insert(0, item.get("trigger", ""))
        ui["text"].delete("1.0", tk.END)
        ui["text"].insert("1.0", self.bind_get_text(item))
        ui["cursor"].delete(0, tk.END)
        cursor_back = item.get("cursor_back", 0)
        ui["cursor"].insert(0, str(cursor_back) if cursor_back else "")

    def bind_add(self, ui):
        trigger = ui["trigger"].get().strip()
        text = ui["text"].get("1.0", tk.END).strip()
        cursor_raw = ui["cursor"].get().strip()
        if not trigger or not text:
            messagebox.showwarning("Проверьте данные", "Заполните триггер и текст.")
            return
        if cursor_raw and not cursor_raw.isdigit():
            messagebox.showwarning("Проверьте данные", "Сдвиг курсора должен быть числом.")
            return
        cursor_back = int(cursor_raw) if cursor_raw else 0
        data_list = getattr(self, ui["data_ref"])
        item = {"trigger": trigger, "text": text}
        if cursor_back:
            item["cursor_back"] = cursor_back
        original_index = len(data_list)
        data_list.append(item)
        if ui["label"] == "Команды":
            self.maybe_add_alias(data_list, trigger, text, cursor_back, ui["label"])
        save_json(ui["path"], data_list)
        self._reload_binder_map()
        self.append_log("Добавлено", f'{ui["label"]}: {trigger} -> {text}')
        self.update_info_files()
        self.refresh_bind_list(ui, data_list)
        if original_index in ui["index_map"]:
            ui["listbox"].selection_clear(0, tk.END)
            ui["listbox"].selection_set(ui["index_map"].index(original_index))

    def bind_update(self, ui):
        idx = self.get_selected_index(ui)
        if idx is None:
            messagebox.showwarning("Нет выбора", "Выберите элемент для изменения.")
            return
        trigger = ui["trigger"].get().strip()
        text = ui["text"].get("1.0", tk.END).strip()
        cursor_raw = ui["cursor"].get().strip()
        if not trigger or not text:
            messagebox.showwarning("Проверьте данные", "Заполните триггер и текст.")
            return
        if cursor_raw and not cursor_raw.isdigit():
            messagebox.showwarning("Проверьте данные", "Сдвиг курсора должен быть числом.")
            return
        cursor_back = int(cursor_raw) if cursor_raw else 0
        data_list = getattr(self, ui["data_ref"])
        if idx >= len(data_list):
            return
        item = data_list[idx]
        old_trigger = item.get("trigger", "")
        old_text = self.bind_get_text(item)
        item["trigger"] = trigger
        self.bind_set_text(item, text)
        if cursor_back:
            item["cursor_back"] = cursor_back
        else:
            item.pop("cursor_back", None)
        if ui["label"] == "Команды":
            self.maybe_add_alias(data_list, trigger, text, cursor_back, ui["label"])
        save_json(ui["path"], data_list)
        self._reload_binder_map()
        self.append_log(
            "Изменено",
            f'{ui["label"]}: {old_trigger} -> {old_text} | {trigger} -> {text}',
        )
        self.update_info_files()
        self.refresh_bind_list(ui, data_list)
        if idx in ui["index_map"]:
            ui["listbox"].selection_clear(0, tk.END)
            ui["listbox"].selection_set(ui["index_map"].index(idx))

    def bind_delete(self, ui):
        idx = self.get_selected_index(ui)
        if idx is None:
            messagebox.showwarning("Нет выбора", "Выберите элемент для удаления.")
            return
        data_list = getattr(self, ui["data_ref"])
        if idx >= len(data_list):
            return
        if not messagebox.askyesno("Подтвердите", "Удалить выбранный элемент?"):
            return
        item = data_list[idx]
        old_trigger = item.get("trigger", "")
        old_text = self.bind_get_text(item)
        data_list.pop(idx)
        save_json(ui["path"], data_list)
        self._reload_binder_map()
        self.append_log("Удалено", f'{ui["label"]}: {old_trigger} -> {old_text}')
        self.update_info_files()
        self.refresh_bind_list(ui, data_list)
        ui["trigger"].delete(0, tk.END)
        ui["text"].delete("1.0", tk.END)

    def build_autofix_screen(self):
        card = self.build_screen_shell(
            "Автоисправление",
            "Автоисправление",
            "Автоматическая замена текста при вводе.",
        )
        self.add_manage_switcher(card)

        self.autofix_data = self.load_dict(AUTOFIX_PATH, {"layout": [], "custom": []})

        self.add_section_header(card, "Раскладка (ru → en)")
        layout_ui = self.build_autofix_group(card, "layout")
        spacer = ttk.Frame(card, height=10, style="CardBody.TFrame")
        spacer.pack(fill="x")
        self.add_section_header(card, "Пользовательские замены")
        custom_ui = self.build_autofix_group(card, "custom")

        self.autofix_ui = {"layout": layout_ui, "custom": custom_ui}
        self.refresh_autofix_list("layout")
        self.refresh_autofix_list("custom")

    def build_autofix_group(self, parent, key):
        group = ttk.Frame(parent, style="Subcard.TFrame", padding=12)
        group.pack(fill="both", expand=True)

        main = ttk.Frame(group, style="Subcard.TFrame")
        main.pack(fill="both", expand=True)

        listbox = tk.Listbox(main, width=26)
        listbox.pack(side="left", fill="y", padx=(0, 12))
        style_listbox(listbox)

        right = ttk.Frame(main, style="Subcard.TFrame")
        right.pack(fill="both", expand=True)

        ttk.Label(right, text="Из", style="Subcard.TLabel").pack(anchor="w")
        from_entry = tk.Entry(right)
        from_entry.pack(fill="x", pady=(2, 10))
        style_entry(from_entry)

        ttk.Label(right, text="В", style="Subcard.TLabel").pack(anchor="w")
        to_entry = tk.Entry(right)
        to_entry.pack(fill="x", pady=(2, 10))
        style_entry(to_entry)

        btns = ttk.Frame(right, style="Subcard.TFrame")
        btns.pack(pady=6)

        ui = {
            "key": key,
            "listbox": listbox,
            "from": from_entry,
            "to": to_entry,
            "label": "Автоисправление",
        }

        self.create_button(btns, text="Добавить", command=lambda: self.autofix_add(ui)).pack(
            side="left", padx=4
        )
        self.create_button(btns, text="Изменить", command=lambda: self.autofix_update(ui)).pack(
            side="left", padx=4
        )
        self.create_button(btns, text="Удалить", command=lambda: self.autofix_delete(ui)).pack(
            side="left", padx=4
        )

        listbox.bind("<<ListboxSelect>>", lambda e: self.autofix_on_select(ui))
        return ui

    def refresh_autofix_list(self, key):
        ui = self.autofix_ui[key]
        ui["listbox"].delete(0, tk.END)
        for item in self.autofix_data.get(key, []):
            label = f'{item.get("from", "")} → {item.get("to", "")}'
            ui["listbox"].insert(tk.END, label)

    def autofix_on_select(self, ui):
        selection = ui["listbox"].curselection()
        if not selection:
            return
        idx = selection[0]
        items = self.autofix_data.get(ui["key"], [])
        if idx >= len(items):
            return
        item = items[idx]
        ui["from"].delete(0, tk.END)
        ui["from"].insert(0, item.get("from", ""))
        ui["to"].delete(0, tk.END)
        ui["to"].insert(0, item.get("to", ""))

    def autofix_add(self, ui):
        from_val = ui["from"].get().strip()
        to_val = ui["to"].get().strip()
        if not from_val or not to_val:
            messagebox.showwarning("Проверьте данные", "Заполните оба поля.")
            return
        items = self.autofix_data.setdefault(ui["key"], [])
        items.append({"from": from_val, "to": to_val})
        save_json(AUTOFIX_PATH, self.autofix_data)
        self.append_log("Добавлено", f'{ui["label"]} ({ui["key"]}): {from_val} -> {to_val}')
        self.update_info_files()
        self.refresh_autofix_list(ui["key"])
        ui["listbox"].selection_clear(0, tk.END)
        ui["listbox"].selection_set(tk.END)

    def autofix_update(self, ui):
        selection = ui["listbox"].curselection()
        if not selection:
            messagebox.showwarning("Нет выбора", "Выберите элемент для изменения.")
            return
        idx = selection[0]
        from_val = ui["from"].get().strip()
        to_val = ui["to"].get().strip()
        if not from_val or not to_val:
            messagebox.showwarning("Проверьте данные", "Заполните оба поля.")
            return
        items = self.autofix_data.get(ui["key"], [])
        if idx >= len(items):
            return
        old = items[idx]
        items[idx] = {"from": from_val, "to": to_val}
        save_json(AUTOFIX_PATH, self.autofix_data)
        self.append_log(
            "Изменено",
            f'{ui["label"]} ({ui["key"]}): {old.get("from")} -> {old.get("to")} | {from_val} -> {to_val}',
        )
        self.update_info_files()
        self.refresh_autofix_list(ui["key"])
        ui["listbox"].selection_clear(0, tk.END)
        ui["listbox"].selection_set(idx)

    def autofix_delete(self, ui):
        selection = ui["listbox"].curselection()
        if not selection:
            messagebox.showwarning("Нет выбора", "Выберите элемент для удаления.")
            return
        idx = selection[0]
        items = self.autofix_data.get(ui["key"], [])
        if idx >= len(items):
            return
        if not messagebox.askyesno("Подтвердите", "Удалить выбранный элемент?"):
            return
        old = items.pop(idx)
        save_json(AUTOFIX_PATH, self.autofix_data)
        self.append_log(
            "Удалено",
            f'{ui["label"]} ({ui["key"]}): {old.get("from")} -> {old.get("to")}',
        )
        self.update_info_files()
        self.refresh_autofix_list(ui["key"])
        ui["from"].delete(0, tk.END)
        ui["to"].delete(0, tk.END)

    def build_variables_screen(self):
        card = self.build_screen_shell(
            "Переменные",
            "Переменные",
            "Переменные доступны в командах и фразах.",
        )

        ttk.Label(card, text="Discord-переменные задаются в настройках.", style="CardMuted.TLabel").pack(
            anchor="w", pady=(0, 10)
        )

        main = ttk.Frame(card, style="CardBody.TFrame")
        main.pack(fill="both", expand=True)

        left = ttk.Frame(main, style="CardBody.TFrame")
        left.pack(side="left", fill="y", padx=(0, 12))

        self.variables_list_visible = False
        btn_show_list = self.create_button(
            left,
            text="Добавленные",
            command=self._toggle_variables_list,
        )
        btn_show_list.pack(pady=(0, 8))

        self.variables_list = tk.Listbox(left, width=28)
        style_listbox(self.variables_list)

        right = ttk.Frame(main, style="CardBody.TFrame")
        right.pack(fill="both", expand=True)

        self.variables_form = ttk.Frame(right, style="CardBody.TFrame")
        self.variables_form_visible = False

        ttk.Label(self.variables_form, text="Имя", style="Card.TLabel").pack(anchor="w")
        self.var_key = tk.Entry(self.variables_form)
        self.var_key.pack(fill="x", pady=(2, 10))
        style_entry(self.var_key)

        ttk.Label(self.variables_form, text="Значение", style="Card.TLabel").pack(anchor="w")
        self.var_value = tk.Entry(self.variables_form)
        self.var_value.pack(fill="x", pady=(2, 10))
        style_entry(self.var_value)

        btns = ttk.Frame(right, style="CardBody.TFrame")
        btns.pack(pady=6)

        self.create_button(btns, text="Добавить", command=self.variables_add).pack(side="left", padx=4)
        self.create_button(btns, text="Изменить", command=self.variables_update).pack(side="left", padx=4)
        self.create_button(btns, text="Удалить", command=self.variables_delete).pack(side="left", padx=4)

        self.variables_list.bind("<<ListboxSelect>>", self.variables_on_select)
        self.refresh_variables_list()

    def refresh_variables_list(self):
        self.variables = self.config.get("variables", {})
        self.variables_list.delete(0, tk.END)
        for key in sorted(self.variables.keys()):
            self.variables_list.insert(tk.END, f"{key} = {self.variables[key]}")

    def variables_on_select(self, _):
        selection = self.variables_list.curselection()
        if not selection:
            return
        idx = selection[0]
        key = sorted(self.variables.keys())[idx]
        self.var_key.delete(0, tk.END)
        self.var_key.insert(0, key)
        self.var_value.delete(0, tk.END)
        self.var_value.insert(0, str(self.variables.get(key, "")))

    def variables_add(self):
        if not self.variables_form_visible:
            self._show_variables_form(clear=True)
            return
        key = self.var_key.get().strip()
        value = self.var_value.get().strip()
        if not key or not value:
            messagebox.showwarning("Проверьте данные", "Заполните оба поля.")
            return
        self.config.setdefault("variables", {})[key] = value
        save_config(self.config)
        self.append_log("Добавлено", f"Переменные: {key} = {value}")
        self.update_info_files()
        self.refresh_variables_list()

    def variables_update(self):
        if not self.variables_form_visible:
            self._show_variables_form()
            return
        selection = self.variables_list.curselection()
        if not selection:
            messagebox.showwarning("Нет выбора", "Выберите элемент для изменения.")
            return
        key = self.var_key.get().strip()
        value = self.var_value.get().strip()
        if not key or not value:
            messagebox.showwarning("Проверьте данные", "Заполните оба поля.")
            return
        original_key = sorted(self.variables.keys())[selection[0]]
        old_value = self.variables.get(original_key, "")
        if key != original_key:
            self.variables.pop(original_key, None)
        self.variables[key] = value
        self.config["variables"] = self.variables
        save_config(self.config)
        self.append_log(
            "Изменено",
            f"Переменные: {original_key} = {old_value} | {key} = {value}",
        )
        self.update_info_files()
        self.refresh_variables_list()

    def variables_delete(self):
        selection = self.variables_list.curselection()
        if not selection:
            messagebox.showwarning("Нет выбора", "Выберите элемент для удаления.")
            return
        key = sorted(self.variables.keys())[selection[0]]
        if not messagebox.askyesno("Подтвердите", "Удалить переменную?"):
            return
        old_value = self.variables.pop(key, None)
        self.config["variables"] = self.variables
        save_config(self.config)
        self.append_log("Удалено", f"Переменные: {key} = {old_value}")
        self.update_info_files()
        self.refresh_variables_list()
        self.var_key.delete(0, tk.END)
        self.var_value.delete(0, tk.END)

    def build_profiles_screen(self):
        card = self.build_screen_shell(
            "Профили",
            "Профили",
            "Наборы команд, фраз и автозамен.",
        )

        self.profiles_data = self.load_list(PROFILES_PATH)
        if not self.profiles_data:
            self.profiles_data = ["default"]
            save_json(PROFILES_PATH, self.profiles_data)

        self.active_profile = self.config.get("active_profile", self.profiles_data[0])
        if self.active_profile not in self.profiles_data:
            self.active_profile = self.profiles_data[0]
            self.config["active_profile"] = self.active_profile
            save_config(self.config)

        self.profile_label = ttk.Label(
            card,
            text=f"Активный профиль: {self.active_profile}",
            style="CardMuted.TLabel",
        )
        self.profile_label.pack(anchor="w", pady=(0, 10))

        main = ttk.Frame(card, style="CardBody.TFrame")
        main.pack(fill="both", expand=True)

        self.profiles_list = tk.Listbox(main, width=26)
        self.profiles_list.pack(side="left", fill="y", padx=(0, 12))
        style_listbox(self.profiles_list)

        right = ttk.Frame(main, style="CardBody.TFrame")
        right.pack(fill="both", expand=True)

        ttk.Label(right, text="Имя профиля", style="Card.TLabel").pack(anchor="w")
        self.profile_entry = tk.Entry(right)
        self.profile_entry.pack(fill="x", pady=(2, 10))
        style_entry(self.profile_entry)

        btns = ttk.Frame(right, style="CardBody.TFrame")
        btns.pack(pady=6)

        self.create_button(btns, text="Добавить", command=self.profiles_add).pack(side="left", padx=4)
        self.create_button(btns, text="Удалить", command=self.profiles_delete).pack(side="left", padx=4)
        self.create_button(btns, text="Сделать активным", command=self.profiles_set_active).pack(
            side="left", padx=4
        )

        self.profiles_list.bind("<<ListboxSelect>>", self.profiles_on_select)
        self.refresh_profiles_list()

    def refresh_profiles_list(self):
        self.profiles_list.delete(0, tk.END)
        for name in self.profiles_data:
            self.profiles_list.insert(tk.END, name)

    def profiles_on_select(self, _):
        selection = self.profiles_list.curselection()
        if not selection:
            return
        idx = selection[0]
        if idx >= len(self.profiles_data):
            return
        self.profile_entry.delete(0, tk.END)
        self.profile_entry.insert(0, self.profiles_data[idx])

    def profiles_add(self):
        name = self.profile_entry.get().strip()
        if not name:
            messagebox.showwarning("Проверьте данные", "Введите имя профиля.")
            return
        if name in self.profiles_data:
            messagebox.showwarning("Дубликат", "Такой профиль уже существует.")
            return
        self.profiles_data.append(name)
        save_json(PROFILES_PATH, self.profiles_data)
        self.append_log("Добавлено", f"Профили: {name}")
        self.update_info_files()
        self.refresh_profiles_list()

    def profiles_delete(self):
        selection = self.profiles_list.curselection()
        if not selection:
            messagebox.showwarning("Нет выбора", "Выберите профиль для удаления.")
            return
        idx = selection[0]
        name = self.profiles_data[idx]
        if name == self.active_profile:
            messagebox.showwarning("Нельзя удалить", "Сначала выберите другой активный профиль.")
            return
        if not messagebox.askyesno("Подтвердите", f"Удалить профиль '{name}'?"):
            return
        self.profiles_data.pop(idx)
        save_json(PROFILES_PATH, self.profiles_data)
        self.append_log("Удалено", f"Профили: {name}")
        self.update_info_files()
        self.refresh_profiles_list()
        self.profile_entry.delete(0, tk.END)

    def profiles_set_active(self):
        selection = self.profiles_list.curselection()
        if not selection:
            messagebox.showwarning("Нет выбора", "Выберите профиль.")
            return
        idx = selection[0]
        if idx >= len(self.profiles_data):
            return
        old = self.active_profile
        self.active_profile = self.profiles_data[idx]
        self.config["active_profile"] = self.active_profile
        save_config(self.config)
        self.profile_label.config(text=f"Активный профиль: {self.active_profile}")
        self.append_log("Изменено", f"Профили: активный {old} -> {self.active_profile}")
        self.update_info_files()

    def build_import_export_screen(self):
        card = self.build_screen_shell(
            "Импорт / Экспорт",
            "Импорт / Экспорт",
            "Сохранение и восстановление данных биндера.",
        )

        btn_export = self.create_button(card, text="Экспортировать данные", command=self.export_data, expand_x=True)
        self.pack_content_button(btn_export, pady=6)
        btn_import = self.create_button(card, text="Импортировать данные", command=self.import_data, expand_x=True)
        self.pack_content_button(btn_import, pady=6)

    def export_data(self):
        path = filedialog.asksaveasfilename(
            title="Экспорт данных",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
        )
        if not path:
            return
        payload = {
            "config": load_json(CONFIG_PATH, {}),
            "binds": load_json(BINDS_PATH, []),
            "phrases": load_json(PHRASES_PATH, []),
            "autofix": load_json(AUTOFIX_PATH, {"layout": [], "custom": []}),
            "profiles": load_json(PROFILES_PATH, ["default"]),
        }
        save_json(path, payload)
        messagebox.showinfo("Готово", "Данные экспортированы.")

    def import_data(self):
        path = filedialog.askopenfilename(
            title="Импорт данных",
            filetypes=[("JSON files", "*.json")],
        )
        if not path:
            return
        data = load_json(path, {})
        if not isinstance(data, dict):
            messagebox.showwarning("Ошибка", "Файл импорта повреждён.")
            return
        if "config" in data:
            save_json(CONFIG_PATH, data["config"])
            self.config = load_config()
            self.refresh_variables_list()
            self.active_profile = self.config.get("active_profile", self.active_profile)
        if "binds" in data:
            save_json(BINDS_PATH, data["binds"])
            self.commands_data = self.load_list(BINDS_PATH)
            self.refresh_bind_list(self.commands_ui, self.commands_data)
        if "phrases" in data:
            save_json(PHRASES_PATH, data["phrases"])
            self.phrases_data = self.load_list(PHRASES_PATH)
            self.refresh_bind_list(self.phrases_ui, self.phrases_data)
        if "autofix" in data:
            save_json(AUTOFIX_PATH, data["autofix"])
            self.autofix_data = self.load_dict(AUTOFIX_PATH, {"layout": [], "custom": []})
            self.refresh_autofix_list("layout")
            self.refresh_autofix_list("custom")
        if "profiles" in data:
            save_json(PROFILES_PATH, data["profiles"])
            self.profiles_data = self.load_list(PROFILES_PATH)
            if not self.profiles_data:
                self.profiles_data = ["default"]
                save_json(PROFILES_PATH, self.profiles_data)
            if self.active_profile not in self.profiles_data:
                self.active_profile = self.profiles_data[0]
                self.config["active_profile"] = self.active_profile
                save_config(self.config)
            self.refresh_profiles_list()
        self.profile_label.config(text=f"Активный профиль: {self.active_profile}")
        self._reload_binder_map()
        self.update_info_files()
        self.append_log("Импорт", f"Данные из {os.path.basename(path)}")
        messagebox.showinfo("Готово", "Данные импортированы.")

    def build_settings_screen(self):
        card = self.build_screen_shell(
            "Настройки",
            "Настройки",
            "Поведение приложения и Discord-данные.",
        )

        btn_discord = self.create_button(card, text="Discord", command=self.open_discord_settings, expand_x=True)
        self.pack_content_button(btn_discord, pady=4)
        btn_behavior = self.create_button(
            card,
            text="Поведение биндера",
            command=lambda: self.open_settings_stub("Поведение биндера"),
            expand_x=True,
        )
        self.pack_content_button(btn_behavior, pady=4)
        btn_manage = self.create_button(
            card,
            text="Управление командами",
            command=lambda: self.show_screen("Команды"),
            expand_x=True,
        )
        self.pack_content_button(btn_manage, pady=4)
        btn_autofix = self.create_button(
            card,
            text="Автозамены",
            command=lambda: self.open_settings_stub("Автозамены"),
            expand_x=True,
        )
        self.pack_content_button(btn_autofix, pady=4)
        btn_log = self.create_button(card, text="Log", command=self.open_log_window, expand_x=True)
        self.pack_content_button(btn_log, pady=4)

        options = ttk.Frame(card, style="CardBody.TFrame")
        options.pack(fill="x", pady=(16, 0))

        self.auto_alias_state = self.config.get("auto_alias_ru", True)
        self.auto_info_state = self.config.get("auto_update_info", True)

        toggle_row1 = ttk.Frame(options, style="CardBody.TFrame")
        toggle_row1.pack(anchor="w", pady=4, fill="x")
        toggle1 = ToggleSwitch(
            toggle_row1,
            value=self.auto_alias_state,
            command=lambda v: setattr(self, "auto_alias_state", v),
        )
        toggle1.pack(side="left")
        ttk.Label(
            toggle_row1,
            text="Авто-алиасы RU→EN для команд",
            style="CardMuted.TLabel",
        ).pack(side="left", padx=10)

        toggle_row2 = ttk.Frame(options, style="CardBody.TFrame")
        toggle_row2.pack(anchor="w", pady=4, fill="x")
        toggle2 = ToggleSwitch(
            toggle_row2,
            value=self.auto_info_state,
            command=lambda v: setattr(self, "auto_info_state", v),
        )
        toggle2.pack(side="left")
        ttk.Label(
            toggle_row2,
            text="Авто-обновление подсказок (Информация)",
            style="CardMuted.TLabel",
        ).pack(side="left", padx=10)

        self.create_button(options, text="Сохранить настройки", command=self.save_settings_options).pack(
            anchor="w", pady=(8, 0)
        )

    def open_discord_settings(self):
        win = tk.Toplevel(self.root)
        win.title("Discord")
        win.geometry("420x300")
        win.configure(bg=THEME["bg"])

        fields = [
            ("Discord ГА", "discord_ga"),
            ("Discord зГА", "discord_zga"),
            ("Мой Discord", "discord_me"),
        ]

        entries = {}
        for label, key in fields:
            ttk.Label(win, text=label).pack()
            e = tk.Entry(win, width=40)
            e.pack(pady=(2, 8))
            style_entry(e)
            e.insert(0, self.config.get(key, ""))
            entries[key] = e

        def save():
            for k, e in entries.items():
                self.config[k] = e.get()
            save_config(self.config)
            win.destroy()
            messagebox.showinfo("Готово", "Discord сохранён")

        self.create_button(win, text="Сохранить", command=save).pack(pady=10)

    def open_settings_stub(self, title):
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry("420x180")
        win.configure(bg=THEME["bg"])
        ttk.Label(win, text="Раздел будет реализован позже.").pack(padx=20, pady=20)

    def save_settings_options(self):
        old_alias = self.config.get("auto_alias_ru", True)
        old_info = self.config.get("auto_update_info", True)
        self.config["auto_alias_ru"] = bool(self.auto_alias_state)
        self.config["auto_update_info"] = bool(self.auto_info_state)
        save_config(self.config)
        if old_alias != self.config["auto_alias_ru"]:
            self.append_log("Изменено", f"Настройки: авто-алиасы RU→EN -> {self.config['auto_alias_ru']}")
        if old_info != self.config["auto_update_info"]:
            self.append_log("Изменено", f"Настройки: авто-обновление подсказок -> {self.config['auto_update_info']}")
        if self.config["auto_update_info"]:
            self.update_info_files()
        messagebox.showinfo("Готово", "Настройки сохранены.")


if __name__ == "__main__":
    ensure_dirs()
    root = tk.Tk()
    app = BinderApp(root)
    root.update_idletasks()
    w = root.winfo_width() or 1080
    h = root.winfo_height() or 720
    x = (root.winfo_screenwidth() // 2) - (w // 2)
    y = (root.winfo_screenheight() // 2) - (h // 2)
    root.geometry(f"{w}x{h}+{x}+{y}")
    root.state("normal")
    root.deiconify()
    root.attributes("-alpha", 1.0)
    root.lift()
    root.focus_force()
    root.attributes("-topmost", True)
    root.after(300, lambda: root.attributes("-topmost", False))
    root.mainloop()
