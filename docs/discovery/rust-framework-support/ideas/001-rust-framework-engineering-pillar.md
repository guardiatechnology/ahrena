---
id: "rust-framework-support/ideas/001-rust-framework-engineering-pillar"
topic: "rust-framework-support"
problem: "O framework Ahrena não cobre Rust como linguagem de engenharia formalmente suportada, embora exista trabalho técnico interno já investido (PR #1, ~1546 linhas) propondo Lexis e Codex Rust focados em qualidade de produção; times que adotam Rust ficam sem governance equivalente à de Python e TypeScript."
hypothesis: "Se o framework consolidar uma clade engineering/rust/ com pelo menos 8 Lexis aplicáveis (unsafe isolation, panic-free, no-blocking-in-async, library error types, non-exhaustive types, no-regex-in-loops, no-assume-utf8, ffi-safety) e 7 Codex (api-design, async-architecture, system-design, error-handling, performance, oss-maintenance, burntsushi-ecosystem), os times Rust adotarão o framework com paridade aos times Python, medido pela cobertura de Lexis aplicáveis em PRs Rust de pelo menos 80% em 90 dias após release."
target_user: "Engineers (Guardia ou consumidores externos do framework) que escrevem Rust em projetos de produção — runtime async (Tokio), CLI tools, storage engines, search, serviços de baixa latência"
success_metric: "Número de Lexis e Codex Rust ativos no framework — baseline 0 (estado atual em main) → target 8 Lexis e 7 Codex em uma release minor; secundário: 100% das PRs Rust subsequentes referenciam pelo menos 1 Lexis Rust no body"
effort_estimate: "M (1-2 sprints — material técnico já existe na PR #1; o trabalho é revisão de conteúdo, adaptação aos templates Ahrena atuais, tri-tradução pt-BR/es/en, resolução do overlap com a PR #2, e registro das entradas em framework/platforms.yaml conforme lex-platforms-rules)"
linked_insights:
  - "rust-framework-support/insights/001-advanced-rust-lexis-codex"
created_at: "2026-05-22T04:09:25Z"
updated_at: "2026-05-22T04:09:25Z"
---

# Idea: Formalizar Rust como pilar de engenharia no framework Ahrena

## Síntese

A PR #1 já investiu trabalho técnico substancial (16 arquivos, ~1546 linhas, baseado em 6 fontes da indústria — ripgrep, tokio, tikv, meilisearch, alacritty, burntsushi.net) propondo Lexis e Codex Rust focados em qualidade de produção. Promover esse material a uma clade `engineering/rust/` formal dá ao framework cobertura de Rust comparável à atual em Python e TypeScript, e converte a PR em limbo em adoção governada. A hipótese central é que governance disponível leva a adoção mensurável (80% de cobertura em PRs Rust em 90 dias), validável após a release minor.

## Insights de origem

1. **rust-framework-support/insights/001-advanced-rust-lexis-codex** — PR #1 propôs 16 arquivos com 8 Lexis (unsafe isolation, panic-free, no-blocking-in-async, library error types, non-exhaustive types, no-assume-utf8, no-regex-in-loops, ffi-safety) e 7 Codex (api design, async architecture, system design, error handling, performance, oss maintenance, burntsushi ecosystem); material derivado do estudo de ripgrep, tokio, tikv, meilisearch, alacritty e do blog de Andrew Gallant.

## Próximos passos

- Resolver o overlap declarado com a PR #2 (4 arquivos com path idêntico): decidir a versão canônica de cada Lex em conflito antes de promover qualquer um dos materiais ao framework
- Identificar um owner declarado para a clade `engineering/rust/` antes de mergear o material (sem owner, o material acumula débito de manutenção)
- Confirmar com o time Guardia se os perfis de workload representados pelas fontes da PR #1 (CLI, runtime async, storage, search, terminal) refletem os usos reais ou planejados de Rust internamente
- Mapear interseção com Lexis transversais existentes (`lex-logging-decorator`, `lex-test-pyramid`, `lex-dry`) e garantir que a clade Rust referencia em vez de duplicar
- Decidir se a tri-tradução (pt-BR/es/en) entra como parte do escopo desta release ou como release subsequente, considerando que `lex-framework-language` exige completude em `language.i18n`
