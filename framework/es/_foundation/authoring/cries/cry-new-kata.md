# Cry: Crear Nuevo Kata

> **Prefijo:** `cry-` | **Tipo:** Comando Recurrente | **Alcance:** Creación de Katas (procedimientos repetibles)

## Descripción

Comando rápido para crear un nuevo Kata en Ahrena. Invoca `kata-create-kata`, que consulta `codex-katas` y el template oficial para producir un procedimiento estandarizado completo en los tres idiomas obligatorios.

## Uso

```
/cry-new-kata <tarea> [contexto] [--clade clade/subclade]
```

## Parámetros

| Parámetro | Obligatorio | Descripción | Ejemplo |
|-----------|:-----------:|-------------|---------|
| `tarea` | Sí | Tarea a estandarizar en procedimiento | `"crear ADR"` |
| `contexto` | No | Información adicional sobre el dominio o restricciones | `"proyectos con microservicios"` |
| `--clade` | No | Clade/subclade en la taxonomía. Si se omite, el agente lo infiere de la tarea | `--clade engineering/architecture` |

## Lo que el Comando Hace

1. Lee `.ahrena/.directives` para obtener idiomas y convenciones
2. Consulta `codex-katas` para criterios de calidad
3. Lee `templates/kata-sample.md` como base estructural
4. Ejecuta `kata-create-kata` con los parámetros proporcionados
5. Crea el Kata en el idioma por defecto y traduce a los demás idiomas
6. Reporta los archivos creados

## Prompt Template

```
Contexto:
- Tarea: {{tarea}}
- Contexto adicional: {{contexto}} (o ninguno)
- Clade/Subclade: {{clade}} (o inferir de la tarea)

Tarea:
Ejecute kata-create-kata. Consulte .ahrena/.directives para obtener los
idiomas obligatorios. Consulte codex-katas para criterios de calidad.
Use templates/kata-sample.md como base. Cree el Kata en el idioma por
defecto y traduzca a todos los idiomas de language.i18n.

Formato de salida:
Lista de archivos creados con confirmación de que el Kata tiene inputs definidos,
pasos atómicos y validación final.
```

## Ejemplo de Invocación

**Crear Kata con tarea:**

```
/cry-new-kata "crear ADR"
```

**Output:**

```
Kata creado con éxito.

Tarea: Crear ADR (Architecture Decision Record)
Pasos: 6 pasos definidos
Inputs: 3 (decisión, contexto, alternativas)

Archivos creados:
1. framework/pt-BR/engineering/architecture/katas/kata-create-adr.md ✓
2. framework/es/engineering/architecture/katas/kata-create-adr.md ✓
3. framework/en/engineering/architecture/katas/kata-create-adr.md ✓
```

## Restricciones

- Si la tarea tiene menos de 4 pasos, sugiere crear un Cry en lugar de Kata
- Siempre ejecuta `kata-create-kata` (nunca crea directamente)
- Siempre crea en los tres idiomas obligatorios

## Diferencia con Kata

| Aspecto | Cry | Kata |
|---------|-----|------|
| **Naturaleza** | Invocación rápida (1 comando) | Procedimiento completo (6 pasos) |
| **Complejidad** | Baja (tarea + contexto) | Alta (descomposición, redacción, validación) |
| **¿Configura agente?** | No | Sí (define comportamiento) |
| **Ejemplo** | `/cry-new-kata "crear ADR"` | Workflow de 6 pasos con checklist |

## Referencias

- `kata-create-kata` — Procedimiento ejecutado por este Cry
- `codex-katas` — Criterios de calidad consultados
- `templates/kata-sample.md` — Template base
