# Kata: Design do Catálogo Tripartido de Ferramentas

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Engenharia — Agents: design do catálogo de ferramentas (`tools.md`) do agent em `operational-concrete`

## Objetivo

Produzir o catálogo canônico de ferramentas do agent, dividido em **três categorias** per `lex-agent-construction-directives::Diretriz 03 — Ferramentas Concretas`:

1. **Deterministic** — funções determinísticas (busca por chave, validações, parsing controlado)
2. **ML** — modelos treinados ou inferência específica (classificação, embeddings, OCR)
3. **MCP** — ferramentas expostas via servidor MCP (per `lex-mcp` e `codex-mcp-common`)

O catálogo declara contrato (input, output, idempotência, latência típica, lateral effects) de cada ferramenta. Cobre rigorosamente a **Diretriz 03**.

## Quando Usar

- Após `kata-agent-orchestrator-design` e (quando aplicável) `kata-agent-specialists-design`
- Quando o agent precisa de revisão do catálogo (nova ferramenta adicionada, ferramenta deprecada via ADR)

## Inputs

| Input | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| `context` | Sim | Bounded Context |
| `agent` | Sim | Slug do agent |
| `orchestrator_path` | Sim | `docs/{context}/agents/{agent}/orchestrator.md` |
| `specialists_paths` | Não | Lista de `docs/{context}/agents/{agent}/specialists/{name}.md` |
| `--from-pov <path>` | Não | PoV path; herda subset de tools experimentadas e desambigua catálogo de produção |

## Workflow

```
Progresso:
- [ ] 1. Extrair tools mencionadas em orchestrator + specialists
- [ ] 2. Classificar cada tool (deterministic | ML | MCP)
- [ ] 3. Declarar contrato de cada tool (I/O, idempotência, lateral effects)
- [ ] 4. Verificar idempotência onde escrita está envolvida
- [ ] 5. Validação de input em fronteira
- [ ] 6. Validação final
```

### Passo 1: Extrair tools mencionadas

Lê `orchestrator.md::Workflow (com tools e dependências)` e cada `specialists/{name}.md::Tools consumidas`. Consolida lista única.

### Passo 2: Classificar cada tool

| Sinal | Categoria |
|-------|-----------|
| Função pura sem chamada externa, output 100% determinístico para input fixo | **Deterministic** |
| Inferência via modelo (classificador, embeddings, regressor, OCR, ASR) | **ML** |
| Chamada via servidor MCP listado em `mcp.servers` no `.ahrena/.directives` | **MCP** |
| Chamada HTTP externa sem MCP | **MCP** (DEVE ser exposta via MCP per `lex-mcp` quando possível) ou justificativa em ADR |

Cada tool aparece em **exatamente uma** categoria. Duplicar é proibido.

### Passo 3: Declarar contrato de cada tool

Template canônico para `tools.md`:

```markdown
# Tools — {agent}

> **Bounded Context:** {context}
> **Agent:** {agent}
> **Source of truth:** este arquivo. Tools usadas em runtime DEVEM constar deste catálogo; tools fora do catálogo são bloqueadas por guardrail (cross-link `guardrails.md::Tool injection`).

## Deterministic

### `{tool-name}`

- **Descrição:** {1-2 frases}
- **Quando usar:** {gatilho concreto}
- **Input schema:** {JSON schema ou referência a Pydantic model}
- **Output schema:** {JSON schema}
- **Idempotência:** sim (função pura)
- **Lateral effects:** nenhum
- **Latência típica:** < {N}ms
- **Erros possíveis:** {códigos per lex-error-handling}

(repetir para cada deterministic tool)

## ML

### `{tool-name}`

- **Descrição:** {modelo + versão + dataset de treino}
- **Quando usar:** {gatilho}
- **Input schema:** {}
- **Output schema:** {com confidence score}
- **Idempotência:** parcial (mesmo modelo + mesma versão → output determinístico modulo random seed)
- **Lateral effects:** uso de inferência paga (custo declarado em ADR de modelo)
- **Latência típica:** ~ {N}ms p99
- **Threshold de confidence:** {valor} (abaixo → escalonar via `escalation.md`)
- **Versão do modelo:** {tag/SHA}
- **Retrain trigger:** {quando o modelo é retreinado}

(repetir para cada ML tool)

## MCP

### `{tool-name}`

- **Servidor MCP:** `{server-name}` (declarado em `mcp.servers` no `.ahrena/.directives`)
- **Descrição:** {1-2 frases}
- **Quando usar:** {gatilho}
- **Input schema:** {}
- **Output schema:** {}
- **Idempotência:** sim/não — quando "não", DEVE receber `Idempotency-Key` no input per `lex-idempotency`
- **Lateral effects:** {escrita em sistema externo: ERP, banco, e-mail, S3}
- **Latência típica:** ~ {N}ms p99
- **Retry policy:** {exponential backoff, max retries, circuit breaker}
- **Erros possíveis:** {códigos per lex-error-handling}
- **Auth:** credenciais via variável de ambiente per `lex-mcp` (nunca em código)

(repetir para cada MCP tool)

## Idempotência

Tools que produzem efeito lateral (categoria MCP, em sua maioria) DEVEM ser idempotentes per `lex-idempotency`. Implementação:

- Endpoint recebe `Idempotency-Key` no header ou input
- Servidor MCP deduplica por chave + hash do payload
- Retry com mesma chave + mesmo payload retorna mesmo resultado (não duplica efeito)

Tools que falham este requisito DEVEM ser deprecadas e substituídas.

## Validação de input em fronteira

Toda tool DEVE validar o input antes de executar:

- Schema validation via Pydantic ou Zod
- Type checking estrito
- Bounds checking (e.g., `amount > 0` per invariante do aggregate)
- `org_id`/`client_id` checking — tool nunca cruza fronteira de tenant

Cross-link `guardrails.md::Tool injection` para controles OWASP.

## Referências

- `lex-agent-construction-directives::Diretriz 03`
- `lex-mcp`, `codex-mcp-common`
- `lex-idempotency`
- `lex-error-handling`, `codex-known-errors`
- `guardrails.md` — controles OWASP aplicados às tools
- `orchestrator.md`, `specialists/` — quem invoca o quê
```

### Passo 4: Verificar idempotência onde escrita está envolvida

Para cada tool em `MCP` com `lateral effects ≠ nenhum`:

1. Confirma que aceita `Idempotency-Key`
2. Confirma que o servidor MCP deduplica
3. Confirma que retry policy não duplica efeito

Quando falha, registra tool como `pending idempotency review` no PR de promoção; bloqueia merge até resolver.

### Passo 5: Validação de input em fronteira

Para cada tool:

- Existe schema (Pydantic, Zod ou equivalente)
- Schema valida `org_id`/`client_id` quando aplicável
- Erros de validação retornam `ERR400_INVALID_PARAMETER` per `lex-error-handling`

### Validação Final

- [ ] Toda tool aparece em exatamente uma categoria
- [ ] Tools com lateral effects têm idempotência verificada
- [ ] Tools ML declaram versão do modelo + threshold de confidence
- [ ] Tools MCP referenciam servidor declarado em `mcp.servers`
- [ ] Schemas declarados (input + output) — não placeholders
- [ ] Cross-references com `guardrails.md` para OWASP applied controls

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| `tools.md` | Markdown | `docs/{context}/agents/{agent}/tools.md` |

## Restrições

- Toda tool DEVE estar em uma das 3 categorias; quarta categoria proibida sem ADR
- Tools com lateral effects sem idempotência são proibidas em `operational-concrete`
- Tool exposta diretamente sem servidor MCP é proibida quando MCP é viável (per `lex-mcp`); justificativa exige ADR
- Não duplicar tools entre categorias

---

**Modelo:** Kata produz catálogo tripartido (deterministic | ML | MCP) com contratos claros. Toda tool em runtime DEVE constar deste arquivo; guardrails bloqueiam tools fora do catálogo.
