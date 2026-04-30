# Lexis: Desarrollo Issue-First

> **Prefijo:** `lex-` | **Tipo:** Ley Inquebrantable | **Alcance:** Todos los cambios de código en repositorios Guardia

## Ley

> **Todo cambio de código — funcionalidad, corrección de bug, refactorización, actualización de dependencia o cambio de configuración — DEBE originarse en un Issue de GitHub existente. Antes de abrir un Issue nuevo, el contribuyente DEBE verificar si ya existe un Issue (abierto o recién cerrado) que cubra el tópico; el primer Issue coincidente es dueño del trabajo, e Issues paralelos para el mismo alcance están PROHIBIDOS. No se PUEDE crear ninguna rama ni abrir ningún PR sin un Issue asociado. El cuerpo del PR DEBE referenciar el Issue con `Closes #N` (lo resuelve completamente) o `Refs #N` (lo aborda parcialmente). Los PRs sin referencia a un Issue están PROHIBIDOS. La única excepción es para correcciones triviales (errores tipográficos, puntuación o formato sin ningún cambio de lógica), que PUEDEN enviarse sin un Issue previo usando el tipo `docs:` o `style:` de Conventional Commits.**

## Cobertura

- **Se aplica a:** todas las contribuciones de código en todos los repositorios Guardia.
- **Agentes vinculados:** desarrolladores, agentes de IA (warrior-athena, warrior-apollo, warrior-hephaestus).
- **Excepciones:** correcciones triviales (solo tipo `docs:` o `style:`, sin cambio de lógica). Todas las demás excepciones requieren justificación explícita registrada en el Issue.

## Reglas

### 1. Issue antes de la rama

Antes de crear una rama:

1. **Busque Issues existentes** (abiertos y recién cerrados) que ya cubran el trabajo planificado — por título, label, alcance o discusión relacionada. Use `gh issue list --search "<términos>"` o la búsqueda de la UI de GitHub. El primer Issue compatible es dueño del trabajo.
2. **Si ya existe un Issue** para el tópico: úselo como anchor — referencie mediante `Closes #N` (resolución total) o `Refs #N` (resolución parcial). No abra un Issue paralelo cubriendo el mismo alcance. Casos válidos para un Issue nuevo aun con tópico relacionado: (a) el trabajo actual es genuinamente independiente del Issue existente, (b) el alcance evolucionó y justifica un desdoblamiento documentado en los comentarios del Issue original.
3. **Si no existe Issue**: abra uno usando `kata-contributing-issue` con: **qué** (descripción clara del objetivo), **por qué** (motivación e impacto), **resultado esperado** (criterios de aceptación o definición de listo).
4. Solo entonces cree la rama siguiendo `lex-git-branches`: `{type}/{issue-number}-{slug}`.

### 2. Calidad del Issue

Un Issue DEBE contener como mínimo:

- Un título claro que resume el objetivo.
- Un cuerpo que describe el problema u objetivo, contexto y resultado esperado.
- Un tipo asignado mediante la plantilla en `.ahrena/contributing_templates/` (`feature-request`, `epic`, `user-story-for-api` o `user-story-for-frontend`).

### 3. El PR referencia el Issue

Todo cuerpo de PR DEBE incluir uno de los siguientes:

- `Closes #N` — el PR resuelve completamente el Issue (GitHub lo cierra automáticamente al hacer merge).
- `Refs #N` — el PR aborda parcialmente el Issue (el Issue permanece abierto).

Los PRs sin referencia a un Issue son rechazados durante la revisión.

### 4. Excepción: correcciones triviales

Los cambios limitados exclusivamente a errores tipográficos, puntuación o formato (sin cambio de comportamiento o lógica) PUEDEN enviarse directamente como PR sin un Issue previo. Estos DEBEN usar el tipo `docs:` o `style:` de Conventional Commits.

## Ejemplos

### Correctos

```
# Issue #42 existe: "Añadir autenticación OAuth2"
Rama: feat/42-oauth2-authentication
Cuerpo del PR incluye: "Closes #42"
```

```
# Issue #123 existe: "Null pointer en el procesamiento de transacciones"
Rama: fix/123-null-pointer-in-transaction
Cuerpo del PR incluye: "Closes #123"
```

```
# Corrección trivial — sin Issue necesario
Commit: docs: fix typo in CONTRIBUTING guide
```

### Incorrectos

```
# ❌ Rama creada sin un Issue
Rama: feat/new-payment-dashboard
# No existe Issue correspondiente

# ❌ Cuerpo del PR sin referencia al Issue
Cuerpo del PR: "Este PR añade la nueva funcionalidad de pago."
# Sin "Closes #N" o "Refs #N"

# ❌ Cambio no trivial enviado sin un Issue
Commit: refactor: restructure entire auth module
# La refactorización no es una corrección trivial
```

## Validación Automatizada

- **Herramienta:** plantilla de PR con campo obligatorio `Closes #` o `Refs #`; verificación de GitHub Actions en el cuerpo del PR para referencia al Issue.
- **Cuándo:** al crear y actualizar el PR.
- **Métrica:** 0 PRs fusionados (excluyendo excepciones triviales) sin un Issue asociado.
