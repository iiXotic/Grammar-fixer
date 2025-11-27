import os
import threading
from grammar_fixer.utils.config import Config
from grammar_fixer.utils.logger import logger
from grammar_fixer.integrations.virustotal import VirusTotalClient

class Scanner:
    def __init__(self):
        self.vt_client = VirusTotalClient()
        self.whitelist = set(Config.get_whitelist())
        self.blacklist = set(Config.get_blacklist())
        self.stop_event = threading.Event()
        self.is_scanning = False

    def stop_scan(self):
        self.stop_event.set()

    def heuristic_check(self, file_path):
        """Returns score (0-100) and reasons."""
        score = 0
        reasons = []
        filename = os.path.basename(file_path).lower()
        
        # Double extensions
        if filename.count('.') > 1:
            parts = filename.split('.')
            if len(parts) >= 3:
                ext = parts[-1]
                if ext in ['exe', 'bat', 'cmd', 'vbs', 'scr', 'com']:
                    score += 50
                    reasons.append(f"Suspicious double extension ending in .{ext}")

        # Suspicious extensions in sensitive folders (e.g. Downloads, Temp - handled by caller location mostly)
        # But generally:
        sus_exts = ('.exe', '.bat', '.vbs', '.scr', '.ps1', '.jar')
        if filename.endswith(sus_exts):
             score += 10 
        
        # Files starting with dot but executable
        if filename.startswith('.') and filename.endswith(sus_exts):
            score += 60
            reasons.append("Hidden executable file")

        # Check for very long filenames
        if len(filename) > 150:
            score += 20
            reasons.append("Unusually long filename")

        return score, reasons

    def count_files(self, path):
        total = 0
        for root, dirs, files in os.walk(path):
            total += len(files)
        return total

    def scan_directory(self, path, check_vt=False, progress_callback=None):
        results = []
        self.is_scanning = True
        self.stop_event.clear()
        
        # Reload whitelist/blacklist
        self.whitelist = set(Config.get_whitelist())
        self.blacklist = set(Config.get_blacklist())

        total_files = self.count_files(path)
        scanned_count = 0

        for root, dirs, files in os.walk(path):
            if self.stop_event.is_set():
                break
                
            for file in files:
                if self.stop_event.is_set():
                    break
                    
                file_path = os.path.join(root, file)
                scanned_count += 1
                
                if progress_callback:
                    progress_callback(scanned_count, total_files, file_path)

                if file_path in self.whitelist:
                    continue

                # Heuristic Scan
                score, reasons = self.heuristic_check(file_path)
                
                if file_path in self.blacklist:
                    score = 100
                    reasons.append("Blacklisted file")

                vt_result = None
                
                # Strategy: If check_vt is True, we only check if suspicious (score > 20) or if explicitly asked for all?
                # Checking ALL files against VT is too slow and quota heavy.
                # Let's say check_vt checks files that have some heuristic suspicio OR all executables?
                # For this implementation, let's limit VT checks to heuristics > 20 to save quota
                
                if check_vt and score >= 10:
                    vt_result = self.vt_client.scan_file(file_path)
                    
                    if vt_result and "data" in vt_result:
                        try:
                            stats = vt_result["data"]["attributes"]["last_analysis_stats"]
                            malicious = stats.get("malicious", 0)
                            if malicious > 0:
                                score = 100 # Max score
                                reasons.append(f"VirusTotal: {malicious} vendors flagged this")
                            elif malicious == 0:
                                # Confirmed safe by VT
                                if score > 0:
                                    reasons.append("VirusTotal: Clean")
                                    # Reduce score if VT says clean?
                                    # Maybe keep heuristics but note it's clean on VT
                        except KeyError:
                            pass
                    elif vt_result and "error" in vt_result:
                        reasons.append(f"VT Error: {vt_result['error']}")

                if score >= 50:
                    results.append({
                        "path": file_path,
                        "score": score,
                        "reasons": reasons,
                        "vt_data": vt_result
                    })

        self.is_scanning = False
        return results
