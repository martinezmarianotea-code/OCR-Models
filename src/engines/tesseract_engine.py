"""Tesseract sobre la página completa, con limpieza previa en OpenCV."""

import shutil

import cv2
import numpy as np
import pytesseract

LABEL = "Tesseract"
DESCRIPTION = "Página completa: escala de grises, reducción de ruido y binarización Otsu antes del OCR."
USES_NETWORK = False

TESS_CONFIG = "--oem 1 --psm 4 -l spa+eng"


def available() -> bool:
    return shutil.which("tesseract") is not None


def read_gray(image_path: str) -> np.ndarray:
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"No se pudo abrir la imagen: {image_path}")
    return img


def binarize(gray: np.ndarray) -> np.ndarray:
    denoised = cv2.fastNlMeansDenoising(gray, h=10)
    _, binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return binary


def extract(image_path: str) -> str:
    return pytesseract.image_to_string(binarize(read_gray(image_path)), config=TESS_CONFIG)
