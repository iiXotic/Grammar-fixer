import schedule
import time
import threading
from grammar_fixer.core.scanner import Scanner
from grammar_fixer.utils.logger import logger

class ScanScheduler:
    def __init__(self):
        self.scanner = Scanner()
        self.running = False
        self.thread = None

    def start(self):
        if self.running: return
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        logger.info("Scheduler started")

    def stop(self):
        self.running = False
        logger.info("Scheduler stopped")

    def _run(self):
        while self.running:
            schedule.run_pending()
            time.sleep(1)

    def schedule_daily_scan(self, path, time_str="02:00"):
        """Schedule a daily scan at specific time (HH:MM)"""
        schedule.every().day.at(time_str).do(self.run_scan, path)
        logger.info(f"Scheduled daily scan for {path} at {time_str}")

    def run_scan(self, path):
        logger.info(f"Starting scheduled scan for {path}")
        # Note: This runs in the background thread. 
        # Results are logged but not shown in UI unless we link them.
        results = self.scanner.scan_directory(path)
        logger.info(f"Scheduled scan finished for {path}. Found {len(results)} issues.")
        # We could save report to file here
