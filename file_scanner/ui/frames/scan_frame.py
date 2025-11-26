import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import os
from file_scanner.core.scanner import Scanner
from file_scanner.core.quarantine import QuarantineManager
from file_scanner.core.monitor import FolderMonitor

class ScanFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.scanner = Scanner()
        self.quarantine_manager = QuarantineManager()
        self.monitor = FolderMonitor(self.on_monitor_event)
        self.scan_thread = None
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1) # Results area expands

        # Control Panel
        self.control_frame = ctk.CTkFrame(self)
        self.control_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        self.path_entry = ctk.CTkEntry(self.control_frame, placeholder_text="Select directory to scan...")
        self.path_entry.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        
        self.browse_btn = ctk.CTkButton(self.control_frame, text="Browse", width=80, command=self.browse_directory)
        self.browse_btn.pack(side="left", padx=5, pady=5)

        # Options
        self.options_frame = ctk.CTkFrame(self)
        self.options_frame.grid(row=1, column=0, padx=10, pady=(0,10), sticky="ew")
        
        self.vt_var = ctk.BooleanVar(value=False)
        self.vt_check = ctk.CTkCheckBox(self.options_frame, text="Enable VirusTotal Scan (Slower)", variable=self.vt_var)
        self.vt_check.pack(side="left", padx=10, pady=5)
        
        self.monitor_var = ctk.BooleanVar(value=False)
        self.monitor_check = ctk.CTkCheckBox(self.options_frame, text="Real-time Monitor", variable=self.monitor_var, command=self.toggle_monitor)
        self.monitor_check.pack(side="left", padx=10, pady=5)
        
        self.scan_btn = ctk.CTkButton(self.options_frame, text="Start Scan", command=self.toggle_scan, fg_color="green")
        self.scan_btn.pack(side="right", padx=10, pady=5)

        # Progress
        self.progress_frame = ctk.CTkFrame(self)
        self.progress_frame.grid(row=2, column=0, padx=10, pady=(0,10), sticky="ew")
        
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame)
        self.progress_bar.pack(fill="x", padx=10, pady=5)
        self.progress_bar.set(0)
        
        self.status_label = ctk.CTkLabel(self.progress_frame, text="Ready")
        self.status_label.pack(side="left", padx=10)

        # Results
        self.results_frame = ctk.CTkScrollableFrame(self, label_text="Scan Results")
        self.results_frame.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")

    def browse_directory(self):
        path = filedialog.askdirectory()
        if path:
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, path)

    def toggle_monitor(self):
        if self.monitor_var.get():
            path = self.path_entry.get()
            if os.path.exists(path):
                self.monitor.add_path(path)
                self.monitor.start()
                messagebox.showinfo("Monitor", f"Monitoring started for {path}")
            else:
                self.monitor_var.set(False)
                messagebox.showerror("Error", "Invalid path for monitoring")
        else:
            self.monitor.stop()
            messagebox.showinfo("Monitor", "Monitoring stopped")

    def on_monitor_event(self, file_path):
        # Quick heuristic check
        try:
            score, reasons = self.scanner.heuristic_check(file_path)
            if score >= 50:
                self.after(0, lambda: messagebox.showwarning("Threat Detected", f"Real-time monitor detected suspicious file:\n{file_path}\nReason: {reasons}"))
                self.after(0, lambda: self.add_result_item({
                    "path": file_path,
                    "score": score,
                    "reasons": reasons,
                    "vt_data": None
                }))
        except Exception as e:
            print(f"Monitor check failed: {e}")

    def toggle_scan(self):
        if self.scanner.is_scanning:
            self.scanner.stop_scan()
            self.scan_btn.configure(text="Stopping...", state="disabled")
        else:
            path = self.path_entry.get()
            if not os.path.exists(path):
                messagebox.showerror("Error", "Invalid directory path")
                return
            
            self.clear_results()
            self.scan_btn.configure(text="Stop Scan", fg_color="red")
            self.progress_bar.set(0)
            self.status_label.configure(text="Scanning...")
            
            check_vt = self.vt_var.get()
            
            self.scan_thread = threading.Thread(target=self.run_scan, args=(path, check_vt))
            self.scan_thread.start()

    def run_scan(self, path, check_vt):
        def update_progress(scanned, total, current_file):
            try:
                progress = scanned / total if total > 0 else 0
                self.progress_bar.set(progress)
                self.status_label.configure(text=f"Scanning: {os.path.basename(current_file)}")
            except:
                pass

        results = self.scanner.scan_directory(path, check_vt=check_vt, progress_callback=update_progress)
        
        # Finished
        self.after(0, lambda: self.on_scan_finished(results))


    def on_scan_finished(self, results):
        self.scan_btn.configure(text="Start Scan", fg_color="green", state="normal")
        self.status_label.configure(text=f"Scan complete. Found {len(results)} threats.")
        self.progress_bar.set(1)
        self.populate_results(results)

    def populate_results(self, results):
        for res in results:
            self.add_result_item(res)

    def add_result_item(self, res):
        path = res["path"]
        score = res["score"]
        reasons = ", ".join(res["reasons"])
        
        item_frame = ctk.CTkFrame(self.results_frame)
        item_frame.pack(fill="x", padx=5, pady=2)
        
        # Info
        info_label = ctk.CTkLabel(item_frame, text=f"{os.path.basename(path)} (Score: {score})", anchor="w", font=("Arial", 12, "bold"))
        info_label.pack(side="top", fill="x", padx=5, pady=2)
        
        reason_label = ctk.CTkLabel(item_frame, text=reasons, anchor="w", text_color="gray")
        reason_label.pack(side="top", fill="x", padx=5, pady=0)
        
        path_label = ctk.CTkLabel(item_frame, text=path, anchor="w", font=("Arial", 10))
        path_label.pack(side="top", fill="x", padx=5, pady=0)
        
        # Actions
        actions_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        actions_frame.pack(side="top", fill="x", padx=5, pady=5)
        
        q_btn = ctk.CTkButton(actions_frame, text="Quarantine", height=24, width=80, 
                              command=lambda p=path, f=item_frame: self.quarantine_file(p, f))
        q_btn.pack(side="left", padx=5)
        
        w_btn = ctk.CTkButton(actions_frame, text="Whitelist", height=24, width=80,
                              command=lambda p=path, f=item_frame: self.whitelist_file(p, f))
        w_btn.pack(side="left", padx=5)

    def clear_results(self):
        for widget in self.results_frame.winfo_children():
            widget.destroy()

    def quarantine_file(self, path, frame):
        success, msg = self.quarantine_manager.quarantine_file(path)
        if success:
            frame.destroy()
            messagebox.showinfo("Success", f"File quarantined.\n{path}")
        else:
            messagebox.showerror("Error", msg)

    def whitelist_file(self, path, frame):
        from file_scanner.utils.config import Config
        Config.add_to_whitelist(path)
        frame.destroy()
        messagebox.showinfo("Success", f"File added to whitelist.\n{path}")
