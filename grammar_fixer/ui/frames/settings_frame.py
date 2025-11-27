import customtkinter as ctk
from tkinter import messagebox
import os
import json
from grammar_fixer.utils.config import Config
from grammar_fixer.core.scheduler import ScanScheduler

class SettingsFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.scheduler = ScanScheduler()
        self.scheduler.start()
        
        self.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(self, text="Settings", font=("Arial", 16, "bold")).pack(pady=10)
        
        # API Key
        self.api_frame = ctk.CTkFrame(self)
        self.api_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(self.api_frame, text="VirusTotal API Key:").pack(side="left", padx=10)
        self.api_entry = ctk.CTkEntry(self.api_frame, width=300)
        self.api_entry.pack(side="left", padx=10)
        self.api_entry.insert(0, Config.VIRUSTOTAL_API_KEY)
        
        save_btn = ctk.CTkButton(self.api_frame, text="Save", width=60, command=self.save_api_key)
        save_btn.pack(side="left", padx=10)
        
        # Scheduler
        ctk.CTkLabel(self, text="Daily Schedule", font=("Arial", 14, "bold")).pack(pady=(20, 5))
        
        self.sched_frame = ctk.CTkFrame(self)
        self.sched_frame.pack(fill="x", padx=10, pady=5)
        
        self.sched_path = ctk.CTkEntry(self.sched_frame, placeholder_text="Path to scan daily")
        self.sched_path.pack(side="left", fill="x", expand=True, padx=5)
        
        self.sched_time = ctk.CTkEntry(self.sched_frame, width=80, placeholder_text="HH:MM")
        self.sched_time.pack(side="left", padx=5)
        self.sched_time.insert(0, "02:00")
        
        sched_btn = ctk.CTkButton(self.sched_frame, text="Schedule", width=80, command=self.add_schedule)
        sched_btn.pack(side="left", padx=5)
        
        # Whitelist
        ctk.CTkLabel(self, text="Whitelist (JSON)", font=("Arial", 14, "bold")).pack(pady=(20, 5))
        self.whitelist_text = ctk.CTkTextbox(self, height=200)
        self.whitelist_text.pack(fill="x", padx=10)
        
        # Load whitelist
        try:
            wl = Config.get_whitelist()
            self.whitelist_text.insert("0.0", json.dumps(wl, indent=4))
        except:
            pass
            
        save_wl_btn = ctk.CTkButton(self, text="Save Whitelist", command=self.save_whitelist)
        save_wl_btn.pack(pady=10)

    def save_api_key(self):
        key = self.api_entry.get().strip()
        Config.VIRUSTOTAL_API_KEY = key
        
        # Update .env file
        env_path = ".env"
        lines = []
        if os.path.exists(env_path):
            with open(env_path, "r") as f:
                lines = f.readlines()
        
        new_lines = []
        found = False
        for line in lines:
            if line.startswith("VIRUSTOTAL_API_KEY="):
                new_lines.append(f"VIRUSTOTAL_API_KEY={key}\n")
                found = True
            else:
                new_lines.append(line)
        
        if not found:
            if new_lines and not new_lines[-1].endswith('\n'):
                 new_lines.append('\n')
            new_lines.append(f"VIRUSTOTAL_API_KEY={key}\n")
            
        with open(env_path, "w") as f:
            f.writelines(new_lines)
            
        messagebox.showinfo("Success", "API Key saved.")

    def add_schedule(self):
        path = self.sched_path.get()
        time_str = self.sched_time.get()
        if os.path.exists(path):
            # Basic validation for time
            try:
                # check format
                if len(time_str.split(':')) != 2: raise ValueError
                self.scheduler.schedule_daily_scan(path, time_str)
                messagebox.showinfo("Success", f"Scheduled daily scan for {path} at {time_str}")
            except:
                 messagebox.showerror("Error", "Invalid time format (use HH:MM)")
        else:
            messagebox.showerror("Error", "Invalid path")

    def save_whitelist(self):
        try:
            text = self.whitelist_text.get("0.0", "end")
            data = json.loads(text)
            if not isinstance(data, list):
                raise ValueError("Whitelist must be a list of strings")
            
            Config.save_list(Config.WHITELIST_FILE, data)
            messagebox.showinfo("Success", "Whitelist saved.")
        except Exception as e:
            messagebox.showerror("Error", f"Invalid JSON: {e}")
