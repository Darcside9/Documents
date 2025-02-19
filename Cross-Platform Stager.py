import platform, requests, socket, time

def get_device_info():
    return {
        "os": platform.system(),
        "hostname": socket.gethostname(),
        "ip": requests.get('https://api.ipify.org').text
    }

while True:
    try:
        data = get_device_info()
        requests.post("http://127.0.0.1:4040/log", json=data)
        time.sleep(3600)  # Report hourly
    except requests.ConnectionError:
        time.sleep(300)  # Check every 5mins if offline