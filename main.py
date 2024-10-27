from fasthtml.common import *
from PIL import Image, ImageDraw, ImageFont
import os

app,rt = fast_app()

headers = (Script(src="https://cdn.tailwindcss.com"),
           Link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/daisyui@4.11.1/dist/full.min.css"))

messages = [
    {"role":"user", "content":"Hello"},
    {"role":"assistant", "content":"Hi, how can I assist you?"}
]

def ChatMessage(msg):
    return Div(
        Div(msg['role'], cls="chat-header"),
        Div(msg['content'], cls=f"chat-bubble chat-bubble-{'primary' if msg['role'] == 'user' else 'secondary'}"),
        cls=f"chat chat-{'end' if msg['role'] == 'user' else 'start'}")

chatbox = Div(
    Div(*[ChatMessage(msg) for msg in messages], cls="chat-box", id="chatlist"),
    cls="max-w-screen-md mx-auto"
)

chatinput = Div(
    P("Input user here"),cls="max-w-screen-md mx-auto pt-4"
)

mainsc = Div(
    chatbox(),
    chatinput(),
)


@rt('/')
def get(): return Html(*headers, mainsc)

# Path to the certificate template
TEMPLATE_PATH = "certificate_template.png"

def create_certificate(name):
    certificate = Image.open(TEMPLATE_PATH)
    draw = ImageDraw.Draw(certificate)

    font_path = "arial.ttf" 
    font_size = 70
    font = ImageFont.truetype(font_path, font_size)

    text_bbox = draw.textbbox((0, 0), name, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    text_x = (certificate.width - text_width) // 2
    text_y = (certificate.height - text_height + 310) // 2

    draw.text((text_x, text_y), name, fill="black", font=font)

    output_path = f"certificate/{name}_certificate.png"
    certificate.save(output_path)
    return output_path

@app.route("/generate/{name}", methods=['GET'])
def generate_certificate(name: str):
    if not name:
        return "Name parameter is required", 400
    
    certificate_path = create_certificate(name)
    return FileResponse(f'{certificate_path}', filename=f'{name}_certificate.png', headers={"Content-Disposition": f"attachment; filename={name}_certificate.png"})
    # return FileResponse(f'{certificate_path}')



serve()