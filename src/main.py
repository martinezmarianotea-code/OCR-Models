"""Compara los motores OCR desde la terminal.

    python -m src.main assets/samples/receta-demo.png
    python -m src.main foto.jpg --engines tesseract layout
    python -m src.main foto.jpg --reference transcripcion.txt --save resultados/

Si junto a la imagen existe un .txt con el mismo nombre, se usa como referencia
para calcular CER y WER.
"""

import argparse
import sys
import tempfile
from pathlib import Path

from rich import box
from rich.console import Console
from rich.table import Table

from src import documents, engines, metrics

console = Console()


def _fmt_rate(value: float | None) -> str:
    return "—" if value is None else f"{value:.1%}"


def compare(image: Path, selected: list[str], reference: str | None) -> list[tuple[engines.EngineRun, float | None, float | None]]:
    rows = []
    for key in selected:
        with console.status(f"{engines.load(key).LABEL}…"):
            run = engines.run(key, str(image))
        scored = reference is not None and run.error is None
        rows.append((
            run,
            metrics.cer(run.text, reference) if scored else None,
            metrics.wer(run.text, reference) if scored else None,
        ))
    return rows


def print_table(rows, has_reference: bool) -> None:
    table = Table(box=box.SIMPLE_HEAD)
    table.add_column("Motor")
    table.add_column("Tiempo", justify="right")
    table.add_column("Caracteres", justify="right")
    if has_reference:
        table.add_column("CER", justify="right")
        table.add_column("WER", justify="right")
    table.add_column("Red", justify="center")

    for run, cer, wer in rows:
        if run.error:
            table.add_row(f"{run.label} [red](error)[/red]", *["—"] * (len(table.columns) - 1))
            continue
        cells = [run.label, f"{run.seconds:.2f} s", str(len(run.text))]
        if has_reference:
            cells += [_fmt_rate(cer), _fmt_rate(wer)]
        cells.append("sí" if run.uses_network else "no")
        table.add_row(*cells)
    console.print(table)
    for run, _, _ in rows:
        if run.error:
            console.print(f"[red]{run.label}:[/red] {run.error}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Compara motores OCR sobre una imagen o PDF.")
    parser.add_argument("file", type=Path, help="imagen o PDF (se usa la primera página)")
    parser.add_argument("--engines", nargs="+", choices=list(engines.ENGINES), default=["tesseract", "layout"])
    parser.add_argument("--reference", type=Path, help="transcripción correcta para medir CER/WER")
    parser.add_argument("--save", type=Path, metavar="DIR", help="guarda el texto de cada motor en DIR")
    args = parser.parse_args()

    if not args.file.exists():
        sys.exit(f"No existe el archivo: {args.file}")
    if not documents.is_supported(args.file.name):
        sys.exit("Formato no admitido. Usa PNG, JPG, WEBP, TIFF o PDF.")

    ref_path = args.reference or args.file.with_suffix(".txt")
    reference = ref_path.read_text(encoding="utf-8") if ref_path.exists() else None

    with tempfile.TemporaryDirectory() as tmp:
        source = args.file
        if source.suffix.lower() == ".pdf":
            source = Path(tmp) / "entrada.pdf"
            source.write_bytes(args.file.read_bytes())
        rows = compare(documents.as_image(source), args.engines, reference)

    print_table(rows, reference is not None)
    if reference is None:
        console.print("[dim]Sin referencia: añade --reference para medir CER y WER.[/dim]")

    if args.save:
        args.save.mkdir(parents=True, exist_ok=True)
        for run, _, _ in rows:
            (args.save / f"{run.key}.txt").write_text(run.text + "\n", encoding="utf-8")
        console.print(f"Textos guardados en {args.save}/")


if __name__ == "__main__":
    main()
