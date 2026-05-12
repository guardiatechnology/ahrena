---
plan_id: "030"
title: "product-analytics-required"
status: pending
agent: claude
issue: "TBD (a abrir antes da branch — lex-issue-first)"
created_at: "2026-05-08T00:00:00Z"
updated_at: "2026-05-08T00:00:00Z"
---

# Plano: lex-product-analytics-required — PostHog Obrigatório em Toda Superfície de UI

## Objetivo

Codificar `lex-product-analytics-required` como nova Lei irmã de `lex-observability-required` cobrindo o lado **client-side** (analytics de produto), separada por escopo, audiência e pilha tecnológica. Toda superfície de UI sob governança Ahrena — frontend web, app mobile, widgets de skill, scripts de skill que renderizam UI — DEVE inicializar PostHog, identificar usuário (sem PII), capturar pageview/screenview e os eventos de produto declarados pelo time. Entrega script determinístico (`scripts/analytics/check_posthog.py`) que plan-029 consome no `kata-skill-validate` e que CI roda como check (modo report-only inicialmente, igual plan-028 Fase A → D).

## Contexto

### Por que separada de `lex-observability-required`

| Eixo | `lex-observability-required` | `lex-product-analytics-required` (nova) |
|------|------------------------------|------------------------------------------|
| Lado | Server (endpoint, consumer, job)            | Client (UI surface)                      |
| Sinais | Trace + métrica + log estruturado          | Pageview + identify + product events     |
| Audiência | SRE, on-call                             | Produto, growth, PM                      |
| Pilha | OpenTelemetry, CloudWatch, Datadog APM     | PostHog                                  |
| Privacidade | Logs sem PII (mascarar CPF, e-mail)    | Identify sem PII; eventos sem payload sensível |

Mesma intenção de enforcement, escopos disjuntos. Não dá para alargar a Lex existente sem perder clareza — Lexis nova é a chamada certa.

### Por que PostHog (no nível Codex, não Lexis)

A Lex declara o **princípio** ("toda UI deve ter analytics de produto" + 4 eventos mínimos); o **fornecedor** (PostHog) fica em `codex-posthog-integration`. Assim, troca de fornecedor no futuro é mudança de Codex, não revogação de Lei. Espelha o padrão de `lex-design-system-library` (Lex) + `codex-design-system` (manual).

### Acoplamento com plan-029 (warrior-claudionor)

- plan-029 cria `kata-skill-validate` que invoca validadores determinísticos contra `lex-skill-project-structure`.
- plan-030 entrega `scripts/analytics/check_posthog.py` na raiz do repo.
- `kata-skill-validate` chama `check_posthog.py --target {paths.skills_root}/{slug}/` quando o skill declara `widgets/` ou scripts UI.
- **Acoplamento soft, ordem flexível:** se plan-030 mergear depois, `kata-skill-validate` skipa o check (script ausente). Não há dependência hard de ordem; ideal é plan-030 antes para fechar Fase A do enforcement, mas plan-029 sai mesmo sem ele.

### Mapeamento de fluxo

```
cry-analytics-check --scope working-tree|diff|pr <N> --target frontend|mobile|skill <slug>|all
  └─→ kata-product-analytics-check
        └─→ scripts/analytics/check_posthog.py
              ├─ detecta SDK declarado (package.json / pyproject.toml / Podfile / Gradle)
              ├─ detecta init em código (posthog.init / PostHog.shared / etc.)
              ├─ detecta eventos mínimos: pageview/screenview, identify
              ├─ detecta payload com PII (regex: cpf, email, phone, fullname)
              └─ retorna JSON [{rule, severity, file, message}]

CI:
  .github/workflows/analytics-check.yml (on: pull_request)
    Fase A — report-only: comenta no PR, check sempre verde
    Fase D — enforcement: check vermelho se findings sem waiver
```

### Quatro eventos mínimos (declarados pela Lex)

1. **Init na carga da app** — antes de qualquer interação
2. **Identify após login** (anônimo antes; sem PII no payload — `distinct_id` derivado de hash do user_id)
3. **`$pageview` (web) / `$screen` (mobile)** automático em cada navegação
4. **Eventos de produto declarados** — toda jornada crítica em `docs/{context}/metrics/events.md` (subcatálogo metrics/ reservado em `lex-feature-design-docs`)

### Mecanismo de waiver

Mesmo padrão do plan-028 (Mnemosyne). PR pode declarar:

```
analytics-waiver: rule-pii-leak
reason: campo é hash, não PII bruto; falso positivo do regex
expires: 2026-08-08
```

Waiver é registro consciente, expira, e relatório mensal lista ativos por idade.

## Escopo

### Artefatos a criar (todos em pt-BR + es + en)

| # | Tipo  | Nome                              | Path                                                                              |
|---|-------|-----------------------------------|-----------------------------------------------------------------------------------|
| 1 | Lexis | `lex-product-analytics-required`  | `framework/{lang}/_foundation/quality/lexis/lex-product-analytics-required.md`    |
| 2 | Codex | `codex-posthog-integration`       | `framework/{lang}/engineering/analytics/codex/codex-posthog-integration.md`       |
| 3 | Kata  | `kata-product-analytics-check`    | `framework/{lang}/_foundation/quality/katas/kata-product-analytics-check.md`      |
| 4 | Cry   | `cry-analytics-check`             | `framework/{lang}/_foundation/quality/cries/cry-analytics-check.md`               |

Subclade nova `engineering/analytics/` reservada para futuros codex (feature flags, experimentação, métricas de produto). Lexis fica em `_foundation/quality/` espelhando `lex-observability-required`.

### Artefatos a atualizar

| # | Tipo  | Nome                              | Mudança                                                                                  |
|---|-------|-----------------------------------|------------------------------------------------------------------------------------------|
| 5 | Lexis | `lex-observability-required`      | Nota de cross-link "complementar a `lex-product-analytics-required` (lado client)"        |
| 6 | Lexis | `lex-feature-design-docs`         | Subcatálogo `metrics/` recebe arquivo `events.md` listando eventos de produto da feature |
| 7 | Kata  | `kata-frontend-implement`         | Cita `lex-product-analytics-required` na seção de quality gate                           |
| 8 | Kata  | `kata-frontend-review`            | Adiciona checagem de PostHog                                                             |
| 9 | Kata  | `kata-mobile-implement`           | Cita `lex-product-analytics-required`                                                    |
| 10| Config | `framework/platforms.yaml`       | Registrar `lex-product-analytics-required` e `codex-posthog-integration` em `cursor.rules` |

### Acoplamento explícito com plan-029

| #  | Artefato (plan-029)        | Mudança                                                                                  |
|----|----------------------------|------------------------------------------------------------------------------------------|
| 11 | `kata-skill-validate`      | Quando `widgets/` ou `scripts/` UI presente, invoca `scripts/analytics/check_posthog.py --target {paths.skills_root}/{slug}/` |

Se plan-029 ainda não mergeou quando plan-030 for mergeado, este step é nota de execução, não edição (espera plan-029 entrar e o autor de plan-029 leva esse acoplamento como parte do scope dele). Cross-link bidirecional fica no PR description.

### Tooling

| #  | Arquivo                                          | Descrição                                                                                       |
|----|--------------------------------------------------|-------------------------------------------------------------------------------------------------|
| 12 | `scripts/analytics/check_posthog.py`             | Detector determinístico cross-stack (web/mobile/skill widget/skill script)                       |
| 13 | `scripts/analytics/__init__.py` + tests          | Test suite com fixtures por stack: React app, React Native, Flutter, vanilla widget, Python script com UI |
| 14 | `.github/workflows/analytics-check.yml`          | Workflow PR-time. Fase A: report-only com comment. Fase D: status check vermelho                |

### Catálogo de débito (gerado, não criado a mão)

| #  | Arquivo                                          | Descrição                                                                                       |
|----|--------------------------------------------------|-------------------------------------------------------------------------------------------------|
| 15 | `docs/analytics-debt/baseline-{YYYY-MM-DD}.md`   | Snapshot da auditoria retroativa: UI sem PostHog, eventos faltando, vazamentos de PII em payload |
| 16 | Issues no GitHub                                 | Tracking por área; labels `analytics-debt` + `documentation 📃`                                  |

## Steps

### Fase A — Construir auditor em report-only

- [ ] **A.1. Issue** — abrir issue (`feature-request`, labels `feature request ➕` + `framework` + `analytics`, Issue Type `Feature`, assignee `@me`) com Why/What/How
- [ ] **A.2. Worktree** — `feat/{N}-product-analytics-required` em `.worktrees/{N}-product-analytics-required/`
- [ ] **A.3. Lexis `lex-product-analytics-required` (pt-BR)** — `templates/lex-sample.md`. Conteúdo: HARD-GATE bloqueando ship de UI sem PostHog; preconditions (init + identify + pageview/screen + eventos de produto da feature); contra-pretextos ("é só um POC", "vamos adicionar depois", "é interno"); cláusula transitória "Fase A — report-only até débito catalogado"
- [ ] **A.4. Tradução `lex-product-analytics-required`** — es e en
- [ ] **A.5. Codex `codex-posthog-integration` (pt-BR)** — `templates/codex-sample.md`. Setup por stack: React (posthog-js), React Native (posthog-react-native), Flutter (posthog_flutter), Vanilla widget (CDN snippet), Python script com UI (posthog python). Padrões de `identify` sem PII (hash de user_id), opt-out, sampling
- [ ] **A.6. Tradução `codex-posthog-integration`** — es e en
- [ ] **A.7. `framework/platforms.yaml`** — registrar `lex-product-analytics-required` e `codex-posthog-integration` em `cursor.rules` (`lex-platforms-rules`)
- [ ] **A.8. Script `check_posthog.py`** — detector cross-stack: parsing de `package.json` (frontend), `pyproject.toml` (Python), `Podfile`/`Package.swift` (iOS), `build.gradle` (Android); regex de init/identify/capture; regex anti-PII (`cpf`, `email`, `phone`, `full_name`, `password`); output JSON
- [ ] **A.9. Tests do script** — fixtures por stack: app válido, app sem SDK, init sem identify, identify com email no payload, evento sem nome semântico ("button_clicked" vs "approval_submitted")
- [ ] **A.10. Kata `kata-product-analytics-check` (pt-BR)** — `templates/kata-sample.md`. Procedimento: detectar stack do target; rodar `check_posthog.py`; produzir relatório markdown com seções "✅ presentes / ⚠️ ausentes / ❌ violações"
- [ ] **A.11. Tradução `kata-product-analytics-check`** — es e en
- [ ] **A.12. Cry `cry-analytics-check` (pt-BR)** — `templates/cry-sample.md`. Args: `--scope working-tree|diff|pr <N>`, `--target frontend|mobile|skill <slug>|all`
- [ ] **A.13. Tradução `cry-analytics-check`** — es e en
- [ ] **A.14. Atualizar `lex-observability-required` (3 línguas)** — nota de cross-link
- [ ] **A.15. Atualizar `lex-feature-design-docs` (3 línguas)** — subcatálogo `metrics/` recebe `events.md` formal; cross-link para `lex-product-analytics-required`
- [ ] **A.16. Atualizar `kata-frontend-implement`, `kata-frontend-review`, `kata-mobile-implement` (3 línguas cada)** — cita Lex nova
- [ ] **A.17. Workflow `analytics-check.yml`** — modo report-only: checkout, setup Python, rodar `check_posthog.py` no diff, postar comment no PR, check sempre verde
- [ ] **A.18. Sync platforms** — `python3 scripts/install.py --self --target . --platform claude-code` + `--platform cursor`

### Fase B — Auditoria retroativa

- [ ] **B.1. Rodar `cry-analytics-check --scope working-tree --target all`** sobre `main` do Ahrena (escopo: skills existentes; framework não tem UI)
- [ ] **B.2. Repetir a auditoria nos repositórios consumidores conhecidos** (Guardia frontend, app mobile) — execução manual; documentar no baseline
- [ ] **B.3. Gerar `docs/analytics-debt/baseline-2026-05-08.md`** consolidando findings por target
- [ ] **B.4. Abrir issues de débito** — uma por target; label `analytics-debt`
- [ ] **B.5. Triagem** — corrigir agora / backlog / waiver

### Fase C — Validação cruzada

- [ ] **C.1. Validar Modo Cry manual** — `cry-analytics-check` em fixture limpa (zero findings) e fixture com violação induzida
- [ ] **C.2. Validar Modo CI** — abrir PR de teste com violação proposital; verificar comment correto
- [ ] **C.3. Acoplamento com plan-029** — se plan-029 já mergeado: editar `kata-skill-validate` (3 línguas) para invocar `check_posthog.py`. Se ainda não: anotar no PR description que plan-029 absorve o acoplamento

### Fase D — Ligar enforcement (em PR separado)

> **Não executar nesta PR.** Critério: débito Fase B reduzido a < 5 issues abertas OU 60 dias após Fase B fechar (o que vier primeiro).

- [ ] **D.1. Atualizar `lex-product-analytics-required`** — remover cláusula "Fase A — report-only", deixar HARD-GATE puro
- [ ] **D.2. Atualizar Action** — `report_only: false`; check vira `failure` em findings sem waiver
- [ ] **D.3. Documentar formato do waiver** em `lex-product-analytics-required` e `lex-pr-quality`
- [ ] **D.4. Anunciar** corte da Fase D no changelog

### Fechamento (Fase A)

- [ ] **E.1. Commits atômicos**: (1) `feat(quality): add lex-product-analytics-required + codex-posthog-integration`; (2) `feat(analytics): add check_posthog.py + tests`; (3) `feat(quality): add kata + cry analytics-check`; (4) `chore: cross-link existing katas/lexis to product analytics`; (5) `feat(ci): add analytics-check workflow in report-only`; (6) `chore: sync .claude and .cursor`
- [ ] **E.2. PR** — `Closes #{N}`, labels mirroring + `analytics`, size label, reviewers via CODEOWNERS

## Dependências

- **Pré-requisitos (existentes):**
  - `lex-observability-required` — referência de padrão (Lexis irmã)
  - `lex-hard-gate-pattern` — sintaxe do bloco
  - `lex-feature-design-docs` — subcatálogo `metrics/` será o registro de eventos por feature
  - `lex-template-usage`, `lex-pr-quality`, `lex-issue-quality`
  - Tooling MCP `github` (issues de débito + comments)
- **Acoplamento com plan-029 (soft):** plan-029 cria `kata-skill-validate`; este plano entrega `check_posthog.py` que será chamado lá. Ordem ideal: plan-030 mergeia primeiro; ordem aceitável: paralelo, com Step C.3 cobrindo o branch de qualquer ordem
- **Independente de plan-027 (Janus) e plan-028 (Mnemosyne)** estruturalmente. Reaproveita 100% do padrão fásico de plan-028 (build → backfill → validar → enforcement) e do mecanismo de waiver

## Riscos

| # | Risco                                                                                                       | Probabilidade | Mitigação                                                                                                                          |
|---|-------------------------------------------------------------------------------------------------------------|:-------------:|------------------------------------------------------------------------------------------------------------------------------------|
| 1 | Action em report-only nunca vira enforcement (mesma armadilha do plan-028)                                  | Alta          | Critério explícito de Fase D (débito < 5 OR 60d); revisão agendada                                                                  |
| 2 | Detector tem falsos positivos massivos em projetos com SDK wrapper customizado                              | Média         | Aceitar `analytics_sdk_wrapper` em `.ahrena/.directives` para apontar para wrapper local; check_posthog.py segue o ponteiro         |
| 3 | Regex anti-PII bloqueia legitimamente hash de e-mail (false positive)                                       | Média         | Lista allow-list por contexto: `email_hash`, `phone_hash`, `tax_id_last4` permitidos                                               |
| 4 | Multilingue incompleto                                                                                       | Média         | Steps separados por língua; Mnemosyne (plan-028) flagaria como par 1 quando ativo                                                  |
| 5 | "Eventos de produto declarados" vira escopo aberto sem catálogo                                             | Alta          | Step A.15 ancora em `lex-feature-design-docs` subcatálogo `metrics/events.md`. Sem evento declarado por feature, check pula etapa "eventos" e roda só init/identify/pageview |
| 6 | Conflito com privacidade/LGPD: identificação cross-device pode disparar consentimento exigido               | Média         | Codex `codex-posthog-integration` documenta `respect_dnt`, opt-in explícito, anonymous-first até consent; cross-link para LGPD     |
| 7 | Acoplamento com plan-029 cria deadlock se ambos esperam ordem                                                | Baixa         | Step C.3 explícito cobre os dois sentidos; soft coupling por design                                                                |
| 8 | Custo de PostHog em projetos grandes (event volume)                                                         | Baixa         | Codex documenta sampling, batching, e quando usar self-hosted vs cloud                                                             |

## Decisões em aberto (a tratar na execução)

- **Subclade da Lex confirmada `_foundation/quality/`** (espelha `lex-observability-required`).
- **Subclade do Codex confirmada `engineering/analytics/`** (nova, abre espaço para futuros codex de feature flags / experimentação).
- **Quatro eventos mínimos** vs lista mais ampla: começar com 4 (init, identify, pageview/screen, eventos de produto declarados). Validar com PM/Growth se "outros eventos universais" devem entrar (e.g., session_start, error_boundary).
- **Anonymous-first vs identify-on-load**: Codex recomenda anonymous-first com upgrade pós-login; revisar com legal por causa de LGPD.
- **Eventos de produto: schema canônico?** — defer. Plano futuro pode codificar event schema (`{event_name, properties: {feature, action, surface, ...}}`) em `lex-event-naming` (analytics-side, distinta de `lex-entity-naming`).
