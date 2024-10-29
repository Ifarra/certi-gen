from fasthtml.common import *
from PIL import Image, ImageDraw, ImageFont
import os
import tempfile
import urllib
import qrcode
import base64
from datetime import datetime

app,rt = fast_app()

headers = (Script(src="https://cdn.tailwindcss.com"),
           Link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/daisyui@4.11.1/dist/full.min.css"),
           Link(rel="icon", href="favicon.ico", type="image/x-icon"))

mainsc = Div(
    Div(
        H1("Certificate Generator", cls="text-2xl font-bold mb-4 text-gray-300"),
        Div(
            Input(type="text", id="name", placeholder="Enter Name", cls="input input-bordered w-full"),
            cls="mb-4"
        ),
        Div(
            Button(
                "Download Certificate",
                onclick=f"window.location.href='/generate/' + document.getElementById('name').value + '/' + window.location.hostname",
                cls="btn btn-primary flex-1"
            ),
            Button(
                "Preview Certificate",
                onclick=f"window.location.href='/preview/' + document.getElementById('name').value + '/' + window.location.hostname",
                cls="btn btn-primary flex-1"
            ),

            cls="flex w-full gap-2"
        ),
        cls="bg-gray-700 p-8 rounded-lg shadow-md w-96"
    ),
    cls="flex flex-col items-center justify-center min-h-screen bg-gray-900"
)


@rt('/')
def get(): return Html(*headers, mainsc)

# Path to the certificate template
TEMPLATE_PATH = "web/certificate_template.png"

def encrypt():
    datenew = datetime.now().strftime("%Y-%m-%d")
    
    encoded_date = base64.b64encode(datenew.encode()).decode()
    
    return encoded_date, datenew

def decrypt(encoded_date):
    decoded_date = base64.b64decode(encoded_date).decode()
    
    return decoded_date

def generate_qr_code(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=5,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white")

def create_certificate(name, host):
    with Image.open(TEMPLATE_PATH) as certificate:
        draw = ImageDraw.Draw(certificate)
        name = urllib.parse.unquote(name)

        font_path = "web/arial.ttf"
        font_size = 70 if len(name) <= 25 else 45
        font = ImageFont.truetype(font_path, font_size)
        fontdate = ImageFont.truetype(font_path, 50)

        text_bbox = draw.textbbox((0, 0), name, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        text_x = (certificate.width - text_width) // 2
        text_y = (certificate.height - text_height + 310) // 2

        draw.text((text_x, text_y), name, fill="black", font=font)
        
        date, date_new = encrypt()

        img_qr = generate_qr_code(f"https://{host}/certificate/{date}/{name}/{host}")
        img_qr = img_qr.convert("RGBA")

        pos_x = certificate.width - img_qr.width - 50
        pos_y = certificate.height - img_qr.height - 50
        certificate.paste(img_qr, (pos_x, pos_y), img_qr)
        draw.text((409, 1050), date_new, fill="black", font=fontdate)

        signature = Image.open("web/signature.png")
        pos_x = 680
        pos_y = 985
        certificate.paste(signature, (pos_x, pos_y), signature)
        

        # Use a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
            certificate.save(tmp_file.name)
            return tmp_file.name

def view_certificate(name, date, host):
    with Image.open(TEMPLATE_PATH) as certificate:
        draw = ImageDraw.Draw(certificate)
        name = urllib.parse.unquote(name)

        font_path = "web/arial.ttf"
        font_size = 70 if len(name) <= 25 else 45
        font = ImageFont.truetype(font_path, font_size)
        fontdate = ImageFont.truetype(font_path, 50)

        text_bbox = draw.textbbox((0, 0), name, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        text_x = (certificate.width - text_width) // 2
        text_y = (certificate.height - text_height + 310) // 2

        draw.text((text_x, text_y), name, fill="black", font=font)

        img_qr = generate_qr_code(f"https://{host}/certificate/{date}/{name}/{host}")
        img_qr = img_qr.convert("RGBA")

        date = decrypt(date)

        pos_x = certificate.width - img_qr.width - 50
        pos_y = certificate.height - img_qr.height - 50
        certificate.paste(img_qr, (pos_x, pos_y), img_qr)
        draw.text((409, 1050), date, fill="black", font=fontdate)

        signature = Image.open("web/signature.png")
        pos_x = 680
        pos_y = 985
        certificate.paste(signature, (pos_x, pos_y), signature)

        # Use a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
            certificate.save(tmp_file.name)
            return tmp_file.name

@app.route("/generate/{name}/{host}", methods=['GET'])
def generate_certificate(name: str, host: str):
    if not name:
        return "Name parameter is required", 400

    try:
        certificate_path = create_certificate(name, host)
        return FileResponse(certificate_path, filename=f'{name}_certificate.png', headers={"Content-Disposition": f"attachment; filename={name}_certificate.png"})
    except Exception as e:
        return f"An error occurred: {str(e)}", 500

@app.route("/preview/{name}/{host}", methods=['GET'])
def preview_certificate(name: str, host: str):
    if not name:
        return "Name parameter is required", 400
    try:
        certificate_path = create_certificate(name, host)
        return FileResponse(certificate_path)
    except Exception as e:
        return f"An error occurred: {str(e)}", 500

@app.route("/certificate/{date}/{name}/{host}", methods=['GET'])
def get_certificate(name: str, date: str, host: str):
    if not name:
        return "Name parameter is required", 400
    try:
        certificate_path = view_certificate(name, date, host)
        return FileResponse(certificate_path, media_type="image/png")
    except Exception as e:
        return f"An error occurred: {str(e)}", 500




serve()