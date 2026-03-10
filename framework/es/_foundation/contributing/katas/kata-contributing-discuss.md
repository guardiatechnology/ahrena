# Kata: Abrir discusión en GitHub Discussions

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Creación de discusión en el repositorio origin (Golden Circle; MCP de GitHub cuando esté disponible)

## Objetivo

Este Kata define el procedimiento estandarizado para abrir una discusión en GitHub Discussions del repositorio origin, siguiendo el **Golden Circle** (QUÉ, POR QUÉ, CÓMO). No hay plantilla .md — el contenido se estructura en esos tres ejes. La creación de la discusión **DEBE priorizar el MCP de GitHub** cuando esté disponible; respaldo con apertura manual o `gh` CLI.

## Cuándo Usar

- Cuando el usuario quiere proponer una idea o cambio significativo antes de abrir issue/PR
- Cuando se invoca por cry-new-discuss o por cry-contribute con acción discuss
- Según codex-contributing: discusión primero, luego issue/PR

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| QUÉ (What) | Sí | Qué se propone: idea, feature o cambio en una frase clara |
| POR QUÉ (Why) | Sí | Por qué importa: impacto, problema que resuelve, valor |
| CÓMO (How) | No | Cómo podría hacerse: enfoque sugerido, opciones técnicas o de proceso |

## Workflow

```
Progreso:
- [ ] 1. Recoger QUÉ, POR QUÉ, CÓMO (con el usuario)
- [ ] 2. Redactar el cuerpo de la discusión (Golden Circle)
- [ ] 3. Crear discusión vía MCP de GitHub (o indicar pasos manuales)
- [ ] 4. Verificación final
```

### Paso 1: Recoger QUÉ, POR QUÉ, CÓMO

1. Preguntar o inferir del contexto: **QUÉ** (resumen objetivo), **POR QUÉ** (motivación y beneficio), **CÓMO** (opcional — sugerencia de implementación o flujo).
2. Si el usuario ya aporta texto, estructurarlo en los tres ejes.

### Paso 2: Redactar el cuerpo de la discusión

1. Montar el body en Markdown con secciones claras: **QUÉ**, **POR QUÉ**, **CÓMO** (si aplica).
2. Incluir categoría sugerida: en general "Ideas" (según codex-contributing).
3. Título de la discusión: frase que resuma el QUÉ.

### Paso 3: Crear discusión vía MCP de GitHub

1. **Preferencia:** usar MCP de GitHub si el servidor expone creación de discusión (p. ej. herramienta de discussions). Indicar servidor y parámetros (owner, repo, category, title, body).
2. **Respaldo:** si el MCP no está disponible o no hay herramienta para discussions: presentar al usuario el título y el body listos; indicar que abra manualmente en: GitHub del repositorio → Discussions → New discussion (categoría Ideas); o usar `gh` CLI si hay soporte.

### Paso 4: Verificación final

- [ ] La discusión se creó (o el contenido se entregó para apertura manual)
- [ ] El texto sigue el Golden Circle (QUÉ, POR QUÉ, CÓMO)
- [ ] Se presentaron al usuario el enlace de la discusión o las instrucciones

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Discusión | GitHub Discussion | Repositorio origin (categoría Ideas) |
| URL de la discusión o instrucciones | Enlace / texto | Presentado al usuario |

## Restricciones

- No hay plantilla .md en el framework para discusión; el contenido es libre dentro del Golden Circle.
- Estructurar siempre la propuesta en QUÉ, POR QUÉ y (cuando aplique) CÓMO.
- Si no es posible crear vía MCP, no inventar comando `gh` para discussions — indicar apertura manual y proporcionar título + body listos.

## Referencias

- `codex-contributing` — Flujo de contribución Guardia (discusión primero; categoría Ideas)
- Golden Circle — QUÉ, POR QUÉ, CÓMO
- MCP de GitHub (cuando esté disponible para creación de discusión)
- cry-new-discuss, cry-contribute — Atajos que invocan este Kata
