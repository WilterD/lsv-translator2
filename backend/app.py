import time
from flask import Flask
from flask_socketio import SocketIO, emit
from vosk import Model, KaldiRecognizer
import sounddevice as sd
import queue, threading, json, os, re

# ---------- Config -----------------------------------------------------------
MODEL_PATH = "model"          # carpeta con el modelo Vosk (ya descomprimido)
SAMPLE_RATE = 16_000          # Hz
BLOCK_SIZE  = 8_000           # ≃ 0.5 s
CHANNELS    = 1               # mono
GLOSA_MAP = {                 # texto → glosa
    "casa": "Casa", "hola": "HOLA",
    "yo": "YO",   "estoy": "YO",
    "clases": "CLASES", "comiendo": "COMIENDO"
}
ANIMACIONES_MAP = {           # glosa → nombre de animación en el GLB
    "Casa": "Casa",
    "HOLA": "Hola",
    "YO":   "Yo",
    "CLASES": "Clases",
    "COMIENDO": "Comiendo"
}
# ------------------------------------------------------------------------------

# ---------- Flask‑Socket.IO ----------------------------------------------------
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")


# ---------- Vosk --------------------------------------------------------------
if not os.path.isdir(MODEL_PATH):
    raise FileNotFoundError(f"Modelo Vosk no encontrado en {MODEL_PATH}")

model       = Model(MODEL_PATH)
recognizer  = KaldiRecognizer(model, SAMPLE_RATE)
recognizer.SetWords(True)

# ---------- Estado de la captura ---------------------------------------------
audio_q: queue.Queue[bytes] = queue.Queue(maxsize=32)
streaming = False

def a_texto_glosa(texto: str) -> list[str]:
    """Convierte frase a lista de glosas usando GLOSA_MAP"""
    palabras = re.findall(r"\w+", texto.lower())
    return [GLOSA_MAP.get(p, p.upper()) for p in palabras if GLOSA_MAP.get(p)]

def mic_callback(indata, frames, time_, status):
    if status:
        print("⚠️  Mic status:", status)
    audio_q.put(bytes(indata))

def reconocer_en_hilo():
    global streaming
    with sd.RawInputStream(samplerate=SAMPLE_RATE,
                           blocksize=BLOCK_SIZE,
                           dtype='int16',
                           channels=CHANNELS,
                           callback=mic_callback):
        print("🎤  Escucha en tiempo real iniciada")
        while streaming:
            data = audio_q.get()
            if recognizer.AcceptWaveform(data):
                texto_final = json.loads(recognizer.Result()).get("text", "")
                if not texto_final:
                    continue
                for glosa in a_texto_glosa(texto_final):
                    anim = ANIMACIONES_MAP.get(glosa)  # puede ser None
                    print(f"✋  Glosa: {glosa}  → anim: {anim}")
                    # Log antes de emitir
                    print(f"[DEBUG] Emitting glosa via socket: glosa={glosa}, animacion={anim}")
                    socketio.emit("glosa", {"glosa": glosa, "animacion": anim, "timestamp": time.time()})
                    print(f"✅ Emitido: {glosa} | {anim or 'sin animación'}")

# ---------- Eventos Socket.IO -------------------------------------------------
@socketio.on("iniciar_reconocimiento")
def iniciar():
    global streaming
    if not streaming:                    # evita hilos duplicados
        streaming = True
        threading.Thread(target=reconocer_en_hilo, daemon=True).start()
    emit("estado", {"mensaje": "Reconocimiento iniciado"})

@socketio.on("detener_reconocimiento")
def detener():
    global streaming
    streaming = False
    emit("estado", {"mensaje": "Reconocimiento detenido"})

# ---------- start -------------------------------------------------------------
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
