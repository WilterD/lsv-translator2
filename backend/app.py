from flask import Flask
from flask_socketio import SocketIO, emit
from vosk import Model, KaldiRecognizer
import sounddevice as sd
import queue
import threading
import json
import os

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

MODEL_PATH = "model/"
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"No se encontró el modelo Vosk en {MODEL_PATH}")

model = Model(MODEL_PATH)
recognizer = KaldiRecognizer(model, 16000)
recognizer.SetWords(True)

audio_queue = queue.Queue()
streaming = False

def texto_a_glosas(texto):
    GLOSA_MAP = {
        "casa": "CASA", "hola": "HOLA", "yo": "YO", "estoy": "YO",
        "clases": "CLASES", "comiendo": "COMIENDO"
    }
    palabras = texto.lower().split()
    return [GLOSA_MAP.get(p, p.upper()) for p in palabras if GLOSA_MAP.get(p, p.upper())]

def audio_callback(indata, frames, time, status):
    if status:
        print("⚠️ Mic status:", status)
    audio_queue.put(bytes(indata))

def recognize_stream():
    global streaming
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16', channels=1, callback=audio_callback):
        print("🎤 Iniciando escucha en tiempo real")
        while streaming:
            data = audio_queue.get()
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                texto = result.get("text", "")
                glosas = texto_a_glosas(texto)
                for g in glosas:
                    print(f"✋ Glosa detectada: {g}")
                    animacion = "Casa" if g == "CASA" else None
                    socketio.emit('glosa', {'glosa': g, 'animacion': animacion})

@socketio.on("iniciar_reconocimiento")
def iniciar():
    global streaming
    if not streaming:
        streaming = True
        threading.Thread(target=recognize_stream, daemon=True).start()
    emit("estado", {"mensaje": "Reconocimiento iniciado"})

@socketio.on("detener_reconocimiento")
def detener():
    global streaming
    streaming = False
    emit("estado", {"mensaje": "Reconocimiento detenido"})


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
