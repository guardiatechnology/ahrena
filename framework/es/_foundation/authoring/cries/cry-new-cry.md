# Cry: Crear Nuevo Cry

> **Prefijo:** `cry-` | **Tipo:** Comando Recurrente | **Alcance:** Creación de Cries (comandos recurrentes)

## Descripción

Comando rápido para crear un nuevo Cry en Ahrena. Invoca `kata-create-cry`, que consulta `codex-cries` y el template oficial para producir un comando recurrente completo en los tres idiomas obligatorios. Este es el Cry que crea Cries — el atajo para el mecanismo de autorreplicación.

## Uso

```
/cry-new-cry <acción> [kata] [--clade clade/subclade]
```

## Parámetros

| Parámetro | Obligatorio | Descripción | Ejemplo |
|-----------|:-----------:|-------------|---------|
| `acción` | Sí | Lo que el nuevo comando hace | `"generar changelog"` |
| `kata` | No | Kata que el Cry invocará. Si se omite, el agente identifica o sugiere su creación | `kata-generate-changelog` |
| `--clade` | No | Clade/subclade en la taxonomía. Si se omite, el agente lo infiere de la acción | `--clade engineering/process` |

## Lo que el Comando Hace

1. Lee `.ahrena/.directives` para obtener idiomas y convenciones
2. Invoca `kata-create-cry` con los parámetros proporcionados; el Kata consulta `codex-cries` y el template oficial y produce el Cry (y verifica si el Kata asociado existe)
3. (El Kata) Crea el Cry en el idioma por defecto y traduce a los demás idiomas
4. Reporta los archivos creados

## Prompt Template

```
Contexto:
- Acción: {{acción}}
- Kata asociado: {{kata}} (o identificar/sugerir)
- Clade/Subclade: {{clade}} (o inferir de la acción)

Tarea:
Ejecute kata-create-cry. El Kata consulta .ahrena/.directives, codex-cries
y templates/cry-sample.md. Verifique si el Kata asociado existe. Cree el Cry
en el idioma por defecto y traduzca a todos los idiomas de language.i18n.

Formato de salida:
Lista de archivos creados con confirmación de que el Cry tiene sintaxis clara,
parámetros mínimos y prompt template referenciando el Kata.
```

## Ejemplo de Invocación

**Crear Cry con acción:**

```
/cry-new-cry "generar changelog"
```

**Output:**

```
Cry creado con éxito.

Comando: /cry-changelog
Acción: Generar changelog a partir de los commits
Kata asociado: kata-generate-changelog (sugerido — aún no existe)

Archivos creados:
1. framework/pt-BR/engineering/process/cries/cry-changelog.md ✓
2. framework/es/engineering/process/cries/cry-changelog.md ✓
3. framework/en/engineering/process/cries/cry-changelog.md ✓

Pendencia: kata-generate-changelog necesita ser creado.
Sugerencia: /cry-new-kata "generar changelog"
```

**Con Kata explícito:**

```
/cry-new-cry "traducir documento" kata-translate --clade documentation/i18n
```

## Restricciones

- Todo Cry debe referenciar un Kata — si el Kata no existe, señalar como pendencia
- Siempre ejecuta `kata-create-cry` (nunca crea directamente)
- Siempre crea en los tres idiomas obligatorios

## Diferencia con Kata

| Aspecto | Cry | Kata |
|---------|-----|------|
| **Naturaleza** | Invocación rápida (1 comando) | Procedimiento completo (6 pasos) |
| **Complejidad** | Baja (acción + kata) | Alta (diseño de comando, prompt, validación) |
| **¿Configura agente?** | No | Sí (define comportamiento) |
| **Ejemplo** | `/cry-new-cry "generar changelog"` | Workflow de 6 pasos con checklist |

## Referencias

- `kata-create-cry` — Procedimiento ejecutado por este Cry (el Kata consulta los criterios de calidad aplicables; ver documentación del Kata)
- `templates/cry-sample.md` — Template base
