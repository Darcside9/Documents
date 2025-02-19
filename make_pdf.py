from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from http.server import BaseHTTPRequestHandler, HTTPServer
from io import BytesIO
import sys
import threading
import json
import requests


def create_tracking_pdf(filename, tracking_url):
    """
    Generates a PDF file with an embedded tracking pixel linked to the provided tracking URL.

    :param filename: Name of the PDF file to be created.
    :param tracking_url: URL pointing to the tracking pixel endpoint.
    """
    try:
        c = canvas.Canvas(filename, pagesize=letter)
        c.drawString(100, 750, "This PDF has tracking enabled.")
        c.drawImage(f"{tracking_url}/tracking-pixel.png", 0, 0, width=1, height=1, mask='auto')
        c.save()
        print(f"[✅] PDF '{filename}' generated with tracking pixel pointing to {tracking_url}.")
    except Exception as e:
        print(f"[❌] Error generating PDF: {e}")


class TrackingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/tracking-pixel.png":
            self.send_response(200)
            self.send_header("Content-type", "image/png")
            self.end_headers()
            pixel = (
                b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
                b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0bIDATx\x9cc``\x00\x00"
                b"\x00\x02\x00\x01\xe2!\xbc33\x00\x00\x00\x00IEND\xaeB`\x82"
            )
            self.wfile.write(pixel)
            print(f"[📡] Tracking pixel requested from: {self.client_address[0]}")
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        return  # Suppress default logging


def start_tracking_server(port=8001):
    try:
        server = HTTPServer(("", port), TrackingHandler)
        print(f"[✅] Tracking server running on port {port}...")
        server.serve_forever()
    except OSError as e:
        print(f"[❌] Failed to start server on port {port}: {e}")
        sys.exit(1)


def get_ngrok_tracking_url(target_port=8001):
    try:
        response = requests.get("http://127.0.0.1:4040/api/tunnels")
        tunnels = response.json().get("tunnels", [])
        for tunnel in tunnels:
            if tunnel["config"]["addr"].endswith(str(target_port)):
                print(f"[✅] Found ngrok tunnel for port {target_port}: {tunnel['public_url']}")
                return tunnel["public_url"]
        print("[❌] No matching ngrok tunnel found for the tracking server.")
        sys.exit(1)
    except Exception as e:
        print(f"[❌] Could not retrieve ngrok tracking URL: {e}")
        sys.exit(1)


def main():
    if len(sys.argv) != 2:
        print("Usage: python generate_pdf.py <output_filename.pdf>")
        sys.exit(1)

    filename = sys.argv[1]
    port = 8001  # Tracking server port

    # Start the tracking server in a separate thread
    server_thread = threading.Thread(target=start_tracking_server, args=(port,), daemon=True)
    server_thread.start()

    tracking_url = get_ngrok_tracking_url(port)
    create_tracking_pdf(filename, tracking_url)


if __name__ == "__main__":
    main()
