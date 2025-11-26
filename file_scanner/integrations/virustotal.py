import requests
import hashlib
import time
import os
from file_scanner.utils.config import Config
from file_scanner.utils.logger import logger

class VirusTotalClient:
    BASE_URL = "https://www.virustotal.com/api/v3"

    def __init__(self, api_key=None):
        self.api_key = api_key or Config.VIRUSTOTAL_API_KEY
        if not self.api_key:
            logger.warning("VirusTotal API Key not found. Integration will be limited.")
        
        self.headers = {
            "x-apikey": self.api_key
        }

    def calculate_hash(self, file_path):
        """Calculates SHA-256 hash of a file."""
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            logger.error(f"Error calculating hash for {file_path}: {e}")
            return None

    def get_file_report(self, file_hash):
        """Retrieves file report using file hash."""
        if not self.api_key:
            return {"error": "No API Key"}

        url = f"{self.BASE_URL}/files/{file_hash}"
        try:
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return {"error": "File not found in VirusTotal database"}
            elif response.status_code == 429:
                return {"error": "Rate limit exceeded"}
            elif response.status_code == 401:
                return {"error": "Invalid API Key"}
            else:
                logger.error(f"VirusTotal API Error {response.status_code}: {response.text}")
                return {"error": f"API Error: {response.status_code}"}
        except Exception as e:
            logger.error(f"Request failed: {e}")
            return {"error": str(e)}

    def scan_file(self, file_path):
        """Scans a file by hash lookup."""
        file_hash = self.calculate_hash(file_path)
        if not file_hash:
            return None
        
        return self.get_file_report(file_hash)
