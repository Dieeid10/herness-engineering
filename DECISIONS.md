# Decisiones de diseño del harness

## 2026-09-19: Separación por modelo en vez de por herramienta
Decidimos organizar `models/` por modelo (claude, kimi-k2) llamando
directo a sus APIs/endpoints, en vez de por herramienta (Claude Code,
Cursor). Razón: control total del system prompt y costo cero para
tareas rutinarias vía Kimi K2 local.
