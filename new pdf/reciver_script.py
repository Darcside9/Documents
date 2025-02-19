from flask import Flask, request
from pyngrok import ngrok
import threading

app = Flask(__name__)
print("[*] Starting server...")

@app.route('/log', methods=['POST'])
def log():
    data = request.json
    print(f"\n[!] Device Info:\nOS: {data['os']}\nIP: {data['ip']}\nHostname: {data['hostname']}")
    return "OK"

def start_ngrok():
    ngrok.set_auth_token("{{YOUR_NGROK_AUTH_TOKEN}}")  # Get from ngrok dashboard
    public_url = ngrok.connect(5000, bind_tls=True).public_url
    print(f"\n[+] Ngrok URL: {public_url}/log")

if __name__ == "__main__":
    threading.Thread(target=start_ngrok).start()
    app.run(host='0.0.0.0', port=5000)