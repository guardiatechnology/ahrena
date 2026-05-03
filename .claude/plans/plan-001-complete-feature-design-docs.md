---
plan_id: "001"
title: "complete-feature-design-docs"
status: done
agent: claude
issue: "guardiatechnology/ahrena#34"
created_at: "2026-05-02T14:30:00Z"
updated_at: "2026-05-03T12:00:00Z"
---

# Plano: Concluir migração feature-design-docs — atualizar cries e katas

## Objetivo

Concluir a atualização dos Cries e katas que ainda referenciam `paths.oas`, `paths.events` e `paths.domain` após a introdução de `lex-feature-design-docs`. Warriors, katas principais e os novos artefatos `_foundation` de planejamento já foram criados nesta sessão; o que falta são os Cries (entry points do usuário) e 2 katas com referências residuais, além de todos os seus equivalentes en/es e os .cursor/commands correspondentes.

## Escopo

**Cries (4 × 3 línguas = 12 arquivos):**
- `framework/pt-BR/engineering/platform/cries/cry-api-design.md` — 8 refs a `paths.oas`
- `framework/pt-BR/engineering/platform/cries/cry-event-storm.md` — 7 refs a `paths.events`
- `framework/pt-BR/engineering/platform/cries/cry-feature-design.md` — 5 refs a `paths.domain`/`paths.oas`/`paths.events`
- `framework/pt-BR/engineering/platform/cries/cry-full-design.md` — 9 refs a `paths.oas`/`paths.events`
- Equivalentes em `framework/en/` e `framework/es/` (mesma estrutura)

**Katas (2 × 3 línguas = 6 arquivos):**
- `framework/pt-BR/engineering/platform/katas/kata-api-design-review.md` — 1 ref a `paths.oas`
- `framework/pt-BR/engineering/platform/katas/kata-api-design-doc.md` — 3 refs stale a `.ahrena/.directives` (linhas 41, 83, 110)
- Equivalentes em `framework/en/` e `framework/es/`

**Cursor derivatives (cries têm skills e commands):**
- `.cursor/commands/` correspondentes aos 4 cries
- `.cursor/skills/` correspondentes aos 4 cries (se existirem)

**Novos artefatos de planejamento (já criados nesta sessão, ainda uncommitted):**
- `framework/pt-BR/_foundation/process/lexis/lex-agent-planning.md`
- `framework/pt-BR/_foundation/process/codex/codex-agent-planning.md`
- `framework/pt-BR/_foundation/process/katas/kata-plan-task.md`
- Equivalentes `framework/en/` e `framework/es/`
- `.cursor/rules/_foundation/process/lex-agent-planning.mdc`
- `.cursor/rules/_foundation/process/codex-agent-planning.mdc`
- `.cursor/skills/kata-plan-task/SKILL.md`
- `.claude/rules/_foundation/process/lex-agent-planning.md`
- `.claude/rules/_foundation/process/codex-agent-planning.md`
- `.claude/skills/kata-plan-task/SKILL.md`
- `framework/platforms.yaml` (2 novas entradas + todas as modificações anteriores)

Total estimado: ~30 arquivos.

## Etapas

- [x] 1. Abrir issue no GitHub para rastrear o trabalho de migração dos cries
- [x] 2. Criar branch `feat/{N}-complete-feature-design-docs`
- [x] 3. Atualizar `cry-api-design.md` (pt-BR, en, es) — remover refs a `paths.oas`
- [x] 4. Atualizar `cry-event-storm.md` (pt-BR, en, es) — remover refs a `paths.events`
- [x] 5. Atualizar `cry-feature-design.md` (pt-BR, en, es) — remover refs a `paths.domain`/`paths.oas`/`paths.events`
- [x] 6. Atualizar `cry-full-design.md` (pt-BR, en, es) — remover refs a `paths.oas`/`paths.events`
- [x] 7. Atualizar `kata-api-design-review.md` (pt-BR, en, es) — corrigir 1 ref a `paths.oas`
- [x] 8. Corrigir `kata-api-design-doc.md` (pt-BR, en, es) — linhas ~41, ~83, ~110 que referenciam `.ahrena/.directives` de forma stale
- [x] 9. Verificar e atualizar `.cursor/commands/` correspondentes aos 4 cries
- [x] 10. Commitar todos os artefatos (novos artefatos de planejamento + warriors/katas já modificados + cries + katas)
- [x] 11. Abrir PR referenciando a issue

## Dependências

- Trabalho anterior (uncommitted): `lex-feature-design-docs`, `codex-feature-design-docs`, `kata-feature-design-docs`, warriors (prometheus, theseus, daedalus, kronos), katas (domain-model, api-design-oas, event-storm, events-doc)
- Novos artefatos de planejamento criados nesta sessão (uncommitted): `lex-agent-planning`, `codex-agent-planning`, `kata-plan-task` (pt-BR, en, es + cursor + claude derivatives)
- `framework/platforms.yaml` já atualizado (uncommitted)

## Riscos

- Cries em en/es ainda não foram modificados — usar versões pt-BR como fonte de verdade para as traduções
- `cry-feature-design` tem 3 tipos de paths stale (`paths.domain`, `paths.oas`, `paths.events`) — verificar todas as ocorrências
- `kata-api-design-doc` tem refs stale nas linhas ~41, ~83, ~110 — ler o arquivo antes de editar para localizar com precisão
- `.cursor/commands/` dos cries podem ter referências similares — verificar antes de concluir
