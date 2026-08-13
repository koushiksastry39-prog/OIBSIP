import tkinter as tk
from tkinter import messagebox
import secrets
import string
import pyperclip


# =========================================================
# CHARACTER SETS
# =========================================================

UPPERCASE = string.ascii_uppercase
LOWERCASE = string.ascii_lowercase
NUMBERS = string.digits
SYMBOLS = string.punctuation
AMBIGUOUS = "0Ol1I"

history = []
dark_mode = True
password_visible = True


# =========================================================
# COLORS
# =========================================================

DARK = {
    "bg": "#0f172a",
    "card": "#1e293b",
    "input": "#020617",
    "text": "#f8fafc",
    "secondary": "#94a3b8",
    "blue": "#2563eb",
    "blue_hover": "#1d4ed8",
    "green": "#22c55e",
    "green_hover": "#16a34a",
    "orange": "#f59e0b",
    "red": "#ef4444",
    "red_hover": "#dc2626",
    "border": "#334155"
}

LIGHT = {
    "bg": "#eef2ff",
    "card": "#ffffff",
    "input": "#f8fafc",
    "text": "#0f172a",
    "secondary": "#475569",
    "blue": "#2563eb",
    "blue_hover": "#1d4ed8",
    "green": "#16a34a",
    "green_hover": "#15803d",
    "orange": "#d97706",
    "red": "#dc2626",
    "red_hover": "#b91c1c",
    "border": "#cbd5e1"
}


# =========================================================
# MAIN WINDOW
# =========================================================

root = tk.Tk()
root.title("Secure Password Generator")

# Initial size
root.geometry("900x850")

# Minimum size
root.minsize(650, 650)

root.configure(bg=DARK["bg"])


# =========================================================
# VARIABLES
# =========================================================

length_var = tk.IntVar(value=18)

uppercase_var = tk.BooleanVar(value=True)
lowercase_var = tk.BooleanVar(value=True)
numbers_var = tk.BooleanVar(value=True)
symbols_var = tk.BooleanVar(value=True)

exclude_ambiguous_var = tk.BooleanVar(value=False)

password_var = tk.StringVar()

strength_text = tk.StringVar(value="Strength: --")

character_info = tk.StringVar(
    value="Select options and generate a password"
)

status_text = tk.StringVar(
    value="Ready to generate a secure password"
)

# Live-update whenever any option changes (no need to click Generate first)
uppercase_var.trace_add("write", lambda *a: live_update())
lowercase_var.trace_add("write", lambda *a: live_update())
numbers_var.trace_add("write", lambda *a: live_update())
symbols_var.trace_add("write", lambda *a: live_update())
exclude_ambiguous_var.trace_add("write", lambda *a: live_update())


# =========================================================
# RESPONSIVE CONFIGURATION
# =========================================================

root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)


# =========================================================
# FUNCTIONS
# =========================================================

def get_colors():
    return DARK if dark_mode else LIGHT


def update_length_label(value=None):
    length_label.config(
        text=f"Password Length: {length_var.get()} characters"
    )
    live_update()


def set_length(value):
    length_var.set(int(value))
    update_length_label()


# =========================================================
# HOVER EFFECT HELPER
# =========================================================

class Tooltip:
    """Small popup hint that appears on hover."""

    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip = None
        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)

    def show(self, event=None):
        if self.tip or not self.text:
            return

        x = self.widget.winfo_rootx() + 10
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 6

        self.tip = tk.Toplevel(self.widget)
        self.tip.wm_overrideredirect(True)
        self.tip.wm_geometry(f"+{x}+{y}")

        label = tk.Label(
            self.tip,
            text=self.text,
            font=("Arial", 8),
            bg="#111827",
            fg="white",
            padx=8,
            pady=4,
            relief="flat"
        )
        label.pack()

    def hide(self, event=None):
        if self.tip:
            self.tip.destroy()
            self.tip = None


def add_hover(widget, hover_key, normal_key):
    """Lighten/darken a button on mouseover using theme color keys."""

    def on_enter(event):
        if str(widget.cget("state")) != "disabled":
            widget.config(bg=get_colors()[hover_key])

    def on_leave(event):
        if str(widget.cget("state")) != "disabled":
            widget.config(bg=get_colors()[normal_key])

    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)


# =========================================================
# LIVE VALIDATION (runs as soon as options change, no click needed)
# =========================================================

def live_update(*args):

    selected_count = sum([
        uppercase_var.get(),
        lowercase_var.get(),
        numbers_var.get(),
        symbols_var.get()
    ])

    if selected_count < 2:

        generate_button.config(
            state="disabled",
            bg=get_colors()["secondary"],
            text="⚠  SELECT AT LEAST 2 CHARACTER TYPES"
        )

        status_text.set(
            "Select at least 2 character types to enable generation"
        )

    else:

        generate_button.config(
            state="normal",
            bg=get_colors()["blue"],
            text="⚡  GENERATE SECURE PASSWORD"
        )

        if status_text.get().startswith("Select at least"):
            status_text.set("Ready to generate a secure password")

    # Live preview of what strength this configuration would produce
    length = length_var.get()

    if selected_count >= 2:
        preview_calculate_strength(length, selected_count)


# =========================================================
# GENERATE PASSWORD
# =========================================================

def generate_password():

    global password_visible

    length = length_var.get()

    if length < 8:
        messagebox.showerror(
            "Invalid Length",
            "Password length must be at least 8 characters."
        )
        return

    selected = []

    if uppercase_var.get():
        selected.append(("Uppercase", UPPERCASE))

    if lowercase_var.get():
        selected.append(("Lowercase", LOWERCASE))

    if numbers_var.get():
        selected.append(("Numbers", NUMBERS))

    if symbols_var.get():
        selected.append(("Symbols", SYMBOLS))

    if len(selected) < 2:
        messagebox.showerror(
            "Character Types Required",
            "Please select at least 2 character types."
        )
        return

    character_sets = []

    for name, charset in selected:

        if exclude_ambiguous_var.get():
            charset = "".join(
                c for c in charset
                if c not in AMBIGUOUS
            )

        if charset:
            character_sets.append((name, charset))

    if len(character_sets) < 2:
        messagebox.showerror(
            "Invalid Selection",
            "Not enough characters remain after exclusions."
        )
        return

    # Guarantee one character from every selected type
    password_chars = []

    for name, charset in character_sets:
        password_chars.append(
            secrets.choice(charset)
        )

    # Combined character pool
    all_characters = "".join(
        charset for name, charset in character_sets
    )

    # Fill remaining characters
    for _ in range(length - len(password_chars)):
        password_chars.append(
            secrets.choice(all_characters)
        )

    # Secure shuffle
    for i in range(len(password_chars) - 1, 0, -1):

        j = secrets.randbelow(i + 1)

        password_chars[i], password_chars[j] = (
            password_chars[j],
            password_chars[i]
        )

    password = "".join(password_chars)

    password_var.set(password)

    password_visible = True

    password_entry.config(show="")

    show_button.config(text="🙈 Hide")

    # Automatically copy
    copy_to_clipboard(auto=True)

    # Add history
    add_to_history(password)

    # Strength
    calculate_strength(
        length,
        len(character_sets)
    )

    # Information
    ambiguous_text = (
        "Ambiguous characters excluded"
        if exclude_ambiguous_var.get()
        else "All characters allowed"
    )

    character_info.set(
        f"{length} characters  •  "
        f"{len(character_sets)} character types  •  "
        f"{ambiguous_text}"
    )

    status_text.set(
        "✓ Secure password generated and copied to clipboard"
    )


# =========================================================
# STRENGTH
# =========================================================

def calculate_strength(length, diversity, prefix="Strength: "):

    if length >= 20 and diversity == 4:

        strength = "VERY STRONG"
        value = 100
        bar_color = get_colors()["green"]

    elif length >= 16 and diversity >= 3:

        strength = "STRONG"
        value = 85
        bar_color = get_colors()["green"]

    elif length >= 12 and diversity >= 3:

        strength = "MEDIUM"
        value = 65
        bar_color = get_colors()["orange"]

    else:

        strength = "WEAK"
        value = 35
        bar_color = get_colors()["red"]

    strength_text.set(
        f"{prefix}{strength}"
    )

    strength_value.config(
        text=f"{value}%"
    )

    strength_bar.place(
        relx=0,
        rely=0,
        relwidth=value / 100,
        relheight=1
    )

    strength_bar.config(
        bg=bar_color
    )


def preview_calculate_strength(length, diversity):
    """Shows a live 'would-be' strength as the user adjusts settings,
    before they actually generate a password."""

    calculate_strength(length, diversity, prefix="If generated now: ")


# =========================================================
# COPY
# =========================================================

def copy_to_clipboard(auto=False):

    password = password_var.get()

    if not password:

        if not auto:
            messagebox.showwarning(
                "Nothing to Copy",
                "Generate a password first."
            )

        return

    try:

        pyperclip.copy(password)

        if not auto:
            status_text.set(
                "✓ Password copied to clipboard"
            )

    except Exception:

        messagebox.showerror(
            "Clipboard Error",
            "Could not copy password."
        )


# =========================================================
# SHOW / HIDE
# =========================================================

def toggle_password():

    global password_visible

    password_visible = not password_visible

    if password_visible:

        password_entry.config(show="")

        show_button.config(
            text="🙈 Hide"
        )

    else:

        password_entry.config(show="•")

        show_button.config(
            text="👁 Show"
        )


# =========================================================
# CLEAR
# =========================================================

def clear_password():

    password_var.set("")

    strength_text.set(
        "Strength: --"
    )

    strength_value.config(
        text="0%"
    )

    character_info.set(
        "Select options and generate a password"
    )

    status_text.set(
        "Password cleared"
    )

    strength_bar.place_forget()


# =========================================================
# HISTORY
# =========================================================

def add_to_history(password):

    # Avoid duplicate consecutive entries
    if password in history:
        history.remove(password)

    history.insert(0, password)

    # Keep only latest 5
    if len(history) > 5:
        history.pop()

    update_history()


def update_history():

    # Clear old history widgets
    for widget in history_frame.winfo_children():
        widget.destroy()

    # Always create 5 rows
    for index in range(5):

        row = tk.Frame(
            history_frame,
            bg=get_colors()["input"],
            height=32,
            cursor="hand2"
        )

        row.pack(
            fill="x",
            pady=2
        )

        row.pack_propagate(False)

        if index < len(history):

            row_password = history[index]

            def on_row_enter(event, r=row):
                r.config(bg=get_colors()["border"])
                for child in r.winfo_children():
                    if not isinstance(child, tk.Button):
                        child.config(bg=get_colors()["border"])

            def on_row_leave(event, r=row):
                r.config(bg=get_colors()["input"])
                for child in r.winfo_children():
                    if not isinstance(child, tk.Button):
                        child.config(bg=get_colors()["input"])

            def on_row_click(event, p=row_password):
                pyperclip.copy(p)
                status_text.set("✓ Copied password from history")

            row.bind("<Enter>", on_row_enter)
            row.bind("<Leave>", on_row_leave)
            row.bind("<Button-1>", on_row_click)

        # Number
        number = tk.Label(
            row,
            text=str(index + 1),
            width=4,
            font=("Arial", 9, "bold"),
            bg=get_colors()["input"],
            fg=get_colors()["blue"]
        )

        number.pack(
            side="left"
        )

        if index < len(history):
            number.config(cursor="hand2")
            number.bind("<Enter>", on_row_enter)
            number.bind("<Leave>", on_row_leave)
            number.bind("<Button-1>", on_row_click)

        # Password
        if index < len(history):

            password = history[index]

            display_password = password

            if len(password) > 45:
                display_password = (
                    password[:42] + "..."
                )

            password_label = tk.Label(
                row,
                text=display_password,
                font=("Consolas", 10),
                bg=get_colors()["input"],
                fg=get_colors()["text"],
                anchor="w"
            )

            password_label.pack(
                side="left",
                fill="x",
                expand=True
            )

            password_label.config(cursor="hand2")
            password_label.bind("<Enter>", on_row_enter)
            password_label.bind("<Leave>", on_row_leave)
            password_label.bind("<Button-1>", on_row_click)

            Tooltip(password_label, "Click to copy this password")

            # Use button
            use_button = tk.Button(
                row,
                text="Use",
                command=lambda p=password: use_history_password(p),
                font=("Arial", 8, "bold"),
                bg=get_colors()["blue"],
                fg="white",
                activebackground=get_colors()["blue_hover"],
                relief="flat",
                cursor="hand2",
                padx=10
            )

            use_button.pack(
                side="right",
                padx=4
            )

            add_hover(use_button, "blue_hover", "blue")

        else:

            empty_label = tk.Label(
                row,
                text="—",
                font=("Consolas", 10),
                bg=get_colors()["input"],
                fg=get_colors()["secondary"]
            )

            empty_label.pack(
                side="left"
            )


def use_history_password(password):

    global password_visible

    password_var.set(password)

    password_visible = True

    password_entry.config(
        show=""
    )

    show_button.config(
        text="🙈 Hide"
    )

    status_text.set(
        "Password selected from history"
    )


# =========================================================
# PRESETS
# =========================================================

def preset(length):

    set_length(length)

    generate_password()


# =========================================================
# THEME
# =========================================================

def toggle_theme():

    global dark_mode

    dark_mode = not dark_mode

    apply_theme()


def apply_theme():

    c = get_colors()

    root.configure(
        bg=c["bg"]
    )

    header.configure(
        bg=c["bg"]
    )

    title.configure(
        bg=c["bg"],
        fg=c["text"]
    )

    subtitle.configure(
        bg=c["bg"],
        fg=c["secondary"]
    )

    status_label.configure(
        bg=c["bg"],
        fg=c["secondary"]
    )

    security_label.configure(
        bg=c["bg"],
        fg=c["secondary"]
    )

    main_card.configure(
        bg=c["card"]
    )

    # Update all main widgets
    widgets = [
        length_label,
        preset_label,
        type_label,
        upper_check,
        lower_check,
        number_check,
        symbol_check,
        ambiguous_check,
        strength_text_label,
        info_label,
        history_title
    ]

    for widget in widgets:

        widget.configure(
            bg=c["card"],
            fg=c["text"]
        )

    preset_frame.configure(
        bg=c["card"]
    )

    check_frame.configure(
        bg=c["card"]
    )

    action_frame.configure(
        bg=c["card"]
    )

    history_container.configure(
        bg=c["card"]
    )

    history_frame.configure(
        bg=c["card"]
    )

    length_slider.configure(
        bg=c["card"],
        fg=c["text"],
        troughcolor=c["input"],
        activebackground=c["blue"]
    )

    password_entry.configure(
        bg=c["input"],
        fg=c["green"],
        insertbackground=c["text"]
    )

    theme_button.configure(
        bg=c["card"],
        fg=c["text"]
    )

    update_history()


# =========================================================
# HEADER
# =========================================================

header = tk.Frame(
    root,
    bg=DARK["bg"]
)

header.grid(
    row=0,
    column=0,
    sticky="ew",
    padx=30,
    pady=(15, 5)
)

header.grid_columnconfigure(
    0,
    weight=1
)


title = tk.Label(
    header,
    text="🔐 Secure Password Generator",
    font=("Arial", 24, "bold"),
    bg=DARK["bg"],
    fg="white"
)

title.grid(
    row=0,
    column=0,
    sticky="w"
)


theme_button = tk.Button(
    header,
    text="☀ Light Mode",
    command=toggle_theme,
    font=("Arial", 9, "bold"),
    bg=DARK["card"],
    fg="white",
    relief="flat",
    padx=10,
    pady=6,
    cursor="hand2"
)

theme_button.grid(
    row=0,
    column=1,
    sticky="e"
)

add_hover(theme_button, "border", "card")


subtitle = tk.Label(
    header,
    text="Cryptographically secure password generation",
    font=("Arial", 10),
    bg=DARK["bg"],
    fg=DARK["secondary"]
)

subtitle.grid(
    row=1,
    column=0,
    columnspan=2,
    pady=(5, 0)
)


# =========================================================
# MAIN CARD
# =========================================================

main_card = tk.Frame(
    root,
    bg=DARK["card"],
    padx=25,
    pady=18
)

main_card.grid(
    row=1,
    column=0,
    sticky="nsew",
    padx=30,
    pady=(5, 10)
)

main_card.grid_columnconfigure(
    0,
    weight=1
)


# =========================================================
# LENGTH
# =========================================================

length_label = tk.Label(
    main_card,
    text="Password Length: 18 characters",
    font=("Arial", 12, "bold"),
    bg=DARK["card"],
    fg="white"
)

length_label.grid(
    row=0,
    column=0,
    sticky="w"
)


length_slider = tk.Scale(
    main_card,
    from_=8,
    to=64,
    orient="horizontal",
    variable=length_var,
    command=update_length_label,
    showvalue=False,
    bg=DARK["card"],
    fg="white",
    highlightthickness=0,
    troughcolor=DARK["input"],
    activebackground=DARK["blue"]
)

length_slider.grid(
    row=1,
    column=0,
    sticky="ew",
    pady=(2, 8)
)


# QUICK LENGTH

preset_label = tk.Label(
    main_card,
    text="Quick Length",
    font=("Arial", 10, "bold"),
    bg=DARK["card"],
    fg="white"
)

preset_label.grid(
    row=2,
    column=0,
    sticky="w"
)


preset_frame = tk.Frame(
    main_card,
    bg=DARK["card"]
)

preset_frame.grid(
    row=3,
    column=0,
    sticky="w",
    pady=(4, 8)
)


for value in [12, 16, 20, 32]:

    button = tk.Button(
        preset_frame,
        text=str(value),
        command=lambda v=value: preset(v),
        font=("Arial", 9, "bold"),
        bg=DARK["input"],
        fg="white",
        relief="flat",
        padx=15,
        pady=4,
        cursor="hand2"
    )

    button.pack(
        side="left",
        padx=(0, 7)
    )

    add_hover(button, "blue", "input")


# CHARACTER TYPES

type_label = tk.Label(
    main_card,
    text="Character Types",
    font=("Arial", 12, "bold"),
    bg=DARK["card"],
    fg="white"
)

type_label.grid(
    row=4,
    column=0,
    sticky="w"
)


check_frame = tk.Frame(
    main_card,
    bg=DARK["card"]
)

check_frame.grid(
    row=5,
    column=0,
    sticky="w"
)


upper_check = tk.Checkbutton(
    check_frame,
    text="Uppercase A-Z",
    variable=uppercase_var,
    font=("Arial", 9),
    bg=DARK["card"],
    fg="white",
    activebackground=DARK["card"],
    activeforeground="white",
    selectcolor=DARK["input"],
    cursor="hand2"
)

upper_check.grid(
    row=0,
    column=0,
    sticky="w"
)


lower_check = tk.Checkbutton(
    check_frame,
    text="Lowercase a-z",
    variable=lowercase_var,
    font=("Arial", 9),
    bg=DARK["card"],
    fg="white",
    activebackground=DARK["card"],
    activeforeground="white",
    selectcolor=DARK["input"],
    cursor="hand2"
)

lower_check.grid(
    row=0,
    column=1,
    sticky="w",
    padx=(15, 0)
)


number_check = tk.Checkbutton(
    check_frame,
    text="Numbers 0-9",
    variable=numbers_var,
    font=("Arial", 9),
    bg=DARK["card"],
    fg="white",
    activebackground=DARK["card"],
    activeforeground="white",
    selectcolor=DARK["input"],
    cursor="hand2"
)

number_check.grid(
    row=1,
    column=0,
    sticky="w"
)


symbol_check = tk.Checkbutton(
    check_frame,
    text="Symbols !@#$",
    variable=symbols_var,
    font=("Arial", 9),
    bg=DARK["card"],
    fg="white",
    activebackground=DARK["card"],
    activeforeground="white",
    selectcolor=DARK["input"],
    cursor="hand2"
)

symbol_check.grid(
    row=1,
    column=1,
    sticky="w",
    padx=(15, 0)
)


# AMBIGUOUS

ambiguous_check = tk.Checkbutton(
    main_card,
    text="Exclude ambiguous characters (0, O, l, 1, I)",
    variable=exclude_ambiguous_var,
    font=("Arial", 9),
    bg=DARK["card"],
    fg="#fbbf24",
    activebackground=DARK["card"],
    activeforeground="#fbbf24",
    selectcolor=DARK["input"],
    cursor="hand2"
)

ambiguous_check.grid(
    row=6,
    column=0,
    sticky="w",
    pady=(5, 8)
)

Tooltip(
    ambiguous_check,
    "Useful when the password will be typed by hand or read aloud"
)


# GENERATE

generate_button = tk.Button(
    main_card,
    text="⚡  GENERATE SECURE PASSWORD",
    command=generate_password,
    font=("Arial", 11, "bold"),
    bg=DARK["blue"],
    fg="white",
    activebackground=DARK["blue_hover"],
    relief="flat",
    pady=9,
    cursor="hand2"
)

generate_button.grid(
    row=7,
    column=0,
    sticky="ew",
    pady=(0, 8)
)

add_hover(generate_button, "blue_hover", "blue")



# PASSWORD DISPLAY


password_entry = tk.Entry(
    main_card,
    textvariable=password_var,
    font=("Consolas", 14, "bold"),
    justify="center",
    bg=DARK["input"],
    fg=DARK["green"],
    insertbackground="white",
    relief="flat"
)

password_entry.grid(
    row=8,
    column=0,
    sticky="ew",
    ipady=9
)

password_entry.config(cursor="hand2")
password_entry.bind("<Button-1>", lambda event: copy_to_clipboard(False))

Tooltip(password_entry, "Click to copy")



# ACTION BUTTONS


action_frame = tk.Frame(
    main_card,
    bg=DARK["card"]
)

action_frame.grid(
    row=9,
    column=0,
    sticky="ew",
    pady=8
)


show_button = tk.Button(
    action_frame,
    text="🙈 Hide",
    command=toggle_password,
    font=("Arial", 9, "bold"),
    bg=DARK["border"],
    fg="white",
    relief="flat",
    padx=12,
    pady=6,
    cursor="hand2"
)

show_button.pack(
    side="left",
    padx=(0, 5)
)

add_hover(show_button, "secondary", "border")


copy_button = tk.Button(
    action_frame,
    text="📋 Copy",
    command=lambda: copy_to_clipboard(False),
    font=("Arial", 9, "bold"),
    bg=DARK["blue"],
    fg="white",
    relief="flat",
    padx=12,
    pady=6,
    cursor="hand2"
)

copy_button.pack(
    side="left",
    padx=5
)

add_hover(copy_button, "blue_hover", "blue")


new_button = tk.Button(
    action_frame,
    text="🔄 Generate Another",
    command=generate_password,
    font=("Arial", 9, "bold"),
    bg=DARK["green"],
    fg="white",
    relief="flat",
    padx=12,
    pady=6,
    cursor="hand2"
)

new_button.pack(
    side="left",
    padx=5
)

add_hover(new_button, "green_hover", "green")


clear_button = tk.Button(
    action_frame,
    text="🧹 Clear",
    command=clear_password,
    font=("Arial", 9, "bold"),
    bg=DARK["red"],
    fg="white",
    relief="flat",
    padx=12,
    pady=6,
    cursor="hand2"
)

clear_button.pack(
    side="right"
)

add_hover(clear_button, "red_hover", "red")


# STRENGTH


strength_text_label = tk.Label(
    main_card,
    textvariable=strength_text,
    font=("Arial", 11, "bold"),
    bg=DARK["card"],
    fg="white"
)

strength_text_label.grid(
    row=10,
    column=0,
    pady=(2, 4)
)


strength_container = tk.Frame(
    main_card,
    bg=DARK["input"],
    height=10
)

strength_container.grid(
    row=11,
    column=0,
    sticky="ew"
)

strength_container.grid_propagate(False)


strength_bar = tk.Frame(
    strength_container,
    bg=DARK["green"]
)

strength_value = tk.Label(
    main_card,
    text="0%",
    font=("Arial", 8, "bold"),
    bg=DARK["card"],
    fg=DARK["secondary"]
)

strength_value.grid(
    row=12,
    column=0,
    sticky="e"
)

info_label = tk.Label(
    main_card,
    textvariable=character_info,
    font=("Arial", 9),
    bg=DARK["card"],
    fg=DARK["secondary"]
)

info_label.grid(
    row=13,
    column=0,
    pady=(0, 5)
)


history_title = tk.Label(
    main_card,
    text="🕘 Recent Passwords — Last 5",
    font=("Arial", 11, "bold"),
    bg=DARK["card"],
    fg="white"
)

history_title.grid(
    row=14,
    column=0,
    sticky="w",
    pady=(3, 4)
)


history_container = tk.Frame(
    main_card,
    bg=DARK["card"]
)

history_container.grid(
    row=15,
    column=0,
    sticky="ew"
)

history_frame = tk.Frame(
    history_container,
    bg=DARK["card"]
)

history_frame.pack(
    fill="x"
)



status_label = tk.Label(
    root,
    textvariable=status_text,
    font=("Arial", 9),
    bg=DARK["bg"],
    fg=DARK["secondary"]
)

status_label.grid(
    row=2,
    column=0,
    pady=(0, 3)
)


security_label = tk.Label(
    root,
    text="",
    font=("Arial", 8),
    bg=DARK["bg"],
    fg=DARK["secondary"]
)

security_label.grid(
    row=3,
    column=0,
    pady=(0, 8)
)

root.bind(
    "<Return>",
    lambda event: generate_password()
)

root.bind(
    "<Control-n>",
    lambda event: generate_password()
)

root.bind(
    "<Control-c>",
    lambda event: copy_to_clipboard(False)
)

root.bind(
    "<Control-l>",
    lambda event: clear_password()
)

root.bind(
    "<Control-t>",
    lambda event: toggle_theme()
)

root.bind(
    "<Escape>",
    lambda event: toggle_password()
)


update_length_label()

update_history()

live_update()

root.mainloop()