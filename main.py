from fasthtml.common import *

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

serve()