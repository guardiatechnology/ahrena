---
plan_id: "013"
title: "split-apollo-api-jobs-agents"
status: in-progress
agent: claude
issue: "guardiatechnology/ahrena#124"
created_at: "2026-05-07T22:00:00Z"
updated_at: "2026-05-12T17:30:00Z"
---

# Plano: Split do `warrior-apollo` em três especialistas (api, jobs, agents)

## Objetivo

Decompor o `warrior-apollo` monolítico ("Senior Python Engineer") em **três especialistas alinhados aos components do `bounded-context-template`**: `warrior-apollo-api` (FastAPI + FastMCP), `warrior-apollo-jobs` (AWS Lambda Powertools + Step Functions), `warrior-apollo-agents` (Strands + Bedrock). Manter `warrior-apollo` como **roteador retrocompatível** que detecta o component-alvo e delega ao especialista. Atualizar Athena (`lex-issue-driven`) para invocar diretamente o especialista quando o component está declarado em Phase 3. Reduzir o footprint de contexto carregado por chamada e melhorar precisão das decisões técnicas.

## Contexto

### Diagnóstico (consolidado do plan-011)

Apollo atual carrega em uma só persona conhecimento de **três stacks distintas**:

| Stack | Apollo precisa saber? | Carregamento atual | Carregamento alvo |
|---|:--:|---|---|
| FastAPI + Pydantic + httpx + FastMCP | quando feature é API HTTP | Sempre (eager) | Apenas quando component é `api` (lazy) |
| `aws-lambda-powertools` + `moto` + Step Functions input/output schemas | quando feature é worker async | Sempre (eager) | Apenas quando component é `jobs` (lazy) |
| `strands-agents` + boto3 Bedrock + SSE streaming + tool registry + memory layer | quando feature é agent | Sempre (eager) | Apenas quando component é `agents` (lazy) |
| SQLAlchemy + Alembic | cross-component (api e jobs) | Sempre | Cross — fica com Apollo roteador + cada especialista que toca DB |
| pytest + Hypothesis + mypy strict + Ruff | cross-component | Sempre | Cross — fica com todos |
| OpenTelemetry, structured logging | cross-component | Sempre | Cross — fica com todos |

**Métricas alvo** (a confirmar com baseline real medido no step 4):

- Apollo monolítico atual: **140 linhas** no `.md` + N Lexis Python eagerly loadable
- Cada especialista alvo: **< 80 linhas** + apenas Lexis Python específicas + Lexis cross
- Apollo roteador alvo: **< 60 linhas** + descrição da delegação

### Naming dos especialistas (decisão default — sujeita a override do Gate 1 do plan-011)

| Warrior | Caminho relativo (em `framework/{lang}/`) | Component |
|---|---|---|
| `warrior-apollo-api` | `engineering/backend/warriors/warrior-apollo-api.md` | `components/api/` |
| `warrior-apollo-jobs` | `engineering/backend/warriors/warrior-apollo-jobs.md` | `components/jobs/` |
| `warrior-apollo-agents` | `engineering/backend/warriors/warrior-apollo-agents.md` | `components/agents/` |
| `warrior-apollo` (preservado) | `engineering/backend/warriors/warrior-apollo.md` | router/coordenador |

**Override possível no Gate 1 do plan-011:** personas mitológicas distintas (e.g., `warrior-hermes-agents`, `warrior-talos-jobs` — Hephaestus já é frontend). Se o usuário escolher esse caminho, este plan-013 substitui os nomes mantendo o resto do escopo idêntico.

### Decisões fechadas (assumidas — confirmar no Gate 1)

| Decisão | Valor | Por quê |
|---|---|---|
| `warrior-apollo` permanece | Sim, como **router retrocompatível** | Cries existentes (`cry-python-implement`, `cry-python-review`) continuam apontando para Apollo; Apollo decide o especialista |
| Detecção de component | Apollo lê escopo: caminho de arquivos tocados, `pyproject.toml` próximo, declaração explícita do usuário | Heurística simples; usuário sempre pode forçar via `cry-python-implement-api`/`-jobs`/`-agents` (cries novas) |
| Cries novas | `cry-python-implement-api`, `cry-python-implement-jobs`, `cry-python-implement-agents` | Caminho explícito para quem já sabe o component; bypass do Apollo router |
| Cries existentes | `cry-python-implement`, `cry-python-review`, `cry-python-refactor`, `cry-python-debug` mantidos | Apontam para Apollo router (que despacha) — backward compat |
| Lexis Python existentes | Mantidas como **cross-component**; cada especialista as lista | Ainda valem para api+jobs+agents (typing, error handling, immutability, security, testing) |
| Lexis específicas a um component | Surgem aos poucos via PRs filhos; este plan **não cria nenhuma nova Lexis** | Evita inflação prematura; só cria Lexis quando uma regra de fato é específica e bloqueante |
| Katas existentes | `kata-python-implement`, `kata-python-review`, `kata-python-refactor`, `kata-python-debug` ganham preâmbulo "Componente alvo (api / jobs / agents)" e seção "Padrões específicos por component" | Resolução: kata tem ponteiro de component; warriors especialistas referenciam o kata e o codex-component-{X} simultaneamente |
| Apollo router pode delegar para múltiplos especialistas no mesmo task? | Sim — feature transversal (e.g., publica evento via job e expõe API) pode requerer dois especialistas; Apollo coordena | Cobre o caso real de feature multi-component |
| Athena (Phase 3 / Phase 4) | Quando `03-architecture.md` declara `component: api`/`jobs`/`agents` na tabela de componentes, Athena invoca o especialista direto | Pula um nível de indireção quando o component é claro |
| Idiomas | 3 idiomas (pt-BR canonical + es + en) por warrior | `lex-framework-language` |
| Registro em `platforms.yaml` | Sim, 1 entry por especialista em `cursor.agents` e `claude-code.agents` | Padrão dos warriors existentes |

## Escopo

### Artefatos a criar (3 idiomas cada)

| Pilar | Caminho | Conteúdo principal |
|---|---|---|
| Warrior | `engineering/backend/warriors/warrior-apollo-api.md` | Identity (Apollo-API); Mission (FastAPI + MCP correctness); Lexis carregadas (cross-Python: typing, testing, security, error-handling, immutability, result-type, error-object); Codex consultados (codex-component-api, codex-python-fastapi, codex-restful-apis, codex-oas-structure, codex-feature-design-docs, codex-python-sqlalchemy quando há DB); Katas (kata-python-implement, kata-python-review, kata-python-refactor, kata-python-debug — com flag `component=api`); persona idêntica ao Apollo, escopo restrito a HTTP/MCP request-response |
| Warrior | `engineering/backend/warriors/warrior-apollo-jobs.md` | Identity (Apollo-Jobs); Mission (idempotent serverless tasks); Lexis carregadas (cross-Python + lex-idempotency); Codex consultados (codex-component-jobs, codex-aws-services para Step Functions, codex-python-error-handling); Katas idem com `component=jobs`; persona Apollo focada em handler signatures Lambda, Powertools, retry semantics, idempotency keys |
| Warrior | `engineering/backend/warriors/warrior-apollo-agents.md` | Identity (Apollo-Agents); Mission (LLM-using agents with deterministic guardrails); Lexis carregadas (cross-Python + lex-mcp); Codex consultados (codex-component-agents, codex-python-observability — fundamental para tracing tool calls); Katas idem com `component=agents`; persona Apollo focada em orchestrator+specialists, tool registry, memory layer, prompt boundaries, SSE streaming |
| Cry | `_foundation/contributing/cries/cry-python-implement-api.md` | Atalho para `warrior-apollo-api` |
| Cry | `_foundation/contributing/cries/cry-python-implement-jobs.md` | Atalho para `warrior-apollo-jobs` |
| Cry | `_foundation/contributing/cries/cry-python-implement-agents.md` | Atalho para `warrior-apollo-agents` |

### Atualizações em artefatos existentes (3 idiomas)

| Arquivo | Mudança |
|---|---|
| `warrior-apollo.md` | Reescrita: passa de "Senior Python Engineer" implementador para **"Python coordinator / router"**. Identity preservada (mesma persona); Mission ajustada para "decide qual especialista (api / jobs / agents) implementa, ou coordena especialistas múltiplos quando a feature é transversal"; Lexis carregadas reduz a cross-Python apenas; Codex passa a referenciar `codex-component-architecture`. Encolhe para < 60 linhas |
| `kata-python-implement.md` | Adicionar bloco "Component target" no início (resolve `component=api/jobs/agents` antes de prosseguir); seção "Padrões específicos por component" remete aos `codex-component-{api,jobs,agents}` |
| `kata-python-review.md` | Idem — reviewer aplica checks específicos do component declarado |
| `kata-python-refactor.md` | Idem |
| `kata-python-debug.md` | Idem |
| `lex-issue-driven.md` (Phase 3 e Phase 4) | Phase 3 tabela de componentes ganha coluna `component: api/jobs/agents/ui/deployment`; Phase 4 delegation: quando `component` está declarado e é `api/jobs/agents`, Athena invoca o especialista direto (`warrior-apollo-api/jobs/agents`); quando feature é transversal ou ambígua, invoca `warrior-apollo` (router) |
| `framework/platforms.yaml` | 3 entries novas em `cursor.agents` e `claude-code.agents` (uma por especialista); 3 entries em `cursor.commands` e `claude-code.commands` (uma por cry novo); atualizar entry de `warrior-apollo` se descrição mudar |
| `framework/.directives.sample` | Sem mudança — não há nova diretiva |

### Métricas a coletar (antes/depois)

Reusar `kata-pr-cost-stamp` (plan-007) se mergeado; senão, medir manualmente via `ccusage`:

- Tokens consumidos para: implementar feature `api`-only → comparar Apollo monolítico vs Apollo-API
- Tokens consumidos para: implementar feature `jobs`-only → comparar
- Tokens consumidos para: implementar feature `agents`-only → comparar
- Linhas no warrior `.md` antes/depois

Resultado vai para o body da PR final (seção "Cost & footprint impact").

## Fora de escopo

- **Criar Lexis novas específicas a um component** — primeira iteração reusa o que existe; novas Lexis emergem em PRs futuros quando uma regra concreta provar ser específica.
- **Refactor dos codex Python existentes** (`codex-python-fastapi`, `codex-python-sqlalchemy`, etc.) — apenas referenciados pelos novos warriors; permanecem onde estão.
- **Mover warriors existentes** (Hephaestus, Iris, Atlas, etc.) — não tocamos. Plan-014 audita os demais.
- **Criar warriors para `ui/` e `deployment/`** — `warrior-hephaestus` já cobre `ui` (revisar em plan-014); `warrior-atlas` já cobre `deployment`. Sem warriors novos fora do trio Apollo split.
- **Mudar a estrutura de cries existentes** (manter `cry-python-implement` apontando para Apollo router).
- **Tocar `lex-pr-quality`, `kata-quality-gate`, `kata-contributing-pr`** — fluxo de PR não muda.

## Steps

- [ ] 1. Confirmar plan-011 com Gate 1 aprovado **e** decisões de naming travadas
- [ ] 2. Confirmar plan-012 mergeado (codex-component-architecture e codex-component-{api,jobs,agents} disponíveis)
- [ ] 3. Abrir issue com template `feature-request`, Issue Type `Feature`, label `feature request ➕`, título "feat(framework): split warrior-apollo into api, jobs, agents specialists aligned with bounded-context-template components"
- [ ] 4. **Baseline measurement:** medir tokens de uma sessão Claude Code reproduzindo "implementar endpoint Y" com Apollo atual em projeto sandbox; registrar baseline no body da issue
- [ ] 5. Criar branch `feat/{N}-split-apollo-component-specialists` e worktree
- [ ] 6. Atualizar status deste plan para `in-progress`
- [ ] 7. Redigir `warrior-apollo-api.md` em pt-BR — usar `templates/warrior-sample.md`; cross-reference obrigatório a `codex-component-api`
- [ ] 8. Redigir `warrior-apollo-jobs.md` em pt-BR — cross-reference a `codex-component-jobs` e `lex-idempotency`
- [ ] 9. Redigir `warrior-apollo-agents.md` em pt-BR — cross-reference a `codex-component-agents` e `lex-mcp`
- [ ] 10. Reescrever `warrior-apollo.md` em pt-BR como router (< 60 linhas); preservar Identity/persona; documentar regra de delegação
- [ ] 11. Criar `cry-python-implement-api.md`, `cry-python-implement-jobs.md`, `cry-python-implement-agents.md` em pt-BR (atalhos curtos, padrão dos cries existentes)
- [ ] 12. Atualizar `kata-python-implement.md` em pt-BR com bloco "Component target" e seção "Padrões específicos"
- [ ] 13. Idem para `kata-python-review.md`, `kata-python-refactor.md`, `kata-python-debug.md` em pt-BR
- [ ] 14. Atualizar `lex-issue-driven.md` em pt-BR (Phase 3 ganha coluna component; Phase 4 delegation rule)
- [ ] 15. Replicar todos os artefatos novos e modificados para `es` e `en`
- [ ] 16. Atualizar `framework/platforms.yaml`: 3 entries em `cursor.agents`/`claude-code.agents` (especialistas) + 3 em `cursor.commands`/`claude-code.commands` (cries) + revisão da entry `warrior-apollo` (descrição como router)
- [ ] 17. Rodar `python3 scripts/install.py --self --target . --platform claude-code` e idem `cursor`
- [ ] 18. **Smoke test (api):** subir uma sessão Claude Code num projeto sandbox; invocar `cry-python-implement-api` com feature trivial (e.g., "add GET /health-rich endpoint"); verificar que apenas Lexis/Codex de api+cross são carregadas; medir tokens
- [ ] 19. **Smoke test (jobs):** invocar `cry-python-implement-jobs` ("add Step Functions task that processes refund event"); medir tokens
- [ ] 20. **Smoke test (agents):** invocar `cry-python-implement-agents` ("add specialist for tax classification"); medir tokens
- [ ] 21. **Smoke test (router):** invocar `cry-python-implement` (sem componente declarado) com feature ambígua; verificar que Apollo pergunta o component antes de prosseguir
- [ ] 22. **Smoke test (Athena):** rodar `cry-implement-issue` num issue sandbox onde `03-architecture.md` declara `component: api`; verificar que Athena pula direto para `warrior-apollo-api` na Phase 4
- [ ] 23. **Regressão:** rodar `cry-python-implement` com feature como antes — confirmar que Apollo router responde (zero quebra) e que ele consulta o usuário sobre o component
- [ ] 24. Coletar métricas finais; preencher seção "Cost & footprint impact" no body da PR
- [ ] 25. Commits atômicos por artefato (subject inglês + body bilíngue, assinados); tamanho controlado para ficar < `size/XL` ideal
- [ ] 26. Push e abrir PR via `kata-contributing-pr`; PR carrega stamp de custo se plan-007 estiver mergeado
- [ ] 27. Após merge: arquivar plan e remover worktree

## Dependências

- **Plan-011 com Gate 1 aprovado** — naming, mapeamento e decisões travadas (bloqueante)
- **Plan-012 mergeado** — codex-component-{api,jobs,agents} disponíveis para os warriors referenciarem (bloqueante)
- Plan-002, Plan-003 (lazy-load via `paths:` em `platforms.yaml`) já mergeados
- **Independente** de plan-006 (Athena stacked PRs) — Athena delegation rule deste plan-013 é aditiva e não conflita
- **Sinérgico** com plan-007 (token cost stamp) — se ambos mergeados, a PR final mostra a economia mensurada
- `templates/warrior-sample.md`, `templates/cry-sample.md` presentes
- `bounded-context-template` PR #1 mergeado (referência canônica para padrões dos especialistas)

## Riscos

- **Regressão silenciosa em chamadas existentes a Apollo monolítico.** Mitigação: step 23 (smoke test de regressão); Apollo router preserva interface pública via cries existentes.
- **Apollo router escolhe component errado.** Mitigação: heurística é conservadora — em ambiguidade, **pergunta ao usuário** ao invés de chutar; cries explícitas (`cry-python-implement-api`) bypassam o router.
- **Tokens não caem na proporção esperada.** Mitigação: baseline no step 4 + medições nos steps 18-20 dão dados reais; se ganho < 30%, plan ainda agrega valor por **clareza de responsabilidade** e **precisão técnica**, mas registra o resultado honestamente na PR e revisita lazy-load (paths) para extrair mais.
- **Conflito com plan-006 (Athena stacked PRs)** quando Phase 3 ganhar coluna `component`. Mitigação: ambos editam `lex-issue-driven` Phase 3; merger atento — coluna `component` é aditiva e não compete com bloco `stack:`.
- **Tradução para 3 idiomas com volume grande** (3 warriors + 3 cries + 4 katas + 1 lex × 2 idiomas extras). Mitigação: PR pode ser stacked usando o framework recém-mergeado (plan-004/005) — camada 1: pt-BR + platforms.yaml; camada 2: es; camada 3: en. Reduz risco de revisão única gigante.
- **Athena não detectar `component:` em `03-architecture.md` corretamente.** Mitigação: smoke test step 22 com issue real; spec do parsing fica explícita no novo trecho de `lex-issue-driven`.
- **Naming dos warriors com hífen duplo** (`warrior-apollo-api`) é incomum. Mitigação: Lexis `lex-naming` permite kebab-case com múltiplos hífens; Cursor/Claude Code aceitam. Verificar no smoke test.
- **Conflito do PR com plan-014 (audit dos demais warriors)** se rodam em paralelo. Mitigação: plan-014 só começa após plan-013 mergeado.

## Verificação

1. **Estrutura:** 3 warriors novos × 3 idiomas + 3 cries novos × 3 idiomas + 1 warrior reescrito × 3 idiomas + 4 katas atualizados × 3 idiomas + 1 lex atualizada × 3 idiomas = **42 arquivos** tocados em `framework/`
2. **`platforms.yaml`:** 3 entries de warriors novos + 3 entries de cries novos + entry do warrior-apollo revisada
3. **Token footprint medido:** redução ≥ 30% no contexto carregado por sessão `cry-python-implement-api` (e equivalentes) vs Apollo monolítico baseline; se < 30%, registrar na PR e revisitar
4. **Linhas por warrior:** cada especialista < 80 linhas; Apollo router < 60 linhas
5. **Backward compat:** `cry-python-implement` continua funcionando — sem component declarado, Apollo router pergunta; com component declarado pelo usuário ou contexto, despacha para o especialista
6. **Smoke tests passam:** api, jobs, agents, router, Athena delegation, regressão (steps 18-23)
7. **`kata-artifact-self-review`** rodado em cada warrior novo + warrior reescrito + cada cry novo
8. **PR final:** body referencia `Closes #{N}`, plan-013, e plan-011 (decisões); inclui seção "Cost & footprint impact" com baseline + medidos; HARD-GATE de `lex-pr-quality` atendido
9. **Sem nova Lexis** criada neste plan (verificação contra inflação prematura)
10. **Sem alteração** em: lex-pr-quality, kata-quality-gate, kata-contributing-pr, lex-template-usage, lex-platforms-rules, lex-naming, framework/.directives.sample