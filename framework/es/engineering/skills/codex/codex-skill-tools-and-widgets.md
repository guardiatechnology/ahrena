# Codex: Convención Ahrena — `tools/` (MCP) y `widgets/` (React)

> **Prefijo:** `codex-` | **Tipo:** Manual de Referencia | **Alcance:** Extensión Ahrena al formato Anthropic Agent Skills — convención para empaquetar tools MCP (lógica) y widgets React (UI) dentro de un proyecto de skill, y cómo los widgets se vinculan a scripts y tools

## Visión General

La spec Anthropic Agent Skills (per `codex-skill-anthropic-agent-skills`) **no define** layout para tools MCP ni para widgets de UI. Este Codex establece la **convención Ahrena** que cubre esa brecha: cómo organizar `tools/` y `widgets/` dentro de `skills/{slug}/`, cuál es el schema del manifest de cada uno, y cómo los widgets declaran binding con scripts y tools.

Los agentes externos que conocen solo la spec **ignoran** esos directorios — siguen consumiendo `SKILL.md`, `references/`, `scripts/`, `assets/` normalmente. La convención es aditiva: skills sin `tools/`/`widgets/` permanecen 100% spec-compliant. Skills con esos directorios entregan capacidades adicionales a hosts que reconocen la convención (Claude Code con integración Ahrena, Guardia agentic surface).

## Contexto

- **Dominio:** estructura interna de `tools/` y `widgets/` dentro de proyectos de skill, y el contrato de binding entre ellos
- **Público objetivo:** autores de skill que requieren UI o lógica MCP propia
- **Actualización:** cuando el schema de los manifests evolucione; cuando la spec Anthropic absorba primitivas equivalentes (en cuyo caso, este codex documenta la transición)

## Estado — Convención, no Spec

> **Atención:** `tools/` y `widgets/` **no** forman parte de la spec Anthropic Agent Skills. Esta es una convención del framework Ahrena. El `SKILL.md` generado en proyectos con esos directorios **debe** incluir un encabezado de aviso explícito para que los consumidores externos sepan qué esperar.

## Contenido

### `tools/` — MCP tools propias del skill

Las tools MCP empaquetadas con el skill exponen capacidades de dominio que el agente externo invoca durante la ejecución. No reemplazan MCP servers globales (GitHub, Notion, Figma) — atienden necesidades específicas del skill.

#### Layout

```
tools/
├── mcp.config.json # registro de las tools
└── handlers/ # implementaciones
 ├── validate_amount.py
 └── ...
```

Lenguajes de los handlers: Python (default — alineado a `codex-python-architecture`) o JavaScript/TypeScript (Node). Se permite mezcla.

#### `mcp.config.json` — schema

```json
{
 "schema_version": 1,
 "mcp": {
 "name": "{slug}-tools",
 "description": "MCP tools bundled with this skill (Ahrena convention).",
 "tools": [
 {
 "name": "validate_amount",
 "description": "Validate that a transfer amount is within the allowed range and currency.",
 "input_schema": {
 "type": "object",
 "properties": {
 "amount": { "type": "integer", "minimum": 1 },
 "currency": { "type": "string", "pattern": "^[A-Z]{3}$" }
 },
 "required": ["amount", "currency"]
 },
 "handler": "handlers/validate_amount.py:run"
 }
 ]
 }
}
```

| Campo | Descripción |
|-------|-------------|
| `schema_version` | Entero; reservado para evolución del schema (actual: `1`) |
| `mcp.name` | `{slug}-tools` por convención; identificador local del server |
| `mcp.description` | Frase única que describe el propósito del conjunto |
| `mcp.tools[].name` | snake_case; identificador de la tool dentro del server |
| `mcp.tools[].description` | Texto que el agente lee para decidir cuándo invocar |
| `mcp.tools[].input_schema` | JSON Schema Draft 7+ |
| `mcp.tools[].handler` | `<path-relativo>:<funcion>` — el build resuelve a un runnable |

#### Convenciones para handlers

- Python: el handler es `def run(input: dict) -> dict | Result[T, E]`. Aplicar `lex-python-typing`, `lex-python-error-handling`, `lex-python-result-type` (cuando el uso de Result sea natural), `lex-python-security`, `lex-mcp`.
- JS/TS: el handler es `export async function run(input): Promise<unknown>`. Aplicar `lex-frontend-typing` (cuando TS), tratamiento idiomático de error.
- El logging en cualquier lenguaje sigue `lex-logging-decorator`.

### `widgets/` — Componentes React

Los widgets son componentes React (TypeScript) renderizados por el agente host en la superficie de chat. La arquitectura hereda **íntegramente** `codex-frontend-architecture`: capas (Pages → Features → Components → Hooks → Services → State), state management apropiado por alcance, props tipadas, server state vía TanStack Query / SWR cuando hay fetch real.

#### Layout

```
widgets/
├── package.json # React 18 + TS strict + Vite
├── tsconfig.json # strict: true, noUncheckedIndexedAccess: true
├── manifest.json # registro de los componentes expuestos
└── src/
 ├── components/ # primitivos reutilizables
 ├── features/ # bloques por feature
 └── transfer-form/ # ejemplo de componente de feature
 └── index.tsx
```

#### `manifest.json` — schema

```json
{
 "schema_version": 1,
 "components": [
 {
 "name": "TransferForm",
 "entry": "src/transfer-form/index.tsx",
 "props_schema": {
 "type": "object",
 "properties": {
 "default_amount": { "type": "integer" },
 "currency": { "type": "string" }
 }
 },
 "events": [
 {
 "name": "submit",
 "payload_schema": {
 "type": "object",
 "properties": {
 "amount": { "type": "integer" },
 "currency": { "type": "string" }
 },
 "required": ["amount", "currency"]
 }
 }
 ],
 "bindings": [
 {
 "kind": "tool",
 "ref": "validate_amount"
 },
 {
 "kind": "script",
 "ref": "scripts/src/format_currency.py",
 "called_via": "http://localhost:5174/format-currency"
 }
 ]
 }
 ]
}
```

| Campo | Descripción |
|-------|-------------|
| `schema_version` | Entero; reservado (actual: `1`) |
| `components[].name` | PascalCase; identificador expuesto al host |
| `components[].entry` | Path relativo del componente que el build empaqueta |
| `components[].props_schema` | JSON Schema de las props aceptadas |
| `components[].events[]` | Eventos que el componente emite, con payload tipado |
| `components[].bindings[]` | Dependencias externas (tools MCP o scripts) — ver abajo |

### Binding widget ↔ script ↔ tool

Los widgets declaran explícitamente las dependencias externas en `bindings[]`. El host resuelve en runtime conforme al entorno:

| `kind` | Cuándo usar | Resolución en dev (localhost) | Resolución en prod (host agente) |
|--------|-------------|-------------------------------|----------------------------------|
| `tool` | Lógica MCP del skill (`tools/`) o de otro server MCP activo | Tool stub local en `localhost:5175` | El host invoca la tool MCP directamente |
| `script` | Utilitario en `scripts/` invocado por HTTP/JSON | `fetch(called_via)` al script runner en `localhost:5174` | El host ejecuta script bundleado y expone endpoint efímero, o rutea vía tool MCP |

**Principio:** el widget **no importa** scripts directamente. Toda dependencia cruza una frontera tipada (HTTP/JSON o MCP) — esto mantiene al widget renderizable en aislamiento (preview en Storybook, smoke en Playwright) sin requerir el runtime del skill completo.

`called_via` en bindings `kind: script`:

- En **dev**, apunta al script runner local (`http://localhost:{scripts_port}/...`)
- En **prod**, es reescrito por el build: se convierte en un path relativo que el host resuelve vía tool MCP equivalente, o un endpoint efímero. El stack de build del proyecto consumidor es responsable de esa reescritura conforme `skill.config.json`.

### Reuso de codex y Lexis

| Contenido | Codex de arquitectura | Lexis aplicables |
|-----------|----------------------|------------------|
| `widgets/` React+TS | `codex-frontend-architecture` | `lex-frontend-typing`, `lex-frontend-accessibility`, `lex-frontend-security`, `lex-frontend-testing`, `lex-design-system-library` (en superficie Guardia), `lex-tone` (microcopy) |
| `tools/handlers/` Python | `codex-mcp-common`, `codex-python-architecture`, `codex-python-tooling` | `lex-mcp`, `lex-python-typing`, `lex-python-testing`, `lex-python-security`, `lex-python-error-handling`, `lex-python-result-type`, `lex-logging-decorator` |
| `tools/handlers/` JS/TS | `codex-mcp-common` | `lex-mcp`, `lex-frontend-typing` (cuando TS), `lex-logging-decorator` |
| Manifest y schemas | (de este codex) | `lex-skill-project-structure` |

### Compatibilidad con la spec

| Aspecto | Spec Anthropic | Convención Ahrena |
|---------|----------------|-------------------|
| `SKILL.md`, frontmatter, body | Definidos | Sin cambios |
| `references/`, `scripts/`, `assets/` | Definidos | Sin cambios — Ahrena no modifica esos directorios |
| `tools/`, `widgets/` | **No cubiertos** | Añadidos — los agentes spec-only los ignoran |
| `.skill-manifest.json` | No cubierto | Manifest raíz Ahrena (auditoría, hashes — ver `lex-skill-project-structure`) |

Cuando la spec evolucione y cubra tools/widgets, este codex documenta la transición (mapeo, deprecaciones). Las skills que adoptaron la convención siguen funcionando mientras los agentes Ahrena reconozcan el layout — la migración a la forma canónica de la spec será incremental.

## Restricciones

- El autor **no infiere** binding — toda dependencia externa se declara en `manifest.json` (widgets) o `mcp.config.json` (tools)
- El widget **no importa** script directamente; siempre cruza frontera HTTP/MCP
- `bindings[].kind: script` se resuelve con `called_via` en dev y se reescribe por el build para prod — no usar URL hardcoded de producción
- Los manifests deben ser validados por el build del proyecto consumidor antes del empaquetado; el fallo de schema aborta con error específico

## Glosario

| Término | Definición |
|---------|------------|
| Binding | Declaración explícita, en el `manifest.json` del widget, de dependencia a una tool MCP o a un script |
| Manifest raíz | `.skill-manifest.json` en la raíz del proyecto — distinto de los manifests de `tools/` y `widgets/` |

## Referencias

- `codex-skill-anthropic-agent-skills` — spec externa
- `codex-skill-project-architecture` — layout del proyecto y rol de los directorios
- `codex-frontend-architecture` — arquitectura aplicada a los widgets
- `codex-python-architecture`, `codex-python-tooling` — arquitectura aplicada a handlers Python
- `codex-mcp-common` — patrones compartidos de servidores MCP
- `lex-skill-project-structure` — ley del layout
- `lex-frontend-*`, `lex-python-*`, `lex-mcp`, `lex-logging-decorator` — calidad aplicable
