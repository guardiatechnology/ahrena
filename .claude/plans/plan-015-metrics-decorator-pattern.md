---
plan_id: "015"
title: "metrics-decorator-pattern"
status: pending
agent: claude
issue: "TBD (a abrir antes da branch — lex-issue-first)"
created_at: "2026-05-07T22:30:00Z"
updated_at: "2026-05-07T22:30:00Z"
---

# Plano: Padrão de métricas via decorator (espelho do `lex-logging-decorator`)

## Objetivo

Codificar como Lex que toda métrica produzida por código de aplicação MUST vir de (a) bootstrap centralizado do meter e (b) decorator `@measured(operation=..., labels=...)` aplicado a função/método/handler. Chamadas diretas a primitivas de métrica (`meter.counter().add()`, `histogram.record()`, `gauge.set()`) dentro do corpo de funções de aplicação ficam proibidas — exceções limitadas ao módulo de bootstrap, ao próprio decorator e a handlers globais. Espelha exatamente a `lex-logging-decorator` para criar simetria entre os dois sinais (logs + métricas) que já são exigidos por `lex-observability-required`.

## Contexto

### Estado atual

- `lex-logging-decorator` já obriga decorator para logs em todas as linguagens (allow-list em `pyproject.toml`/`.eslintrc`/`.golangci.yaml` sob `ahrena.logging.allowed_modules`)
- `lex-observability-required` exige que toda nova HTTP endpoint/consumer/job emita span+métrica+log, mas **deixa o "como" da métrica livre** — implementações divergem
- Nenhuma Lex ou codex prescreve `@measured` ou pattern equivalente para métricas
- `codex-python-observability` cobre OpenTelemetry mas trata como reference, não como contrato

### Por que decorator (não middleware nem observer)

| Padrão | Prós | Contras |
|---|---|---|
| **Decorator** ✅ | Simétrico ao logs (já adotado); explícito na fronteira da função; força o operation name a ficar declarado; testável isoladamente | Não cobre métricas que dependem de estado interno do loop (resolvido via allow-list para `meter.observe(...)`) |
| Middleware | Captura tudo automaticamente | Só funciona em endpoints HTTP; perde scope para jobs/agents; operation name fica genérico |
| Observer | Desacopla emissor de coletor | Indireção desnecessária; debugging difícil; viola "explicit over implicit" do Apollo |
| Inline (`meter.counter(...).add(1)` no corpo) | Flexível | É **exatamente o que a Lex quer banir** — paralelo ao `logger.info` no corpo |

### Decisões fechadas

| Decisão | Valor | Por quê |
|---|---|---|
| Padrão obrigatório | Decorator (`@measured`) | Simetria com logs; explícito; testável |
| Nome do decorator | `@measured(operation, labels=...)` em Python; `measured(...)` HOC em TS | Espelho de `@logged(operation, ...)`; familiaridade |
| Métricas geradas automaticamente | Latência (histogram) + outcome (counter `success/error`) por padrão | Cobertura mínima sem pedir input extra |
| Métricas customizadas dentro do corpo | Permitido apenas via `meter.observe(...)` em allow-list (mesmo modelo do logging para boundary handlers) | Cobre estado-interno (e.g., counter por item processado) |
| Lint rule | Proíbe `meter.counter`, `meter.histogram`, `meter.gauge` etc. fora dos módulos em `ahrena.metrics.allowed_modules` | Mesmo enforcement do logs |
| Idiomas | 3 (pt-BR canonical + es + en) | `lex-framework-language` |
| Aplicação | Cross-component (api, jobs, agents) — todos os warriors backend usam | Padrão único reduz divergência |
| Frontend | Mesma Lex aplica via wrapper TS/JS análogo (`measured(metricName, fn)`) | Simetria multilíngue |

## Escopo

### Artefatos a criar (3 idiomas cada)

| Pilar | Caminho relativo | Conteúdo principal |
|---|---|---|
| Lexis | `_foundation/quality/lexis/lex-metrics-decorator.md` | Lei (decorator obrigatório; chamadas inline proibidas; allow-list); exemplos certo/errado em Python, TS, Go (espelho exato de `lex-logging-decorator`); validação automatizada |
| Codex | `_foundation/quality/codex/codex-metrics-decorator.md` | Padrões de implementação: signature do `@measured`, default labels (operation, outcome), histogram bucket strategy, integração com OpenTelemetry, allow-list de exceções (boundary handlers, observe-no-loop), referência a `codex-python-observability` |

### Atualizações em artefatos existentes (3 idiomas)

| Arquivo | Mudança |
|---|---|
| `_foundation/quality/lexis/lex-observability-required.md` | Acrescentar nota: "A parte 'métrica' das três sinais MUST ser implementada via padrão definido em `lex-metrics-decorator`. A parte 'log' via `lex-logging-decorator`. A parte 'trace' segue OpenTelemetry SDK conforme `codex-python-observability`" |
| `engineering/backend/codex/codex-python-observability.md` | Acrescentar seção "Padrão `@measured`" remetendo para `lex-metrics-decorator` |
| `engineering/frontend/codex/codex-frontend-architecture.md` | Acrescentar seção "Métricas no client" remetendo para `lex-metrics-decorator` (versão TS) |
| `framework/.directives.sample` | Adicionar bloco comentado `ahrena.metrics.allowed_modules` espelhando o existente `ahrena.logging.allowed_modules` |
| `framework/platforms.yaml` | Registrar Lex e Codex novos em `cursor.rules` + `claude-code.rules` (Lex) e `claude-code.docs` (Codex) |

### Lint rule (sample provido pelo plano, projeto-alvo implementa)

- **Python**: extensão custom de Ruff (regra `T20X` análoga ao `T201/T203` do print) detectando `meter.counter`, `meter.histogram`, `meter.gauge` fora da allow-list lida do `pyproject.toml`
- **TypeScript/JS**: regra ESLint custom `no-direct-meter-primitives` análoga ao `no-console`
- **Go**: `forbidigo` patterns análogos aos de `log.Print*`

O plan **não implementa** as lint rules (cada projeto cliente do framework implementa); apenas documenta os patterns no codex.

## Fora de escopo

- **Implementação concreta do decorator** em algum projeto cliente — Lex prescreve interface e contrato; cada projeto implementa conforme stack
- **Reescrita das métricas existentes** que hoje são inline — adoção é gradual; novos endpoints devem seguir; existentes ficam até refactor natural
- **Mudança em `lex-logging-decorator`** — preservada idêntica; nova Lex se ancora nela
- **Padrão para traces** — `codex-python-observability` já cobre; seria over-engineering criar `lex-trace-decorator` (instrumentação OTel já é declarativa via SDK)
- **Backend de coleta** (Prometheus, CloudWatch, OTLP) — Lex agnostic; codex cita opções

## Steps

- [ ] 1. Abrir issue com template `feature-request`, Issue Type `Feature`, label `feature request ➕`, título "feat(framework): metrics decorator pattern (lex-metrics-decorator + codex)"
- [ ] 2. Criar branch `feat/{N}-metrics-decorator-pattern` e worktree
- [ ] 3. Atualizar status deste plan para `in-progress`
- [ ] 4. Redigir `lex-metrics-decorator.md` em pt-BR usando `templates/lex-sample.md` — espelho estrutural de `lex-logging-decorator.md`
- [ ] 5. Redigir `codex-metrics-decorator.md` em pt-BR (`templates/codex-sample.md`)
- [ ] 6. Atualizar `lex-observability-required.md` em pt-BR com a nota de divisão dos três sinais
- [ ] 7. Atualizar `codex-python-observability.md` em pt-BR com seção "Padrão `@measured`"
- [ ] 8. Atualizar `codex-frontend-architecture.md` em pt-BR com seção "Métricas no client"
- [ ] 9. Adicionar bloco `ahrena.metrics.allowed_modules` em `framework/.directives.sample`
- [ ] 10. Atualizar `framework/platforms.yaml` com 2 entries novas
- [ ] 11. Traduzir os 2 artefatos novos + as 3 atualizações para `es` e `en`
- [ ] 12. Rodar `python3 scripts/install.py --self --target . --platform claude-code` e `cursor`
- [ ] 13. **Smoke test sandbox**: criar projeto sandbox; aplicar `@measured(operation="test.op")` numa função; rodar; verificar que histogram e counter foram emitidos com labels corretos via OpenTelemetry collector local
- [ ] 14. **Smoke test lint**: configurar Ruff custom rule no sandbox bloqueando `meter.counter` fora da allow-list; verificar que falha; mover função para módulo permitido; verificar que passa
- [ ] 15. Rodar `kata-artifact-self-review` em Lex e Codex novos
- [ ] 16. Commits atômicos por artefato (subject inglês + body bilíngue, assinados)
- [ ] 17. Push e abrir PR via `kata-contributing-pr` referenciando `Closes #{N}` e plan-015
- [ ] 18. Após merge: arquivar plan e remover worktree

## Dependências

- `lex-logging-decorator` mergeado (já está) — fornece o template estrutural
- `lex-observability-required` mergeado (já está)
- `templates/lex-sample.md`, `templates/codex-sample.md` presentes
- **Independente** dos plans 006-014 e 016-021
- **Sinérgico** com plan-013 (especialistas Apollo) — `apollo-api`, `apollo-jobs`, `apollo-agents` referenciam o novo padrão; pode mergear antes ou depois sem conflito

## Riscos

- **Lex prescritiva sem reference impl gera divergência entre projetos.** Mitigação: codex inclui exemplo concreto Python + TS; sandbox smoke test valida contrato antes do merge
- **Conflito com convenções existentes em projetos clientes.** Mitigação: adoção gradual; Lex se aplica a "novo código de aplicação" — refactor de métricas existentes não é gate
- **Lint rules divergem entre linguagens.** Mitigação: codex documenta os 3 (Python/TS/Go) com mesmo conceito; cada projeto implementa o que precisa
- **Métricas custom em loops** (e.g., contar items processados) parecem violar a Lex. Mitigação: allow-list explícita para `meter.observe(...)` em módulos declarados; codex documenta os 2-3 casos legítimos
- **Confusão com `@logged`** se nomes ficarem parecidos. Mitigação: codex tem seção "quando usar cada um" com tabela compacta (logs = eventos discretos; métricas = agregação numérica)

## Verificação

1. `lex-metrics-decorator` × 3 idiomas + `codex-metrics-decorator` × 3 idiomas = 6 arquivos novos
2. `lex-observability-required` × 3 idiomas atualizado com nota de divisão dos sinais
3. `codex-python-observability` × 3 idiomas atualizado com seção `@measured`
4. `codex-frontend-architecture` × 3 idiomas atualizado com seção métricas no client
5. `framework/.directives.sample` tem bloco `ahrena.metrics.allowed_modules`
6. `framework/platforms.yaml` lista os 2 novos artefatos
7. Smoke test sandbox emite métricas pelo decorator; lint rule bloqueia primitivas fora da allow-list
8. **Sem alteração** em `lex-logging-decorator`, kata-quality-gate, lex-pr-quality, framework structure
9. PR final passa HARD-GATE de `lex-pr-quality`; carrega stamp de custo se plan-007 mergeado