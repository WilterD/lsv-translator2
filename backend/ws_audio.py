import json
import queue
from vosk import Model, KaldiRecognizer
import numpy as np

from .glosa_converter import texto_a_glosas
from .state import add_glosa, append_transcript



model = Model("backend/models/vosk-model-es")

def handle_audio_stream(ws):
    recognizer = KaldiRecognizer(model, 16000)
    buffer = queue.Queue(maxsize=2)

    def process():
        while True:
            data = buffer.get()
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("text", "")
                if text:
                    append_transcript(text)
                    glosas = texto_a_glosas(text)
                    anims = glosas_a_animaciones(glosas)
                    for glosa, anim in zip(glosas, anims):
                        add_glosa(glosa)
                        ws.send(json.dumps({"glosa": glosa, "animacion": anim}))
            else:
                partial = json.loads(recognizer.PartialResult())
                # opcional: enviar parciales si deseas

    import threading
    threading.Thread(target=process, daemon=True).start()

    while True:
        data = ws.receive()
        if data is None:
            break
        buffer.put(data)