from transformers import pipeline

summarizer = pipeline("summarization", model="t5-small")

def generate_summary(texto: str) -> str:
    out = summarizer(texto, max_length=100, min_length=30, do_sample=False)
    return out[0]['summary_text']