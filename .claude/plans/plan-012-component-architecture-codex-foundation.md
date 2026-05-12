---
plan_id: "012"
title: "component-architecture-codex-foundation"
status: pending
agent: claude
issue: "TBD (a abrir antes da branch — lex-issue-first)"
created_at: "2026-05-07T22:00:00Z"
updated_at: "2026-05-07T22:00:00Z"
---

# Plano: Codex base de arquitetura por Component (api, agents, jobs, ui, deployment)

## Objetivo

Codificar no framework Ahrena a **arquitetura por components** estabelecida no `bounded-context-template`. Entregar um codex-mãe (`codex-component-architecture`) que define o conceito e as fronteiras, mais 5 codex-filhos especializados (`codex-component-api`, `codex-component-agents`, `codex-component-jobs`, `codex-component-ui`, `codex-component-deployment`). Plan **somente codex** — não cria warriors, não modifica katas, não muda diretivas. Sai como fundação para o plan-013 (split do Apollo) consumir.

## Contexto

### Por que codex e não Lexis

- A arquitetura por component é **convenção forte do monorepo Guardia**, não lei universal de toda Ahrena. Outros projetos (skill projects, ahrena-self) podem ter outras estruturas.
- **Codex informa**, **Lexis obriga.** Não queremos forçar `components/` em todo projeto Ahrena — queremos que projetos Guardia consultem o codex e o sigam por convenção, com ADR caso desviem.
- Se no futuro emergir necessidade de obrigatoriedade (e.g., na linha base do `guardia-platform`), abre-se Lexis em plan separado citando este codex.

### Como o codex existente já trata arquitetura (e por que precisa ser reorganizado)

Codex Python atuais e seu escopo:

| Codex existente | Escopo declarado | Problema com o split por component |
|---|---|---|
| `codex-python-architecture` | Clean Architecture (ports & adapters), camadas, dependency direction | Genérico — não distingue api/agents/jobs |
| `codex-python-fastapi` | Padrões FastAPI (routers, dependencies, middleware) | **Específico de API** — naturalmente cabe sob `codex-component-api` |
| `codex-python-sqlalchemy` | SQLAlchemy 2.0 async, repository pattern, Alembic | Aplica a api e jobs (e às vezes agents memory) — fica como cross-cutting |
| `codex-python-testing` | pytest, fixtures, async testing | Cross-cutting — todos os components Python testam com pytest |
| `codex-python-observability` | OpenTelemetry setup, structured logging | Cross-cutting |
| `codex-python-tooling` | Ruff, mypy, pre-commit, deps | Cross-cutting |
| `codex-python-logging` | Loguru + decorator pattern | Cross-cutting |

**Estratégia adotada:** não mexer nos codex Python cross-cutting; criar uma **camada acima** (component-architecture + per-component) que referencia os codex Python existentes como "consultar para detalhes Python". Os codex per-component focam em **o que é específico daquele component** (e.g., FastMCP server pattern só importa para api; Strands tools/specialists só importa para agents; Lambda handler signature só importa para jobs).

### Decisões fechadas

| Decisão | Valor | Justificativa |
|---|---|---|
| Tipo de artefato | Codex (não Lexis) | Convenção, não obrigação universal |
| Localização | `framework/{lang}/engineering/architecture/codex/codex-component-*.md` | Novo subclade `architecture` sob `engineering` (não existe ainda) — cabem aqui artefatos transversais a backend/frontend/mobile |
| Alternativa rejeitada | Espalhar (api em `engineering/backend/`, agents em `engineering/ai/`, jobs em `engineering/backend/`, ui em `engineering/frontend/`) | Quebra a unidade conceitual — leitor precisa pular entre 4 subclades para entender uma decisão arquitetural |
| Codex-mãe vs 5 filhos isolados | **Codex-mãe + 5 filhos** | Mãe define o que é "component", fronteiras, mapeamento para `bounded-context-template`; filhos detalham cada um. Permite leitura por demanda |
| Idiomas | Os 6 codex em pt-BR (canonical) + es + en, conforme `language.i18n` | Sem exceção de `lex-framework-language` |
| Registro em `platforms.yaml` | Sim — `cursor.rules` + `claude-code.docs` para cada um, com `paths:` para lazy-load quando aplicável | Mantém o padrão dos demais codex |

## Escopo

### Artefatos a criar (3 idiomas cada — pt-BR canonical)

| Codex | Caminho relativo (em `framework/{lang}/`) | Conteúdo principal |
|---|---|---|
| `codex-component-architecture` | `engineering/architecture/codex/codex-component-architecture.md` | Conceito de component; fronteiras (1 component = 1 dep manifest = 1 test suite = 1 deploy unit); mapeamento canônico do `bounded-context-template`; tabela "tipo de feature → component candidato"; regras de coexistência (api+agents podem chamar a mesma DB; jobs nunca chama api síncrona) |
| `codex-component-api` | `engineering/architecture/codex/codex-component-api.md` | Stack: FastAPI + FastMCP + uvicorn + httpx (test); estrutura interna (adapters/inbound, adapters/outbound, application/ports, application/use_cases, domain, infra); MCP endpoint mount em `/mcp`; OpenTelemetry-FastAPI instrumentation; dependency injection patterns; referência cruzada para `codex-python-fastapi`, `codex-restful-apis`, `codex-oas-structure`, `codex-feature-design-docs` |
| `codex-component-agents` | `engineering/architecture/codex/codex-component-agents.md` | Stack: strands-agents + strands-agents-tools + boto3 (Bedrock) + sse-starlette (streaming); estrutura interna (`model.py`, `memory.py`, `orchestrator.py`, `specialists/`, `tools/`, `infra/bedrock.py`); padrão "orchestrator + specialists" do template; tools determinísticas vs ML tools; SSE para streaming de raciocínio; referência cruzada para `codex-python-architecture` (Clean Architecture aplicada), `codex-python-observability` (OTel para tracing de tool calls) |
| `codex-component-jobs` | `engineering/architecture/codex/codex-component-jobs.md` | Stack: aws-lambda-powertools + boto3 + Pydantic (sem FastAPI); estrutura interna (`tasks/`, `middleware.py`, `errors.py`, `infra/aws.py`); idempotência via Powertools; integração com Step Functions (input/output schema); test com `moto[stepfunctions,lambda]`; referência cruzada para `lex-idempotency`, `codex-python-error-handling` (Result/Error patterns), `codex-aws-services` |
| `codex-component-ui` | `engineering/architecture/codex/codex-component-ui.md` | Stack: Next.js 15 + Tailwind CSS + tsup (build de NPM package) + Storybook + Cypress (e2e) + Jest (unit); estrutura interna (`src/widgets/`, `src/shared/`, `src/app/api/{invoke,stream}/`); modo dual (sandbox app dev + library export); referência cruzada para `codex-frontend-architecture`, `codex-design-system`, `lex-design-system-library`, `lex-frontend-accessibility` |
| `codex-component-deployment` | `engineering/architecture/codex/codex-component-deployment.md` | Stack: AWS CDK Python; estrutura `app.py + stacks/`; convenções de tagging por component; padrão de naming `{context}-{component}-{env}`; referência cruzada para `codex-aws-services`, `codex-aws-well-architected`, `lex-aws-iac`, `lex-aws-cost`, `lex-aws-security` |

### Estrutura de cada codex per-component (template comum)

```markdown
# Codex: Component {Name} — {one-line role}

> **Prefix:** codex- | **Type:** Reference Manual | **Scope:** ...

## Overview
2-4 sentences: what this component does and what it does NOT do.

## Canonical Stack
Table: dependency, version constraint, role.

## Internal Structure
ASCII tree of `components/{name}/src/...` from bounded-context-template.

## Key Patterns
3-7 patterns specific to this component (e.g., for api: hexagonal, OAS-first, idempotency-key middleware; for agents: orchestrator+specialists, tool registry, memory layer).

## What This Component Owns
Bullet list of responsibilities exclusive to this component.

## What This Component Does NOT Own
Bullet list with explicit redirects (e.g., "Domain modeling → see codex-component-{N} or warrior-theseus").

## Cross-Cutting References
Table linking each cross-cutting Lexis/Codex consumed (logging, observability, testing, error-handling, typing).

## Anti-Patterns
3-5 specific anti-patterns + correction.

## References
Lexis, Codex, external (bounded-context-template paths).
```

### Atualizações em artefatos existentes (3 idiomas)

| Arquivo | Mudança |
|---|---|
| `framework/{lang}/engineering/backend/codex/codex-python-architecture.md` | Acrescentar nota no início: "Para arquitetura **por component** do bounded-context Guardia, consulte `codex-component-architecture` antes deste documento. Este codex permanece como referência **cross-component** das camadas Clean Architecture aplicadas a Python" |
| `framework/{lang}/engineering/backend/codex/codex-python-fastapi.md` | Idem, redirecionando para `codex-component-api` para o quadro mais amplo |
| `framework/{lang}/engineering/frontend/codex/codex-frontend-architecture.md` | Idem, redirecionando para `codex-component-ui` |
| `framework/platforms.yaml` | Adicionar 6 entries em `cursor.rules` e `claude-code.docs` (uma para cada novo codex). `paths:` lazy-load: `codex-component-api` → `["components/api/**"]`; `codex-component-agents` → `["components/agents/**"]`; `codex-component-jobs` → `["components/jobs/**"]`; `codex-component-ui` → `["components/ui/**"]`; `codex-component-deployment` → `["deployment/**", "infra/**"]`; `codex-component-architecture` → `alwaysApply: false` sem paths (carrega por descrição) |
| `framework/.directives.sample` | Sem alteração — codex não introduz nova diretiva |
| `lex-platforms-rules` | Sem alteração — `lex-platforms-rules` já obriga registro de todo codex em `platforms.yaml`; cumprimos |

### Subclade `engineering/architecture/`

Não existe ainda — será criado por este plan. Validação:

- `naming.reserved_clades` em `.directives` não inclui `architecture` — **OK criar**
- `engineering/` é clade existente; novo subclade respeita o padrão
- `lex-naming` e `lex-framework-language` continuam atendidos

## Fora de escopo

- **Criar warriors** que consomem estes codex — fica para plan-013 (Apollo split) e plan-014 (audit dos demais).
- **Modificar Lexis Python existentes** (`lex-python-typing`, `lex-python-error-handling`, etc.) — continuam aplicando cross-component; nenhum split de Lexis aqui.
- **Renomear ou mover codex Python existentes** — apenas adicionar nota de redirect; preservar URLs e references.
- **Criar codex específico de "agentes" como Pilar do framework** — agents aqui é **component** (módulo de implementação), não Pilar. Pilares do framework continuam sendo Lexis/Codex/Katas/Warriors/Cries.
- **Documentar `docs/`, `scripts/`, `.github/`** do bounded-context-template — só os 5 components produtivos + deployment. `docs/` já está coberto por `codex-feature-design-docs`.

## Steps

- [ ] 1. Confirmar plan-011 com Gate 1 aprovado e topology doc publicado em `docs/internal/warrior-topology-2026.md`
- [ ] 2. Abrir issue com template `feature-request`, Issue Type `Feature`, label `documentation 📃`, título "feat(framework): codex foundation for component-based architecture (api, agents, jobs, ui, deployment)"
- [ ] 3. Criar branch `feat/{N}-component-architecture-codex` e worktree `.worktrees/{N}-component-architecture-codex/`
- [ ] 4. Atualizar status deste plan para `in-progress`
- [ ] 5. Criar diretório `framework/pt-BR/engineering/architecture/codex/` (idem es, en)
- [ ] 6. Redigir `codex-component-architecture` em pt-BR (canonical) — usar `templates/codex-sample.md` como base
- [ ] 7. Redigir `codex-component-api` em pt-BR consultando `bounded-context-template/components/api/` e os codex Python existentes
- [ ] 8. Redigir `codex-component-agents` em pt-BR consultando `bounded-context-template/components/agents/example/`
- [ ] 9. Redigir `codex-component-jobs` em pt-BR consultando `bounded-context-template/components/jobs/example/`
- [ ] 10. Redigir `codex-component-ui` em pt-BR consultando `bounded-context-template/components/ui/`
- [ ] 11. Redigir `codex-component-deployment` em pt-BR consultando `bounded-context-template/deployment/`
- [ ] 12. Acrescentar nota de redirect em `codex-python-architecture`, `codex-python-fastapi`, `codex-frontend-architecture` (pt-BR)
- [ ] 13. Atualizar `framework/platforms.yaml` com as 6 entries novas + `paths:` lazy-load
- [ ] 14. Traduzir os 6 codex novos para `es`
- [ ] 15. Traduzir os 6 codex novos para `en`
- [ ] 16. Replicar as notas de redirect em `es` e `en`
- [ ] 17. Rodar `python3 scripts/install.py --self --target . --platform claude-code` e idem para `cursor`
- [ ] 18. Validar visualmente que `.cursor/rules/.../codex-component-*.mdc` existem e que `.claude/docs/.../codex-component-*.md` existem
- [ ] 19. Commits atômicos por codex (subject em inglês + body bilíngue, assinados); 1 commit final para `platforms.yaml` + redirect notes
- [ ] 20. Push e abrir PR via `kata-contributing-pr` referenciando `Closes #{N}` e `Refs` ao plan-011
- [ ] 21. Após merge: arquivar plan e remover worktree

## Dependências

- **Plan-011 com Gate 1 aprovado** (decisões de naming e estrutura travadas) — bloqueante
- `bounded-context-template` PR #1 mergeado (já está) — fonte canônica para os exemplos
- `templates/codex-sample.md` presente — usado como template
- Plan-002, Plan-003 (lazy-load mechanics) já mergeados — `paths:` em `platforms.yaml` é o caminho usado
- **Independente** de plans 006, 007, 008, 010, 013, 014

## Riscos

- **Codex per-component fica genérico demais** (re-empacotamento de wikis sobre FastAPI/Strands sem agregar valor). Mitigação: cada codex tem seções "What this component owns" e "What this component does NOT own" obrigatórias — força recorte específico do contexto Guardia, não tutorial genérico.
- **Subclade `architecture` cria precedente para inflar a taxonomia.** Mitigação: manter rigoroso — só artefatos transversais a backend/frontend/mobile entram aqui; cada review de PR no clade verifica.
- **Nota de redirect nos codex Python existentes confunde leitor.** Mitigação: nota curta (2-3 linhas), sempre na primeira seção depois do header, padrão idêntico nos 3 codex que recebem redirect.
- **Tradução para es/en rouba tempo desproporcional.** Mitigação: pt-BR canonical primeiro; tradução pode vir em PR separado dentro da mesma issue (Refs #N) se o volume justificar — `lex-framework-language` permite isso enquanto `language.i18n` não fica completo no merge.
- **Stack do bounded-context-template muda** (e.g., Strands sai, FastMCP sobe versão). Mitigação: codex cita "stack adotado em `bounded-context-template/{path}` — verificar versão atual antes de adotar"; auditoria trimestral.
- **Conflito com `codex-python-architecture` existente** sobre quem é dono de "Clean Architecture". Mitigação: divisão clara — `codex-python-architecture` continua dono do **paradigma** (ports & adapters em Python); `codex-component-{api,agents,jobs}` é dono da **aplicação do paradigma a esse component específico**.

## Verificação

1. 6 novos codex × 3 idiomas = 18 arquivos novos sob `framework/{lang}/engineering/architecture/codex/`
2. `framework/platforms.yaml` lista os 6 codex em `cursor.rules` E em `claude-code.docs`, com `paths:` lazy-load corretos
3. `codex-python-architecture`, `codex-python-fastapi`, `codex-frontend-architecture` (3 idiomas) têm nota de redirect curta no topo
4. `lex-platforms-rules` validation passa (todo codex novo registrado em `platforms.yaml`)
5. `scripts/install.py --self` produz `.cursor/rules/...` e `.claude/docs/...` com os novos artefatos
6. **Sem mudança em**: warriors, katas, cries, Lexis, `.directives.sample`, kata-quality-gate, lex-issue-driven, qualquer artefato fora de codex
7. PR final referencia issue, plan-011, e tem stamp de custo (se plan-007 já mergeado)
8. Os 6 novos codex passam por `kata-artifact-self-review` antes do PR
