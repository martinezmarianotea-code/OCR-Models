"""Transcripción con un modelo multimodal de Google Gemini.

Requiere GEMINI_API_KEY (Google AI Studio). La imagen sale de tu equipo, así
que no uses este motor con documentos reales que contengan datos personales.
"""

import base64
import mimetypes
import os
import time

import requests
from dotenv import load_dotenv

load_dotenv()

LABEL = "Gemini"
DESCRIPTION = "Modelo multimodal vía API. Envía la imagen a Google; requiere clave e internet."
USES_NETWORK = True

API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
PROMPT = (
    "Transcribe exactamente el texto visible en esta imagen de una receta médica. "
    "Conserva el orden y los saltos de línea. No agregues comentarios, títulos, "
    "formato Markdown ni texto que no aparezca en la imagen. "
    "Si una palabra es ilegible, escribe [ilegible]."
)


def _api_key() -> str:
    return os.getenv("GEMINI_API_KEY", "")


def _model() -> str:
    return os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


def available() -> bool:
    return bool(_api_key())


def _strip_fences(text: str) -> str:
    lines = text.strip().splitlines()
    if lines and lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].startswith("```"):
        lines = lines[:-1]
    return "\n".join(lines)


def extract(image_path: str) -> str:
    key = _api_key()
    if not key:
        raise RuntimeError("Falta GEMINI_API_KEY en el archivo .env.")

    mime = mimetypes.guess_type(image_path)[0] or "image/png"
    with open(image_path, "rb") as f:
        data = base64.b64encode(f.read()).decode()

    payload = {
        "contents": [{"parts": [
            {"text": PROMPT},
            {"inline_data": {"mime_type": mime, "data": data}},
        ]}],
        "generationConfig": {"temperature": 0},
    }
    url = API_URL.format(model=_model())
    headers = {"x-goog-api-key": key}

    for attempt in range(3):
        response = requests.post(url, json=payload, headers=headers, timeout=90)
        if response.status_code != 429:
            break
        time.sleep(5 * (attempt + 1))

    if response.status_code == 429:
        raise RuntimeError("Gemini respondió 429: se agotó la cuota. Intenta más tarde.")
    if response.status_code != 200:
        raise RuntimeError(f"Gemini respondió {response.status_code}: {response.text[:200]}")

    candidates = response.json().get("candidates") or []
    parts = candidates[0].get("content", {}).get("parts", []) if candidates else []
    text = "".join(p.get("text", "") for p in parts)
    if not text:
        raise RuntimeError("Gemini no devolvió texto (posible bloqueo por filtros de seguridad).")
    return _strip_fences(text)
