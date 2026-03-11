# Cry: Realizar Commit

> **Prefijo:** `cry-` | **Tipo:** Comando Recurrente | **Alcance:** Atajo para crear commits estandarizados

## Invocación

```
/cry-commit [tipo] [alcance] [descripción]
```

## Parámetros

| Parámetro | Obligatorio | Descripción | Ejemplo |
|-----------|:-----------:|-------------|---------|
| `tipo` | No | Tipo Conventional Commits | `feat`, `fix`, `docs` |
| `alcance` | No | Módulo o dominio | `auth`, `api`, `payments` |
| `descripción` | No | Texto del subject en inglés | `"implement OAuth2"` |

Si se omiten los parámetros, el agente analiza `git diff --staged` y sugiere automáticamente.

## Ejemplos de Uso

```
# Commit con todos los parámetros
/cry-commit feat auth "implement OAuth2 authentication"

# Commit con tipo y descripción (sin alcance)
/cry-commit fix "resolve null pointer in transaction"

# Commit automático — el agente analiza el diff y sugiere
/cry-commit
```

## Comportamiento

1. Invoca `kata-commit` pasando los parámetros proporcionados
2. Si se omiten los parámetros, el agente:
   - Ejecuta `git diff --staged`
   - Infiere tipo, alcance y descripción
   - Presenta la sugerencia para confirmación
3. Valida contra las 4 Lexis de commit
4. Ejecuta el commit firmado

## Kata Asociado

`kata-commit` — Procedimiento completo de creación de commit

## Referencias

- `kata-commit` — Procedimiento ejecutado por este Cry (el Kata consulta las Lexis y el Codex de commits; ver documentación del Kata)
