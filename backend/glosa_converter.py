import re

GLOSA_MAP = {
    "estoy": "YO",
    "en": "",
    "la": "",
    "el": "",
    "una": "",
    "casa": "CASA",
    "clases": "CLASES",
    "yo": "YO",
    "comiendo": "COMIENDO",
    "comer": "COMER",
    "comida": "COMIDA",
    "hola": "HOLA",
    "mundo": "MUNDO",
}

def texto_a_glosas(texto: str) -> list[str]:
    palabras = re.findall(r"\w+", texto.lower())
    return [GLOSA_MAP.get(p, p.upper()) for p in palabras if GLOSA_MAP.get(p, p.upper())]