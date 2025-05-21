from flask import Flask
from flask_sock import Sock

from .ws_audio import handle_audio_stream
from .summarizer import generate_summary
from .state import get_full_transcript



app = Flask(__name__)
sock = Sock(app)

@app.route("/resumen", methods=["GET"])
def resumen():
    texto = get_full_transcript()
    resumen = generate_summary(texto)
    return {"resumen": resumen}

@sock.route("/stream")
def stream(ws):
    handle_audio_stream(ws)