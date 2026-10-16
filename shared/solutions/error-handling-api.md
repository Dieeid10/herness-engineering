# Patrón: manejo de errores en endpoints FastAPI

Cuando generes o revises un endpoint:
- Usar HTTPException con status_code explícito, nunca un 500 genérico sin loguear.
- Validar input con Pydantic antes de tocar la lógica de negocio.
- Loguear el error completo server-side, devolver mensaje genérico al cliente.
