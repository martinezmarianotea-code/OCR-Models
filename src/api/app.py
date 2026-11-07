"""API local para comparar motores OCR.

    uvicorn src.api.app:app --port 8000

Los archivos subidos se escriben en un directorio temporal y se borran en
cuanto termina el procesamiento.
"""

import asyncio
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src import documents, engines, metrics

from . import history_store
from .models import EngineResult, HistoryEntry, ProcessResponse

ROOT = Path(__file__).resolve().parents[2]
SAMPLE = ROOT / "assets" / "samples" / "receta-demo.png"
FRONTEND_DIST = ROOT / "frontend" / "dist"
MAX_UPLOAD_BYTES = 15 * 1024 * 1024

app = FastAPI(title="OCR-Models", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)


def _to_result(run: engines.EngineRun, reference: str | None) -> EngineResult:
    scored = reference is not None and run.error is None
    return EngineResult(
        engine=run.key,
        label=run.label,
        text=run.text,
        seconds=run.seconds,
        chars=len(run.text),
        uses_network=run.uses_network,
        noise=round(metrics.noise_ratio(run.text), 4),
        cer=round(metrics.cer(run.text, reference), 4) if scored else None,
        wer=round(metrics.wer(run.text, reference), 4) if scored else None,
        error=run.error,
    )


def _parse_engines(raw: str) -> list[str]:
    selected = [key.strip() for key in raw.split(",") if key.strip() in engines.ENGINES]
    if not selected:
        raise HTTPException(400, "Selecciona al menos un motor válido.")
    return selected


async def _process(image: Path, filename: str, selected: list[str], reference: str | None) -> ProcessResponse:
    runs = await asyncio.gather(*(asyncio.to_thread(engines.run, key, str(image)) for key in selected))
    results = [_to_result(run, reference) for run in runs]
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    history_store.add(HistoryEntry(
        filename=filename,
        timestamp=timestamp,
        results=[r.model_copy(update={"text": ""}) for r in results],
    ))
    return ProcessResponse(
        filename=filename,
        has_reference=reference is not None,
        reference=reference,
        results=results,
        timestamp=timestamp,
    )


@app.get("/api/engines")
def list_engines():
    return engines.describe()


@app.get("/api/sample")
def sample_image():
    return FileResponse(SAMPLE, media_type="image/png")


@app.post("/api/sample/process", response_model=ProcessResponse)
async def process_sample(engines_param: str = Form("tesseract,layout", alias="engines")):
    reference = SAMPLE.with_suffix(".txt").read_text(encoding="utf-8")
    return await _process(SAMPLE, SAMPLE.name, _parse_engines(engines_param), reference)


@app.post("/api/process", response_model=ProcessResponse)
async def process_upload(
    file: UploadFile = File(...),
    engines_param: str = Form("tesseract,layout", alias="engines"),
    reference: str | None = Form(None),
):
    filename = Path(file.filename or "documento").name
    if not documents.is_supported(filename):
        raise HTTPException(400, "Formato no admitido. Usa PNG, JPG, WEBP, TIFF o PDF.")
    selected = _parse_engines(engines_param)

    data = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, "El archivo supera 15 MB.")

    with tempfile.TemporaryDirectory(prefix="ocr-models-") as tmp:
        path = Path(tmp) / f"entrada{Path(filename).suffix.lower()}"
        path.write_bytes(data)
        try:
            image = documents.as_image(path)
        except RuntimeError as exc:
            raise HTTPException(422, str(exc)) from exc
        return await _process(image, filename, selected, (reference or "").strip() or None)


@app.get("/api/history", response_model=list[HistoryEntry])
def history():
    return history_store.all_entries()


@app.delete("/api/history", status_code=204)
def clear_history():
    history_store.clear()


@app.get("/api/health")
def health():
    return {"status": "ok"}


# Si existe un build del frontend, se sirve desde la misma app (python -m src.api).
if FRONTEND_DIST.is_dir():
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")
