# Harness multi-modelo (Claude + Kimi K2 + Ollama)

## Estructura

```
harness/
├── models/
│   ├── claude/
│   │   ├── settings.json   # config API Anthropic
│   │   ├── tools/          # tools tipo MCP
│   │   └── skills/         # prompts/skills reutilizables
│   ├── kimi-k2/
│   │   ├── settings.json   # config endpoint vLLM local
│   │   ├── tools/          # definiciones de tools
│   │   └── skills/
│   └── ollama/
│       └── settings.json   # config API local de Ollama
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

4. Para usar Ollama, instalarlo, descargar el modelo configurado y asegurarse
   de que el servicio esté activo en `http://localhost:11434`:

```bash
ollama pull phi3:mini
```

En `proyectos/<proyecto>/config.json`, establecer `"model": "ollama"` para
usar el perfil definido en `models/ollama/settings.json`. El perfil actual usa
`phi3:mini`; para usar otro modelo, primero descárgalo con `ollama pull <modelo>`
y cambia el campo `model` de ese archivo.

5. Correr el runner apuntando a un proyecto:

```bash
python runner.py proyecto-a "Generá el CRUD de usuarios"
python runner.py proyecto-b "Diseñá la arquitectura del modulo de pagos"
```

El runner:
- lee `proyectos/<proyecto>/config.json` para saber qué modelo usar,
- carga `models/<modelo>/settings.json`, las definiciones de `tools/` y las
  instrucciones de `skills/`,
- arma el system prompt combinando guías generales + skills + el SDD del proyecto,
- llama al provider correspondiente (`anthropic`, `vllm-local` u `ollama`).

El runner devuelve texto generado por el modelo. Actualmente no escribe
archivos ni envía/ejecuta las tools declaradas; para probar el código, guarda
manualmente la respuesta y ejecútala o ábrela con la herramienta correspondiente.

## Probar Ollama con un proyecto pequeño

El proyecto `proyecto-test` ya selecciona Ollama. Con el servicio activo y el
modelo descargado, ejecuta desde la raíz del repositorio:

```bash
.venv/bin/python runner.py proyecto-test "Crea una mini app de lista de tareas en un único archivo index.html, con HTML, CSS y JavaScript integrados. Debe permitir agregar tareas, marcarlas como completadas y eliminarlas. Guarda las tareas en localStorage. Devuelve únicamente el contenido completo del archivo, sin explicaciones ni bloques Markdown."
```

Guarda la respuesta como `index.html`, ábrela en un navegador y verifica que
puedas agregar, completar y eliminar tareas, y que sigan guardadas al recargar.
Si usas otro entorno Python, reemplaza `.venv/bin/python` por su intérprete.

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
