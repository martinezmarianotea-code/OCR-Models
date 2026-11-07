"""Detección de bloques de texto con OpenCV y OCR bloque por bloque.

En vez de pedirle a Tesseract que entienda toda la página, primero se buscan
las regiones con texto: se binariza, se dilata en horizontal para fundir las
letras de una misma línea y se toman los contornos resultantes. Cada región se
recorta y se lee por separado, en orden de lectura (arriba-abajo, izquierda-derecha).
"""

import cv2
import numpy as np
import pytesseract

from .tesseract_engine import available, read_gray  # noqa: F401  (available se reexporta)

LABEL = "Bloques + Tesseract"
DESCRIPTION = "Detecta líneas y bloques con morfología de OpenCV y aplica OCR a cada recorte."
USES_NETWORK = False

LINE_CONFIG = "--oem 1 --psm 7 -l spa+eng"
MIN_HEIGHT = 12
PADDING = 6


def find_blocks(gray: np.ndarray) -> list[tuple[int, int, int, int]]:
    """Devuelve rectángulos (x, y, w, h) que probablemente contienen una línea de texto."""
    binary = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 31, 15
    )
    # Quita puntos aislados (ruido de escaneo) antes de unir letras.
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))

    kernel_w = max(15, gray.shape[1] // 60)
    merged = cv2.dilate(binary, cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_w, 3)))
    contours, _ = cv2.findContours(merged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    boxes = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        # Descarta ruido y líneas de regla (muy anchas y delgadas).
        if h < MIN_HEIGHT or w < h or (w > 20 * h and h < 2 * MIN_HEIGHT):
            continue
        boxes.append((x, y, w, h))

    return boxes


def group_lines(boxes: list[tuple[int, int, int, int]]) -> list[list[tuple[int, int, int, int]]]:
    """Agrupa rectángulos que comparten franja vertical y los ordena para leerlos."""
    lines: list[list[tuple[int, int, int, int]]] = []
    for box in sorted(boxes, key=lambda b: b[1] + b[3] / 2):
        center = box[1] + box[3] / 2
        if lines:
            top = min(b[1] for b in lines[-1])
            bottom = max(b[1] + b[3] for b in lines[-1])
            if top <= center <= bottom:
                lines[-1].append(box)
                continue
        lines.append([box])
    return [sorted(line, key=lambda b: b[0]) for line in lines]


def extract(image_path: str) -> str:
    gray = read_gray(image_path)
    height, width = gray.shape
    lines = []
    for line in group_lines(find_blocks(gray)):
        words = []
        for x, y, w, h in line:
            x0, y0 = max(0, x - PADDING), max(0, y - PADDING)
            x1, y1 = min(width, x + w + PADDING), min(height, y + h + PADDING)
            crop = gray[y0:y1, x0:x1]
            _, crop = cv2.threshold(crop, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            text = pytesseract.image_to_string(crop, config=LINE_CONFIG).strip()
            if text:
                words.append(text)
        if words:
            lines.append(" ".join(words))
    return "\n".join(lines)
