from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from vosk import Model, KaldiRecognizer
import base64
import wave
import json
import io

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
model = Model("model")
rec = KaldiRecognizer(model, 16000)

@socketio.on('connect')
def handle_connect():
    print("🔌 Cliente conectado")

@socketio.on('audio_chunk')
def handle_audio(data):
    try:
        audio_bytes = base64.b64decode(data)
        if rec.AcceptWaveform(audio_bytes):
            result = json.loads(rec.Result())
            text = result.get("text", "")
            if text:
                print("🗣️ Glosa reconocida:", text)
                emit("message", {"glosa": text, "animacion": text}, broadcast=True)
        else:
            partial = json.loads(rec.PartialResult())
            emit("message", {"glosa": partial.get("partial", ""), "animacion": ""})
    except Exception as e:
        print("❌ Error en procesamiento de audio:", str(e))

@app.route("/resumen")
def resumen():
    return jsonify({"resumen": "Resumen generado por IA"})

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000)
