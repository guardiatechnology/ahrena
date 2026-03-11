# Cry: Crear Nuevo Codex

> **Prefijo:** `cry-` | **Tipo:** Comando Recurrente | **Alcance:** Creación de Codex (manuales de referencia)

## Descripción

Comando rápido para crear un nuevo Codex en Ahrena. Invoca `kata-create-codex`, que consulta `codex-codex` y el template oficial para producir un manual de referencia completo en los tres idiomas obligatorios.

## Uso

```
/cry-new-codex <dominio> [público] [--clade clade/subclade]
```

## Parámetros

| Parámetro | Obligatorio | Descripción | Ejemplo |
|-----------|:-----------:|-------------|---------|
| `dominio` | Sí | Área de conocimiento a documentar | `"arquitectura del sistema"` |
| `público` | No | Quién consultará el Codex. Si se omite, se asume "agentes de IA y desarrolladores" | `"backend team"` |
| `--clade` | No | Clade/subclade en la taxonomía. Si se omite, el agente lo infiere del dominio | `--clade engineering/architecture` |

## Lo que el Comando Hace

1. Lee `.ahrena/.directives` para obtener idiomas y convenciones
2. Invoca `kata-create-codex` con los parámetros proporcionados; el Kata consulta `codex-codex` y el template oficial y produce el Codex
3. (El Kata) Crea el Codex en el idioma por defecto y traduce a los demás idiomas
4. Reporta los archivos creados

## Prompt Template

```
Contexto:
- Dominio: {{dominio}}
- Público objetivo: {{público}} (o "agentes de IA y desarrolladores")
- Clade/Subclade: {{clade}} (o inferir del dominio)

Tarea:
Ejecute kata-create-codex. El Kata consulta .ahrena/.directives, codex-codex
y templates/codex-sample.md. Cree el Codex en el idioma por
defecto y traduzca a todos los idiomas de language.i18n.

Formato de salida:
Lista de archivos creados con confirmación de que el Codex tiene alcance
delimitado, principios accionables y disparador de actualización.
```

## Ejemplo de Invocación

**Crear Codex con dominio:**

```
/cry-new-codex "patrones de API REST"
```

**Output:**

```
Codex creado con éxito.

Dominio: Patrones de API REST
Principios: 4 principios definidos
Disparador de actualización: a cada nueva versión de la API

Archivos creados:
1. framework/pt-BR/engineering/backend/codex/codex-api-patterns.md ✓
2. framework/es/engineering/backend/codex/codex-api-patterns.md ✓
3. framework/en/engineering/backend/codex/codex-api-patterns.md ✓
```

## Restricciones

- No crea Codex enciclopédicos — sugiere dividir si el alcance es muy amplio
- Siempre ejecuta `kata-create-codex` (nunca crea directamente)
- Siempre crea en los tres idiomas obligatorios

## Diferencia con Kata

| Aspecto | Cry | Kata |
|---------|-----|------|
| **Naturaleza** | Invocación rápida (1 comando) | Procedimiento completo (6 pasos) |
| **Complejidad** | Baja (dominio + público) | Alta (estructuración, redacción, validación) |
| **¿Configura agente?** | No | Sí (define comportamiento) |
| **Ejemplo** | `/cry-new-codex "patrones de API"` | Workflow de 6 pasos con checklist |

## Referencias

- `kata-create-codex` — Procedimiento ejecutado por este Cry (el Kata consulta los criterios de calidad aplicables; ver documentación del Kata)
- `templates/codex-sample.md` — Template base
