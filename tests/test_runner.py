"""Tests básicos del runner. Correr con: pytest tests/"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from runner import build_session


def test_build_session_proyecto_a_usa_kimi():
    session = build_session("proyecto-a")
    assert session["model_name"] == "kimi-k2"
    assert session["model_settings"]["provider"] == "vllm-local"


def test_build_session_proyecto_b_usa_claude():
    session = build_session("proyecto-b")
    assert session["model_name"] == "claude"
    assert session["model_settings"]["provider"] == "anthropic"


def test_system_prompt_incluye_sdd():
    session = build_session("proyecto-a")
    assert "Proyecto A" in session["system_prompt"]


def test_proyecto_inexistente_lanza_error():
    try:
        build_session("no-existe")
        assert False, "Debería haber lanzado FileNotFoundError"
    except FileNotFoundError:
        pass
