import customtkinter as ctk
from tkinter import messagebox
import os
from file_scanner.core.quarantine import QuarantineManager

class QuarantineFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.manager = QuarantineManager()
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header
        header = ctk.CTkFrame(self)
        header.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        title = ctk.CTkLabel(header, text="Quarantine Manager", font=("Arial", 16, "bold"))
        title.pack(side="left", padx=10, pady=10)
        
        refresh_btn = ctk.CTkButton(header, text="Refresh", width=80, command=self.load_items)
        refresh_btn.pack(side="right", padx=10)

        # List
        self.list_frame = ctk.CTkScrollableFrame(self)
        self.list_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        self.load_items()

    def load_items(self):
        # Clear existing
        for widget in self.list_frame.winfo_children():
            widget.destroy()
            
        self.manager.load_metadata()
        items = self.manager.get_quarantined_files()
        
        if not items:
            ctk.CTkLabel(self.list_frame, text="No quarantined files.").pack(pady=20)
            return

        for q_name, info in items.items():
            self.add_item(q_name, info)

    def add_item(self, q_name, info):
        item_frame = ctk.CTkFrame(self.list_frame)
        item_frame.pack(fill="x", padx=5, pady=2)
        
        lbl_text = f"{info['original_name']}\nFrom: {info['original_path']}\nDate: {info['quarantine_date']}"
        lbl = ctk.CTkLabel(item_frame, text=lbl_text, anchor="w", justify="left")
        lbl.pack(side="left", padx=10, pady=5)
        
        btn_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        btn_frame.pack(side="right", padx=5)
        
        restore_btn = ctk.CTkButton(btn_frame, text="Restore", width=70, fg_color="green",
                                    command=lambda n=q_name: self.restore(n))
        restore_btn.pack(side="left", padx=2)
        
        del_btn = ctk.CTkButton(btn_frame, text="Delete", width=70, fg_color="red",
                                command=lambda n=q_name: self.delete(n))
        del_btn.pack(side="left", padx=2)

    def restore(self, q_name):
        if messagebox.askyesno("Restore", "Are you sure you want to restore this file?"):
            success, msg = self.manager.restore_file(q_name)
            if success:
                self.load_items()
            else:
                messagebox.showerror("Error", msg)

    def delete(self, q_name):
        if messagebox.askyesno("Delete", "Are you sure you want to permanently delete this file?"):
            success, msg = self.manager.delete_file(q_name)
            if success:
                self.load_items()
            else:
                messagebox.showerror("Error", msg)
