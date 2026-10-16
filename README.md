# Harness multi-modelo (Claude + Kimi K2 local)

## Estructura

```
harness/
├── models/
│   ├── claude/
│   │   ├── settings.json   # config API Anthropic
│   │   ├── tools/          # tools tipo MCP
│   │   └── skills/         # prompts/skills reutilizables
│   └── kimi-k2/
│       ├── settings.json   # config endpoint vLLM local
│       ├── tools/          # tools function-calling
│       └── skills/
├── proyectos/
│   ├── proyecto-a/
│   │   ├── SDD.md          # Software Design Document
│   │   └── config.json     # que modelo usa este proyecto
│   └── proyecto-b/
│       ├── SDD.md
│       └── config.json
├── shared/
│   ├── tools/               # tools comunes
│   └── prompts/             # guias generales para todos los modelos
├── runner.py                 # orquestador: arma contexto y llama al modelo
└── README.md
```

## Uso

1. Instalar dependencias:

```bash
pip install requests
```

2. Para usar Claude, exportar la API key:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

3. Para usar Kimi K2 local, levantar el servidor vLLM (requiere GPU con VRAM
   suficiente; para modelos grandes como Kimi K2 full, considerar una
   variante cuantizada AWQ/GGUF si no tenés hardware de gama alta):

```bash
vllm serve moonshotai/Kimi-K2-Instruct --port 8000
```

4. Correr el runner apuntando a un proyecto:

```bash
python runner.py proyecto-a "Generá el CRUD de usuarios"
python runner.py proyecto-b "Diseñá la arquitectura del modulo de pagos"
```

El runner:
- lee `proyectos/<proyecto>/config.json` para saber qué modelo usar,
- carga `models/<modelo>/settings.json`, `tools/` y `skills/`,
- arma el system prompt combinando guías generales + skills + el SDD del proyecto,
- llama al provider correspondiente (`anthropic` o `vllm-local`).

## Agregar un proyecto nuevo

```bash
mkdir -p proyectos/mi-proyecto
cp proyectos/proyecto-a/SDD.md proyectos/mi-proyecto/SDD.md   # y completar
cat > proyectos/mi-proyecto/config.json << 'EOF'
{
  "model": "kimi-k2",
  "notes": "..."
}
EOF
```

## Agregar una tool o skill a un modelo

- Tools: agregar un `.json` en `models/<modelo>/tools/`.
- Skills: agregar un `.md` en `models/<modelo>/skills/`.

Ambos se cargan automáticamente al correr el runner.
