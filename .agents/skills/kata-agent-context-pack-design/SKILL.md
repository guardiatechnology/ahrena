---
name: kata-agent-context-pack-design
description: "Design do Context Pack (com Ponte `--from-pov`). Engenharia — Agents: design do context pack (context-pack.md) do agent em operational-concrete, incluindo a ponte canônica que consome saída do warrior-claudionor (PoV → Operação Concreta)"
---

# Kata: Design do Context Pack (com Ponte `--from-pov`)

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Engenharia — Agents: design do context pack (`context-pack.md`) do agent em `operational-concrete`, incluindo a ponte canônica que consome saída do `warrior-claudionor` (PoV → Operação Concreta)

## Contrato de input `--from-pov`

Quando o flag `--from-pov` é fornecido, o Kata espera os seguintes arquivos no path indicado (todos produzidos por katas POV de `warrior-claudionor`):

| Arquivo | Produzido por | Conteúdo consumido |
|---------|---------------|---------------------|
| `pov.md` | `kata-pov-scope-define` | Caso de uso primário (para confirmar alinhamento) |
| `scope.md` | `kata-pov-scope-define` | Fora de escopo (para validar negativos) |
| `system-prompt.md` | `kata-pov-system-prompt` | Identidade pré-operacional (referência) |
| `tools.md` | `kata-pov-tools-select` | Tools experimentadas no PoV |
| `context-pack.md` | `kata-pov-context-curate` | **Few-shot positivos + anti-padrões — fonte primária do enrichment** |
| `feedback.md` | `kata-pov-feedback-attach` | Métrica de valor + pivot trigger |
| `value-proof.md` | `kata-pov-value-track` | Leading metric provada, decisão `ready_for_dooc` (token canônico machine-readable, language-invariant) |
| `observability/value-metrics.md` | `kata-pov-observability-instrument` | Métricas operacionais observadas |
| `observability/prompts-log.md` | `kata-pov-observability-instrument` | Edge cases identificados em produção (referências, sem PII) |
| `observability/tool-calls-log.md` | `kata-pov-observability-instrument` | Padrões de uso de tools |
| `observability/traces-spec.md` | `kata-pov-observability-instrument` | Snippets de traces típicos |
| `implementation/skill.md` ou `subagent.md` | `kata-skill-implement` ou `kata-agent-author` | Referência da implementação executada no PoV |

**Pressuposto de PII redaction:** o Kata confia que `kata-pov-value-track::Passo 4` aplicou o gate de PII grep antes de marcar `ready_for_dooc` (registrado em `value-proof.md`). Não revalida PII no input; documenta na seção `Validação de input em fronteira` o trust boundary.

Se o PoV ainda **não está** `ready_for_dooc` em `value-proof.md`, o Kata aborta com erro claro — context pack baseado em PoV imaturo viola o espírito da DoOC.

## Workflow

```
Progresso:
- [ ] 1. Validar input --from-pov (quando aplicável)
- [ ] 2. Curar ≥ 5 few-shot positivos
- [ ] 3. Curar ≥ 10 exemplos negativos
- [ ] 4. Selecionar snippets de telemetria (30-90 dias)
- [ ] 5. Declarar política de re-curadoria
- [ ] 6. Validação final
```

### Passo 1: Validar input `--from-pov` (quando aplicável)

1. Se `--from-pov` fornecido:
   - Verifica que `pov_path/value-proof.md::status == ready_for_dooc`. Falha se diferente
   - Verifica que `pov_path/context-pack.md` existe (é a fonte primária)
   - Verifica que `pov_path/observability/` contém os 4 arquivos esperados
2. Se `--from-pov` ausente:
   - Em `entry_mode: direct-entry`, registra modo `cold-start`: few-shot precisarão ser sintetizados a partir do domínio (sem inputs reais); marca obrigação de re-curadoria após primeiros 7 dias de produção via runbook automatizado

### Passo 2: Curar ≥ 5 few-shot positivos

Source de prioridade (em ordem):

1. **PoV `context-pack.md`** (quando `with-pov`) — copia/refina os exemplos que provaram acerto consistente
2. **PoV `observability/prompts-log.md`** (sample real do uso pré-operacional, anonimizado)
3. **Domínio** (quando `direct-entry`/`cold-start`) — sintetiza a partir de `docs/{context}/entities/` + `docs/{context}/features/`

Cada few-shot DEVE conter:

```markdown
### Exemplo positivo #{N}: {nome curto}

**Cenário:** {1-2 frases sobre o contexto}

**Input (sanitizado):**
```
{input do usuário, com PII redacted}
```

**Pensamento esperado:**
```
{thought process — para padrões react/reflexion}
```

**Tools invocadas:**
- `{tool-name}` com input `{}`

**Output esperado:**
```
{output canônico, conforme schema declarado em system-prompt.md::Bloco 4}
```

**Origem:** PoV {agent-pov-slug} | sintético derivado de {entity}
```

### Passo 3: Curar ≥ 10 exemplos negativos

Exemplos negativos = anti-padrões. **Mínimo 10** em produção (vs. ≥ 2 no PoV — rigor diferencial). Categorias obrigatórias:

| Categoria | Mínimo | Source |
|-----------|--------|--------|
| Out-of-scope (input fora do escopo do agent) | 2 | scope.md do PoV + síntese |
| Ambiguidade não resolvida (precisa pedir esclarecimento, não chutar) | 2 | observability do PoV |
| PII leakage (agent NÃO DEVE revelar PII em determinado contexto) | 2 | guardrails |
| Prompt injection (input adversarial tenta override system prompt) | 2 | `kata-system-prompt-adversarial-validate` outputs |
| Tool injection (input pede tool fora do catálogo) | 1 | guardrails |
| Cross-tenant boundary (input pede dados de outro `org_id`) | 1 | guardrails |

Cada exemplo negativo:

```markdown
### Exemplo negativo #{N}: {nome curto}

**Categoria:** out-of-scope | ambiguity | pii-leakage | prompt-injection | tool-injection | cross-tenant

**Input (adversarial ou edge case):**
```
{input}
```

**Comportamento INCORRETO:**
```
{o que o agent NÃO DEVE fazer — e por quê}
```

**Comportamento CORRETO:**
```
{recusa estruturada com código de erro per lex-error-handling | escalonamento via escalation.md | pedido de esclarecimento}
```

**Origem:** PoV observability | guardrails | adversarial suite
```

### Passo 4: Selecionar snippets de telemetria

Quando `with-pov`, inclui:

1. Trace típico (`agent.turn` + `agent.tool_call` para um caso fácil) — sanitizado
2. Trace de edge case (caso médio com ambiguidade resolvida) — sanitizado
3. Distribuição de outcomes observada no PoV (% sucesso, % escalado, % rejeitado)

Snippets DEVEM ser hash-only para qualquer PII residual.

Em `direct-entry`/`cold-start`, omite esta seção; marca obrigação de adicionar após 30 dias de produção (re-curadoria).

### Passo 5: Declarar política de re-curadoria

```markdown
## Política de re-curadoria

- **Cadência:** {weekly | monthly | quarterly} — default quarterly
- **Trigger automático:** pivot trigger disparado em `feedback.md`
- **Owner:** {owner do agent declarado em overview.md}
- **Processo:** invocar `kata-agent-context-pack-design --refresh` com snapshot da telemetria mais recente
- **Versionamento:** mudanças em `context-pack.md` registradas em `Apêndice — Versões` com data + PR ref
```

### Validação Final

- [ ] ≥ 5 few-shot positivos com schema completo
- [ ] ≥ 10 exemplos negativos cobrindo as 6 categorias obrigatórias (mínimos por categoria)
- [ ] Em `with-pov`, fonte de cada exemplo declarada (PoV path ou síntese)
- [ ] Snippets de telemetria sanitizados quando `with-pov`
- [ ] Política de re-curadoria declarada com cadência + owner
- [ ] PII redaction confirmada no input (trust boundary documentado para `with-pov`)

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| `context-pack.md` | Markdown | `docs/{context}/agents/{agent}/context-pack.md` |

## Estrutura do arquivo `context-pack.md`

```markdown
# Context Pack — {agent}

> **Bounded Context:** {context}
> **Agent:** {agent}
> **Source:** {with-pov: docs/{context}/agents-pov/{pov-agent}/} | {direct-entry: synthesized from domain}
> **Re-curation cadence:** {cadence}
> **Last refresh:** {ISO 8601}

## Validação de input em fronteira

- **PII trust boundary:** confiamos no gate de PII grep aplicado por `kata-pov-value-track::Passo 4` no PoV de origem (quando `with-pov`). Este Kata não revalida PII; assume `pov_path/value-proof.md::status == ready_for_dooc` como prova de aprovação do gate
- **Source attribution:** cada exemplo declara origem (PoV path | sintético)
- **Versionamento:** mudanças passam por `kata-system-prompt-adversarial-validate` quando alterar negativos relacionados a prompt injection

## Few-shot positivos (≥ 5)

(seções `### Exemplo positivo #{N}` per Passo 2)

## Exemplos negativos (≥ 10)

(seções `### Exemplo negativo #{N}` per Passo 3)

## Telemetria observada (30-90 dias)

(snippets do Passo 4)

## Política de re-curadoria

(per Passo 5)

## Apêndice — Versões

- v1.0.0 — {data} — primeira versão derivada de PoV {pov-path} (PR ref)
- v1.1.0 — {data} — re-curadoria trimestral (PR ref)

## Restrições

- < 5 few-shot positivos viola Diretriz 06 em rigor de produção
- < 10 exemplos negativos viola Diretriz 06 em rigor de produção
- Few-shot inventado quando há PoV disponível é proibido — preferir fontes reais
- PoV imaturo (`value-proof.md::status != ready_for_dooc`) como fonte é proibido — aborta o Kata
- Snippets de telemetria com PII clara (não sanitizada) são proibidos

---

**Modelo:** Kata é a ponte canônica PoV → Operação Concreta. Lê 12 arquivos do output de Claudionor quando `--from-pov`, enriquece context pack com material real (few-shot + negativos + telemetria). Em `direct-entry`, opera em modo cold-start com obrigação de re-curadoria pós-deploy. Confia (não revalida) o gate de PII do PoV.
