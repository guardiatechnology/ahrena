# Kata: Design de las 3 Capas de Memoria

> **Prefijo:** `kata-` | **Tipo:** Skill Repetible | **Alcance:** Ingeniería — Agents: design de la memoria del agent en `operational-concrete`, produciendo `memory.md` con 3 capas obligatorias

## Objetivo

Producir el archivo canónico de memoria del agent, con **3 capas obligatorias** per `lex-agent-construction-directives::Directriz 02 — Memoria en Capas`:

1. **Corta** — ventana de contexto de la sesión actual
2. **Media** — histórico del cliente (por `org_id`/`client_id`), TTL semanas a meses
3. **Larga** — conocimiento estable (reglas de negocio, taxonomías, embeddings de catálogo) — TTL indefinido con retraining

Cada capa DEBE declarar schema, TTL, retención (per `lex-data-retention`) y tratamiento de PII. Cubre rigurosamente la **Directriz 02**.

## Cuándo Usar

- Tras `kata-agent-tools-design` (las tools son consumidoras de memoria; orden importa)
- Cuando el agent necesita revisión de la arquitectura de memoria (cambio de retención, expansión de capa larga)

## Inputs

| Input | Obligatorio | Descripción |
|-------|:-----------:|-------------|
| `context` | Sí | Bounded Context |
| `agent` | Sí | Slug del agent |
| `overview_path` | Sí | `docs/{context}/agents/{agent}/overview.md` (para tier + caso de uso) |
| `tools_path` | Sí | `docs/{context}/agents/{agent}/tools.md` |
| `--from-pov <path>` | No | PoV path; en pre-operacional solo había capa corta — Mêtis expande para 3 |

## Workflow

```
Progreso:
- [ ] 1. Leer overview + tools
- [ ] 2. Declarar capa corta (sesión)
- [ ] 3. Declarar capa media (histórico del cliente)
- [ ] 4. Declarar capa larga (conocimiento estable)
- [ ] 5. Declarar política de retención (per lex-data-retention)
- [ ] 6. Declarar tratamiento de PII (redaction, anonimización, right-to-be-forgotten)
- [ ] 7. Validación final
```

### Paso 1: Leer overview + tools

1. Lee `overview.md` para extraer tier, caso de uso primario y `serves_features`
2. Lee `tools.md` para identificar cuáles tools consumen cada capa
3. En `with-pov`, lee `pov-path/system-prompt.md` y cualquier nota sobre memoria — generalmente solo capa corta (ventana de la sesión)

### Paso 2: Declarar capa corta

Capa corta = ventana de contexto de la sesión actual. Siempre presente. Schema típico:

```yaml
capa_corta:
  scope: "session"
  storage: "in-process (LLM context window)"
  ttl: "session lifetime"
  size_limit: "tokens (per modelo)"
  schema:
    - turn_history: lista de turnos (user, assistant, tool_call, tool_result)
    - working_memory: variables acumuladas en el loop de razonamiento
  pii_handling: "PII de input del usuario permanece en la ventana durante la sesión; persiste solo en forma redacted en capas media/larga"
  retention: "cerrada al final de la sesión"
```

### Paso 3: Declarar capa media

Capa media = histórico del cliente, indexado por `org_id`/`client_id`. Retorna contexto entre sesiones. Schema típico:

```yaml
capa_media:
  scope: "per-tenant (org_id + client_id)"
  storage: "Postgres o DynamoDB (declarar)"
  ttl: "{30 a 180 días, conforme política de retención}"
  size_limit: "{N} eventos por cliente"
  schema:
    - event_id: UUID v7
    - org_id: UUID
    - client_id: UUID
    - agent_id: slug
    - event_type: enum
    - payload: JSON
    - created_at: timestamp
    - pii_redacted: boolean
  pii_handling: "PII redacted por default; fields sensibles (CPF, email, teléfono) sustituidos por hash + last 4 dígitos cuando audit-relevant"
  retention: "per docs/data-retention.yaml; default 90 días tras última actividad del cliente"
  right_to_be_forgotten: "DELETE por client_id en ≤ 15 días del pedido (LGPD Art. 18)"
```

### Paso 4: Declarar capa larga

Capa larga = conocimiento estable compartido entre tenants. No contiene PII. Schema típico:

```yaml
capa_larga:
  scope: "shared (sin org_id/client_id)"
  storage: "S3 + index (Pinecone, OpenSearch o pgvector — declarar)"
  ttl: "indefinida (con retraining)"
  size_limit: "{N} documentos / embeddings"
  schema:
    - doc_id: UUID v7
    - doc_type: enum (rule | taxonomy | example | embedding)
    - content: text o vector
    - version: semver
    - created_at: timestamp
    - source: path/URL
  pii_handling: "CERO PII — content es genérico (reglas, taxonomías). Contenidos derivados de cliente DEBEN ser anonimizados antes de entrar"
  retention: "indefinida; retraining/actualización registrada vía versión"
  versioning: "semver; cambios disruptivos exigen ADR + re-embedding"
```

### Paso 5: Declarar política de retención (per `lex-data-retention`)

```yaml
retention_policy:
  reference: "docs/data-retention.yaml"
  classes:
    - name: "agent-{agent}-medium-memory"
      retention: "90 days after last activity"
      legal_basis: "LGPD Art. 16 — operacional, mínimo necesario"
      storage: "Postgres + S3 archive after 30d"
      enforcement: "cron job + retention column"
    - name: "agent-{agent}-long-memory"
      retention: "indefinite (with retraining)"
      pii: "none"
      storage: "S3 + vector index"
```

### Paso 6: Declarar tratamiento de PII

Per `lex-data-retention` y `lex-frontend-security` (PII handling):

1. **Redaction at boundary:** PII detectada en la entrada (regex CPF, email, etc.) es redacted antes de persistir en capas media/larga
2. **Anonimización para capa larga:** cualquier dato derivado de cliente entra solo anonimizado; identificadores hashed
3. **Right to be forgotten:** API `DELETE /agents/{agent}/memory?client_id={id}` elimina capas media/larga del cliente; capa corta se cierra en la sesión
4. **Audit log:** todas las operaciones de lectura/escritura de PII registradas en log estructurado (per `lex-observability-required`)

### Validación Final

- [ ] Las 3 capas declaradas (corta, media, larga) — ninguna omitida
- [ ] Cada capa declara schema, TTL, retención, PII handling
- [ ] Capa larga no contiene PII
- [ ] Capa media referencia `lex-data-retention` y `docs/data-retention.yaml`
- [ ] Right to be forgotten implementado (camino de DELETE declarado)
- [ ] Tools que consumen cada capa listadas (cross-link `tools.md`)

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| `memory.md` | Markdown | `docs/{context}/agents/{agent}/memory.md` |
| Actualización en `docs/data-retention.yaml` | YAML | añadir clases del agent (cuando aún no existen) |

## Estructura del archivo `memory.md`

```markdown
# Memory — {agent}

> **Bounded Context:** {context}
> **Agent:** {agent}
> **3 capas obligatorias per `lex-agent-construction-directives::Directriz 02`.**

## Capas

### Corta

(YAML del Paso 2)

### Media

(YAML del Paso 3)

### Larga

(YAML del Paso 4)

## Right to be forgotten

- **API endpoint:** {path}
- **SLA:** ≤ 15 días del pedido (LGPD Art. 18)
- **Capas afectadas:** media + larga (anonimización retroactiva cuando aplicable)
- **Audit log:** registrado en {observability backend}

## Referencias

- `lex-agent-construction-directives::Directriz 02`
- `lex-data-retention`
- `docs/data-retention.yaml`
- `tools.md` — cuáles tools consumen cada capa
- `metrics.md` — métricas operacionales de la capa (cache hit, query latency)
```

## Restricciones

- Capa corta siempre presente (no es decisión)
- Capa larga puede estar vacía en agent simple — declarar `no usada` es aceptado; OMITIR la sección está prohibido
- PII en la capa larga está prohibido per LGPD/GDPR
- Retención indefinida en capas con PII está prohibida
- Compartir memoria entre tenants (`org_id` cross) está prohibido en capas media/corta

---

**Modelo:** Kata produce el catálogo de 3 capas. Toda capa declarada con schema, TTL, PII handling. Right to be forgotten implementado. Cross-link riguroso con `lex-data-retention`.
