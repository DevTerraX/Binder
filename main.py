import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
HELP_DIR = os.path.join(BASE_DIR, "help")

CONFIG_PATH = os.path.join(DATA_DIR, "config.json")
BINDS_PATH = os.path.join(DATA_DIR, "binds.json")
PHRASES_PATH = os.path.join(DATA_DIR, "phrases.json")
AUTOFIX_PATH = os.path.join(DATA_DIR, "autofix.json")
PROFILES_PATH = os.path.join(DATA_DIR, "profiles.json")

NAV_BUTTONS = [
    "Команды",
    "Фразы",
    "Автоисправление",
    "Переменные",
    "Профили",
    "Импорт / Экспорт",
    "Информация",
    "Настройки",
]

INFO_BUTTONS = [
    ("Журнал изменений", "changelog.txt"),
    ("Подсказки", "hints.txt"),
    ("Телепорты", "teleport.txt"),
    ("Новости", "tips.txt"),
]

THEME = {
    "bg": "#1c1e22",
    "panel": "#24272c",
    "card": "#23262b",
    "card_alt": "#1a1c20",
    "button": "#2c3036",
    "input": "#17191d",
    "border": "#343a42",
    "fg": "#e6e6e6",
    "muted": "#a9a9a9",
    "accent": "#3b82f6",
}


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
        highlightthickness=1,
        highlightbackground=THEME["border"],
        highlightcolor=THEME["accent"],
    )


def style_listbox(widget):
    widget.configure(
        bg=THEME["input"],
        fg=THEME["fg"],
        selectbackground=THEME["accent"],
        selectforeground=THEME["fg"],
        relief="flat",
        highlightthickness=1,
        highlightbackground=THEME["border"],
        activestyle="none",
    )


def style_text(widget):
    widget.configure(
        bg=THEME["input"],
        fg=THEME["fg"],
        insertbackground=THEME["fg"],
        relief="flat",
        highlightthickness=1,
        highlightbackground=THEME["border"],
        highlightcolor=THEME["accent"],
    )


class BinderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Binder")
        self.root.geometry("980x640")
        self.root.configure(bg=THEME["bg"])
        self.root.resizable(False, False)

        self.config = load_config()
        self.setup_style()
        self.build_ui()

    def setup_style(self):
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("TFrame", background=THEME["bg"])
        style.configure("Nav.TFrame", background=THEME["panel"])
        style.configure("Card.TFrame", background=THEME["card"], borderwidth=1, relief="solid")
        style.configure("CardBody.TFrame", background=THEME["card"], borderwidth=0, relief="flat")
        style.configure("Subcard.TFrame", background=THEME["card_alt"], borderwidth=1, relief="solid")

        style.configure("TLabel", background=THEME["bg"], foreground=THEME["fg"])
        style.configure("Muted.TLabel", background=THEME["bg"], foreground=THEME["muted"])
        style.configure("Card.TLabel", background=THEME["card"], foreground=THEME["fg"])
        style.configure("CardMuted.TLabel", background=THEME["card"], foreground=THEME["muted"])
        style.configure("Subcard.TLabel", background=THEME["card_alt"], foreground=THEME["fg"])
        style.configure(
            "ScreenTitle.TLabel",
            background=THEME["bg"],
            foreground=THEME["fg"],
            font=("Segoe UI", 18, "bold"),
        )
        style.configure(
            "Section.TLabel",
            background=THEME["card"],
            foreground=THEME["fg"],
            font=("Segoe UI", 12, "bold"),
        )

        style.configure(
            "TButton",
            background=THEME["button"],
            foreground=THEME["fg"],
            borderwidth=0,
            focusthickness=0,
            padding=(10, 6),
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
            padding=(12, 8),
            anchor="w",
        )
        style.map(
            "Nav.TButton",
            background=[("active", THEME["accent"]), ("pressed", THEME["accent"])],
            foreground=[("active", THEME["fg"]), ("pressed", THEME["fg"])],
        )

    def build_ui(self):
        ttk.Label(self.root, text="Binder", style="ScreenTitle.TLabel").pack(pady=(12, 6))

        main = ttk.Frame(self.root)
        main.pack(fill="both", expand=True, padx=12, pady=12)
        main.columnconfigure(1, weight=1)
        main.rowconfigure(0, weight=1)

        nav = ttk.Frame(main, width=220, style="Nav.TFrame")
        nav.grid(row=0, column=0, sticky="ns", padx=(0, 12))

        for name in NAV_BUTTONS:
            ttk.Button(
                nav,
                text=name,
                style="Nav.TButton",
                command=lambda n=name: self.show_screen(n),
            ).pack(fill="x", pady=4)

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

    def create_screens(self):
        self.screens = {}
        for name in NAV_BUTTONS:
            frame = ttk.Frame(self.content)
            frame.grid(row=0, column=0, sticky="nsew")
            self.screens[name] = frame

    def show_screen(self, name):
        self.screens[name].tkraise()

    def build_screen_shell(self, screen_name, title, subtitle=None):
        parent = self.screens[screen_name]
        header = ttk.Frame(parent)
        header.pack(fill="x", padx=16, pady=(10, 6))

        ttk.Label(header, text=title, style="ScreenTitle.TLabel").pack(anchor="w")
        if subtitle:
            ttk.Label(header, text=subtitle, style="Muted.TLabel").pack(anchor="w", pady=(2, 0))

        card = ttk.Frame(parent, style="Card.TFrame", padding=14)
        card.pack(fill="both", expand=True, padx=16, pady=(0, 14))
        return card

    def add_section_header(self, parent, text):
        ttk.Label(parent, text=text, style="Section.TLabel").pack(anchor="w", pady=(0, 6))

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

    def build_info_screen(self):
        card = self.build_screen_shell(
            "Информация",
            "Информация",
            "Справка и полезные материалы (открываются в отдельном окне).",
        )

        for title, filename in INFO_BUTTONS:
            path = os.path.join(HELP_DIR, filename)
            ttk.Button(
                card,
                text=title,
                command=lambda t=title, p=path: self.open_text_window(t, p),
            ).pack(fill="x", pady=4)

    def open_text_window(self, title, path):
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry("520x420")
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

        main = ttk.Frame(card, style="CardBody.TFrame")
        main.pack(fill="both", expand=True)

        listbox = tk.Listbox(main, width=24)
        listbox.pack(side="left", fill="y", padx=(0, 12))
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

        btns = ttk.Frame(right, style="CardBody.TFrame")
        btns.pack(pady=10)

        ui = {
            "listbox": listbox,
            "trigger": trigger_entry,
            "text": text_entry,
            "path": data_path,
            "data_ref": data_ref,
        }

        ttk.Button(btns, text="Добавить", command=lambda: self.bind_add(ui)).pack(side="left", padx=4)
        ttk.Button(btns, text="Изменить", command=lambda: self.bind_update(ui)).pack(side="left", padx=4)
        ttk.Button(btns, text="Удалить", command=lambda: self.bind_delete(ui)).pack(side="left", padx=4)

        listbox.bind("<<ListboxSelect>>", lambda e: self.bind_on_select(ui))
        return ui

    def refresh_bind_list(self, ui, data_list):
        ui["listbox"].delete(0, tk.END)
        for item in data_list:
            trigger = item.get("trigger", "") if isinstance(item, dict) else ""
            label = trigger if trigger else "<без триггера>"
            ui["listbox"].insert(tk.END, label)

    def bind_on_select(self, ui):
        selection = ui["listbox"].curselection()
        if not selection:
            return
        idx = selection[0]
        data_list = getattr(self, ui["data_ref"])
        if idx >= len(data_list):
            return
        item = data_list[idx]
        ui["trigger"].delete(0, tk.END)
        ui["trigger"].insert(0, item.get("trigger", ""))
        ui["text"].delete("1.0", tk.END)
        ui["text"].insert("1.0", self.bind_get_text(item))

    def bind_add(self, ui):
        trigger = ui["trigger"].get().strip()
        text = ui["text"].get("1.0", tk.END).strip()
        if not trigger or not text:
            messagebox.showwarning("Проверьте данные", "Заполните триггер и текст.")
            return
        data_list = getattr(self, ui["data_ref"])
        item = {"trigger": trigger, "text": text}
        data_list.append(item)
        save_json(ui["path"], data_list)
        self.refresh_bind_list(ui, data_list)
        ui["listbox"].selection_clear(0, tk.END)
        ui["listbox"].selection_set(tk.END)

    def bind_update(self, ui):
        selection = ui["listbox"].curselection()
        if not selection:
            messagebox.showwarning("Нет выбора", "Выберите элемент для изменения.")
            return
        idx = selection[0]
        trigger = ui["trigger"].get().strip()
        text = ui["text"].get("1.0", tk.END).strip()
        if not trigger or not text:
            messagebox.showwarning("Проверьте данные", "Заполните триггер и текст.")
            return
        data_list = getattr(self, ui["data_ref"])
        if idx >= len(data_list):
            return
        item = data_list[idx]
        item["trigger"] = trigger
        self.bind_set_text(item, text)
        save_json(ui["path"], data_list)
        self.refresh_bind_list(ui, data_list)
        ui["listbox"].selection_clear(0, tk.END)
        ui["listbox"].selection_set(idx)

    def bind_delete(self, ui):
        selection = ui["listbox"].curselection()
        if not selection:
            messagebox.showwarning("Нет выбора", "Выберите элемент для удаления.")
            return
        idx = selection[0]
        data_list = getattr(self, ui["data_ref"])
        if idx >= len(data_list):
            return
        if not messagebox.askyesno("Подтвердите", "Удалить выбранный элемент?"):
            return
        data_list.pop(idx)
        save_json(ui["path"], data_list)
        self.refresh_bind_list(ui, data_list)
        ui["trigger"].delete(0, tk.END)
        ui["text"].delete("1.0", tk.END)

    def build_autofix_screen(self):
        card = self.build_screen_shell(
            "Автоисправление",
            "Автоисправление",
            "Автоматическая замена текста при вводе.",
        )

        self.autofix_data = self.load_dict(AUTOFIX_PATH, {"layout": [], "custom": []})

        self.add_section_header(card, "Раскладка (ru → en)")
        layout_ui = self.build_autofix_group(card, "layout")

        ttk.Separator(card, orient="horizontal").pack(fill="x", pady=10)

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
        }

        ttk.Button(btns, text="Добавить", command=lambda: self.autofix_add(ui)).pack(side="left", padx=4)
        ttk.Button(btns, text="Изменить", command=lambda: self.autofix_update(ui)).pack(side="left", padx=4)
        ttk.Button(btns, text="Удалить", command=lambda: self.autofix_delete(ui)).pack(side="left", padx=4)

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
        items[idx] = {"from": from_val, "to": to_val}
        save_json(AUTOFIX_PATH, self.autofix_data)
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
        items.pop(idx)
        save_json(AUTOFIX_PATH, self.autofix_data)
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

        self.variables_list = tk.Listbox(main, width=28)
        self.variables_list.pack(side="left", fill="y", padx=(0, 12))
        style_listbox(self.variables_list)

        right = ttk.Frame(main, style="CardBody.TFrame")
        right.pack(fill="both", expand=True)

        ttk.Label(right, text="Имя", style="Card.TLabel").pack(anchor="w")
        self.var_key = tk.Entry(right)
        self.var_key.pack(fill="x", pady=(2, 10))
        style_entry(self.var_key)

        ttk.Label(right, text="Значение", style="Card.TLabel").pack(anchor="w")
        self.var_value = tk.Entry(right)
        self.var_value.pack(fill="x", pady=(2, 10))
        style_entry(self.var_value)

        btns = ttk.Frame(right, style="CardBody.TFrame")
        btns.pack(pady=6)

        ttk.Button(btns, text="Добавить", command=self.variables_add).pack(side="left", padx=4)
        ttk.Button(btns, text="Изменить", command=self.variables_update).pack(side="left", padx=4)
        ttk.Button(btns, text="Удалить", command=self.variables_delete).pack(side="left", padx=4)

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
        key = self.var_key.get().strip()
        value = self.var_value.get().strip()
        if not key or not value:
            messagebox.showwarning("Проверьте данные", "Заполните оба поля.")
            return
        self.config.setdefault("variables", {})[key] = value
        save_config(self.config)
        self.refresh_variables_list()

    def variables_update(self):
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
        if key != original_key:
            self.variables.pop(original_key, None)
        self.variables[key] = value
        self.config["variables"] = self.variables
        save_config(self.config)
        self.refresh_variables_list()

    def variables_delete(self):
        selection = self.variables_list.curselection()
        if not selection:
            messagebox.showwarning("Нет выбора", "Выберите элемент для удаления.")
            return
        key = sorted(self.variables.keys())[selection[0]]
        if not messagebox.askyesno("Подтвердите", "Удалить переменную?"):
            return
        self.variables.pop(key, None)
        self.config["variables"] = self.variables
        save_config(self.config)
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

        ttk.Button(btns, text="Добавить", command=self.profiles_add).pack(side="left", padx=4)
        ttk.Button(btns, text="Удалить", command=self.profiles_delete).pack(side="left", padx=4)
        ttk.Button(btns, text="Сделать активным", command=self.profiles_set_active).pack(side="left", padx=4)

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
        self.active_profile = self.profiles_data[idx]
        self.config["active_profile"] = self.active_profile
        save_config(self.config)
        self.profile_label.config(text=f"Активный профиль: {self.active_profile}")

    def build_import_export_screen(self):
        card = self.build_screen_shell(
            "Импорт / Экспорт",
            "Импорт / Экспорт",
            "Сохранение и восстановление данных биндера.",
        )

        ttk.Button(card, text="Экспортировать данные", command=self.export_data).pack(fill="x", pady=6)
        ttk.Button(card, text="Импортировать данные", command=self.import_data).pack(fill="x", pady=6)

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
        messagebox.showinfo("Готово", "Данные импортированы.")

    def build_settings_screen(self):
        card = self.build_screen_shell(
            "Настройки",
            "Настройки",
            "Поведение приложения и Discord-данные.",
        )

        ttk.Button(card, text="Discord", command=self.open_discord_settings).pack(fill="x", pady=4)
        ttk.Button(
            card,
            text="Поведение биндера",
            command=lambda: self.open_settings_stub("Поведение биндера"),
        ).pack(fill="x", pady=4)
        ttk.Button(
            card,
            text="Управление командами",
            command=lambda: self.open_settings_stub("Управление командами"),
        ).pack(fill="x", pady=4)
        ttk.Button(
            card,
            text="Автозамены",
            command=lambda: self.open_settings_stub("Автозамены"),
        ).pack(fill="x", pady=4)

    def open_discord_settings(self):
        win = tk.Toplevel(self.root)
        win.title("Discord")
        win.geometry("360x260")
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

        ttk.Button(win, text="Сохранить", command=save).pack(pady=10)

    def open_settings_stub(self, title):
        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry("360x160")
        win.configure(bg=THEME["bg"])
        ttk.Label(win, text="Раздел будет реализован позже.").pack(padx=20, pady=20)


if __name__ == "__main__":
    ensure_dirs()
    root = tk.Tk()
    app = BinderApp(root)
    root.mainloop()
