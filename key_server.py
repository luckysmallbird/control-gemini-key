import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import sys
from pathlib import Path
import threading
import time

sys.path.append(str(Path(__file__).parent))

from key_manager import KeyManager

key_mgr = KeyManager()

class KeyRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/get_key':
            try:
                key = key_mgr.get_available_key()
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"key": key}).encode())
            except Exception as e:
                self.send_response(503) 
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/report_usage':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data)
                key = data.get("key")
                
                if key:
                    key_mgr.increment_usage(key)
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "ok"}).encode())
                else:
                    self.send_response(400)
                    self.end_headers()
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        
        elif self.path == '/report_invalid':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data)
                key = data.get("key")
                
                if key:
                    key_mgr.mark_key_invalid(key)
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "ok"}).encode())
                else:
                    self.send_response(400)
                    self.end_headers()
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())

        else:
            self.send_response(404)
            self.end_headers()

def scheduled_key_reload(interval=1800):
    print(f"[KeyServer] Background Key Scanner started (checks every {interval} seconds)")
    while True:
        try:
            time.sleep(interval)
            print("[KeyServer] Performing scheduled Key scan...")
            key_mgr.load_keys()
        except Exception as e:
            print(f"[KeyServer] Error during scheduled scan: {e}")

def run(server_class=HTTPServer, handler_class=KeyRequestHandler, port=5000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    
    reloader_thread = threading.Thread(target=scheduled_key_reload, args=(1800,), daemon=True)
    reloader_thread.start()
    
    print(f'Starting Key Server on port {port}...')
    print(f'API Endpoints:')
    print(f'  GET  http://localhost:{port}/get_key')
    print(f'  POST http://localhost:{port}/report_usage {{ "key": "..."}}')
    print(f'  POST http://localhost:{port}/report_invalid {{ "key": "..."}}')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Key Server...")
        httpd.server_close()

if __name__ == '__main__':
    run()
