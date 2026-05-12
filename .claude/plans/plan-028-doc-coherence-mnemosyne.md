---
plan_id: "028"
title: "doc-coherence-mnemosyne"
status: pending
agent: claude
issue: "TBD (a abrir antes da branch — lex-issue-first)"
created_at: "2026-05-08T00:00:00Z"
updated_at: "2026-05-08T00:00:00Z"
---

# Plano: lex-doc-coherence + warrior-mnemosyne — Coerência Documental como HARD-GATE

## Objetivo

Criar a infraestrutura que assegura coerência entre **código e documentação** no framework Ahrena e nos projetos consumidores. Define `lex-doc-coherence` enumerando pares "mudança X exige atualização em Y" com HARD-GATE; `warrior-mnemosyne` como auditor disparável em dois modos (subagent assíncrono em background durante o trabalho, e GitHub Action headless em PR-time); e `cry-doc-audit` como entrypoint manual. Liga em **fases**: primeiro auditor em report-only para catalogar débito atual sem travar PRs, depois enforcement de fato após o débito ser fechado ou marcado como waiver.

## Contexto

### Diagnóstico

Após plans 005-026, o framework evoluiu rápido (stacked PRs, decorators, components, MCP, skills, examples) e a documentação acumulou drift silencioso. O problema vai além do framework: qualquer projeto que adota Ahrena terá os mesmos pares "código ↔ doc" potencialmente fora de sincronia (endpoint sem OAS, evento publicado sem catálogo, decisão de arquitetura sem ADR). Hoje a única defesa é review humano — frágil e inconsistente.

### Decisões já alinhadas

1. **Lexis nova `lex-doc-coherence`** enumerando 4 pares iniciais (Lexis multilíngue; Lexis/Codex ↔ platforms.yaml; endpoint/event/entity ↔ docs/{context}; decisão arquitetural ↔ ADR).
2. **Warrior `warrior-mnemosyne`** — deusa grega da memória, mãe das Musas. Encaixe semântico exato: manter a memória coerente do framework e do projeto.
3. **Cry `cry-doc-audit`** como entrypoint manual.
4. **Ordem: auditar primeiro, ligar gate depois.** Action começa em modo report-only (comenta no PR mas não falha o check). Após débito ser zerado/waiver-ado, vira gate de fato.
5. **Dois modos de invocação:** subagent in-session (`Agent` com `run_in_background: true`) para feedback durante implementação; GitHub Action headless para enforcement em PR.

### Harmonização com plan-025 (plan-alignment-auditor)

`plan-025` introduz auditor de alinhamento "plan ↔ implementação" — dimensão diferente (diff respeita `## Escopo` do plan ativo?), mas compartilha infraestrutura e convenções com este plan-028. Três pontos de harmonização acordados antes da execução:

1. **Convenção de waiver unificada via labels namespaced.**
   - `waiver:plan-alignment` (plan-025; substitui o original `plan-alignment:waived`)
   - `waiver:doc-coherence` (este plan; substitui o `doc-coherence-waiver:` em body que estava aqui)
   - Comment obrigatório no PR carrega o detalhe estruturado (motivo, expiração, par específico quando aplicável)

2. **Infraestrutura de validação compartilhada (`scripts/_validate/`).** Plan-019 introduz `scripts/validate.py` + módulos. Plan-025 contribui `scripts/_validate/plan_alignment.py`. Plan-028 contribui `scripts/_validate/doc_coherence/`. Mesmo formato de finding (severity, file, message), mesma CLI principal (`validate.py --mode=...`).

3. **Workflow de PR unificado.** Um único `.github/workflows/validate-pr.yml` com **jobs paralelos** (`plan-alignment`, `doc-coherence`, e futuros). Cada job posta seu próprio comment/check; falha agregada. Reduz overhead de checkout/setup vs. dois workflows separados.

Os três pontos exigem **edição cruzada do plan-025** antes da execução de qualquer dos dois — feita simultaneamente a este plan-028.

### Escopo dual: framework + projetos consumidores

A Lexis vale para dois universos:

- **Framework Ahrena (este repo):** pares 1, 2, 4 ativos por padrão (Lexis multilíngue; Lexis/Codex ↔ platforms.yaml; ADR para decisões estruturais).
- **Projetos consumidores (ex: Guardia):** pares 3, 4 ativos por padrão (endpoint/event/entity ↔ docs/{context}; ADR).

Pares ativos por projeto declarados em `.ahrena/.directives` na seção `doc_coherence.active_pairs` — projeto pode ligar/desligar pares conforme aplicabilidade.

### Pares e heurísticas de detecção

| # | Par | Detecção determinística | LLM necessário |
|---|-----|-------------------------|:--------------:|
| 1 | Diff toca `framework/{lang_A}/.../lex-X.md` → mesmo `lex-X.md` em todas as línguas em `language.i18n` foi tocado | Sim (comparar paths no diff) | Não |
| 2 | Novo `framework/{lang}/.../{lex,codex}-Y.md` → key correspondente em `framework/platforms.yaml > cursor.rules` | Sim (parsing YAML + diff) | Não |
| 3 | Diff toca código que declara endpoint (FastAPI router), publica evento (CloudEvents), ou define modelo persistente → `docs/{context}/oas/openapi.yaml`, `events/events.md`, `entities/{e}.md` | Parcial (regex em `*.py`) | Sim (decidir se endpoint é novo, qual context, mapear nome) |
| 4 | Diff "estruturalmente relevante" (mudança de framework, novo padrão arquitetural, nova dependência) → ADR em `docs/adr/` | Não (subjetivo) | Sim (julgamento) |

Pares 1-2: rodam em script Python puro, custo zero, falsos positivos baixos.
Pares 3-4: rodam no warrior via LLM, só quando o pré-filtro determinístico identifica candidatos.

### Arquitetura de invocação

```
┌─ Modo 1 — In-session async (durante implementação) ─────────────────┐
│ Apollo/Hephaestus implementam.                                       │
│ A cada N edits ou ao marcar [x] de step, o agente principal dispara: │
│   Agent(subagent_type='warrior-mnemosyne',                           │
│         run_in_background=True,                                      │
│         prompt='audit diff vs HEAD~N')                               │
│ Report chega ao final, antes do PR. Sem espera.                      │
└──────────────────────────────────────────────────────────────────────┘

┌─ Modo 2 — PR-time async (independente de sessão humana) ────────────┐
│ Action `doc-coherence-audit.yml` em on: pull_request.                │
│ 1. Roda script determinístico (pares 1-2). Se nada → skip resto.     │
│ 2. Se há candidatos pares 3-4 → invoca claude headless com           │
│    --agents warrior-mnemosyne.                                       │
│ 3. Posta resultado como PR comment + status check.                   │
│ 4. Modo report-only (Fase A): check sempre verde, comment informa.   │
│    Modo enforcement (Fase D): check vermelho se findings sem waiver. │
└──────────────────────────────────────────────────────────────────────┘

┌─ Modo 3 — Manual (cry-doc-audit) ──────────────────────────────────┐
│ Humano roda em qualquer momento para auditar working tree atual.    │
└─────────────────────────────────────────────────────────────────────┘
```

### Mecanismo de waiver (harmonizado com plan-025)

Quando enforcement liga (Fase D), Action aceita waiver via **label `waiver:doc-coherence` + comment estruturado** no PR — mesma convenção de `waiver:plan-alignment` (plan-025), garantindo padrão único de namespace.

Exemplo de comment de waiver:

```
[doc-coherence-waiver]
pair: 3
reason: endpoint é experimental, OAS público fica para PR de promoção
expires: 2026-06-08
```

- **Label** `waiver:doc-coherence` aplicado no PR
- **Tag de bloco** `[doc-coherence-waiver]` no comment para o auditor identificar
- `pair: N` — par específico (1, 2, 3 ou 4)
- `reason` — obrigatório, mínimo 20 caracteres
- `expires` — opcional mas recomendado; após a data, waiver vira finding de novo

Waiver é registro consciente, não bypass.

## Escopo

### Artefatos a criar (todos em pt-BR + es + en)

| # | Tipo    | Nome                       | Path                                                                              |
|---|---------|----------------------------|-----------------------------------------------------------------------------------|
| 1 | Lexis   | `lex-doc-coherence`        | `framework/{lang}/_foundation/quality/lexis/lex-doc-coherence.md`                 |
| 2 | Kata    | `kata-doc-coherence-audit` | `framework/{lang}/_foundation/quality/katas/kata-doc-coherence-audit.md`          |
| 3 | Warrior | `warrior-mnemosyne`        | `framework/{lang}/_foundation/quality/warriors/warrior-mnemosyne.md`              |
| 4 | Cry     | `cry-doc-audit`            | `framework/{lang}/_foundation/quality/cries/cry-doc-audit.md`                     |

Subclade `_foundation/quality/` (não `contributing/`) — coerência documental é qualidade, vizinha de `lex-template-usage`, `lex-tone`, `lex-hard-gate-pattern`.

### Artefatos a atualizar

| # | Tipo     | Nome                                              | Mudança                                                                          |
|---|----------|---------------------------------------------------|----------------------------------------------------------------------------------|
| 5 | Config   | `.ahrena/.directives.sample`                      | Adicionar seção `doc_coherence.active_pairs` com defaults                       |
| 6 | Config   | `framework/platforms.yaml`                        | Registrar `lex-doc-coherence` em `cursor.rules`                                 |
| 7 | Lexis    | `lex-framework-language` (rule mandatory completeness) | Adicionar referência a `lex-doc-coherence` para enforcement                |
| 8 | Lexis    | `lex-platforms-rules`                             | Adicionar referência a `lex-doc-coherence`                                      |

### Tooling (compartilhado com plan-019/025)

| #  | Arquivo                                                       | Descrição                                                                                                              |
|----|---------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------|
| 9  | `scripts/_validate/doc_coherence/__init__.py` + `check_pairs.py` | Detector determinístico (pares 1-2). Reusa o framework de `scripts/validate.py` (plan-019); finding format alinhado com plan-025. |
| 10 | `scripts/_validate/doc_coherence/llm_pairs.py`                 | Wrapper que invoca claude headless / `Agent` para pares 3-4 quando o pré-filtro identifica candidatos                 |
| 11 | `tests/validate/test_doc_coherence.py` + fixtures              | Test suite cobrindo pares 1-2 com fixtures de diff sintético; reusa estrutura de fixtures de plan-019/025             |
| 12 | `scripts/validate.py` (atualização)                            | Adicionar `--mode=doc-coherence` invocando o módulo novo (plan-019 introduziu o esqueleto)                            |
| 13 | `.github/workflows/validate-pr.yml` (job `doc-coherence`)      | Job no workflow unificado. Reuso de checkout/setup com job `plan-alignment` (plan-025). Modo report-only inicialmente. |

### Catálogo de débito (gerado, não criado a mão)

| # | Arquivo                                                | Descrição                                                                                       |
|---|--------------------------------------------------------|-------------------------------------------------------------------------------------------------|
| 12 | `docs/doc-debt/baseline-{YYYY-MM-DD}.md`              | Snapshot da auditoria retroativa: lista findings por par, agrupados por arquivo afetado         |
| 13 | Issues no GitHub (uma por finding ou agrupada por par) | Tracking de cada item de débito; label `doc-debt` + `documentation 📃`                          |

## Steps

### Fase A — Construir auditor em report-only

- [ ] **A.1. Issue** — abrir issue (`feature-request`, labels `feature request ➕` + `framework` + `documentation 📃`, assignee `@me`) com Why/What/How
- [ ] **A.2. Worktree** — `feat/{N}-doc-coherence-mnemosyne` em `.worktrees/{N}-doc-coherence-mnemosyne/`
- [ ] **A.3. Lexis `lex-doc-coherence` (pt-BR)** — usar `templates/lex-sample.md`. Estrutura: 4 pares enumerados; HARD-GATE com escopo "todo PR em repo Ahrena ou consumidor"; cláusula transitória "Fase A — report-only até débito catalogado for fechado"
- [ ] **A.4. Tradução `lex-doc-coherence`** — versões es e en
- [ ] **A.5. `.directives.sample`** — adicionar seção `doc_coherence` com `active_pairs` (defaults por contexto: framework vs. consumer) + `report_only: true|false`
- [ ] **A.6. Atualizar `lex-directives.md`** (3 línguas) — documentar nova seção `doc_coherence.*`
- [ ] **A.7. `framework/platforms.yaml`** — registrar `lex-doc-coherence` em `cursor.rules`
- [ ] **A.8. Script `scripts/_validate/doc_coherence/check_pairs.py`** — pares 1 (Lexis multilíngue) e 2 (Lexis/Codex ↔ platforms.yaml). Input: `git diff` ranges via API do `scripts/validate.py` (plan-019). Output: findings no formato compartilhado com plan-025
- [ ] **A.9. Atualizar `scripts/validate.py`** — adicionar `--mode=doc-coherence`. Tests em `tests/validate/test_doc_coherence.py` reusando fixtures de plan-019/025 (diff só em pt-BR, diff multilíngue parcial, novo lex sem entrada em platforms.yaml, etc.)
- [ ] **A.10. Kata `kata-doc-coherence-audit` (pt-BR)** — `templates/kata-sample.md`. Procedimento: roda check_pairs.py; se há candidatos para pares 3-4, invoca LLM com diff + lista determinística; produz report estruturado (markdown)
- [ ] **A.11. Tradução `kata-doc-coherence-audit`** — es e en
- [ ] **A.12. Warrior `warrior-mnemosyne` (pt-BR)** — `templates/warrior-sample.md`. Persona, escopo (read-only audit), uso do `Agent` em background, formato do report. Documentar invocação manual e via Action
- [ ] **A.13. Tradução `warrior-mnemosyne`** — es e en
- [ ] **A.14. Cry `cry-doc-audit` (pt-BR)** — `templates/cry-sample.md`. Args: `--scope working-tree|diff|pr <N>`, `--pairs all|1,2,3,4`. Invoca `warrior-mnemosyne`
- [ ] **A.15. Tradução `cry-doc-audit`** — es e en
- [ ] **A.16. Job `doc-coherence` em `.github/workflows/validate-pr.yml`** — workflow unificado com plan-025. Se `validate-pr.yml` ainda não existir (caso plan-025 não tenha mergeado), criar com este job + placeholder/skip do job `plan-alignment`. Modo report-only: rodar `validate.py --mode=doc-coherence`; se findings determinísticos OU diff toca paths heurísticos pares 3-4 → invocar claude headless com `warrior-mnemosyne`; postar comment no PR taggeado `[doc-coherence-report]`; check sempre verde nesta fase
- [ ] **A.17. Sync** — `python3 scripts/install.py --self --target . --platform claude-code` e `--platform cursor`

### Fase B — Auditoria retroativa do framework

- [ ] **B.1. Rodar `cry-doc-audit --scope working-tree --pairs 1,2`** sobre `main` atual do Ahrena. Pares 1-2 são determinísticos, custo zero, cobrem o débito mais provável (Lexis sem versão multilíngue; Lexis sem entrada platforms.yaml)
- [ ] **B.2. Rodar `cry-doc-audit --pairs 4`** sobre history dos plans 005-026 — identificar mudanças estruturais sem ADR correspondente. Custo: tokens de LLM, mas one-shot
- [ ] **B.3. Gerar `docs/doc-debt/baseline-2026-05-08.md`** consolidando findings
- [ ] **B.4. Abrir issues de débito** — uma por par com lista de arquivos afetados; label `doc-debt`
- [ ] **B.5. Triagem** — classificar débito em (a) corrigir agora, (b) backlog priorizado, (c) waiver com justificativa
- [ ] **B.6. PRs de correção** — só os classificados como (a). Cada PR fecha 1+ issue de débito

### Fase C — Validação do auditor (paralela à Fase B)

- [ ] **C.1. Validar Modo 1 (subagent in-session)** — em uma sessão de trabalho, disparar `Agent(subagent_type='warrior-mnemosyne', run_in_background=True)` durante uma edição. Verificar que report chega sem bloquear
- [ ] **C.2. Validar Modo 2 (Action PR-time)** — abrir PR de teste com violação proposital de cada par; verificar comment correto
- [ ] **C.3. Validar Modo 3 (cry manual)** — `cry-doc-audit` em working tree limpo (zero findings) e em working tree com violação induzida

### Fase D — Ligar enforcement (em PR separado, após débito reduzido)

> **Não executar nesta PR.** Steps abaixo ficam documentados para o follow-up.

- [ ] **D.1. Atualizar `lex-doc-coherence`** — remover cláusula "Fase A — report-only", deixar HARD-GATE puro
- [ ] **D.2. Atualizar Action** — `report_only: false`; check vira `failure` quando há findings sem waiver
- [ ] **D.3. Documentar formato do waiver** no `lex-doc-coherence` e em `lex-pr-quality`
- [ ] **D.4. Anunciar** corte da Fase D em changelog do framework

### Fechamento

- [ ] **E.1. Commits atômicos por agrupamento** (exemplos: `feat(quality): add lex-doc-coherence + script + tests`, `feat(quality): add warrior-mnemosyne + kata + cry`, `feat(ci): add doc-coherence-audit workflow in report-only`)
- [ ] **E.2. PR com `Closes #{N}`**, labels mirroring + `documentation 📃` + `framework` + size label, reviewers via CODEOWNERS

## Dependências

- **Pré-requisitos (Lexis existentes):**
  - `lex-framework-language`, `lex-platforms-rules`, `lex-template-usage`, `lex-hard-gate-pattern`, `lex-issue-driven` (especialmente rule 4 sobre ADR)
  - `lex-tone`, `lex-pr-quality`, `lex-issue-quality`
- **Pré-requisitos (infra):**
  - **`plan-019` mergeado** (introduz `scripts/validate.py` + estrutura `scripts/_validate/`) — bloqueante. Se ainda não estiver mergeado, plan-028 pode contribuir o esqueleto mínimo necessário.
  - Tooling MCP `github` (criar issues de débito, postar comments)
  - Claude Code headless mode disponível em CI (verificar antes da Fase A.16)
- **Sincronização com `plan-025`** (plan-alignment-auditor):
  - Convenção de waiver harmonizada (`waiver:plan-alignment` / `waiver:doc-coherence`) — edição cruzada do plan-025 antes de executar qualquer dos dois
  - Workflow unificado `validate-pr.yml` com jobs `plan-alignment` + `doc-coherence`
  - Mesma estrutura `scripts/_validate/<mode>/`
- **Independente do `plan-027`** (Janus). Podem rodar em paralelo ou em qualquer ordem.

## Riscos

| # | Risco                                                                                                          | Probabilidade | Mitigação                                                                                                                          |
|---|----------------------------------------------------------------------------------------------------------------|:-------------:|------------------------------------------------------------------------------------------------------------------------------------|
| 1 | Action em report-only nunca vira enforcement de fato (débito é grande demais, equipe acomoda no "report-only") | Alta          | Fase D já está roteirizada com critério explícito; agendar prazo para revisão (sugestão: revisar em 60 dias após Fase B fechar)    |
| 2 | Heurística de pares 3-4 gera falsos positivos massivos                                                         | Média         | Iniciar pares 3-4 em modo `--pairs 1,2` no default; adicionar 3-4 só após calibrar com sample manual                               |
| 3 | Custo de LLM no Action por PR fica alto                                                                        | Média         | Pré-filtro determinístico drástico: se diff só toca `tests/`, `*.md`, `package.json` lockfile etc. → skip antes de invocar LLM     |
| 4 | Claude Code headless indisponível ou quebra em CI                                                              | Baixa         | Alternativa: rodar só pares 1-2 (determinísticos) no Action; pares 3-4 ficam exclusivos do Modo 1 (in-session subagent) por hora    |
| 5 | Multilingue incompleto da própria Lexis (irônico)                                                              | Baixa         | Usar o próprio `check_pairs.py` (par 1) no PR deste plano antes de mergear — dogfooding                                            |
| 6 | Subagent in-session via `Agent` background não retorna em tempo útil em sessões longas                         | Baixa         | Documentar no warrior que invocação in-session é "best effort"; a barreira autoritativa é o Action de PR                           |
| 7 | Waiver vira válvula de escape silenciosa                                                                       | Média         | Waiver requer `reason` e `expires`; relatório mensal lista waivers ativos por idade; expirados viram findings ativos               |

## Decisões em aberto (a tratar na execução)

- **Subclade do warrior**: confirmado `_foundation/quality/` (não `contributing/`).
- **Threshold de "diff estruturalmente relevante" (par 4)**: definir durante implementação. Sugestão inicial: ≥ 200 LOC adicionadas em ≥ 3 arquivos sob `app/` ou `framework/`, OU import de novo top-level package no `pyproject.toml`/`package.json`, OU mudança em `Dockerfile`/IaC.
- **Localização do baseline de débito**: `docs/doc-debt/` no repo Ahrena. Em projetos consumidores, mesma convenção.
- **Schema do report**: definir formato canônico (markdown com seções por par). Versionar via `report_schema_version` para futuras evoluções.