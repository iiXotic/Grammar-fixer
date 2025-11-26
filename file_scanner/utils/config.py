import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    VIRUSTOTAL_API_KEY = os.getenv("VIRUSTOTAL_API_KEY", "")
    QUARANTINE_DIR = os.getenv("QUARANTINE_DIR", os.path.join(os.getcwd(), "quarantine"))
    WHITELIST_FILE = "whitelist.json"
    BLACKLIST_FILE = "blacklist.json"
    
    @staticmethod
    def load_list(filename):
        if os.path.exists(filename):
            try:
                with open(filename, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []

    @staticmethod
    def save_list(filename, data):
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)

    @classmethod
    def get_whitelist(cls):
        return cls.load_list(cls.WHITELIST_FILE)

    @classmethod
    def add_to_whitelist(cls, item):
        data = cls.get_whitelist()
        if item not in data:
            data.append(item)
            cls.save_list(cls.WHITELIST_FILE, data)

    @classmethod
    def get_blacklist(cls):
        return cls.load_list(cls.BLACKLIST_FILE)
    
    @classmethod
    def ensure_quarantine_dir(cls):
        if not os.path.exists(cls.QUARANTINE_DIR):
            os.makedirs(cls.QUARANTINE_DIR)

