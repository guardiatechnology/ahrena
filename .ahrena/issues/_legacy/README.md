# `.issues/_legacy/` — Histórico de planos anteriores a ADR-002

Este diretório preserva, **imutável**, os planos do framework Ahrena criados sob o modelo legado de armazenamento (arquivo Markdown committed em `.claude/plans/`), encerrados antes da introdução de ADR-002 (modelo Issue-as-plan em três camadas).

## Por que existe

Per a Open Question #1 de plan-046 (resolvida em 2026-05-11):

> Mover `.claude/plans/archived/` → `.issues/_legacy/` via `git mv` preserva history. README declara congelamento.

A migração foi feita no PR #97 (closes #96).

## O que vive aqui

Planos terminados (`done` ou `abandoned`) cujo ciclo completo aconteceu **antes** de plan-046 mergear. Cada arquivo mantém o YAML front-matter histórico:

```yaml
---
plan_id: "NNN"
title: "slug"
status: done | abandoned
agent: claude
issue: "owner/repo#N"
branch: "type/N-slug"
worktree: ".worktrees/N-slug"
created_at: "..."
updated_at: "..."
merge_commit: "sha"          # opcional, audit
closed_at: "..."             # opcional, audit
---
```

Os campos `merge_commit:` e `closed_at:` permanecem reconhecidos como front-matter opcional aceito per `lex-agent-planning` (modelo novo) — preserva o audit dos plans 043-045 e anteriores sem retrofit.

## O que NÃO vive aqui

- **Planos novos.** A partir de ADR-002, o plano canônico vive no body da Issue do GitHub. `.plans/{N}.md` (gitignored) é cache local da IA. Não criar arquivo Markdown de plano aqui.
- **Phase artifacts.** Documentos das Phases do fluxo Issue-Driven (`01-brief.md` … `06-quality-report.md`) vivem em `.issues/{N}/`, não aqui. Este diretório é exclusivamente histórico congelado.

## Regras

- **Não editar arquivos aqui.** O conteúdo é imutável: representa decisões já registradas e ciclos já encerrados.
- **Não adicionar arquivos novos aqui.** Para novos planos, abrir Issue e seguir `kata-plan-task`.
- **Pode ser consultado livremente** para entender contexto histórico, decisões precedentes, e o caminho até ADR-002.

## Referências

- ADR-002 — `docs/adr/ADR-002-issue-as-plan-three-layer-storage.md`
- `lex-agent-planning` — modelo de 3 camadas
- plan-046 — PR #97 (Closes #96) — migração desta pasta
