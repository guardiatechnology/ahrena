# Kata: Instrumentar Observability em PoV

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Engenharia — Agents (estágio pré-operacional): instrumentação de telemetria nativa no PoV — traces, prompts log, tool calls log, métricas de valor

## Objetivo

Produzir `docs/{context}/agents-pov/{agent}/observability/` com 4 arquivos canônicos (`traces-spec.md`, `prompts-log.md`, `tool-calls-log.md`, `value-metrics.md`) declarando o **contrato** de observability do PoV: quais spans, quais campos de log, quais métricas leading. Observability é **cidadã de primeira classe** no PoV — sem instrumentação, não há base para Diretriz 06 (contexto rico para retrofit) nem para DoOC item 5 (observability data ≥ 7 dias). Aplica `lex-observability-required` no rigor pré-operacional: 1 trace + 1 métrica + structured log são suficientes.

## Quando Usar

- Após `kata-pov-tools-select` (tools são input para `tool-calls-log.md`)
- Em paralelo a `kata-pov-feedback-attach` (value-metrics conversam com critério de feedback)
- Quando uma operação do PoV revela métrica leading nova a rastrear

## Inputs

| Input | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| `docs/{context}/agents-pov/{agent}/pov.md` | Sim | Define value metric leading |
| `docs/{context}/agents-pov/{agent}/tools.md` | Sim | Lista de tools para os logs |
| `lex-observability-required` | Sim | Rigor mínimo (trace + métrica + log) |
| `lex-data-retention` | Sim | Restrições de PII em logs |

## Workflow

```
Progresso:
- [ ] 1. Definir spans (traces-spec.md)
- [ ] 2. Definir schema de prompts log (sem PII)
- [ ] 3. Definir schema de tool calls log
- [ ] 4. Definir métricas leading (value-metrics.md)
- [ ] 5. Cross-link com lex-observability-required (rigor mínimo)
- [ ] 6. Persistir observability/
```

### Passo 1: Definir spans (traces-spec.md)

Estrutura canônica (compatível com OpenTelemetry, **mesmo schema que Mêtis adotará** — facilita ponte):

```yaml
# traces-spec.md (extrato)

spans:
  - name: agent.turn
    attributes:
      - agent.name: <pov-name>
      - agent.stage: pre-operational
      - session_id: <opaque>
      - turn_index: <int>
      - input_tokens: <int>
      - output_tokens: <int>
      - latency_ms: <int>
      - outcome: success | error | refusal

  - name: agent.tool_call
    parent: agent.turn
    attributes:
      - tool.name: <web_search | code_execution | ...>
      - tool.duration_ms: <int>
      - tool.outcome: success | error | timeout
      - tool.error_class: <if outcome=error>
```

Cada PoV declara explicitamente quais spans emite. Mínimo: `agent.turn`. Recomendado quando há tools: `agent.turn` + `agent.tool_call`.

### Passo 2: Definir schema de prompts log (sem PII)

```yaml
# prompts-log.md (extrato)

fields:
  - session_id: opaque, hashed
  - turn_index: int
  - prompt_hash: sha256(user_input)   # NÃO armazena texto bruto
  - prompt_token_count: int
  - context_size_tokens: int
  - timestamp: ISO 8601

excluded:
  - user_input (texto bruto)
  - PII (CPF, CNPJ, email, nome completo)

retention:
  - 30 dias para PoV ativo
  - destruir ao encerrar PoV
```

O schema vive em `lex-data-retention` por default; se o PoV justifica retenção maior, registra em `value-proof.md` com motivo. Aplicar `lex-data-retention` é responsabilidade deste kata.

### Passo 3: Definir schema de tool calls log

```yaml
# tool-calls-log.md (extrato)

fields:
  - session_id: opaque, hashed
  - turn_index: int
  - tool_name: enum [web_search | code_execution | str_replace_editor | bash]
  - parameters_hash: sha256(parameters)   # NÃO armazena parâmetros brutos
  - parameters_size_bytes: int
  - duration_ms: int
  - outcome: success | error | timeout
  - error_class: string | null
  - result_size_bytes: int   # NÃO o conteúdo

excluded:
  - parameters brutos (especialmente se contêm dados do cliente)
  - result content

retention:
  - 30 dias para PoV ativo
```

### Passo 4: Definir métricas leading (value-metrics.md)

Métricas leading **operacionais** que o PoV deve rastrear continuamente:

```markdown
# value-metrics.md (extrato)

## Métrica primária

- nome: reconciliation_auto_rate
- definição: turns onde resposta gerou pareamento com confiança ≥ alta / total turns
- frequência: por sessão e agregada por dia
- janela: rolling 7 dias
- threshold de descontinuação: < 30% após 4 semanas

## Métricas de qualidade

- nome: refusal_rate
  - definição: turns com outcome=refusal / total turns
  - alarme: > 10% indica prompt mal calibrado
- nome: avg_latency_ms
  - definição: p95 latência por turn
  - alarme: > 5000ms indica tool com timeout
```

### Passo 5: Cross-link com lex-observability-required

No final de `traces-spec.md`, adiciona seção `## Conformidade com lex-observability-required`:

| Requisito | Como o PoV atende |
|---|---|
| 1 trace por unidade de trabalho | `agent.turn` span emitido por turn |
| 1 métrica leading | `reconciliation_auto_rate` (ver value-metrics.md) |
| Structured logging com PII redacted | prompt_hash + parameters_hash (nunca raw) |
| Janela ≥ 7 dias para DoOC | retention 30 dias declarada |

### Passo 6: Persistir observability/

Cria diretório `docs/{context}/agents-pov/{agent}/observability/` com:

- `traces-spec.md`
- `prompts-log.md`
- `tool-calls-log.md`
- `value-metrics.md`

Adiciona `README.md` curto listando os 4 arquivos e o propósito do diretório.

### Validação Final

- [ ] 4 arquivos presentes em `observability/`
- [ ] `agent.stage: pre-operational` aparece em `traces-spec.md`
- [ ] Logs declaram **hash** de prompt/parameters, nunca o texto bruto
- [ ] `value-metrics.md` tem 1 métrica primária com threshold de descontinuação
- [ ] Cross-link `lex-observability-required` presente

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| `observability/traces-spec.md` | Markdown + YAML | `docs/{context}/agents-pov/{agent}/observability/` |
| `observability/prompts-log.md` | Markdown + YAML | idem |
| `observability/tool-calls-log.md` | Markdown + YAML | idem |
| `observability/value-metrics.md` | Markdown | idem |
| `observability/README.md` | Markdown | idem |

## Restrições

- **Nunca** armazenar texto bruto de prompt ou de parâmetros de tool — sempre hash.
- **Nunca** ausência de métrica leading — sem métrica, `kata-pov-value-track` não pode operar.
- **Nunca** retention indefinida em PoV — limite máximo é 90 dias e mesmo isso requer justificativa.
- **Sempre** o schema é o mesmo que Mêtis (plan-032) consumirá via `--from-pov`. Divergência aqui quebra a ponte.

---

**Modelo:** Este Kata trata observability como cidadã de primeira classe em PoV. O contrato declarado aqui é a ponte para `kata-dooc-validate` item 5.
