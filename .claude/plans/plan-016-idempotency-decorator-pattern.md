---
plan_id: "016"
title: "idempotency-decorator-pattern"
status: pending
agent: claude
issue: "TBD (a abrir antes da branch — lex-issue-first)"
created_at: "2026-05-07T22:30:00Z"
updated_at: "2026-05-07T22:30:00Z"
---

# Plano: Padrão de idempotência via decorator (`@idempotent`) para api e jobs

## Objetivo

Codificar o **como** da idempotência exigida por `lex-idempotency`. Hoje a Lei obriga endpoints mutantes a aceitar `Idempotency-Key` e eventos a carregarem `idempotencykey`, mas deixa cada warrior implementar à sua maneira — gerando divergência entre `apollo-api` e `apollo-jobs`. Entregar nova `lex-idempotency-implementation` + codex que prescrevem decorator único: `@idempotent(key_source="header:Idempotency-Key", scope="route", store=...)` para api e `@idempotent(key_source="event.idempotencykey", scope="consumer", store=...)` para jobs. Storage backend é abstração; concreto fica com o projeto.

## Contexto

### Estado atual

- `lex-idempotency` (Guardia platform) obriga: APIs mutantes requerem header `Idempotency-Key`; eventos carregam `idempotencykey`; consumer registra e dedup
- **Pattern de implementação não está prescrito** — cada feature reinventa: alguns usam Redis SETNX, outros DynamoDB conditional put, outros middleware FastAPI custom
- `aws-lambda-powertools` já fornece `@idempotent` para Lambda — referência forte
- FastAPI não tem nativo; precisa custom middleware ou decorator

### Por que decorator (e não middleware-only)

Idempotência tem **dois aspectos**:

1. **Validação do request/event** — chave presente, formato correto → naturalmente middleware (HTTP) ou middleware Powertools (Lambda)
2. **Captura de payload + retorno cacheado** — precisa envolver a função de negócio para registrar a saída e retorná-la em re-run → naturalmente decorator

Decorator único cobre os dois (composto sobre middleware quando há); simétrico com `@logged`/`@measured`.

### Decisões fechadas

| Decisão | Valor | Por quê |
|---|---|---|
| Padrão obrigatório | `@idempotent(...)` em ambos api e jobs | Único contrato; alinha apollo-api e apollo-jobs |
| Storage backend | Plugável: Redis, DynamoDB, Postgres (escolha do projeto) | Backend é decisão de infra, não de framework |
| TTL default | 24h (api) / 7d (jobs) | Cobre janelas de retry típicas; sobrescrevível |
| Composição com `@measured` e `@logged` | Decorator stack ordenado — outermost: `@measured` → `@logged` → `@idempotent` → função | Métrica e log capturam resultado final; idempotência é última fronteira antes do negócio |
| Signature da chave | `key_source` literal: `"header:Idempotency-Key"`, `"event.idempotencykey"`, `"path:transaction_id"` | Explícito; sem mágica |
| Conflito de payload (mesma key, payload diferente) | 409 Conflict (api) / log + drop (jobs) | Espelha o que `codex-idempotency` já recomenda |
| Scope de uniqueness | `scope=` parameter — `"route"` (api), `"consumer"` (jobs), `"global"` (raro) | Evita colisão entre handlers que aceitam o mesmo header |
| Lex obriga, codex orienta, allow-list por projeto | Sim | Mesmo modelo de `lex-logging-decorator` |
| Aplicação | Cross-component (api + jobs); agents geralmente não precisa (LLM tools são determinísticas, mas pode haver casos) | Codex documenta quando agents também aplica |
| Idiomas | 3 (pt-BR canonical + es + en) | `lex-framework-language` |

## Escopo

### Artefatos a criar (3 idiomas)

| Pilar | Caminho relativo | Conteúdo principal |
|---|---|---|
| Lexis | `engineering/platform/lexis/lex-idempotency-implementation.md` | Lei: `@idempotent` é único pattern aceito; chamadas manuais a storage de idempotência fora do decorator são proibidas; allow-list em `pyproject.toml`; HARD-GATE per `lex-hard-gate-pattern` |
| Codex | `engineering/platform/codex/codex-idempotency-decorator.md` | Signature do decorator; opções (`key_source`, `scope`, `store`, `ttl`, `on_conflict`); exemplos certo/errado para api (FastAPI) e jobs (Powertools); composição com `@measured`/`@logged`; backends recomendados (Redis, DynamoDB) com pros/cons; testes (replay deve retornar mesmo resultado, conflict path) |

### Atualizações em artefatos existentes (3 idiomas)

| Arquivo | Mudança |
|---|---|
| `lex-idempotency.md` (Guardia platform existente) | Acrescentar referência: "Implementação MUST seguir `lex-idempotency-implementation`" |
| `codex-idempotency.md` | Acrescentar seção "Padrão decorator" remetendo para o novo codex |
| `engineering/architecture/codex/codex-component-api.md` (criado em plan-012) | Acrescentar `@idempotent` em "Key Patterns" |
| `engineering/architecture/codex/codex-component-jobs.md` (criado em plan-012) | Idem |
| `framework/.directives.sample` | Adicionar bloco comentado `ahrena.idempotency.allowed_modules` (allow-list de módulos que podem chamar storage diretamente — bootstrap + decorator + fallback handlers) |
| `framework/platforms.yaml` | Registrar Lex e Codex novos |

## Fora de escopo

- **Reference implementation completa** do decorator (Python e TS) — codex traz signature e contrato; impl concreta fica em projeto cliente. **Exceção:** snippet "starter" no codex (~30 linhas) para Python (FastAPI) e Lambda (Powertools wrapper) com TODO markers
- **Storage backend impl** — Redis, DynamoDB, Postgres ficam plug-in
- **Retroatividade** — endpoints/jobs existentes adotam quando o próximo refactor passar por eles
- **Idempotência em frontend** — fora do escopo de `lex-idempotency` original
- **Conflito com plan-006** (Athena stacked PRs) — não há

## Steps

- [ ] 1. Confirmar plan-012 mergeado (codex-component-api e codex-component-jobs disponíveis para receberem a referência)
- [ ] 2. Abrir issue com template `feature-request`, Issue Type `Feature`
- [ ] 3. Criar branch `feat/{N}-idempotency-decorator-pattern` e worktree
- [ ] 4. Atualizar status deste plan para `in-progress`
- [ ] 5. Redigir `lex-idempotency-implementation.md` em pt-BR (com HARD-GATE)
- [ ] 6. Redigir `codex-idempotency-decorator.md` em pt-BR — incluir starter snippets para FastAPI e Powertools
- [ ] 7. Atualizar `lex-idempotency.md` (existente) e `codex-idempotency.md` em pt-BR
- [ ] 8. Atualizar `codex-component-api.md` e `codex-component-jobs.md` em pt-BR
- [ ] 9. Adicionar bloco `ahrena.idempotency.allowed_modules` em `framework/.directives.sample`
- [ ] 10. Atualizar `framework/platforms.yaml`
- [ ] 11. Traduzir Lex e Codex novos + atualizações para `es` e `en`
- [ ] 12. Rodar `python3 scripts/install.py --self --target . --platform claude-code` e `cursor`
- [ ] 13. **Smoke test api**: aplicar `@idempotent(key_source="header:Idempotency-Key", scope="route", store=RedisStore())` a endpoint POST sandbox; replay com mesma key; verificar que segunda chamada retorna 200 cacheado e função de negócio não rodou de novo; replay com key igual + payload diferente; verificar 409
- [ ] 14. **Smoke test jobs**: aplicar `@idempotent(key_source="event.idempotencykey", scope="consumer", store=DynamoStore())` a Lambda handler; replay; verificar que segunda invocação retorna ack sem reexecutar
- [ ] 15. **Smoke test composição**: empilhar `@measured` → `@logged` → `@idempotent` → função; verificar ordem de execução e que cada decorator vê o resultado correto
- [ ] 16. Rodar `kata-artifact-self-review` em Lex e Codex novos
- [ ] 17. Commits atômicos; push; abrir PR via `kata-contributing-pr`
- [ ] 18. Após merge: arquivar plan e remover worktree

## Dependências

- **Plan-012 mergeado** — codex-component-api e codex-component-jobs precisam existir para receberem a referência (bloqueante)
- `lex-idempotency` e `codex-idempotency` existentes — base que será estendida
- `lex-hard-gate-pattern` — usado para o HARD-GATE da nova Lex
- **Independente** de plans 011, 013, 014, 015, 017, 018, 019, 020, 021
- **Sinérgico** com plan-013 (Apollo specialists vão consumir essa Lex e cada especialista terá-a no seu set carregado)

## Riscos

- **Decorator com muitas opções vira leaky abstraction.** Mitigação: defaults por scope (`scope="route"` defaulta a header `Idempotency-Key`, TTL 24h, store inferido por config); usuário só passa o que diverge do default
- **Storage backend Redis/DynamoDB introduz dependência operacional.** Mitigação: codex lista 3 backends com trade-offs; projeto escolhe; allow-list permite testar com `InMemoryStore()` em dev/test
- **Conflito de payload (mesma key, payload diferente)** — comportamento divergente entre api (409) e jobs (drop+log). Mitigação: codex documenta as duas semânticas; decorator aceita `on_conflict` para override quando necessário
- **Composição com outros decorators (@measured/@logged) gera ordem errada.** Mitigação: codex prescreve ordem canônica (outermost: measured → logged → idempotent → função); smoke test step 15 valida
- **Powertools `@idempotent` já existe e é diferente.** Mitigação: codex documenta que para Lambda específico, `@idempotent` da Ahrena pode ser **alias/wrapper** sobre Powertools com defaults Guardia; reduz reimplementação
- **Confusão com `lex-idempotency` (que continua válida).** Mitigação: separação clara — `lex-idempotency` é o **contrato** (deve ser idempotente); `lex-idempotency-implementation` é o **mecanismo** (deve usar `@idempotent`); codex cross-references explicitam

## Verificação

1. `lex-idempotency-implementation` × 3 idiomas + `codex-idempotency-decorator` × 3 idiomas = 6 arquivos novos
2. HARD-GATE presente em todas as 3 versões da Lex (pt-BR, es, en)
3. `lex-idempotency`, `codex-idempotency`, `codex-component-api`, `codex-component-jobs` × 3 idiomas atualizados com referência ao novo padrão
4. `framework/.directives.sample` tem `ahrena.idempotency.allowed_modules`
5. `framework/platforms.yaml` lista os 2 novos artefatos
6. Smoke tests api + jobs + composição passam
7. Starter snippets no codex compilam e passam tipo (mypy/tsc)
8. **Sem nova Lexis** que duplique `lex-idempotency` (o que existe é estendido, não substituído)
9. PR final passa HARD-GATE de `lex-pr-quality`