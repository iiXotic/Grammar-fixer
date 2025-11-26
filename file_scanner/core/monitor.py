from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
from file_scanner.utils.logger import logger

class RealTimeHandler(FileSystemEventHandler):
    def __init__(self, scanner_callback):
        self.scanner_callback = scanner_callback

    def on_created(self, event):
        if not event.is_directory:
            self.scanner_callback(event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            self.scanner_callback(event.src_path)

class FolderMonitor:
    def __init__(self, callback):
        self.observer = Observer()
        self.handler = RealTimeHandler(callback)
        self.running = False
        self.watched_paths = []

    def add_path(self, path):
        if path not in self.watched_paths:
            self.observer.schedule(self.handler, path, recursive=True)
            self.watched_paths.append(path)

    def start(self):
        if self.running: return
        self.observer.start()
        self.running = True
        logger.info("Started real-time monitoring")

    def stop(self):
        if not self.running: return
        self.observer.stop()
        self.observer.join()
        self.observer = Observer() # Reset observer for restart
        self.watched_paths = []
        self.running = False
        logger.info("Stopped real-time monitoring")
