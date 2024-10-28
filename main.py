from fasthtml.common import *
from PIL import Image, ImageDraw, ImageFont
import os
import tempfile
import urllib

app,rt = fast_app()

headers = (Script(src="https://cdn.tailwindcss.com"),
           Link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/daisyui@4.11.1/dist/full.min.css"))

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
                onclick=f"window.location.href='/generate/' + document.getElementById('name').value",
                cls="btn btn-primary flex-1"
            ),
            Button(
                "Preview Certificate",
                onclick=f"window.location.href='/preview/' + document.getElementById('name').value",
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

def create_certificate(name):
    with Image.open(TEMPLATE_PATH) as certificate:
        draw = ImageDraw.Draw(certificate)
        name = urllib.parse.unquote(name)

        font_path = "web/arial.ttf"
        font_size = 70
        font = ImageFont.truetype(font_path, font_size)

        text_bbox = draw.textbbox((0, 0), name, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        text_x = (certificate.width - text_width) // 2
        text_y = (certificate.height - text_height + 310) // 2

        draw.text((text_x, text_y), name, fill="black", font=font)

        # Use a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
            certificate.save(tmp_file.name)
            return tmp_file.name

@app.route("/generate/{name}", methods=['GET'])
def generate_certificate(name: str):
    if not name:
        return "Name parameter is required", 400

    try:
        certificate_path = create_certificate(name)
        return FileResponse(certificate_path, filename=f'{name}_certificate.png', headers={"Content-Disposition": f"attachment; filename={name}_certificate.png"})
    except Exception as e:
        return f"An error occurred: {str(e)}", 500

@app.route("/preview/{name}", methods=['GET'])
def preview_certificate(name: str):
    if not name:
        return "Name parameter is required", 400
    try:
        certificate_path = create_certificate(name)
        return FileResponse(certificate_path)
    except Exception as e:
        return f"An error occurred: {str(e)}", 500


serve()