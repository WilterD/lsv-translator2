transcript = []
glosa_historial = []

def append_transcript(texto: str):
    transcript.append(texto)

def get_full_transcript() -> str:
    return " ".join(transcript)

def add_glosa(g: str):
    glosa_historial.append(g)

def get_glosa_historial():
    return glosa_historial