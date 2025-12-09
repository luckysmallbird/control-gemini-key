import json
import urllib.request
import urllib.error

class KeyClient:
    def __init__(self, host="http://localhost:5000"):
        self.host = host

    def get_available_key(self):
        url = f"{self.host}/get_key"
        try:
            with urllib.request.urlopen(url) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    return data["key"]
                else:
                    raise Exception(f"Key Server returned status {response.status}")
        except urllib.error.HTTPError as e:
            error_msg = e.read().decode()
            raise Exception(f"Key Server Error ({e.code}): {error_msg}")
        except Exception as e:
            raise Exception(f"Unable to connect to Key Server ({self.host}): {e}\nPlease check if the server is started (python Apeiria/manager_key/key_server.py)")

    def increment_usage(self, key):
        url = f"{self.host}/report_usage"
        data = json.dumps({"key": key}).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'}, method='POST')
        
        try:
            with urllib.request.urlopen(req) as response:
                if response.status != 200:
                    print(f"[KeyClient] Warning: Report usage returned status {response.status}")
        except Exception as e:
            print(f"[KeyClient] Failed to report key usage: {e}")