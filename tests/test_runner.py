"""Tests básicos del runner. Correr con: pytest tests/"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
import runner
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


def test_call_ollama_usa_api_chat(monkeypatch):
    captured = {}

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"message": {"content": "respuesta local"}}

    def fake_post(url, json, timeout):
        captured["url"] = url
        captured["payload"] = json
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr(runner.requests, "post", fake_post)
    session = {
        "model_settings": {
            "base_url": "http://localhost:11434/api",
            "model": "qwen2.5-coder:7b",
            "temperature": 0.3,
            "max_tokens": 2048,
        },
        "system_prompt": "instrucciones del sistema",
    }

    result = runner.call_ollama(session, "hola")

    assert result == "respuesta local"
    assert captured["url"] == "http://localhost:11434/api/chat"
    assert captured["payload"]["model"] == "qwen2.5-coder:7b"
    assert captured["payload"]["stream"] is False
    assert captured["payload"]["options"]["num_predict"] == 2048
    assert captured["payload"]["messages"] == [
        {"role": "system", "content": "instrucciones del sistema"},
        {"role": "user", "content": "hola"},
    ]
