from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import json
import time
from datetime import datetime
import signal
import sys

LOG_FILE = 'payload.log'

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            # Log incoming POST request
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'type': 'POST',
                'client_ip': self.client_address[0],
                'data': post_data.decode()
            }
            with open(LOG_FILE, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "received"}')
            print(f"[+] POST received and logged from {self.client_address[0]} ✅")
        except Exception as e:
            print(f"❌ Error handling POST: {e}")
            self.send_response(500)
            self.end_headers()

    def do_GET(self):
        try:
            client_ip = self.client_address[0]
            user_agent = self.headers.get('User-Agent', 'Unknown')
            query = urlparse(self.path).query
            params = parse_qs(query)

            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'type': 'GET (PDF Opened)',
                'client_ip': client_ip,
                'user_agent': user_agent,
                'params': params
            }
            with open(LOG_FILE, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')

            # Send 200 OK (instead of 204) to prevent browser blocking
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
            self.end_headers()
            self.wfile.write(b'Tracking acknowledged')

            print(f"[+] PDF opened event logged from {client_ip} ({user_agent})")
        except Exception as e:
            print(f"❌ Error handling GET: {e}")
            self.send_response(500)
            self.end_headers()

def graceful_shutdown(signal_received, frame):
    print("\n👋 Shutting down server gracefully. Goodbye!")
    sys.exit(0)

if __name__ == '__main__':
    # Handle Ctrl+C gracefully
    signal.signal(signal.SIGINT, graceful_shutdown)

    server = HTTPServer(('', 8000), Handler)
    print("🚀 [Server] Listening on http://localhost:8000 ...")
    server.serve_forever()
