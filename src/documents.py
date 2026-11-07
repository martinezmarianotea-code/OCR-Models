"""Preparación de archivos de entrada: imágenes tal cual, PDF a PNG con poppler."""

import shutil
import subprocess
from pathlib import Path

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}


def is_supported(filename: str) -> bool:
    suffix = Path(filename).suffix.lower()
    return suffix in IMAGE_SUFFIXES or suffix == ".pdf"


def pdf_first_page(pdf_path: Path, dpi: int = 300) -> Path:
    """Convierte la primera página del PDF en un PNG junto al original."""
    if shutil.which("pdftoppm") is None:
        raise RuntimeError("Para leer PDF instala poppler (comando pdftoppm).")
    stem = pdf_path.with_suffix("")
    result = subprocess.run(
        ["pdftoppm", "-r", str(dpi), "-png", "-f", "1", "-l", "1", "-singlefile", str(pdf_path), str(stem)],
        capture_output=True,
        text=True,
    )
    png = stem.with_suffix(".png")
    if result.returncode != 0 or not png.exists():
        raise RuntimeError(f"No se pudo convertir el PDF: {result.stderr.strip() or 'error desconocido'}")
    return png


def as_image(path: Path) -> Path:
    return pdf_first_page(path) if path.suffix.lower() == ".pdf" else path
