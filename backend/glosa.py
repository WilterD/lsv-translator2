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
def glosas_a_animaciones(glosas: list[str]) -> list[str]:
    animaciones = []
    for glosa in glosas:
        if glosa == "YO":
            animaciones.append("animacion_yo")
        elif glosa == "CASA":
            animaciones.append("animacion_casa")
        elif glosa == "COMIENDO":
            animaciones.append("animacion_comiendo")
        elif glosa == "HOLA":
            animaciones.append("animacion_hola")
        elif glosa == "MUNDO":
            animaciones.append("animacion_mundo")
        else:
            animaciones.append("animacion_default")
    return animaciones