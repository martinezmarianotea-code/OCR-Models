import shutil
from pathlib import Path

import pytest

from src import engines, metrics
from src.engines import gemini_engine

SAMPLE = Path(__file__).resolve().parents[1] / "assets" / "samples" / "receta-demo.png"
REFERENCE = SAMPLE.with_suffix(".txt").read_text(encoding="utf-8")

needs_tesseract = pytest.mark.skipif(shutil.which("tesseract") is None, reason="tesseract no instalado")


@needs_tesseract
@pytest.mark.parametrize("key, max_cer", [("tesseract", 0.10), ("layout", 0.05)])
def test_local_engines_read_the_sample(key, max_cer):
    run = engines.run(key, str(SAMPLE))
    assert run.error is None
    assert "Amoxicilina" in run.text
    assert metrics.cer(run.text, REFERENCE) < max_cer


def test_missing_file_is_reported_not_raised():
    run = engines.run("tesseract", "no-existe.png")
    assert run.error


def test_describe_lists_every_engine():
    info = engines.describe()
    assert set(info) == set(engines.ENGINES)
    assert info["gemini"]["uses_network"] is True


def test_gemini_without_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    run = engines.run("gemini", str(SAMPLE))
    assert "GEMINI_API_KEY" in run.error


def test_gemini_parses_response(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "clave-de-prueba")
    sent = {}

    class FakeResponse:
        status_code = 200

        def json(self):
            return {"candidates": [{"content": {"parts": [{"text": "```\nRx\nAmoxicilina\n```"}]}}]}

    def fake_post(url, json, headers, timeout):
        sent.update(url=url, headers=headers)
        return FakeResponse()

    monkeypatch.setattr(gemini_engine.requests, "post", fake_post)
    assert gemini_engine.extract(str(SAMPLE)) == "Rx\nAmoxicilina"
    # la clave va en el encabezado, no en la URL
    assert "clave-de-prueba" not in sent["url"]
    assert sent["headers"]["x-goog-api-key"] == "clave-de-prueba"
