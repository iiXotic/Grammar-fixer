import shutil
import os
import datetime
import json
from grammar_fixer.utils.config import Config
from grammar_fixer.utils.logger import logger

class QuarantineManager:
    def __init__(self):
        Config.ensure_quarantine_dir()
        self.quarantine_dir = Config.QUARANTINE_DIR
        self.metadata_file = os.path.join(self.quarantine_dir, "quarantine_log.json")
        self.load_metadata()

    def load_metadata(self):
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, 'r') as f:
                    self.metadata = json.load(f)
            except:
                self.metadata = {}
        else:
            self.metadata = {}

    def save_metadata(self):
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=4)

    def quarantine_file(self, file_path, reason="Suspicious"):
        if not os.path.exists(file_path):
            return False, "File not found"

        filename = os.path.basename(file_path)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        quarantine_name = f"{timestamp}_{filename}"
        quarantine_path = os.path.join(self.quarantine_dir, quarantine_name)

        try:
            shutil.move(file_path, quarantine_path)
            
            self.metadata[quarantine_name] = {
                "original_path": file_path,
                "original_name": filename,
                "quarantine_date": timestamp,
                "reason": reason
            }
            self.save_metadata()
            logger.info(f"Quarantined {file_path} to {quarantine_path}")
            return True, "Success"
        except Exception as e:
            logger.error(f"Failed to quarantine {file_path}: {e}")
            return False, str(e)

    def restore_file(self, quarantine_name):
        if quarantine_name not in self.metadata:
            return False, "Record not found"

        info = self.metadata[quarantine_name]
        original_path = info["original_path"]
        quarantine_path = os.path.join(self.quarantine_dir, quarantine_name)

        if not os.path.exists(quarantine_path):
            return False, "Quarantined file missing"

        try:
            # Ensure original directory exists
            os.makedirs(os.path.dirname(original_path), exist_ok=True)
            shutil.move(quarantine_path, original_path)
            
            del self.metadata[quarantine_name]
            self.save_metadata()
            logger.info(f"Restored {quarantine_name} to {original_path}")
            return True, "Success"
        except Exception as e:
            logger.error(f"Failed to restore {quarantine_name}: {e}")
            return False, str(e)

    def delete_file(self, quarantine_name):
        if quarantine_name not in self.metadata:
            # Try to delete file anyway if it exists in dir
            quarantine_path = os.path.join(self.quarantine_dir, quarantine_name)
            if os.path.exists(quarantine_path):
                os.remove(quarantine_path)
                return True, "Deleted orphan file"
            return False, "Record not found"

        quarantine_path = os.path.join(self.quarantine_dir, quarantine_name)
        try:
            if os.path.exists(quarantine_path):
                os.remove(quarantine_path)
            
            del self.metadata[quarantine_name]
            self.save_metadata()
            logger.info(f"Deleted quarantined file {quarantine_name}")
            return True, "Success"
        except Exception as e:
            logger.error(f"Failed to delete {quarantine_name}: {e}")
            return False, str(e)

    def get_quarantined_files(self):
        return self.metadata
