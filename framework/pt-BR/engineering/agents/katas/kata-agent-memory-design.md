# Kata: Design das 3 Camadas de Memória

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Engenharia — Agents: design da memória do agent em `operational-concrete`, produzindo `memory.md` com 3 camadas obrigatórias

## Objetivo

Produzir o arquivo canônico de memória do agent, com **3 camadas obrigatórias** per `lex-agent-construction-directives::Diretriz 02 — Memória em Camadas`:

1. **Curta** — janela de contexto da sessão atual
2. **Média** — histórico do cliente (por `org_id`/`client_id`), TTL semanas a meses
3. **Longa** — conhecimento estável (regras de negócio, taxonomias, embeddings de catálogo) — TTL indefinido com retraining

Cada camada DEVE declarar schema, TTL, retenção (per `lex-data-retention`) e tratamento de PII. Cobre rigorosamente a **Diretriz 02**.

## Quando Usar

- Após `kata-agent-tools-design` (as tools são consumidoras de memória; ordem importa)
- Quando o agent precisa de revisão da arquitetura de memória (mudança de retenção, expansão de camada longa)

## Inputs

| Input | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| `context` | Sim | Bounded Context |
| `agent` | Sim | Slug do agent |
| `overview_path` | Sim | `docs/{context}/agents/{agent}/overview.md` (para tier + caso de uso) |
| `tools_path` | Sim | `docs/{context}/agents/{agent}/tools.md` |
| `--from-pov <path>` | Não | PoV path; em pré-operacional só havia camada curta — Mêtis expande para 3 |

## Workflow

```
Progresso:
- [ ] 1. Ler overview + tools
- [ ] 2. Declarar camada curta (sessão)
- [ ] 3. Declarar camada média (histórico do cliente)
- [ ] 4. Declarar camada longa (conhecimento estável)
- [ ] 5. Declarar política de retenção (per lex-data-retention)
- [ ] 6. Declarar tratamento de PII (redaction, anonimização, right-to-be-forgotten)
- [ ] 7. Validação final
```

### Passo 1: Ler overview + tools

1. Lê `overview.md` para extrair tier, caso de uso primário e `serves_features`
2. Lê `tools.md` para identificar quais tools consomem cada camada
3. Em `with-pov`, lê `pov-path/system-prompt.md` e quaisquer notas sobre memória — geralmente apenas camada curta (janela da sessão)

### Passo 2: Declarar camada curta

Camada curta = janela de contexto da sessão atual. Sempre presente. Schema típico:

```yaml
camada_curta:
  scope: "session"
  storage: "in-process (LLM context window)"
  ttl: "session lifetime"
  size_limit: "tokens (per modelo)"
  schema:
    - turn_history: lista de turnos (user, assistant, tool_call, tool_result)
    - working_memory: variáveis acumuladas no loop de raciocínio
  pii_handling: "PII de input do usuário permanece na janela durante a sessão; persiste só em forma redacted em camadas média/longa"
  retention: "encerrada ao final da sessão"
```

### Passo 3: Declarar camada média

Camada média = histórico do cliente, indexado por `org_id`/`client_id`. Retorna contexto entre sessões. Schema típico:

```yaml
camada_media:
  scope: "per-tenant (org_id + client_id)"
  storage: "Postgres ou DynamoDB (declarar)"
  ttl: "{30 a 180 dias, conforme política de retenção}"
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
  pii_handling: "PII redacted por default; fields sensíveis (CPF, email, telefone) substituídos por hash + last 4 dígitos quando audit-relevant"
  retention: "per docs/data-retention.yaml; default 90 dias após última atividade do cliente"
  right_to_be_forgotten: "DELETE por client_id em ≤ 15 dias do pedido (LGPD Art. 18)"
```

### Passo 4: Declarar camada longa

Camada longa = conhecimento estável compartilhado entre tenants. Não contém PII. Schema típico:

```yaml
camada_longa:
  scope: "shared (sem org_id/client_id)"
  storage: "S3 + index (Pinecone, OpenSearch ou pgvector — declarar)"
  ttl: "indefinida (com retraining)"
  size_limit: "{N} documentos / embeddings"
  schema:
    - doc_id: UUID v7
    - doc_type: enum (rule | taxonomy | example | embedding)
    - content: text ou vector
    - version: semver
    - created_at: timestamp
    - source: path/URL
  pii_handling: "ZERO PII — content é genérico (regras, taxonomias). Conteúdos derivados de cliente DEVEM ser anonimizados antes de entrar"
  retention: "indefinida; retraining/atualização registrada via versão"
  versioning: "semver; mudanças disruptivas exigem ADR + re-embedding"
```

### Passo 5: Declarar política de retenção (per `lex-data-retention`)

```yaml
retention_policy:
  reference: "docs/data-retention.yaml"
  classes:
    - name: "agent-{agent}-medium-memory"
      retention: "90 days after last activity"
      legal_basis: "LGPD Art. 16 — operacional, mínimo necessário"
      storage: "Postgres + S3 archive after 30d"
      enforcement: "cron job + retention column"
    - name: "agent-{agent}-long-memory"
      retention: "indefinite (with retraining)"
      pii: "none"
      storage: "S3 + vector index"
```

### Passo 6: Declarar tratamento de PII

Per `lex-data-retention` e `lex-frontend-security` (PII handling):

1. **Redaction at boundary:** PII detectada na entrada (regex CPF, email, etc.) é redacted antes de persistir em camadas média/longa
2. **Anonimização para camada longa:** quaisquer dados derivados de cliente entram apenas anonimizados; identificadores hashed
3. **Right to be forgotten:** API `DELETE /agents/{agent}/memory?client_id={id}` deleta camadas média/longa do cliente; camada curta encerra na sessão
4. **Audit log:** todas as operações de leitura/escrita de PII registradas em log estruturado (per `lex-observability-required`)

### Validação Final

- [ ] As 3 camadas declaradas (curta, média, longa) — nenhuma omitida
- [ ] Cada camada declara schema, TTL, retenção, PII handling
- [ ] Camada longa não contém PII
- [ ] Camada média referencia `lex-data-retention` e `docs/data-retention.yaml`
- [ ] Right to be forgotten implementado (caminho de DELETE declarado)
- [ ] Tools que consomem cada camada listadas (cross-link `tools.md`)

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| `memory.md` | Markdown | `docs/{context}/agents/{agent}/memory.md` |
| Atualização em `docs/data-retention.yaml` | YAML | adicionar classes do agent (quando ainda não existem) |

## Estrutura do arquivo `memory.md`

```markdown
# Memory — {agent}

> **Bounded Context:** {context}
> **Agent:** {agent}
> **3 camadas obrigatórias per `lex-agent-construction-directives::Diretriz 02`.**

## Camadas

### Curta

(YAML do Passo 2)

### Média

(YAML do Passo 3)

### Longa

(YAML do Passo 4)

## Right to be forgotten

- **API endpoint:** {path}
- **SLA:** ≤ 15 dias do pedido (LGPD Art. 18)
- **Camadas afetadas:** média + longa (anonimização retroativa quando aplicável)
- **Audit log:** registrado em {observability backend}

## Referências

- `lex-agent-construction-directives::Diretriz 02`
- `lex-data-retention`
- `docs/data-retention.yaml`
- `tools.md` — quais tools consomem cada camada
- `metrics.md` — métricas operacionais da camada (cache hit, query latency)
```

## Restrições

- Camada curta sempre presente (não é decisão)
- Camada longa pode estar vazia em agent simples — declarar `não usada` é aceito; OMITIR a seção é proibido
- PII na camada longa é proibido per LGPD/GDPR
- Retenção indefinida em camadas com PII é proibida
- Compartilhar memória entre tenants (`org_id` cross) é proibido em camadas média/curta

---

**Modelo:** Kata produz o catálogo de 3 camadas. Toda camada declarada com schema, TTL, PII handling. Right to be forgotten implementado. Cross-link rigoroso com `lex-data-retention`.
