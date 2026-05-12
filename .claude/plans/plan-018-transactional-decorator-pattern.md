---
plan_id: "018"
title: "transactional-decorator-pattern"
status: pending
agent: claude
issue: "TBD (a abrir antes da branch — lex-issue-first)"
created_at: "2026-05-07T22:30:00Z"
updated_at: "2026-05-07T22:30:00Z"
---

# Plano: Padrão de transação via decorator (`@transactional`) com unit-of-work

## Objetivo

Codificar como Lex e Codex o padrão único para fronteiras de transação em código que toca SQLAlchemy (apollo-api e apollo-jobs). Decorator `@transactional(isolation="...", on_nested="join")` envolvendo use cases / handlers, garantindo: (a) commit atômico ao final; (b) rollback automático em qualquer exception; (c) comportamento determinístico para nested calls (default `join` na transação corrente; opção `nested` para savepoint); (d) injeção implícita do `Session`/`AsyncSession` corrente para repositories. Banir `session.commit()`/`session.rollback()` manual no corpo de funções de aplicação. Aplicação cross-component nos casos onde há DB.

## Contexto

### Estado atual

- `codex-python-sqlalchemy` cobre patterns de SQLAlchemy 2.0 async (sessions, repository pattern, Alembic) **sem prescrever fronteira de transação**
- `codex-python-architecture` (Clean Architecture) implica que use case é a fronteira natural, mas não codifica
- Hoje, cada feature decide: alguns usam `session.begin()` em context manager dentro do use case; outros chamam `commit()` no router; alguns deixam autocommit do FastAPI dependency
- **Resultado:** inconsistência → bugs sutis (commit em meio de saga, rollback que não cobre todos os steps, savepoint mal-aninhado)
- Plan-013 (Apollo split) torna isso urgente: api e jobs dividem a mesma DB layer; sem padrão único, especialistas vão divergir

### Por que decorator (não context manager direto)

| Padrão | Prós | Contras |
|---|---|---|
| `@transactional` ✅ | Fronteira declarativa; combina com `@logged`/`@measured`/`@idempotent`; testável; lint pode validar | Requer DI da session (não trivial em FastAPI mas resolvido com `ContextVar` ou `request.state`) |
| `with session.begin():` no corpo | Explícito | Mistura preocupações de transação com lógica; difícil de mover; cada caller copia o boilerplate |
| Autocommit per-request middleware | Simples | Granularidade errada — request pode ter múltiplas transações lógicas |
| Saga / event-driven | Necessário para distributed | Fora do escopo deste plan (DB local) |

### Decisões fechadas

| Decisão | Valor | Por quê |
|---|---|---|
| Padrão obrigatório | `@transactional(...)` em use cases que mutam DB | Único contrato para fronteira |
| Implementação Python | Wrapper que (a) abre `session.begin()`, (b) injeta session via `ContextVar`, (c) commit on success, rollback on exception | SQLAlchemy 2.0 async-friendly |
| Nested behavior | Default `on_nested="join"` (entra na transação corrente, não cria nova) | Comportamento óbvio para use case que chama outro use case; savepoint vira `on_nested="savepoint"` opt-in |
| Read-only flag | `@transactional(read_only=True)` para queries longas; abre transação SET TRANSACTION READ ONLY | Cobre o caso "read consistency em listagem grande" sem requerer locks |
| Composição com outros decorators | Stack: `@measured` → `@logged` → `@idempotent` → `@resilient` → `@transactional` → função | `@transactional` é o mais interno (mais perto da função); `@resilient` está fora porque retry deve abrir nova transação |
| Repositories acessam session via `ContextVar` | `current_session()` lookup | Evita passar `session` em cada chamada; mantém repositories agnósticos |
| Allow-list | `ahrena.transaction.allowed_modules` em `pyproject.toml`; `session.commit()`/`session.rollback()` manual fora da allow-list proibido | Mesmo modelo de logging/metrics/idempotency/resilience |
| HARD-GATE | Sim | Pattern bloqueante |
| Aplicação | apollo-api (use cases) + apollo-jobs (handlers de Lambda que tocam DB) | apollo-agents geralmente não toca DB transacional; codex marca como opcional |
| Idiomas | 3 | `lex-framework-language` |

## Escopo

### Artefatos a criar (3 idiomas)

| Pilar | Caminho relativo | Conteúdo principal |
|---|---|---|
| Lexis | `engineering/backend/lexis/lex-transactional-decorator.md` | Lei: `@transactional` é única fronteira aceita; commit/rollback manual proibido fora allow-list; HARD-GATE |
| Codex | `engineering/backend/codex/codex-transactional-decorator.md` | Signature; opções (`isolation`, `on_nested`, `read_only`, `propagation`); SQLAlchemy 2.0 async patterns; injeção via ContextVar; integração com FastAPI dependency injection; testes (commit em sucesso; rollback em exception; nested join vs savepoint; read-only não permite mutation); referência a `codex-python-sqlalchemy` |

### Atualizações em artefatos existentes (3 idiomas)

| Arquivo | Mudança |
|---|---|
| `codex-python-sqlalchemy.md` | Acrescentar seção "Transaction boundary" remetendo para o novo codex; mover qualquer guidance existente sobre commit/rollback para lá |
| `codex-python-architecture.md` | Acrescentar nota: "Use case é a fronteira de transação canônica via `@transactional`" |
| `engineering/architecture/codex/codex-component-api.md` (criado em plan-012) | Acrescentar `@transactional` em "Key Patterns" para use cases que mutam |
| `engineering/architecture/codex/codex-component-jobs.md` (criado em plan-012) | Idem |
| `framework/.directives.sample` | Adicionar bloco comentado `ahrena.transaction.allowed_modules` |
| `framework/platforms.yaml` | Registrar Lex e Codex novos |

## Fora de escopo

- **Distributed transactions / saga pattern** — fora; este plan cobre só DB local
- **Outbox pattern** (publicar evento como parte da transação) — pode entrar em plan futuro; fora aqui
- **TypeScript / Node** — sem padrão equivalente neste plan; SQLAlchemy é Python-only. Se houver demanda futura para Node + Prisma/Drizzle, abre plan próprio
- **Read replicas routing** — fora; `read_only=True` apenas marca semântica, não roteia automaticamente
- **Refactor de código existente** — adoção gradual via novos use cases e refactors naturais
- **MongoDB / DynamoDB transactions** — fora; este plan é SQLAlchemy-specific (PostgreSQL/MySQL)

## Steps

- [ ] 1. Confirmar plan-012 mergeado (codex-component-{api,jobs} disponíveis)
- [ ] 2. Abrir issue com template `feature-request`, Issue Type `Feature`
- [ ] 3. Criar branch `feat/{N}-transactional-decorator-pattern` e worktree
- [ ] 4. Atualizar status deste plan para `in-progress`
- [ ] 5. Redigir `lex-transactional-decorator.md` em pt-BR (com HARD-GATE)
- [ ] 6. Redigir `codex-transactional-decorator.md` em pt-BR — incluir starter snippet Python (~50 linhas: ContextVar setup, decorator, FastAPI dependency, repository helper)
- [ ] 7. Atualizar `codex-python-sqlalchemy.md` em pt-BR (mover guidance de commit/rollback para o novo codex)
- [ ] 8. Atualizar `codex-python-architecture.md`, `codex-component-api.md`, `codex-component-jobs.md` em pt-BR
- [ ] 9. Adicionar bloco `ahrena.transaction.allowed_modules` em `framework/.directives.sample`
- [ ] 10. Atualizar `framework/platforms.yaml`
- [ ] 11. Traduzir Lex, Codex e atualizações para `es` e `en`
- [ ] 12. Rodar `python3 scripts/install.py --self --target . --platform claude-code` e `cursor`
- [ ] 13. **Smoke test commit**: use case sandbox que cria 2 entidades; aplicar `@transactional`; verificar que ambas existem após sucesso
- [ ] 14. **Smoke test rollback**: use case que cria entidade A e depois lança exception; verificar que A não está persistida (rollback automático)
- [ ] 15. **Smoke test nested join**: use case A chama use case B (ambos `@transactional`); verificar que B opera na mesma transação de A; rollback de B reverte A inteiro
- [ ] 16. **Smoke test nested savepoint**: use case A chama use case B com `@transactional(on_nested="savepoint")`; verificar que rollback de B preserva A
- [ ] 17. **Smoke test read-only**: aplicar `@transactional(read_only=True)`; tentativa de mutation dentro deve falhar com erro descritivo
- [ ] 18. **Smoke test composição**: stack `@measured` → `@logged` → `@idempotent` → `@resilient` → `@transactional` → função; verificar que retry de `@resilient` abre **nova** transação por attempt (não reutiliza); verificar que `@idempotent` cacheia o resultado pós-commit
- [ ] 19. Rodar `kata-artifact-self-review` em Lex e Codex novos
- [ ] 20. Commits atômicos; push; abrir PR via `kata-contributing-pr`
- [ ] 21. Após merge: arquivar plan e remover worktree

## Dependências

- **Plan-012 mergeado** — codex-component-{api,jobs} (bloqueante)
- `codex-python-sqlalchemy`, `codex-python-architecture` existentes — base estendida
- `lex-hard-gate-pattern` — para HARD-GATE
- **Independente** de plans 011, 013-017, 019-021
- **Sinérgico** com plan-013 (Apollo specialists), plan-016 (idempotency), plan-017 (resilience) — composição decorator é tema de cada um dos codex; cada plan documenta a ordem canônica do seu lado

## Riscos

- **Injeção via ContextVar quebra em código sync ou em workers que não usam asyncio.** Mitigação: codex documenta requirements (asyncio + AsyncSession); fornece variante sync caso projeto não seja 100% async (raro)
- **Nested transactions com savepoint têm caveats por DB.** Mitigação: codex tabula behavior por engine (PostgreSQL: full support; MySQL: limited; SQLite: nested ok in test mode); recomenda PG
- **Read-only flag depende de SET TRANSACTION READ ONLY** que nem todo dialect aceita igual. Mitigação: codex documenta dialects suportados; fallback para "soft" (não emite SQL especial, só doc) quando dialect não suporta
- **Conflito com FastAPI dependency injection** quando use case é chamado diretamente (não via route). Mitigação: codex tem 2 paths — via FastAPI dep e via context manager direto; ambos terminam configurando ContextVar
- **Composição com `@idempotent` pode cachear resultado de transação que foi rolled back.** Mitigação: ordem canônica é `@idempotent` **fora** de `@transactional` — só cacheia após commit; smoke test 18 valida
- **Lex prescritiva pode não caber em projetos read-heavy** que raramente mutam. Mitigação: read paths não precisam de `@transactional` (DB nativo já é consistente para single-statement reads); Lex aplica a use cases que **mutam**

## Verificação

1. `lex-transactional-decorator` × 3 idiomas + `codex-transactional-decorator` × 3 idiomas = 6 arquivos novos
2. HARD-GATE presente nas 3 versões
3. `codex-python-sqlalchemy`, `codex-python-architecture`, `codex-component-{api,jobs}` × 3 idiomas atualizados
4. `framework/.directives.sample` tem `ahrena.transaction.allowed_modules`
5. `framework/platforms.yaml` lista os 2 novos artefatos
6. 6 smoke tests passam (commit, rollback, join, savepoint, read-only, composição)
7. Starter snippet compila (mypy strict)
8. **Sem alteração** em demais decorators (logging, metrics, idempotency, resilience)
9. PR final passa HARD-GATE de `lex-pr-quality`
