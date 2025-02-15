import customtkinter as ctk
import json
import os
import sys

BASE_PATH = getattr(sys, '_MEIPASS', os.path.abspath("."))

assets_dir = os.path.join(BASE_PATH, "assets")
os.makedirs(assets_dir, exist_ok=True)
logoico = os.path.join(assets_dir, "logo.ico")

CONFIG_FILE = "misp_config.json"
HINT_COLOR = "gray"
INPUT_COLOR = "white"


def add_hint(entry, hint_text, is_password=False):
    def on_focus_in(event):
        if entry.get() == hint_text:
            entry.delete(0, "end")
            entry.configure(text_color=INPUT_COLOR)
            if is_password:
                entry.configure(show="*")

    def on_focus_out(event):
        if not entry.get():
            entry.insert(0, hint_text)
            entry.configure(text_color=HINT_COLOR)
            if is_password:
                entry.configure(show="")

    entry.insert(0, hint_text)
    entry.configure(text_color=HINT_COLOR)
    if is_password:
        entry.configure(show="")

    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)


def show_misp_config():
    details_window = ctk.CTkToplevel()
    details_window.title("MISP Configuration")
    details_window.resizable(False, False)

    details_window.update_idletasks()
    screen_width = details_window.winfo_screenwidth()
    screen_height = details_window.winfo_screenheight()
    window_width, window_height = 350, 320
    position_x = (screen_width // 2) - (window_width // 2)
    position_y = (screen_height // 2) - (window_height // 2)
    details_window.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")

    if os.path.exists(logoico):
        details_window.after(500, lambda: details_window.iconbitmap(logoico))
    else:
        print(f"Error: Icon file not found at {logoico}")

    description_label = ctk.CTkLabel(
        details_window,
        text=("This application integrates with MISP to retrieve malware intelligence for "
              "enhanced threat detection and response. If you have MISP database credentials, "
              "please enter them below. Otherwise, you may skip this step."),
        wraplength=320,
        justify="center"
    )
    description_label.pack(pady=5)

    credentials = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                credentials = json.load(f)
        except json.JSONDecodeError:
            credentials = {}

    entry_host = ctk.CTkEntry(details_window, width=300)
    add_hint(entry_host, credentials.get("mysql_host", "Enter MISP MySQL Host"))
    entry_host.pack(pady=2)

    entry_user = ctk.CTkEntry(details_window, width=300)
    add_hint(entry_user, credentials.get("mysql_user", "Enter MISP MySQL User"))
    entry_user.pack(pady=2)

    entry_password = ctk.CTkEntry(details_window, width=300)
    add_hint(entry_password, credentials.get("mysql_password", "Enter MISP MySQL Password"), is_password=True)
    entry_password.pack(pady=2)

    entry_db = ctk.CTkEntry(details_window, width=300)
    add_hint(entry_db, credentials.get("mysql_db", "Enter MISP MySQL Database"))
    entry_db.pack(pady=2)

    def save_credentials():
        new_credentials = {
            "mysql_host": entry_host.get() if entry_host.get() != "Enter MISP MySQL Host" else "",
            "mysql_user": entry_user.get() if entry_user.get() != "Enter MISP MySQL User" else "",
            "mysql_password": entry_password.get() if entry_password.get() != "Enter MISP MySQL Password" else "",
            "mysql_db": entry_db.get() if entry_db.get() != "Enter MISP MySQL Database" else ""
        }
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(new_credentials, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")
        details_window.destroy()

    submit_button = ctk.CTkButton(details_window, text="Submit", command=save_credentials, width=300)
    submit_button.pack(pady=5)

    skip_button = ctk.CTkButton(details_window, text="Skip", command=details_window.destroy, fg_color="gray", width=300)
    skip_button.pack(pady=5)

    details_window.transient()
    details_window.grab_set()
    details_window.wait_window()
