---
plan_id: "017"
title: "resilience-decorator-pattern"
status: pending
agent: claude
issue: "TBD (a abrir antes da branch — lex-issue-first)"
created_at: "2026-05-07T22:30:00Z"
updated_at: "2026-05-07T22:30:00Z"
---

# Plano: Padrão de resiliência via decorator (`@resilient` — retry + circuit-breaker)

## Objetivo

Codificar como Lex e Codex o padrão único para **retry com backoff exponencial** e **circuit-breaker** em chamadas que cruzam fronteiras de processo (HTTP outbound, AWS SDK, integração com terceiros, fila externa). Decorator único `@resilient(retries=3, backoff=exp(base=2, max=30s), breaker=circuit(threshold=5, reset=60s))` aplicado a função/método. Banir reinvenção de retry loops manuais (`for attempt in range(...)`) ou breakers ad-hoc no corpo de funções de aplicação. Implementação concreta em Python via Tenacity; em TS via `p-retry` + `opossum`. Aplica fortemente a `apollo-jobs` (Step Functions task que chama integration externa) e a `apollo-api` (chamadas outbound a serviços terceiros).

## Contexto

### Estado atual

- `lex-error-handling` (Guardia platform) menciona "retry e circuit breaker per specification" mas a "specification" é vaga
- `codex-known-errors` lista códigos de erro retryáveis vs não-retryáveis
- **Pattern de implementação ausente** — cada chamada externa reinventa: alguns usam Tenacity, outros loops manuais, outros HTTPx retries built-in, outros nada
- Sem padrão, behavior é inconsistente: retry agressivo causa thundering herd; sem retry causa flakiness

### Por que decorator (não middleware nem proxy)

- Retry/breaker é decisão **por chamada**, não por rota. Decorator é a granularidade certa.
- Middleware HTTP cobre só inbound; chamadas outbound (AWS SDK, terceiros) ficam de fora.
- Service mesh/sidecar resolve em runtime mas é over-engineering para a maioria dos projetos Guardia hoje.
- Decorator é simétrico com `@logged`/`@measured`/`@idempotent` — mesmo modelo mental.

### Decisões fechadas

| Decisão | Valor | Por quê |
|---|---|---|
| Padrão obrigatório | `@resilient(...)` para toda chamada cross-process | Loops manuais e tentativas ad-hoc proibidos |
| Implementação Python | Wrapper sobre Tenacity (lib madura) | Não reinventar; aproveitar `before_sleep`, `retry_if_exception_type`, jitter |
| Implementação TS | Wrapper sobre `p-retry` + `opossum` (circuit-breaker) | Comparáveis a Tenacity |
| Defaults | `retries=3, backoff=exp(base=2, jitter=true, max=30s), breaker=circuit(threshold=5_failures_in_60s, half_open_after=30s)` | Conservador; suficiente para flakiness típico sem amplificar incidentes |
| Exceções retryáveis | Default: timeouts, 5xx, ConnectionError. Sobrescrevível via `retry_on=[...]` | Codex documenta erros retryáveis vs não (`codex-known-errors`) |
| Composição com outros decorators | Stack: `@measured` → `@logged` → `@resilient` → `@idempotent` → função | Métrica e log capturam o resultado final pós-retry; idempotência aplica antes de cada attempt; `@resilient` é fronteira externa |
| Allow-list | `ahrena.resilience.allowed_modules` em `pyproject.toml`; chamadas a Tenacity primitives fora da allow-list proibidas | Mesmo modelo de logging/metrics |
| HARD-GATE | Sim | Esta Lex bloqueia merge — pattern não é negociável |
| Aplicação | Cross-component (api, jobs, agents) | Qualquer chamada externa cabe |
| Idiomas | 3 (pt-BR canonical + es + en) | `lex-framework-language` |

## Escopo

### Artefatos a criar (3 idiomas)

| Pilar | Caminho relativo | Conteúdo principal |
|---|---|---|
| Lexis | `_foundation/quality/lexis/lex-resilience-decorator.md` | Lei: `@resilient` é único pattern aceito para retry/breaker em cross-process calls; loops manuais proibidos; HARD-GATE; allow-list |
| Codex | `_foundation/quality/codex/codex-resilience-decorator.md` | Signature; opções (`retries`, `backoff`, `breaker`, `retry_on`, `before_sleep`); defaults justificados; integração com Tenacity (Python) e p-retry+opossum (TS); composição com outros decorators; padrões anti-thundering-herd (jitter, deadline budget); testes (mock falha → retry → sucesso; mock falha contínua → breaker abre); referência a `codex-known-errors` para retryável vs não |

### Atualizações em artefatos existentes (3 idiomas)

| Arquivo | Mudança |
|---|---|
| `lex-error-handling.md` (Guardia platform existente) | Acrescentar referência: "Retry e circuit breaker MUST seguir `lex-resilience-decorator`" |
| `codex-known-errors.md` | Acrescentar seção "Retryability matrix" — para cada known-error, marcar `retryable: yes/no/conditional`, base para o `retry_on=` default |
| `engineering/architecture/codex/codex-component-api.md` (criado em plan-012) | Acrescentar `@resilient` em "Key Patterns" (chamadas outbound) |
| `engineering/architecture/codex/codex-component-jobs.md` (criado em plan-012) | Acrescentar `@resilient` em "Key Patterns" (Step Functions task wrapper) |
| `engineering/architecture/codex/codex-component-agents.md` (criado em plan-012) | Acrescentar `@resilient` em "Key Patterns" (LLM API calls, Bedrock invocations) |
| `framework/.directives.sample` | Adicionar bloco comentado `ahrena.resilience.allowed_modules` |
| `framework/platforms.yaml` | Registrar Lex e Codex novos |

## Fora de escopo

- **Reference impl completo** — codex traz starter snippets (~40 linhas Python + ~30 TS); projeto cliente implementa
- **Service mesh / sidecar** (Linkerd, Istio, App Mesh) — fora; decorator-level basta para a maioria
- **Bulkhead pattern** (isolamento por pool) — pode entrar em iteração futura; não neste plan
- **Rate limiting outbound** (token bucket para self-throttle) — fora; cada projeto resolve via lib específica
- **Retroatividade** — código existente com retry manual fica até o próximo refactor passar por ele

## Steps

- [ ] 1. Confirmar plan-012 mergeado (codex-component-{api,jobs,agents} disponíveis)
- [ ] 2. Abrir issue com template `feature-request`, Issue Type `Feature`
- [ ] 3. Criar branch `feat/{N}-resilience-decorator-pattern` e worktree
- [ ] 4. Atualizar status deste plan para `in-progress`
- [ ] 5. Redigir `lex-resilience-decorator.md` em pt-BR (com HARD-GATE)
- [ ] 6. Redigir `codex-resilience-decorator.md` em pt-BR — incluir starter snippets Python (Tenacity) e TS (p-retry + opossum)
- [ ] 7. Atualizar `lex-error-handling.md` em pt-BR
- [ ] 8. Atualizar `codex-known-errors.md` em pt-BR com Retryability matrix
- [ ] 9. Atualizar `codex-component-api.md`, `codex-component-jobs.md`, `codex-component-agents.md` em pt-BR
- [ ] 10. Adicionar bloco `ahrena.resilience.allowed_modules` em `framework/.directives.sample`
- [ ] 11. Atualizar `framework/platforms.yaml`
- [ ] 12. Traduzir Lex, Codex e atualizações para `es` e `en`
- [ ] 13. Rodar `python3 scripts/install.py --self --target . --platform claude-code` e `cursor`
- [ ] 14. **Smoke test retry**: função sandbox que falha 2x e sucesso na 3ª; aplicar `@resilient(retries=3)`; verificar que retorna sucesso após 3 attempts; medir backoff times (devem ser exponenciais com jitter)
- [ ] 15. **Smoke test breaker**: função sandbox que falha sempre; aplicar `@resilient(breaker=circuit(threshold=5))`; verificar que após 5 falhas o breaker abre e chamadas seguintes falham fast (sem chamar a função); aguardar `half_open_after`; verificar que função é chamada de novo
- [ ] 16. **Smoke test composição**: stack `@measured` → `@logged` → `@resilient` → `@idempotent` → função; verificar ordem; verificar que retry interno do `@resilient` não causa duplicação no `@logged` (log fica no resultado final, não em cada attempt — exceto via `before_sleep` callback)
- [ ] 17. **Smoke test allow-list**: chamada direta a `tenacity.retry(...)` fora da allow-list é detectada por lint (referência) — codex documenta o lint pattern
- [ ] 18. Rodar `kata-artifact-self-review` em Lex e Codex novos
- [ ] 19. Commits atômicos; push; abrir PR via `kata-contributing-pr`
- [ ] 20. Após merge: arquivar plan e remover worktree

## Dependências

- **Plan-012 mergeado** — codex-component-{api,jobs,agents} precisam existir (bloqueante)
- `lex-error-handling`, `codex-known-errors` existentes — base que será estendida
- `lex-hard-gate-pattern` — usado no HARD-GATE
- **Independente** de plans 011, 013-016, 018-021
- **Sinérgico** com plan-016 (idempotency) — composição decorator é específica; codex documenta a ordem canônica que envolve ambos

## Riscos

- **Retry agressivo amplifica incidente em vez de mitigar.** Mitigação: defaults conservadores (`retries=3`, jitter obrigatório, max backoff 30s); breaker incluído por default; codex tem seção "anti-thundering-herd" com guidance
- **Breaker estado global vs per-instance** confunde em ambiente multi-pod. Mitigação: codex documenta os dois modelos; default in-process (per-instance) com nota sobre quando usar distribuído (Redis-backed)
- **Tenacity/opossum upgrade quebram contrato.** Mitigação: wrapper isola; pin de versão minima no codex; auditoria trimestral
- **Retry mascarando bug real.** Mitigação: `retry_on=[...]` lista explícita de exceptions retryáveis; deve lançar não-retryáveis sem retry; codex documenta perigo de `retry_on=Exception`
- **Composição com `@idempotent` cria duplo cache.** Mitigação: codex prescreve que `@idempotent` envolve `@resilient` (idempotência por fora; retry tenta dentro do mesmo idempotency window) — smoke test 16 valida
- **Lex prescritiva conflita com libs que já têm retry built-in** (httpx `transport=HTTPTransport(retries=N)`, boto3 `retries={'mode': 'adaptive'}`). Mitigação: codex tem seção "quando o lib nativo é suficiente" — para casos simples, lib nativo OK; para qualquer lógica custom (retry_on específico, breaker, before_sleep callback), `@resilient` obrigatório

## Verificação

1. `lex-resilience-decorator` × 3 idiomas + `codex-resilience-decorator` × 3 idiomas = 6 arquivos novos
2. HARD-GATE presente nas 3 versões
3. `lex-error-handling`, `codex-known-errors`, `codex-component-{api,jobs,agents}` × 3 idiomas atualizados
4. `framework/.directives.sample` tem `ahrena.resilience.allowed_modules`
5. `framework/platforms.yaml` lista os 2 novos artefatos
6. Smoke tests retry, breaker, composição passam
7. Starter snippets compilam (Python tenacity, TS p-retry+opossum)
8. **Sem alteração** em `lex-idempotency*`, `lex-logging-decorator`, `lex-metrics-decorator` (composição é responsabilidade do codex de resilience)
9. PR final passa HARD-GATE de `lex-pr-quality`
