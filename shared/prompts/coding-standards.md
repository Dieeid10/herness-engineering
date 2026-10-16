# Estándares de código (aplican a cualquier proyecto y modelo)

## Seguridad
- Nunca pasar API keys, tokens o secretos por query params ni en URLs. Usar headers o variables de entorno.
- Nunca loguear datos sensibles (passwords, tokens, PII) en texto plano.
- Validar y sanitizar todo input externo antes de usarlo en queries, comandos de shell o templates.

## Tipado
- Tipar siempre parámetros de funciones y su valor de retorno (type hints en Python, tipos explícitos en TS/PHP donde aplique).
- Evitar `Any` / `mixed` salvo que sea estrictamente necesario y esté justificado con un comentario.

## Funciones
- Toda función debe tener un propósito único y claro (single responsibility).
- Si una función puede fallar, documentar qué excepción lanza o qué devuelve en caso de error (no fallar silenciosamente).
- Preferir funciones puras cuando sea posible; si hay side effects, dejarlo explícito en el nombre o el docstring.

## Errores
- No capturar excepciones genéricas (`except Exception`) sin re-lanzar o loguear con contexto.
- Los mensajes de error deben ser accionables, no solo "algo salió mal".

## Testing
- Toda función con lógica de negocio no trivial debe tener al menos un test.
- Los tests no dependen de estado externo (red, DB real) salvo que estén marcados explícitamente como de integración.

## Nombres
- Nombres descriptivos, sin abreviaturas ambiguas.
- Consistencia con el resto del proyecto (si ya existe un patrón, seguirlo salvo que se decida migrar explícitamente).
