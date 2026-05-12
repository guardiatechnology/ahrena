---
plan_id: "011"
title: "component-aligned-warrior-topology"
status: pending
agent: claude
issue: "TBD (a abrir antes da branch — lex-issue-first)"
created_at: "2026-05-07T22:00:00Z"
updated_at: "2026-05-07T22:00:00Z"
---

# Plano: Topologia de Warriors alinhada aos Components do bounded-context-template

## Objetivo

Diagnosticar a "inflação" dos warriors de desenvolvimento (Apollo, Hephaestus, Iris e adjacentes) e desenhar uma **topologia-alvo** em que cada warrior cobre um conjunto de habilidades estritamente correlatas a **um component** do `bounded-context-template` (api, agents, jobs, ui, deployment). Este plano é **estratégico**: produz decisões e o north star — não altera código nem warriors. As implementações ocorrem nos plans 012 (codex base), 013 (split do Apollo) e 014 (audit dos demais).

## Contexto

### Sintoma observado pelo usuário

> "Nossos agentes de desenvolvimento estão muito inflados. Um desenvolvedor de API tem um conjunto de habilidades; um desenvolvedor de Jobs/Workers tem outras; um desenvolvedor de Agentes tem outras. Podemos melhorar muito o desempenho de uso de token se pensarmos de forma mais estratégica em como os agentes se complementam."

### Diagnóstico (medido a partir do estado atual em `framework/en/.../warriors/`)

| Warrior | Linhas | Domínio declarado | Sintoma de inflação |
|---|--:|---|---|
| `warrior-apollo` | 140 | "Senior Python Engineer" — Backend | **Agudo:** mesma persona implementa API HTTP (FastAPI), workers/jobs (Lambda/Step Functions), agentes (Strands/Bedrock), ETL, observability, refactor — todas as habilidades de Python misturadas |
| `warrior-hephaestus` | 132 | Frontend — React/Next.js | **Médio:** mistura web app, biblioteca de widgets, design-system consumer, e revisão de PR — possível split widget-lib vs app |
| `warrior-iris` | 146 | Mobile — iOS/Android, RN/Flutter | **Baixo:** já é especializado em uma surface coesa; manter |
| `warrior-atlas` | 170 | DevOps/Cloud — AWS arquitetura + IaC | **Baixo:** arquiteto, não dev; já especializado |
| `warrior-daedalus` | 138 | API design (RESTful spec) | **Nenhum:** designer de contrato, não dev |
| `warrior-kronos` | 156 | Event Storming + CloudEvents docs | **Nenhum:** designer/arqueólogo de domínio |
| `warrior-theseus` | 142 | Domain modeling (DDD) | **Nenhum:** designer/arqueólogo de domínio |
| `warrior-prometheus` | 172 | Orquestrador de design de feature | **Nenhum:** orquestrador, não dev |
| `warrior-hera` | 133 | QA / test strategy | **Nenhum:** especialista em estratégia de testes |
| `warrior-hestia` | 135 | SRE / on-call | **Nenhum:** especialista em runtime/operação |
| `warrior-demeter` | 150 | Data / DB architect | **Nenhum:** arquiteto, não dev |
| `warrior-athena` | 189 | Issue-Driven flow orchestrator | **Nenhum:** orquestrador |

**Foco do escopo deste plan:** os warriors com sintoma `Agudo` ou `Médio` — Apollo (prioritário) e Hephaestus (secundário).

### Modelo de referência: `bounded-context-template` (PR #1, autores: Douglas Picolotto + Fernando Seguim)

A organização canônica do monorepo Guardia (https://github.com/guardiatechnology/bounded-context-template) separa cada bounded context em **components** isolados, cada um com `pyproject.toml`/`package.json` próprio, dependências distintas e testes próprios:

```
components/
├── api/        # FastAPI + FastMCP + OTel-FastAPI               (HTTP/MCP server)
├── agents/     # strands-agents + boto3 (Bedrock) + SSE         (LLM agents)
├── jobs/       # aws-lambda-powertools + moto + Pydantic        (Step Functions tasks)
└── ui/         # Next.js + Tailwind + Storybook + Cypress       (widget library)
deployment/     # AWS CDK Python                                 (IaC)
docs/           # domain, architecture, events, oas, metrics, adrs, pdrs
```

Dependências confirmadas (lidas dos `pyproject.toml` reais do template):

| Component | Dependências de runtime | Dependências de teste | Skill predominante |
|---|---|---|---|
| `api/` | `fastapi`, `uvicorn`, `fastmcp`, `opentelemetry-instrumentation-fastapi` | `httpx`, `pytest` | HTTP request/response, hexagonal/clean architecture, OAS, MCP |
| `agents/` | `strands-agents`, `strands-agents-tools`, `boto3`, `fastapi`, `uvicorn`, `sse-starlette`, OTel | `pytest`, `pytest-asyncio` | LLM orchestration, prompts, tools, memory, specialists, SSE streaming |
| `jobs/` | `aws-lambda-powertools`, `boto3`, `pydantic`, OTel (sem FastAPI) | `moto[stepfunctions,lambda]`, `pytest` | Lambda handlers, idempotency middleware, Step Functions integration, retries |
| `ui/` | `next`, `tailwindcss`, `tsup`, `react` | `cypress`, `jest`, `storybook` | Widget library export como NPM package, design-system consumer, e2e UX |

**Cada component é uma especialidade diferente.** Um warrior monolítico ("Senior Python Engineer") é forçado a carregar contexto e Lexis dos três mundos Python (api + agents + jobs) toda vez que é invocado, mesmo quando o usuário só quer mexer em um.

### Recomendações do Douglas (Douglas Picolotto / @dopic)

> ⚠️ **Esta é uma seção que você (Fernando) precisa preencher diretamente com o Douglas — o que está aqui é o que consegui recuperar do repositório; o restante depende de conversa com ele.**

#### Recomendações inferíveis pela contribuição rastreada do Douglas

Baseado em commits e PRs assinados por `Douglas Picolotto` no `bounded-context-template` e em `ahrena`:

1. **Organização por components** (`bounded-context-template` first commits, antes do scaffold do Fernando) — separar `components/{api,agents,jobs,ui}` cada um com seu `pyproject.toml`/`package.json` independente, em vez de monorepo Python único.
2. **Validação de branch naming via pre-commit** (`bounded-context-template` commit `3542012`) — hooks locais para branch name + commit msg antes de qualquer push.
3. **Separação `src/` vs `tests/` por component** (`bounded-context-template` commit `8f92947` "chore: change tests structure") — testes co-localizados ao código e não em diretório global.
4. **Python Engineer como warrior dedicado** (`ahrena` PR #4: "feat: Add Python Engineer") — Douglas foi quem formalizou o Apollo como warrior. **A especialização adicional (api/jobs/agents) é evolução natural dessa fundação, não rejeição.**
5. **Suporte a múltiplas plataformas de IDE** (`ahrena` PR #3: "feat/add-cloud-code-support" e PR #15: "feat: allow language files selection during installation") — Douglas trabalhou em flexibilidade de instalação; o split de warriors deve preservar essa flexibilidade (cada warrior continua sendo gerável para Cursor + Claude Code).

#### Recomendações que precisam ser confirmadas com o Douglas

Não consegui localizar comentários técnicos extensos do Douglas em PR reviews ou discussions (suas reviews aparecem como `APPROVED` sem corpo). As **recomendações que você lembra** mas que não estão registradas precisam ser puxadas dele diretamente. Sugestões de ângulos que provavelmente foram discutidos:

- [ ] **Agent vs API vs Worker como contracts diferentes**: como o Douglas vê a fronteira entre "agente que usa LLM" vs "worker síncrono determinístico" vs "API exposta a clientes"?
- [ ] **Quem deve ser dono dos eventos** quando há um worker que consome e um agente que reage — `Apollo-jobs` ou `Apollo-agents`?
- [ ] **Estratégia de teste por component**: Douglas optou por `*.test.py` co-localizado em `src/` no template — o split de warriors deve respeitar essa convenção em todos os 3 katas (api/jobs/agents)?
- [ ] **Reuso de Lexis Python**: alguma Lexis (e.g., `lex-python-typing`, `lex-python-error-handling`) pode aplicar a todos os 3 warriors split, mas algumas (e.g., idempotência de jobs, handler signatures Lambda) seriam de um só?
- [ ] **Naming dos warriors**: manter `warrior-apollo-{api,jobs,agents}` ou separar em personas mitológicas distintas (e.g., Hermes para agentes, Hefesto para workers)?
- [ ] **Existe documento/Notion/Slack** do Douglas com o desenho que ele tinha em mente? **→ Recuperar e linkar aqui antes de fechar Gate 1 do plan-013.**

#### Item de ação

- [ ] Antes de aprovar o **Gate 1 do plan-013** (split do Apollo), abrir issue/discussion convidando o Douglas para revisar este plan-011 e listar o que está faltando da memória dele. **Bloqueante** para começar plan-013.

### Decisões propostas (assumidas — sujeitas a override do usuário)

| Decisão | Valor proposto | Alternativa rejeitada | Por quê |
|---|---|---|---|
| Mapeamento warrior ↔ component | 1:1 estrito | 1:N (um warrior cobre múltiplos components) | Um component = um conjunto coeso de Lexis/Codex/dependências = um budget de contexto previsível |
| Naming dos warriors split | `warrior-apollo-api`, `warrior-apollo-jobs`, `warrior-apollo-agents` | Personas separadas (Hermes, Hefesto, etc.) | Mantém linhagem Apollo (familiaridade) e deixa claro que são especializações da mesma "guild" Python. **Sujeito a confirmação com Douglas — pode preferir personas distintas** |
| Apollo monolítico atual | **Manter como meta-orquestrador** que delega para o trio | Deletar | Backward compat: chamadas existentes a Apollo continuam funcionando; ele detecta o component e despacha. Plan-013 detalha |
| Hephaestus | Manter monolítico **por enquanto** | Split widget-lib vs web-app | Bounded-context-template hoje só tem `ui/` como widget library; até existir um component `web-app/` no template, split é prematuro. Plan-014 reavalia |
| Iris (Mobile) | Manter monolítico | Split iOS vs Android | Cross-platform parity (`lex-mobile-platform-parity`) exige uma persona única que pensa em ambos simultaneamente |
| Atlas, Daedalus, Kronos, Theseus, Prometheus, Hera, Hestia, Demeter | Manter como estão | Split | Não são "dev warriors"; são designers/arquitetos/QA/SRE/data — cada um já tem uma surface coesa |
| Token budget alvo por warrior | < 80 linhas no `.md` do warrior + < 4 Lexis carregadas eagerly | Sem teto | Métrica concreta para validar que o split deu resultado. Plan-013 mede before/after |
| Lazy-load de Lexis/Codex por warrior | Sim — cada warrior split lista apenas seus Lexis/Codex específicos; `lex-python-typing` (cross-Python) carrega eagerly em todos os 3 | Carregar todos os Lexis Python em todos | Aproveita o mecanismo `paths:` no `platforms.yaml` (já em uso desde plan-002) |

## Escopo

### Entregáveis deste plan

| Artefato | Caminho | Conteúdo |
|---|---|---|
| Documento de topologia-alvo | `docs/internal/warrior-topology-2026.md` | Tabela "warrior ↔ component", responsabilidades, fronteiras, regras de delegação, token budget alvo |
| Decisões registradas | seção neste próprio plan | Tabela acima, com override quando o usuário aprovar |
| Recomendações do Douglas (consolidadas) | issue/discussion + seção neste plan | Lista atualizada após conversa com Douglas |
| Plans dependentes | `.claude/plans/plan-012`, `.claude/plans/plan-013`, `.claude/plans/plan-014` | Já criados em paralelo a este (plans irmãos) |

### Fora de escopo

- **Implementação de qualquer warrior, codex ou kata** — fica para plans 012/013/014.
- **Mudança em `.directives` ou `platforms.yaml`** — fica para plans 012/013.
- **Refactor do bounded-context-template** — template é input, não output deste plan.
- **Split de warriors não-dev** (Atlas, Daedalus, Kronos, etc.) — não candidatos.
- **Token cost measurement infra** — plan-007 (`pr-token-cost-stamp`) já cobre. Reusamos a infraestrutura dele para medir antes/depois nos plans 013/014, não construímos paralelo.

## Steps

- [ ] 1. Abrir issue guarda-chuva no repo `guardiatechnology/ahrena` com template `epic` (label `epic`, Issue Type `Epic`), título "Component-aligned warrior topology — split Apollo and align dev warriors with bounded-context-template components"
- [ ] 2. Linkar nesta issue: PR #1 do `bounded-context-template`, este plan-011, e os plans 012/013/014 (uma vez criados como issues também)
- [ ] 3. Abrir discussion no repo `guardiatechnology/ahrena` (categoria Golden Circle) convocando @dopic para revisar este plan e completar a seção "Recomendações do Douglas"
- [ ] 4. Atualizar status deste plan para `in-progress` quando a issue for criada
- [ ] 5. Aguardar resposta do Douglas (timebox: 5 dias úteis); incorporar respostas na seção dedicada
- [ ] 6. Redigir `docs/internal/warrior-topology-2026.md` consolidando: diagnóstico, modelo bounded-context-template, mapeamento alvo, regras de delegação, token budget. **Apenas pt-BR** — documento interno, não é artefato do framework
- [ ] 7. Apresentar para o usuário: este plan revisado + topology doc + recomendações do Douglas → **Gate 1: aprovação humana das decisões**
- [ ] 8. Após Gate 1, registrar overrides do usuário na seção "Decisões propostas" (acima) e travar o plan
- [ ] 9. Sinalizar plans 012, 013, 014 como `desbloqueados` (atualizar status `pending → ready`)
- [ ] 10. Após plans 012/013/014 mergeados, arquivar este plan-011 (status `done → archived`)

## Dependências

- Conversa com **Douglas Picolotto (@dopic)** para preencher a seção "Recomendações do Douglas que precisam ser confirmadas". **Bloqueante** para Gate 1.
- `bounded-context-template` PR #1 (já existe; usado como referência canônica)
- Plans 002, 003 (lazy-load mechanics) já mergeados — fundação técnica para per-warrior Lexis loading
- Plan-007 (token cost stamp) **opcional** mas útil para medir o ganho de tokens dos plans 013/014

## Riscos

- **Douglas indisponível ou não retornar no timebox.** Mitigação: prosseguir com decisões assumidas (tabela acima) marcando-as como "tentativas — pendente Douglas"; cada plan filho (013/014) tem seu próprio Gate 1 onde o Douglas pode ainda intervir antes do merge.
- **Split prematuro do Apollo quebra fluxos existentes** que invocam `cry-python-implement` esperando o monolítico. Mitigação: plan-013 mantém Apollo como meta-orquestrador retrocompatível; cries existentes continuam funcionando.
- **Naming dos sub-warriors** (`apollo-api` vs personas separadas) gera bikeshedding. Mitigação: travar a decisão no Gate 1 deste plan; plan-013 só começa após decisão tomada.
- **Token budget alvo (<80 linhas)** pode ser irreal. Mitigação: medir antes de fechar plan-013; ajustar alvo se necessário com base em dados reais.
- **Hephaestus ficar de fora gera incoerência** ("Por que dividi Apollo e não dividi Hephaestus?"). Mitigação: plan-014 audita Hephaestus explicitamente; se ficar monolítico, decisão é registrada com justificativa ("UI-as-widget-library é uma surface coesa").
- **Doc interno em pt-BR-only** dificulta consulta por contribuidores externos. Mitigação: aceitável neste momento — é doc de decisão, não artefato do framework. Se virar artefato do framework no futuro, traduzir.

## Verificação

1. Issue guarda-chuva aberta com template `epic` e Issue Type `Epic`; labels corretos
2. Discussion aberta convocando @dopic; link presente neste plan
3. `docs/internal/warrior-topology-2026.md` existe, mapeia 1:1 cada warrior dev a um component, com token budget alvo declarado
4. Seção "Recomendações do Douglas" tem `## Confirmadas` e `## Inferidas` claramente separadas; checklist `[ ]` no item de ação fica marcado `[x]` apenas após Douglas responder
5. Tabela de decisões no plan tem coluna "override do usuário" preenchida (aprovação ou modificação) após Gate 1
6. Plans 012, 013, 014 referenciam este plan-011 como dependência hard
7. Nenhum warrior, codex, kata, cry, Lexis ou diretiva foi modificado neste plan (regressão zero)
