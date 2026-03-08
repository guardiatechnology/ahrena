# Cry: Crear Nueva Lexis

> **Prefijo:** `cry-` | **Tipo:** Comando Recurrente | **Alcance:** Creación de Lexis (leyes inquebrantables)

## Descripción

Comando rápido para crear una nueva Lexis en Ahrena. Invoca `kata-create-lexis`, que consulta `codex-lexis` y el template oficial para producir una ley completa en los tres idiomas obligatorios.

## Uso

```
/cry-new-lex <asunto> [alcance] [--clade clade/subclade]
```

## Parámetros

| Parámetro | Obligatorio | Descripción | Ejemplo |
|-----------|:-----------:|-------------|---------|
| `asunto` | Sí | Tema de la ley a crear | `"code review obligatorio"` |
| `alcance` | No | Dónde se aplica la ley. Si se omite, el agente lo infiere del asunto | `"todos los repositorios"` |
| `--clade` | No | Clade/subclade en la taxonomía. Si se omite, el agente lo infiere del asunto | `--clade engineering/quality` |

## Lo que el Comando Hace

1. Lee `.ahrena/.directives` para obtener idiomas y convenciones
2. Consulta `codex-lexis` para criterios de calidad
3. Lee `templates/lex-sample.md` como base estructural
4. Ejecuta `kata-create-lexis` con los parámetros proporcionados
5. Crea la Lexis en el idioma por defecto y traduce a los demás idiomas
6. Reporta los archivos creados

## Prompt Template

```
Contexto:
- Asunto: {{asunto}}
- Alcance: {{alcance}} (o inferir del asunto)
- Clade/Subclade: {{clade}} (o inferir del asunto)

Tarea:
Ejecute kata-create-lexis. Consulte .ahrena/.directives para obtener los
idiomas obligatorios. Consulte codex-lexis para criterios de calidad.
Use templates/lex-sample.md como base. Cree la Lexis en el idioma por
defecto y traduzca a todos los idiomas de language.i18n.

Formato de salida:
Lista de archivos creados con confirmación de que la ley es clara, unívoca
y verificable.
```

## Ejemplo de Invocación

**Crear Lexis con asunto:**

```
/cry-new-lex "code review obligatorio"
```

**Output:**

```
Lexis creada con éxito.

Ley: "Todo PR DEBE tener al menos un revisor aprobado antes del merge."

Archivos creados:
1. framework/pt-BR/engineering/quality/lexis/lex-code-review.md ✓
2. framework/es/engineering/quality/lexis/lex-code-review.md ✓
3. framework/en/engineering/quality/lexis/lex-code-review.md ✓

Validación:
- Univocidad: ✓ (una interpretación posible)
- Verificabilidad: ✓ (verificable vía API de GitHub)
- Excepciones: Ninguna ✓
```

**Con alcance y clade explícitos:**

```
/cry-new-lex "no secrets en repositorio" "todos los repositorios" --clade engineering/security
```

## Restricciones

- No crea Lexis que admitan excepciones — si necesita excepciones, sugiere crear un Codex
- Siempre ejecuta `kata-create-lexis` (nunca crea directamente)
- Siempre crea en los tres idiomas obligatorios

## Diferencia con Kata

| Aspecto | Cry | Kata |
|---------|-----|------|
| **Naturaleza** | Invocación rápida (1 comando) | Procedimiento completo (6 pasos) |
| **Complejidad** | Baja (asunto + alcance) | Alta (concepción, redacción, validación) |
| **¿Configura agente?** | No | Sí (define comportamiento) |
| **Ejemplo** | `/cry-new-lex "code review"` | Workflow de 6 pasos con checklist |

## Referencias

- `kata-create-lexis` — Procedimiento ejecutado por este Cry
- `codex-lexis` — Criterios de calidad consultados
- `templates/lex-sample.md` — Template base
