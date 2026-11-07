import shutil
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.api.app import app

client = TestClient(app)
SAMPLE = Path(__file__).resolve().parents[1] / "assets" / "samples" / "receta-demo.png"
needs_tesseract = pytest.mark.skipif(shutil.which("tesseract") is None, reason="tesseract no instalado")


def test_engines_endpoint():
    data = client.get("/api/engines").json()
    assert {"tesseract", "layout", "gemini"} <= set(data)


def test_rejects_unsupported_file():
    r = client.post("/api/process", files={"file": ("notas.txt", b"hola", "text/plain")})
    assert r.status_code == 400


def test_rejects_unknown_engine():
    r = client.post(
        "/api/process",
        files={"file": ("a.png", SAMPLE.read_bytes(), "image/png")},
        data={"engines": "inexistente"},
    )
    assert r.status_code == 400


@needs_tesseract
def test_sample_is_scored_against_reference():
    r = client.post("/api/sample/process", data={"engines": "tesseract"})
    assert r.status_code == 200
    body = r.json()
    assert body["has_reference"] is True
    assert body["results"][0]["cer"] < 0.1


@needs_tesseract
def test_upload_with_reference_and_history_keeps_no_text():
    client.delete("/api/history")
    r = client.post(
        "/api/process",
        files={"file": ("receta.png", SAMPLE.read_bytes(), "image/png")},
        data={"engines": "tesseract", "reference": SAMPLE.with_suffix(".txt").read_text()},
    )
    assert r.status_code == 200
    assert r.json()["results"][0]["cer"] is not None

    history = client.get("/api/history").json()
    assert history[0]["filename"] == "receta.png"
    assert history[0]["results"][0]["text"] == ""
