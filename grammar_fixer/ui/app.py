import customtkinter as ctk
from grammar_fixer.ui.frames.scan_frame import ScanFrame
from grammar_fixer.ui.frames.quarantine_frame import QuarantineFrame
from grammar_fixer.ui.frames.settings_frame import SettingsFrame

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Grammar Fixer")
        self.geometry("900x600")
        
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        
        # Grid layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Sidebar
        self.sidebar_frame = ctk.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Grammar Fixer", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.sidebar_button_scan = ctk.CTkButton(self.sidebar_frame, text="Scan", command=lambda: self.show_frame("scan"))
        self.sidebar_button_scan.grid(row=1, column=0, padx=20, pady=10)
        
        self.sidebar_button_quarantine = ctk.CTkButton(self.sidebar_frame, text="Quarantine", command=lambda: self.show_frame("quarantine"))
        self.sidebar_button_quarantine.grid(row=2, column=0, padx=20, pady=10)
        
        self.sidebar_button_settings = ctk.CTkButton(self.sidebar_frame, text="Settings", command=lambda: self.show_frame("settings"))
        self.sidebar_button_settings.grid(row=3, column=0, padx=20, pady=10)
        
        # Frames
        self.frames = {}
        
        self.frames["scan"] = ScanFrame(self)
        self.frames["quarantine"] = QuarantineFrame(self)
        self.frames["settings"] = SettingsFrame(self)
        
        self.current_frame = None
        self.show_frame("scan")

    def show_frame(self, name):
        if self.current_frame:
            self.current_frame.grid_forget()
        
        self.current_frame = self.frames[name]
        self.current_frame.grid(row=0, column=1, sticky="nsew")
