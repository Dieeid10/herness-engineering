"""
Runner del harness multi-modelo.

Uso:
    python runner.py <proyecto> "<prompt del usuario>"

Ejemplo:
    python runner.py proyecto-a "Generá el CRUD de usuarios"
    python runner.py proyecto-b "Diseñá la arquitectura del modulo de pagos"

Requiere:
    pip install requests
    export ANTHROPIC_API_KEY=...   # solo si vas a usar el modelo 'claude'
    # para kimi-k2: tener vLLM corriendo local en localhost:8000
    #   ej: vllm serve moonshotai/Kimi-K2-Instruct --port 8000
"""

import json
import os
import sys
from pathlib import Path

import requests

HARNESS_ROOT = Path(__file__).parent


def load_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_text(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def build_session(project_name: str):
    project_dir = HARNESS_ROOT / "proyectos" / project_name
    if not project_dir.exists():
        raise FileNotFoundError(f"No existe el proyecto '{project_name}' en {project_dir}")

    project_config = load_json(project_dir / "config.json")
    model_name = project_config.get("model", "kimi-k2")

    model_dir = HARNESS_ROOT / "models" / model_name
    if not model_dir.exists():
        raise FileNotFoundError(f"No existe la carpeta de modelo '{model_name}' en {model_dir}")

    model_settings = load_json(model_dir / "settings.json")

    sdd_path = project_dir / "SDD.md"
    sdd = load_text(sdd_path) if sdd_path.exists() else ""

    tools = []
    tools_dir = model_dir / "tools"
    if tools_dir.exists():
        for f in sorted(tools_dir.glob("*.json")):
            tools.append(load_json(f))

    skills_prompt = ""
    skills_dir = model_dir / "skills"
    if skills_dir.exists():
        for f in sorted(skills_dir.glob("*.md")):
            skills_prompt += load_text(f) + "\n\n"

    shared_prompts_dir = HARNESS_ROOT / "shared" / "prompts"
    shared_prompt = ""
    if shared_prompts_dir.exists():
        for f in sorted(shared_prompts_dir.glob("*.md")):
            shared_prompt += load_text(f) + "\n\n"

    system_prompt = f"""Sos un agente de ingeniería de software trabajando en el proyecto '{project_name}'.

## Guías generales
{shared_prompt}
## Skills / capacidades del modelo
{skills_prompt}
## Contexto del proyecto (SDD)
{sdd}
""".strip()

    return {
        "project_name": project_name,
        "model_name": model_name,
        "model_settings": model_settings,
        "system_prompt": system_prompt,
        "tools": tools,
    }


def call_anthropic(session: dict, user_prompt: str) -> str:
    settings = session["model_settings"]
    api_key = os.environ.get(settings.get("api_key_env", "ANTHROPIC_API_KEY"))
    if not api_key:
        raise EnvironmentError(
            f"Falta la variable de entorno {settings.get('api_key_env')} con la API key de Anthropic."
        )

    url = f"{settings['base_url']}/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    payload = {
        "model": settings["model"],
        "max_tokens": settings.get("max_tokens", 4096),
        "temperature": settings.get("temperature", 0.2),
        "system": session["system_prompt"],
        "messages": [{"role": "user", "content": user_prompt}],
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=120)
    resp.raise_for_status()
    data = resp.json()
    return "".join(block.get("text", "") for block in data.get("content", []))


def call_vllm_local(session: dict, user_prompt: str) -> str:
    settings = session["model_settings"]
    url = f"{settings['base_url']}/chat/completions"
    headers = {"content-type": "application/json"}
    payload = {
        "model": settings["model"],
        "max_tokens": settings.get("max_tokens", 8000),
        "temperature": settings.get("temperature", 0.3),
        "messages": [
            {"role": "system", "content": session["system_prompt"]},
            {"role": "user", "content": user_prompt},
        ],
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=300)
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]


PROVIDER_DISPATCH = {
    "anthropic": call_anthropic,
    "vllm-local": call_vllm_local,
}


def run(project_name: str, user_prompt: str) -> str:
    session = build_session(project_name)
    provider = session["model_settings"]["provider"]
    handler = PROVIDER_DISPATCH.get(provider)
    if handler is None:
        raise ValueError(f"Provider desconocido: {provider}")

    print(f"[runner] proyecto={project_name} modelo={session['model_name']} provider={provider}", file=sys.stderr)
    return handler(session, user_prompt)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    project = sys.argv[1]
    prompt = sys.argv[2]

    try:
        output = run(project, prompt)
        print(output)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
