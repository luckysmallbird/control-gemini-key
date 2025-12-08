import json
import os
import time
from pathlib import Path
from dotenv import load_dotenv

class KeyManager:
    def __init__(self, key_string=None, usage_file="key_usage.json", max_requests_per_day=19):
        """
        初始化 KeyManager。
        :param key_string: 可以直接傳入逗號分隔的 key 字串。
        :param usage_file: 記錄檔名稱，儲存在 manager_key 資料夾下。
        :param max_requests_per_day: 每個 Key 每日最大請求次數。
        """
        self.base_dir = Path(__file__).parent
        self.usage_file_path = self.base_dir / usage_file
        self.max_requests = max_requests_per_day
        self.keys = []
        
        # 1. 載入 Keys
        if key_string:
            self.keys = [k.strip() for k in key_string.split(',') if k.strip()]
        else:
            self.load_keys()
        
        if not self.keys:
            print("警告: KeyManager 初始化時沒有找到任何 API Key。請檢查 .env, key.txt 或傳入參數。")

        # 2. 載入歷史記錄
        self.usage_data = self._load_usage_data()

    def load_keys(self):
        """從環境變數 (.env) 和 key.txt 載入 Keys"""
        new_keys = []

        # --- 來源 1: .env ---
        try:
            # 重新載入 .env 檔案
            load_dotenv(Path(__file__).parent.parent / '.env', override=True)
            env_keys = os.getenv("GEMINI_API_KEY")
            if env_keys:
                new_keys.extend([k.strip() for k in env_keys.split(',') if k.strip()])
        except Exception as e:
            print(f"[KeyManager] 讀取 .env 失敗: {e}")

        # --- 來源 2: key.txt ---
        key_txt_path = self.base_dir / "key.txt"
        if key_txt_path.exists():
            try:
                with open(key_txt_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        k = line.strip()
                        if k:
                            new_keys.append(k)
            except Exception as e:
                print(f"[KeyManager] 讀取 key.txt 失敗: {e}")
        
        # 將新發現的 Key 加入 self.keys (保持順序且不重複)
        added_count = 0
        for k in new_keys:
            if k not in self.keys:
                # print(f"[KeyManager] 發現新 Key: ...{k[-4:]}")
                self.keys.append(k)
                added_count += 1
        
        if added_count > 0:
            print(f"[KeyManager] 已載入 {added_count} 個新 Key。目前總數: {len(self.keys)}")

    def _load_usage_data(self):
        """讀取持久化的使用記錄"""
        if self.usage_file_path.exists():
            try:
                with open(self.usage_file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[KeyManager] 讀取記錄檔失敗: {e}，將建立新記錄。")
        return {}

    def _save_usage_data(self):
        """儲存使用記錄"""
        try:
            with open(self.usage_file_path, 'w', encoding='utf-8') as f:
                json.dump(self.usage_data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"[KeyManager] 儲存記錄檔失敗: {e}")

    def get_available_key(self):
        """
        獲取一個當前可用的 Key。
        邏輯：
        1. 遍歷所有 Key，進行狀態維護。
        2. 收集所有「可用」(count < max) 的 Key。
        3. 如果沒有可用 Key，嘗試重新載入 .env 和 key.txt 並再試一次。
        4. 排序：優先選擇 count 最大的 (剩餘次數最少)。
        """
        
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
                
                # --- 狀態維護：檢查是否可以重置 ---
                if data["count"] >= self.max_requests:
                    last_used = data.get("last_used_time", 0)
                    if now - last_used > 86400:
                        data["count"] = 0
                        self._save_usage_data() 
                
                # --- 判斷可用性 ---
                if data["count"] < self.max_requests:
                    valid_keys.append( (key, data["count"]) )
            return valid_keys

        # 第一次嘗試
        available_keys = find_valid_keys()

        # 如果沒有可用 Key，嘗試重新載入 keys
        if not available_keys:
            print("[KeyManager] 所有現有 Key 皆已耗盡，正在檢查 .env 和 key.txt 是否有新 Key...")
            self.load_keys()
            # 第二次嘗試
            available_keys = find_valid_keys()

        if not available_keys:
             raise Exception(f"KeyManager 錯誤：所有的 API Key ({len(self.keys)} 個) 皆已用盡或處於冷卻中！")

        # --- 選擇策略：優先選 count 最大的 (即將用完的) ---
        available_keys.sort(key=lambda x: x[1], reverse=True)
        
        best_key = available_keys[0][0]
        return best_key

    def increment_usage(self, key):
        """
        增加 Key 的使用計數。
        必須在 API 呼叫成功後手動呼叫此方法。
        更新 last_used_time 為當前時間。
        """
        if key in self.usage_data:
            self.usage_data[key]["count"] += 1
            self.usage_data[key]["last_used_time"] = time.time()
            self._save_usage_data()
            # print(f"[KeyManager] Key ...{key[-4:]} 計數 +1 (目前: {self.usage_data[key]['count']})")
        else:
            print(f"[KeyManager] 警告：嘗試更新一個未知的 Key ...{key[-4:]}")
