"""Genera una receta médica ficticia para probar los motores OCR.

Todos los datos (clínica, médico, paciente, cédula) son inventados. El script
escribe la imagen y, junto a ella, un .txt con el texto exacto que contiene;
ese archivo sirve como referencia para medir el error de cada motor.

    python scripts/make_sample.py
    python scripts/make_sample.py --clean   # sin ruido ni rotación
"""

import argparse
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT = Path(__file__).resolve().parent.parent / "assets" / "samples" / "receta-demo.png"

FONT_CANDIDATES = [
    "DejaVuSans.ttf",
    "/usr/share/fonts/TTF/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/Library/Fonts/Arial.ttf",
    "C:/Windows/Fonts/arial.ttf",
]

HEADER = ["CLÍNICA SAN ISIDRO DEL VALLE", "Medicina general y familiar"]

BODY = [
    "Dra. Laura Méndez Ortiz",
    "Céd. Prof. 0000000 (ejemplo)",
    "Fecha: 14/03/2025",
    "",
    "Paciente: Juan Pérez Ejemplo",
    "Edad: 34 años",
    "",
    "Rx",
    "1. Amoxicilina 500 mg cápsulas",
    "   Tomar 1 cada 8 horas por 7 días",
    "2. Paracetamol 500 mg tabletas",
    "   Tomar 1 cada 6 horas si hay fiebre",
    "3. Loratadina 10 mg tabletas",
    "   Tomar 1 cada 24 horas por 5 días",
    "",
    "Indicaciones: abundantes líquidos y reposo.",
    "Próxima cita: 21/03/2025",
]

FOOTER = "DOCUMENTO DE EJEMPLO - DATOS FICTICIOS"


def load_font(size: int) -> ImageFont.ImageFont:
    for candidate in FONT_CANDIDATES:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default(size=size)


def render(clean: bool) -> Image.Image:
    width, height = 1240, 1650
    img = Image.new("L", (width, height), 250)
    draw = ImageDraw.Draw(img)

    title, subtitle = load_font(46), load_font(28)
    body, small = load_font(32), load_font(22)

    draw.text((90, 80), HEADER[0], font=title, fill=25)
    draw.text((90, 140), HEADER[1], font=subtitle, fill=70)
    draw.line((90, 195, width - 90, 195), fill=60, width=3)

    y = 240
    for line in BODY:
        if line:
            font = title if line == "Rx" else body
            draw.text((90, y), line, font=font, fill=20)
        y += 58

    draw.line((width - 470, height - 260, width - 90, height - 260), fill=60, width=2)
    draw.text((width - 400, height - 245), "Firma del médico", font=small, fill=80)
    draw.text((90, height - 110), FOOTER, font=small, fill=110)

    if clean:
        return img

    # Simula un escaneo: leve rotación, desenfoque y ruido de papel.
    rng = random.Random(7)
    img = img.rotate(0.8, resample=Image.BICUBIC, fillcolor=250, expand=False)
    img = img.filter(ImageFilter.GaussianBlur(0.6))
    px = img.load()
    for _ in range(width * height // 60):
        x, y = rng.randrange(width), rng.randrange(height)
        px[x, y] = max(0, px[x, y] - rng.randint(20, 90))
    return img


def reference_text() -> str:
    lines = HEADER + BODY + ["Firma del médico", FOOTER]
    return "\n".join(line.strip() for line in lines if line.strip()) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument("--clean", action="store_true", help="sin ruido ni rotación")
    args = parser.parse_args()

    args.out.parent.mkdir(parents=True, exist_ok=True)
    render(args.clean).save(args.out, optimize=True)
    args.out.with_suffix(".txt").write_text(reference_text(), encoding="utf-8")
    print(f"{args.out}\n{args.out.with_suffix('.txt')}")


if __name__ == "__main__":
    main()
