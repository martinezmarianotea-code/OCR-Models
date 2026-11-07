import pytest

from src.metrics import cer, noise_ratio, normalize, wer


def test_normalize_ignores_case_and_spacing():
    assert normalize("  Hola\n\tMUNDO  ") == "hola mundo"


def test_identical_text_has_no_error():
    assert cer("Paracetamol 500 mg", "Paracetamol 500 mg") == 0.0
    assert wer("Paracetamol 500 mg", "Paracetamol 500 mg") == 0.0


def test_cer_counts_character_edits():
    # una sustitución en 10 caracteres
    assert cer("amoxicilia", "amoxicilin") == pytest.approx(0.1)
    # un carácter faltante en 11
    assert cer("amoxicilin", "amoxicilina") == pytest.approx(1 / 11)


def test_wer_counts_word_edits():
    assert wer("tomar 1 cada 8", "tomar 1 cada 6 horas") == pytest.approx(0.4)


def test_empty_reference():
    assert cer("", "") == 0.0
    assert cer("algo", "") == 1.0


def test_noise_ratio():
    assert noise_ratio("Fecha: 14/03/2025") == 0.0
    assert noise_ratio("»|]£") == 1.0
    assert noise_ratio("") == 1.0
