# Kata: Curar Context Pack de PoV

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Ingeniería — Agents (etapa pre-operacional): curación de few-shot + ejemplos negativos del dominio para alimentar el contexto del PoV

## Objetivo

Producir `docs/{context}/agents-pov/{agent}/context-pack.md` con 3-5 few-shot examples reales y 2-3 ejemplos negativos curados (anti-patrones observados en LLM básico del dominio). Aplica la Directriz 06 de `lex-agent-construction-directives` (Contexto Rico) en la óptica de PoV. El context-pack es el **activo que alimenta `--from-pov`** cuando el agent madura: Mêtis usa esos ejemplos como punto de partida para el context-pack de producción.

## Cuándo Usar

- Después de `kata-pov-scope-define` (overview listo)
- Después de `kata-pov-system-prompt` (para alinear tono y formato de ejemplo)
- Cuando una ronda de operación del PoV revela nuevos anti-patrones a curar

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| `docs/{context}/agents-pov/{agent}/pov.md` | Sí | Caso de uso primario |
| `docs/{context}/agents-pov/{agent}/system-prompt.md` | Sí | Formato de salida esperado |
| Domain knowledge | Sí | Conocimiento del dominio del cliente (entrevistas, docs, samples) |
| `--inputs-dir <path>` | No | Directorio con datos reales anonimizados para inspirar ejemplos |

## Workflow

```
Progreso:
- [ ] 1. Leer overview + system-prompt
- [ ] 2. Recopilar 3-5 inputs reales representativos
- [ ] 3. Escribir few-shot positivos (input → respuesta ideal)
- [ ] 4. Identificar 2-3 anti-patrones y escribir ejemplos negativos
- [ ] 5. Anonimizar PII (lex-data-retention)
- [ ] 6. Persistir context-pack.md
```

### Paso 1: Leer overview + system-prompt

1. Se leen los dos archivos.
2. Se anota: caso de uso primario, formato esperado de salida, restricciones del prompt.

### Paso 2: Recopilar 3-5 inputs reales representativos

1. Se cubre el **espacio del caso de uso**: caso fácil, caso medio, caso ambiguo. No 5 versiones del mismo escenario.
2. Si `--inputs-dir` fue pasado, se lista y selecciona; si no, se piden al usuario 3-5 inputs reales. **Sin inputs reales, el kata aborta** — context-pack inventado es violación directa de la Directriz 06.

### Paso 3: Escribir few-shot positivos

Para cada input seleccionado:

- **Bloque Input:** datos literales (anonimizados)
- **Respuesta ideal:** lo que el agent **debería** producir, en el formato declarado en `system-prompt.md`

Los ejemplos siguen el template `<input> → <output>` consistente con el estilo de salida del prompt. Evite el over-engineering: la respuesta ideal es la que el cliente aceptaría, no un ideal perfeccionista.

### Paso 4: Identificar 2-3 anti-patrones y escribir ejemplos negativos

Anti-patrones típicos en LLM básico para el dominio:

- **Alucinación:** inventa ID/valor ausente del input
- **Over-confidence:** dice "alta confianza" cuando los datos son insuficientes
- **Out-of-scope drift:** responde sobre caso de uso secundario no declarado
- **Format breakage:** quiebra el formato declarado en el prompt

Para cada anti-patrón, se escribe:

- **Bloque Input:** el caso que disparó el error
- **❌ Respuesta no deseada:** lo que LLM básico produjo
- **✅ Respuesta correcta:** lo que debería haber producido (misma estructura de los few-shot positivos)

### Paso 5: Anonimizar PII

Se aplica `lex-data-retention`:

- Se remueve o enmascara: CPF/CNPJ, e-mail, teléfono, nombre completo, dirección
- Se mantiene: estructura del input (campos, patrones), valores cuantitativos (con ofuscación ligera si son sensibles)
- Se marca cada ejemplo con `# Origen: anonimizado de datos del cliente en <fecha>` para trazabilidad

### Paso 6: Persistir context-pack.md

Se graba `docs/{context}/agents-pov/{agent}/context-pack.md` con secciones: Few-shot positivos (3-5), Anti-patrones (2-3), Notas de anonimización, Criterios de calidad aplicados.

### Validación Final

- [ ] 3 a 5 few-shot positivos cubriendo casos representativos
- [ ] 2 a 3 anti-patrones con `❌` y `✅`
- [ ] Cero PII (CPF, CNPJ, nombre completo, e-mail)
- [ ] Ejemplos derivados de inputs reales (no ficticios)
- [ ] Formato de salida de los few-shot es consistente con `system-prompt.md`

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| `context-pack.md` | Markdown | `docs/{context}/agents-pov/{agent}/context-pack.md` |

## Ejemplo de Ejecución

### Output (context-pack.md, extracto)

```markdown
## Few-shot positivos

### Ejemplo 1 (caso fácil)

**Input:**
- Extracto: TX-001 | 2026-04-01 | $ 1.200,00 | "Alquiler ref 04/26"
- Asientos:
  - L-100 | 2026-04-01 | $ 1.200,00 | "PAG ALQUILER ABR/26"
  - L-101 | 2026-04-02 | $ 350,00 | "INTERNET"

**Respuesta ideal:**
TX-001 ↔ L-100 | confianza: alta | base: valor + fecha + descripción similar

### Ejemplo 2 (caso medio — descripción divergente)
...

## Anti-patrones

### Anti-patrón A: Alucinación de ID

**Input:**
- Extracto: TX-007 | 2026-04-15 | $ 500,00 | "PIX 12345"
- Asientos: (vacío para esa ventana)

**❌ Respuesta no deseada:**
TX-007 ↔ L-999 | confianza: alta
(L-999 no existe en los asientos — alucinación.)

**✅ Respuesta correcta:**
TX-007 ↔ ningún candidato | confianza: n/a | observación: revisión manual necesaria.
```

## Restricciones

- **Nunca** context-pack con ejemplos inventados — la Directriz 06 exige datos reales.
- **Nunca** PII en el archivo final — `lex-data-retention` aplica.
- **Nunca** menos de 3 ni más de 5 few-shot positivos. La franja codifica el trade-off entre cobertura y ruido.
- **Siempre** marcar el origen del ejemplo (anonymization date stamp) para rastrear retrofit.

---

**Modelo:** Este Kata aplica la Directriz 06 (`lex-agent-construction-directives`). El context-pack es el activo más transferible para Mêtis vía `--from-pov`.
