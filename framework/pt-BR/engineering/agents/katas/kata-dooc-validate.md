# Kata: Validação da Definition of Operational Concrete (DoOC)

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Engenharia — Agents: gate-keeping de promoção de `pre-operational` para `operational-concrete` per `lex-agent-construction-directives`

## Objetivo

Verificar os 9 itens canônicos da Definition of Operational Concrete (DoOC) antes de permitir a promoção de um agent de `pre-operational` para `operational-concrete`. O Kata é a ferramenta executável da HARD-GATE de `lex-agent-construction-directives`: produz um relatório `go`/`no-go` auditável, registrado em `docs/{context}/dooc/{agent}.md`. Não é um HARD-GATE novo — é o verificador do HARD-GATE existente.

## Quando Usar

- Antes de qualquer transição de `stage: pre-operational` → `stage: operational-concrete` em system prompt de agent
- Sempre que `warrior-metis` recebe `cry-agent-design --from-pov docs/{context}/agents-pov/{agent}/`
- No Gate 2 do fluxo Issue-Driven quando a feature toca `docs/{context}/agents/`
- Em auditoria periódica de agentes `legacy-pov` (90 dias após merge de `lex-agent-construction-directives`)

## Inputs

| Input | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| `context` | Sim | Bounded Context do agent (kebab-case) |
| `agent` | Sim | Slug do agent (kebab-case) |
| `--from-pov <path>` | Não | Path para `docs/{context}/agents-pov/{agent}/` quando há PoV. Se ausente, modo `direct-entry` exige ADR/PDR |
| `--entry-mode` | Não | `with-pov` (padrão quando `--from-pov` presente) \| `direct-entry` \| `legacy-pov` |
| `--tier` | Sim | `tier-1` \| `tier-2` \| `tier-3` \| `tier-4` (tier-1/2 dispara obrigação de SLO per `lex-slo-required`) |
| `--owner` | Sim | Nome + papel do stakeholder owner do agent + canal de escalonamento |

## Workflow

Copie este checklist e acompanhe o progresso:

```
Progresso:
- [ ] 1. Resolver paths e modo de entrada
- [ ] 2. Verificar item (a) — Origem do PoV declarada
- [ ] 3. Verificar item (b) — Métrica leading provada
- [ ] 4. Verificar item (c) — Métrica lagging declarada
- [ ] 5. Verificar item (d) — Escopo estabilizado ≥ 2 semanas
- [ ] 6. Verificar item (e) — Observability data ≥ 7 dias
- [ ] 7. Verificar item (f) — Stakeholder owner identificado
- [ ] 8. Verificar item (g) — Capacidade de implementação confirmada
- [ ] 9. Verificar item (h) — Tier declarado (tier-1/2 → SLO mandatório)
- [ ] 10. Verificar item (i) — Stage explícito no system prompt do PoV
- [ ] 11. Aplicar cláusula de exceção quando aplicável (legacy-pov, direct-entry, user-override)
- [ ] 12. Produzir relatório `dooc/{agent}.md` + decisão `go`/`no-go`
```

### Passo 1: Resolver paths e modo de entrada

1. Resolve `pov_path = docs/{context}/agents-pov/{agent}/` se `--from-pov` fornecido; caso contrário registra `pov_path: N/A`
2. Define `entry_mode` per regra de precedência: argumento explícito → `with-pov` quando `pov_path` existe → `direct-entry` quando não
3. Em `entry_mode: direct-entry`, exige path para ADR/PDR em `docs/adr/` declarando: razão do bypass de `pre-operational`, leading metric alvo + janela pós-deploy, plano de observability instrumentado desde o dia 0. Sem ADR/PDR, falha imediato com mensagem clara
4. Em `entry_mode: legacy-pov`, verifica que a data do PoV original é anterior ao merge de `lex-agent-construction-directives` E está dentro da janela de 90 dias após o merge. Fora da janela, falha imediato

### Passo 2: Verificar item (a) — Origem do PoV declarada

| `entry_mode` | Critério |
|--------------|----------|
| `with-pov` | Existe `pov_path/pov.md` válido (contém `stage: pre-operational` no header) → ✅ |
| `direct-entry` | Marca `N/A — direct-entry (ADR: {path})` referenciando o ADR/PDR do Passo 1 → ✅ |
| `legacy-pov` | Existe PoV histórico identificável (commit ref ou path em archive) → ✅ |

Falha se nenhum critério é satisfeito.

### Passo 3: Verificar item (b) — Métrica leading provada

A métrica leading é a evidência operacional de que o agent entrega valor antes do impacto agregado. Critério:

1. Lê `pov_path/value-proof.md` (output de `kata-pov-value-track`) quando `with-pov`
2. Procura por: nome da métrica + threshold declarado + janela de observação ≥ 7 dias + valor observado ≥ threshold por ≥ 2 ciclos consecutivos
3. Em `direct-entry`, marca `N/A — direct-entry` referenciando o ADR; o ADR DEVE declarar a leading metric alvo e a janela pós-deploy (preenchimento posterior)

Falha se:
- `with-pov` sem `value-proof.md` válido
- threshold ou janela não declarados
- valor observado abaixo do threshold

### Passo 4: Verificar item (c) — Métrica lagging declarada

A métrica lagging é a métrica de negócio impactada (e.g., tempo de fechamento contábil, taxa de retrabalho de reconciliação). Critério:

1. Lê `pov_path/value-proof.md` campo `lagging_metric` ou `docs/{context}/features/{feature}.md` quando o agent serve features existentes
2. A métrica DEVE estar declarada com unidade e direção de melhoria esperada (ex.: "reduzir tempo médio de fechamento mensal de 5d para 3d")

Mesmo em `direct-entry`, este item é mandatório. Falha sem ADR explícito de exceção via cláusula `user-override`.

### Passo 5: Verificar item (d) — Escopo estabilizado ≥ 2 semanas

Critério: o escopo do agent (caso de uso primário + fora de escopo declarados) não mudou nas últimas 2 semanas. Verificação:

1. Lê `pov_path/scope.md` (output de `kata-pov-scope-define`) e checa o histórico de commits do arquivo via `git log --since="2 weeks ago" -- {scope.md}`
2. Aceita: 0 mudanças em 14 dias OU apenas mudanças tipográficas (sem alteração de seção `caso de uso primário` ou `fora de escopo`)
3. Em `direct-entry`, marca `N/A — direct-entry`; o escopo é declarado de novo durante o design por Mêtis

Falha se há mudança estrutural recente.

### Passo 6: Verificar item (e) — Observability data ≥ 7 dias

Critério: telemetria mínima de 7 dias do PoV em operação, alinhada a `lex-observability-required` (1 trace + 1 métrica + structured log com correlation_id).

1. Lê `pov_path/observability/` (output de `kata-pov-observability-instrument`)
2. Verifica que `traces-spec.md`, `prompts-log.md`, `tool-calls-log.md` e `value-metrics.md` existem
3. Pede confirmação de que dashboards / agregadores externos têm ≥ 7 dias de coleta (humano confirma ou path para snapshot dos dados)

Em `direct-entry`, marca `N/A — direct-entry`; observability será instrumentada por `warrior-apollo-agents` desde o dia 0 conforme o ADR.

### Passo 7: Verificar item (f) — Stakeholder owner identificado

Critério: nome do owner + papel + canal de escalonamento documentados. Verificação:

1. Argumento `--owner` fornecido OU `pov_path/value-proof.md::owner` populado
2. Canal de escalonamento DEVE ser concreto (Slack `#canal`, email, on-call) — não "TBD" ou "a definir"

Mandatório em todos os `entry_mode`. Falha sem exceção declarada.

### Passo 8: Verificar item (g) — Capacidade de implementação confirmada

Critério:

1. `warrior-apollo-agents` está disponível (plan-013 mergeado — checa via existência do arquivo `framework/{lang}/engineering/agents/warriors/warrior-apollo-agents.md`) → ✅
2. OU caminho alternativo declarado em ADR (`docs/adr/ADR-{N}-{slug}.md`)

Sem nenhum dos dois, falha.

### Passo 9: Verificar item (h) — Tier declarado

Critério:

1. Argumento `--tier` em {`tier-1`, `tier-2`, `tier-3`, `tier-4`}
2. Quando `tier-1` ou `tier-2`, registra obrigação de produzir `docs/{context}/agents/{agent}/metrics.md` com seção SLO per `lex-slo-required` (declarada como precondição para conclusão do design, não para passagem da DoOC)
3. `tier-3` / `tier-4` não dispara obrigação de SLO

Falha se `--tier` ausente ou fora do enum.

### Passo 10: Verificar item (i) — Stage explícito no system prompt do PoV

Critério: `pov_path/system-prompt.md` contém literalmente `stage: pre-operational` (per `lex-system-prompt`).

1. Em `with-pov`, lê o arquivo e procura a string literal
2. Em `direct-entry`, marca `N/A — direct-entry`; Mêtis declarará `stage: operational-concrete` no system prompt produzido
3. Em `legacy-pov`, requer migração manual via `kata-pov-system-prompt --retrofit` antes de prosseguir; sem retrofit, falha

### Passo 11: Aplicar cláusula de exceção quando aplicável

Em `entry_mode: direct-entry`, os itens (a), (b), (d) e (e) podem aparecer como `N/A — direct-entry` se o ADR/PDR do Passo 1 declarar (i) razão do bypass, (ii) leading metric alvo + janela pós-deploy, (iii) plano de observability dia 0. Itens (c) e (f)-(i) permanecem mandatórios.

Em `entry_mode: user-override` (CEO ou Brand owner promove com evidências parciais), exige ADR/PDR declarando (i) quais itens foram overrided, (ii) `Promoted by: {nome}` em `dooc/{agent}.md`, (iii) janela de compensação retroativa (sugerido 30 dias). Itens overrided viram `N/A — user-override`.

### Passo 12: Produzir relatório `dooc/{agent}.md` + decisão

Persiste em `docs/{context}/dooc/{agent}.md` no formato:

```markdown
# DoOC — {agent}

> **Bounded Context:** {context}
> **Entry mode:** with-pov | direct-entry | legacy-pov
> **Tier:** tier-1 | tier-2 | tier-3 | tier-4
> **Promoted by:** {nome, papel} (em user-override)
> **PR ref:** {owner/repo#NNN}
> **Validation date:** {ISO 8601}
> **Validator:** warrior-metis via kata-dooc-validate

## Items (9)

| # | Item | Status | Evidence |
|---|------|:------:|----------|
| a | Origem do PoV declarada | ✅ \| ❌ \| N/A | path ou ADR ref |
| b | Métrica leading provada | ✅ \| ❌ \| N/A | path ou ADR ref |
| c | Métrica lagging declarada | ✅ \| ❌ | path ou ADR ref |
| d | Escopo estabilizado ≥ 2 semanas | ✅ \| ❌ \| N/A | git log evidence |
| e | Observability data ≥ 7 dias | ✅ \| ❌ \| N/A | path |
| f | Stakeholder owner identificado | ✅ \| ❌ | nome + canal |
| g | Capacidade de implementação confirmada | ✅ \| ❌ | warrior path ou ADR |
| h | Tier declarado (SLO se tier-1/2) | ✅ \| ❌ | tier value |
| i | Stage explícito no system prompt do PoV | ✅ \| ❌ \| N/A | path |

## Decisão

`go` quando todos os itens forem ✅ ou `N/A` justificado por ADR/PDR válido.
`no-go` em qualquer outro caso.

## ADRs / PDRs referenciados

- {path/nome}

## Próximos passos quando `go`

Prosseguir com `warrior-metis` orquestrando os 8 katas de design restantes.

## Próximos passos quando `no-go`

Reportar itens faltantes ao usuário; sugerir retomada do PoV (`/cry-pov`) ou ADR de exceção quando aplicável.
```

### Validação Final

Antes de declarar `go`, verificar:

- [ ] Todos os 9 itens com status ✅ ou `N/A` justificado por ADR/PDR existente
- [ ] `dooc/{agent}.md` persistido no path canônico
- [ ] Quando `tier-1` ou `tier-2`, registrar obrigação pendente de SLO em `metrics.md` (a ser produzida por `kata-agent-feedback-design`)
- [ ] Owner + canal de escalonamento concretos (não placeholders)
- [ ] PR ref preenchido quando o Kata é invocado dentro de fluxo Issue-Driven

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| `dooc/{agent}.md` | Markdown | `docs/{context}/dooc/{agent}.md` |
| Decisão | `go` \| `no-go` | retorno ao orquestrador (`warrior-metis`) |
| Lista de itens faltantes | Lista textual | em caso de `no-go`, devolvida ao chamador |

## Exemplo de Execução

### Input de Exemplo

```
kata-dooc-validate \
  --context reconciliation \
  --agent rec-classifier \
  --from-pov docs/reconciliation/agents-pov/rec-pov-classifier/ \
  --tier tier-2 \
  --owner "Marta Souza, Lead Reconciliation, #rec-oncall"
```

### Output de Exemplo (extrato)

```markdown
# DoOC — rec-classifier

> **Bounded Context:** reconciliation
> **Entry mode:** with-pov
> **Tier:** tier-2
> **PR ref:** guardiatechnology/ahrena#543
> **Validation date:** 2026-05-12T15:30:00Z
> **Validator:** warrior-metis via kata-dooc-validate

## Items (9)

| # | Item | Status | Evidence |
|---|------|:------:|----------|
| a | Origem do PoV declarada | ✅ | docs/reconciliation/agents-pov/rec-pov-classifier/pov.md |
| b | Métrica leading provada | ✅ | reconciliation_auto_rate = 62% (threshold 60%) por 21 dias |
| c | Métrica lagging declarada | ✅ | docs/reconciliation/features/transaction-classification.md::lagging_metric |
| d | Escopo estabilizado ≥ 2 semanas | ✅ | git log scope.md: 0 mudanças em 18 dias |
| e | Observability data ≥ 7 dias | ✅ | docs/reconciliation/agents-pov/rec-pov-classifier/observability/ (21 dias) |
| f | Stakeholder owner identificado | ✅ | Marta Souza, Lead Reconciliation, #rec-oncall |
| g | Capacidade de implementação confirmada | ✅ | framework/.../warriors/warrior-apollo-agents.md (plan-013 mergeado) |
| h | Tier declarado | ✅ | tier-2 (SLO obrigatório em metrics.md) |
| i | Stage explícito no system prompt do PoV | ✅ | pov-path/system-prompt.md::stage: pre-operational |

## Decisão

`go` — todos os 9 itens ✅. Prosseguir com design dos 13 arquivos.
```

## Restrições

- O Kata é o **verificador** da HARD-GATE de `lex-agent-construction-directives`; não cria um HARD-GATE novo
- `no-go` é decisão final do Kata; quem decide retomar PoV ou abrir ADR de exceção é o usuário humano
- Em modo `direct-entry`, o ADR/PDR DEVE existir antes do Passo 1; criar ADR retroativo apenas para passar o Kata é proibido (viola o espírito do gate)
- Não persistir `dooc/{agent}.md` quando o output é `no-go` — apenas reportar; o snapshot vai para o destino canônico só após `go`
- Não modificar `lex-agent-construction-directives` nem `lex-agent-design-docs`
- PR ref é obrigatório quando o Kata roda dentro de fluxo Issue-Driven; em auditoria periódica ou rodada manual, preenche com `manual-audit`

---

**Modelo:** Kata gate-keeper canônico de promoção a `operational-concrete`. Executa programaticamente os 9 itens da DoOC, aplica as 3 cláusulas de exceção declaradas em `lex-agent-construction-directives` (legacy-pov, direct-entry, user-override) e persiste o snapshot em `docs/{context}/dooc/{agent}.md` quando `go`. Sempre invocado primeiro por `warrior-metis` antes de qualquer outro kata de design.
