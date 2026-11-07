"""Registro de motores OCR.

Cada motor es un módulo con constantes descriptivas y una función
``extract(image_path) -> str``. El cronometraje y el manejo de errores viven
aquí para que todos se midan de la misma forma.
"""

import importlib
import time
from dataclasses import dataclass, field

ENGINES = {
    "tesseract": "src.engines.tesseract_engine",
    "layout": "src.engines.layout_engine",
    "gemini": "src.engines.gemini_engine",
}


@dataclass
class EngineRun:
    key: str
    label: str
    text: str = ""
    seconds: float = 0.0
    uses_network: bool = False
    error: str | None = None
    extra: dict = field(default_factory=dict)


def load(key: str):
    if key not in ENGINES:
        raise KeyError(f"Motor desconocido: {key}")
    return importlib.import_module(ENGINES[key])


def describe() -> dict[str, dict]:
    info = {}
    for key in ENGINES:
        module = load(key)
        info[key] = {
            "label": module.LABEL,
            "description": module.DESCRIPTION,
            "uses_network": module.USES_NETWORK,
            "available": module.available(),
        }
    return info


def run(key: str, image_path: str) -> EngineRun:
    module = load(key)
    result = EngineRun(key=key, label=module.LABEL, uses_network=module.USES_NETWORK)
    start = time.perf_counter()
    try:
        result.text = module.extract(image_path).strip()
    except Exception as exc:  # cada motor reporta su propio fallo sin tumbar a los demás
        result.error = str(exc).strip() or exc.__class__.__name__
    result.seconds = round(time.perf_counter() - start, 3)
    return result
