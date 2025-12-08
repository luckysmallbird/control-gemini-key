# Control Gemini Key

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Dependencies](https://img.shields.io/badge/dependencies-minimal-green.svg)]()

[English](#english) | [繁體中文](#traditional-chinese)

---

<a name="english"></a>
## 🇬🇧 English

**Control Gemini Key** is a lightweight microservice designed to manage and load-balance Google Gemini API keys. It solves the common problem of hitting rate limits (HTTP 429) by intelligently rotating through a pool of keys and tracking their usage persistence.

This microservice automates the management of available Google Gemini API keys, intelligently rotating them to handle rate limits and ensure continuous operation.

### Requirements

*   Python 3.8+
*   `python-dotenv` (Only for the server)

### Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/luckysmallbird/control-gemini-key.git
    cd control-gemini-key
    ```

2.  Install server dependencies:
    ```bash
    pip install python-dotenv
    ```

3.  **Configuration**: Create a `key.txt` file in the root directory and add your API keys (one per line).
    ```text
    AIzaSyD...
    AIzaSyE...
    ```
    *Alternatively, you can set `GEMINI_API_KEY` in a `.env` file (comma-separated).*

### Usage

#### 1. Start the Server
Run the lightweight HTTP server. By default, it listens on port `5000`.

```bash
python key_server.py
```

#### 2. Integrate the Client
Use the `KeyClient` in your Python application to fetch keys and report usage.

```python
from key_client import KeyClient

# Initialize client (defaults to http://localhost:5000)
client = KeyClient()

try:
    # 1. Get a valid key
    api_key = client.get_available_key()
    print(f"Using key: {api_key}")

    # 2. Perform your API call (e.g., to Google Gemini)
    # response = google_gemini.generate(...)

    # 3. Report usage ONLY if the call was successful
    client.increment_usage(api_key)

except Exception as e:
    print(f"Error: {e}")
```

### API Reference

*   **`GET /get_key`**: Returns a JSON object `{"key": "..."}` with the best available key. Returns 503 if no keys are available.
*   **`POST /report_usage`**: Accepts `{"key": "..."}` to increment the usage counter for that specific key.

---

<a name="traditional-chinese"></a>
## 🇹🇼 繁體中文 (Traditional Chinese)

**Control Gemini Key** 是一個專門設計用於管理和負載平衡 Google Gemini API 金鑰。它解決了一天20次的 (HTTP 429) 問題，透過智慧循環金鑰池並追蹤維護使用量，確保每個key每天最多被使用 20 次，您的應用程式穩定運行。

此微服務旨在自動化管理可用的 Google Gemini API 金鑰，透過智慧輪替以應對速率限制，確保服務不中斷。

### 系統需求

*   Python 3.8+
*   `python-dotenv` (僅伺服器端需要)

### 安裝說明

1.  複製專案：
    ```bash
    git clone https://github.com/luckysmallbird/control-gemini-key.git
    cd control-gemini-key
    ```

2.  安裝伺服器依賴：
    ```bash
    pip install python-dotenv
    ```

3.  **設定金鑰**：在專案根目錄下建立 `key.txt` 檔案，並填入您的 API 金鑰（每行一個）。
    ```text
    AIzaSyD...
    AIzaSyE...
    ```
    *或者，您也可以在 `.env` 檔案中設定 `GEMINI_API_KEY` (以逗號分隔)。*

### 使用方法

#### 1. 啟動伺服器 (Key Server)
執行輕量級 HTTP 伺服器。預設監聽 `5000` 端口。

```bash
python key_server.py
```

#### 2. 客戶端整合 (Key Client)
在您的 Python 應用程式中引入 `KeyClient` 來獲取金鑰並回報使用量。

```python
from key_client import KeyClient

# 初始化客戶端 (預設連線至 http://localhost:5000)
client = KeyClient()

try:
    # 1. 獲取一個可用金鑰
    api_key = client.get_available_key()
    print(f"正在使用金鑰: {api_key}")

    # 2. 執行您的 API 呼叫 (例如呼叫 Google Gemini)
    # response = google_gemini.generate(...)

    # 3. 只有在呼叫「成功」後才回報使用量
    client.increment_usage(api_key)

except Exception as e:
    print(f"發生錯誤: {e}")
```

### API 參考

*   **`GET /get_key`**：回傳 `{"key": "..."}`，提供當前最佳可用金鑰。若無可用金鑰則回傳 503。
*   **`POST /report_usage`**：接收 `{"key": "..."}`，將指定金鑰的使用計數加一。

---
**Note**: Please insure `key.txt` and `.env` are added to your `.gitignore` to prevent leaking sensitive credentials.
**注意**：請確保 `key.txt` 與 `.env` 已加入您的 `.gitignore` 檔案，以防止機密金鑰外洩。
