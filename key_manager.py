import json
import os
import time
from pathlib import Path
from dotenv import load_dotenv

class KeyManager:
    def __init__(self, key_string=None, usage_file="key_usage.json", max_requests_per_day=19):
        self.base_dir = Path(__file__).parent
        self.usage_file_path = self.base_dir / usage_file
        self.max_requests = max_requests_per_day
        self.keys = []
        
        if key_string:
            self.keys = [k.strip() for k in key_string.split(',') if k.strip()]
        else:
            self.load_keys()
        
        if not self.keys:
            print("Warning: No API Keys found during KeyManager initialization. Please check .env, key.txt or passed arguments.")

        self.usage_data = self._load_usage_data()

    def load_keys(self):
        new_keys = []

        try:
            load_dotenv(Path(__file__).parent.parent / '.env', override=True)
            env_keys = os.getenv("GEMINI_API_KEY")
            if env_keys:
                new_keys.extend([k.strip() for k in env_keys.split(',') if k.strip()])
        except Exception as e:
            print(f"[KeyManager] Failed to read .env: {e}")

        key_txt_path = self.base_dir / "key.txt"
        if key_txt_path.exists():
            try:
                with open(key_txt_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        k = line.strip()
                        if k:
                            new_keys.append(k)
            except Exception as e:
                print(f"[KeyManager] Failed to read key.txt: {e}")
        
        added_count = 0
        for k in new_keys:
            if k not in self.keys:
                self.keys.append(k)
                added_count += 1
        
        if added_count > 0:
            print(f"[KeyManager] Loaded {added_count} new Keys. Total: {len(self.keys)}")

    def _load_usage_data(self):
        if self.usage_file_path.exists():
            try:
                with open(self.usage_file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[KeyManager] Failed to read usage file: {e}. A new record will be created.")
        return {}

    def _save_usage_data(self):
        try:
            with open(self.usage_file_path, 'w', encoding='utf-8') as f:
                json.dump(self.usage_data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"[KeyManager] Failed to save usage file: {e}")

    def get_available_key(self):
        
        def find_valid_keys():
            now = time.time()
            valid_keys = []
            
            for key in self.keys:
                if key not in self.usage_data:
                    self.usage_data[key] = {
                        "count": 0,
                        "last_used_time": 0
                    }
                
                data = self.usage_data[key]
                
                if data["count"] >= self.max_requests:
                    last_used = data.get("last_used_time", 0)
                    if now - last_used > 86400:
                        data["count"] = 0
                        self._save_usage_data() 
                
                if data["count"] < self.max_requests:
                    valid_keys.append( (key, data["count"]) )
            return valid_keys

        available_keys = find_valid_keys()

        if not available_keys:
            print("[KeyManager] All existing keys are exhausted. Checking .env and key.txt for new keys...")
            self.load_keys()
            available_keys = find_valid_keys()

        if not available_keys:
             raise Exception(f"KeyManager Error: All API Keys ({len(self.keys)}) are exhausted or in cooldown!")

        available_keys.sort(key=lambda x: x[1], reverse=True)
        
        best_key = available_keys[0][0]
        return best_key

    def increment_usage(self, key):
        if key in self.usage_data:
            self.usage_data[key]["count"] += 1
            self.usage_data[key]["last_used_time"] = time.time()
            self._save_usage_data()
        else:
            print(f"[KeyManager] Warning: Attempting to update an unknown Key ...{key[-4:]}")