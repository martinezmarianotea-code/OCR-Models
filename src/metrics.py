"""Métricas para comparar el texto de un motor contra una referencia.

CER (character error rate) y WER (word error rate) son la distancia de edición
dividida entre la longitud de la referencia. 0.0 es una transcripción perfecta;
pueden superar 1.0 si el motor inventa mucho texto.
"""

import re
import unicodedata


def normalize(text: str) -> str:
    """Unifica Unicode, minúsculas y espacios para no castigar diferencias de formato."""
    text = unicodedata.normalize("NFC", text).lower()
    return re.sub(r"\s+", " ", text).strip()


def _edit_distance(a: list, b: list) -> int:
    if len(a) < len(b):
        a, b = b, a
    previous = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        current = [i]
        for j, y in enumerate(b, 1):
            current.append(min(
                previous[j] + 1,               # borrado
                current[j - 1] + 1,            # inserción
                previous[j - 1] + (x != y),    # sustitución
            ))
        previous = current
    return previous[-1]


def cer(hypothesis: str, reference: str) -> float:
    ref, hyp = normalize(reference), normalize(hypothesis)
    if not ref:
        return 0.0 if not hyp else 1.0
    return _edit_distance(list(hyp), list(ref)) / len(ref)


def wer(hypothesis: str, reference: str) -> float:
    ref, hyp = normalize(reference).split(), normalize(hypothesis).split()
    if not ref:
        return 0.0 if not hyp else 1.0
    return _edit_distance(hyp, ref) / len(ref)


def noise_ratio(text: str) -> float:
    """Proporción de caracteres que no son letras, dígitos, espacios ni puntuación común.

    Sirve como señal aproximada cuando no hay referencia: un OCR que lee basura
    suele producir muchos símbolos sueltos.
    """
    if not text:
        return 1.0
    allowed = set(".,:;()/-%'\"#")
    noisy = sum(not (c.isalnum() or c.isspace() or c in allowed) for c in text)
    return noisy / len(text)
