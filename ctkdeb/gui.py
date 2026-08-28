import customtkinter as ctk
from tkinter import messagebox, filedialog, PhotoImage
import os
import sys
import json

from . import packager

PATH = os.path.dirname(os.path.realpath(__file__))

class CTkDeb(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.appearance_mode_var = ctk.StringVar(value="light")
        self.update_appearance_mode()

        self.title("CTkDeb")
        self.geometry("500x600")

        self.wm_iconbitmap()
        iconpath = PhotoImage(file=os.path.join(PATH, "icon.png"))
        self.iconphoto(False, iconpath)

        self.title_font = ctk.CTkFont(size=18)

        self.fields = {
            "app": {
                "title": "App",
                "items": [
                    {"id": "name", "label": "Name", "placeholder": "myapp"},
                    {"id": "version", "label": "Version", "placeholder": "0.16.2"},
                    {"id": "entryPoint", "label": "Entry point", "placeholder": "main.py"},
                    {"id": "icon", "label": "Icon", "placeholder": "assets/icon.png"},
                    {"id": "iconSize", "label": "Icon size", "placeholder": "512x512"},
                    {"id": "pipDependencies", "label": "Pip dependencies", "placeholder": "somelib potatolib"}
                ]
            },
            "desktopEntry": {
                "title": "Desktop entry",
                "items": [
                    {"type": "button", "text": "Add field", "command": self.add_new_desktop_entry_field},
                    {"id": "Name", "label": "Name", "placeholder": "MyApp"},
                    {"id": "Comment", "label": "Comment", "placeholder": "A simple alarm clock app"}
                ]
            },
            "documentationFiles": {
                "title": "Documentation files (licenses, README.md etc.)",
                "items": [
                    {"type": "button", "text": "Add file", "command": self.add_new_doc_file}
                ]
            },
            "deb": {
                "title": "DEB-specific settings",
                "items": [
                    {"id": "section", "label": "Section", "placeholder": "graphics"},
                    {"id": "depends", "label": "Depends", "placeholder": "somelib, potatolib"},
                    {"id": "maintainer", "label": "Maintainer", "placeholder": "Ivan Ivanov <ivan_dev@example.com>"},
                    {"id": "description", "label": "Description", "placeholder": "A simple alarm clock app"},
                ]
            }
        }
        self.entries = {}
        self.desktop_entry_entries = {}
        self.doc_entries = []

        self.build_interface()

    def update_appearance_mode(self):
        ctk.set_appearance_mode(self.appearance_mode_var.get())

    def build_interface(self):
        self.create_header()
        self.create_cards()
        self.create_footer()

    def create_header(self):
        header = ctk.CTkFrame(self)
        header.pack(padx=5, pady=5, side=ctk.TOP, fill=ctk.X)

        ctk.CTkLabel(header, text="CTkDeb", font=self.title_font).pack(padx=10, pady=10, side=ctk.LEFT)

        appearance_switch = ctk.CTkSwitch(header, text="Dark", variable=self.appearance_mode_var,
                                          offvalue="light", onvalue="dark", command=self.update_appearance_mode)
        appearance_switch.pack(padx=10, pady=10, side=ctk.RIGHT)

    def create_footer(self):
        footer = ctk.CTkFrame(self)
        footer.pack(padx=5, pady=5, side=ctk.BOTTOM, fill=ctk.X)

        import_config_button = ctk.CTkButton(footer, text="Import config", command=self.import_config)
        import_config_button.grid(row=0, column=0, padx=10, pady=10, sticky=ctk.EW)

        export_config_button = ctk.CTkButton(footer, text="Export config", command=self.export_config)
        export_config_button.grid(row=0, column=1, padx=10, pady=10, sticky=ctk.EW)

        create_button = ctk.CTkButton(footer, text="CREATE", command=self.create_deb)
        create_button.grid(row=0, column=2, padx=10, pady=10, sticky=ctk.EW)

        for i in footer.winfo_children():
            footer.columnconfigure(i, weight=1)

    def create_cards(self):
        scrollable = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scrollable.pack(padx=5, fill=ctk.BOTH, expand=True)

        for section, items in self.fields.items():
            self.entries[section] = {}

            card = ctk.CTkFrame(scrollable)
            card.pack(padx=10, pady=10, fill=ctk.X)

            card.grid_columnconfigure(1, weight=1)

            if section == "desktopEntry":
                self.desktop_entry_card = card
            elif section == "documentationFiles":
                self.docs_card = card

            title = ctk.CTkLabel(card, text=items["title"], font=self.title_font)
            title.grid(row=0, column=0, padx=10, pady=10, columnspan=2, sticky=ctk.W)

            for row, widget in enumerate(items["items"], start=1):
                self.create_widget(section, card, widget, row)

    def create_widget(self, section: str, card: ctk.CTkEntry, widget: dict, row: int):
        if widget.get("type") == "button":
            button = ctk.CTkButton(card, text=widget["text"], command=widget["command"])
            button.grid(row=row, column=0, padx=10, pady=(0, 10), columnspan=2, sticky=ctk.EW)
        else:
            if packager.REQUIRED_FIELDS.get(section) and widget["id"] in packager.REQUIRED_FIELDS.get(section):
                characters = "*:"
            else:
                characters = ":"

            entry = self.add_labeled_entry(card, widget["label"] + characters, widget["placeholder"], row)
            self.entries[section][widget["id"]] = entry

    def add_labeled_entry(
        self,
        card: ctk.CTkFrame,
        label_text: str,
        placeholder: str,
        row: int,
        entry_type: bool = False
    ):
        if entry_type:
            label = ctk.CTkEntry(card, placeholder_text=label_text)
        else:
            label = ctk.CTkLabel(card, text=label_text)
        label.grid(row=row, column=0, padx=10, pady=(0, 10), sticky=ctk.W)

        entry = ctk.CTkEntry(card, placeholder_text=placeholder)
        entry.grid(row=row, column=1, padx=10, pady=(0, 10), sticky=ctk.EW)

        if entry_type:
            return label, entry
        else:
            return entry

    def add_new_desktop_entry_field(self) -> ctk.CTkEntry:
        next_row = self.desktop_entry_card.grid_size()[1]

        entry = self.add_labeled_entry(self.desktop_entry_card, "Categories", "Application;Utility;", next_row, True)

        return entry

    def add_new_doc_file(self):
        next_row = self.docs_card.grid_size()[1]

        entry = self.add_labeled_entry(self.docs_card, "File:", "LICENSE", next_row)
        self.doc_entries.append(entry)

    def import_config(self):
        file_path = filedialog.askopenfilename(
            title="Import config",
            filetypes=([("JSON", "*.json")]),
            defaultextension=".json"
        )
        if not file_path:
            return

        with open(file_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        self.destroy_user_widgets()

        # Regular fields
        for section, entries in self.entries.items():
            if section in config:
                for field_id, entry in entries.items():
                    if field_id in config[section]:
                        self.entry_set_text(entry, config[section][field_id])

        # Desktop entry
        for key, value in config["desktopEntry"].items():
            if key in self.entries["desktopEntry"]:
                self.entry_set_text(self.entries["desktopEntry"][key], value)
            else:
                label, entry = self.add_new_desktop_entry_field()
                self.entry_set_text(label, key)
                self.entry_set_text(entry, value)

        # Documentation files
        for value in config["documentationFiles"]:
            self.add_new_doc_file()
            self.entry_set_text(self.doc_entries[-1], value)

        messagebox.showinfo("Config imported", "Config successfully imported")

    def get_config_dict(self) -> dict:
        config = {}

        # Regular fields
        for section, entries in self.entries.items():
            config[section] = {}
            for field_id, entry in entries.items():
                value = entry.get()
                if value:
                    config[section][field_id] = value

        # Desktop entry
        for child in self.desktop_entry_card.winfo_children():
            info = child.grid_info()
            row, col = info["row"], info["column"]

            if col == 0 and isinstance(child, ctk.CTkEntry):
                key = child.get()
                if not key:
                    continue

                for other in self.desktop_entry_card.winfo_children():
                    other_info = other.grid_info()
                    if other_info["row"] == row and other_info["column"] == 1:
                        config["desktopEntry"][key] = other.get()

        config["documentationFiles"] = [entry.get() for entry in self.doc_entries if entry.get()]

        return config

    def export_config(self):
        config = self.get_config_dict()

        file_path = filedialog.asksaveasfilename(
            title="Export config",
            filetypes=([("JSON", "*.json")]),
            defaultextension=".json",
            initialfile="ctkdeb.json"
        )
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent="\t", ensure_ascii=False)
                messagebox.showinfo("Config exported", "Config successfully exported")

    def entry_set_text(self, entry: ctk.CTkEntry, value: str):
        entry.delete(0, ctk.END)
        entry.insert(0, value)

    def destroy_user_widgets(self):
        # Desktop entry
        for child in self.desktop_entry_card.winfo_children():
            info = child.grid_info()
            row, col = info["row"], info["column"]

            if col == 0 and isinstance(child, ctk.CTkEntry):
                for other in self.desktop_entry_card.winfo_children():
                    if other.grid_info()["row"] == row:
                        other.destroy()

        # Documentation files
        for entry in self.doc_entries:
            entry.destroy()
        self.doc_entries.clear()

    def create_deb(self):
        config = self.get_config_dict()

        p = packager.Packager(config)
        p.create_deb()

        messagebox.showinfo("DEB created", "DEB successfully created")
