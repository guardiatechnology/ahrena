---
id: "rust-framework-support/insights/001-advanced-rust-lexis-codex"
topic: "rust-framework-support"
status: approved
source_refs:
  - "https://github.com/guardiatechnology/ahrena/pull/1"
tags:
  - rust
  - production-quality
  - async
  - unsafe
  - ffi
  - error-handling
created_at: "2026-05-22T04:09:25Z"
updated_at: "2026-05-22T04:09:25Z"
merged_into: null
idea_ref: null
rejected_reason: null
awaiting_evidence_reason: null
---

# Insight: Demanda interna por Lexis/Codex Rust focados em qualidade de produção

## Observação

A PR #1 (`feat/rust-agentic-guides-v2`) propôs 16 arquivos (~1546 linhas) com Lexis e Codex Rust voltados a qualidade em código de produção: panic-free (`lex-rust-no-panic-in-production`), isolamento de blocos `unsafe` (`lex-rust-unsafe-isolation`), proibição de bloqueio em contextos assíncronos (`lex-rust-no-blocking-in-async`), tipos de erro próprios em bibliotecas (`lex-rust-library-error-types`, `lex-rust-library-must-define-error-type`), `#[non_exhaustive]` em tipos públicos extensíveis, ausência de assunção de UTF-8 em I/O bruto, e proibição de recompilar regex em loops. Os Codex acompanham com `codex-rust-async-architecture` (Tokio, JoinSet, graceful shutdown, actor pattern), `codex-rust-system-design` (workspaces, batching, FSM, tracing), `codex-rust-api-design`, `codex-rust-burntsushi-ecosystem`, `codex-rust-error-handling`, `codex-rust-oss-maintenance` e `codex-rust-performance-and-search`. A PR está aberta desde a v2 dos guias agênticos sem caminho declarado de adoção no framework atual.

## Fonte

- PR #1 (`feat(rust): Lexis e Codex avançados para desenvolvimento agêntico em Rust`): 16 arquivos adicionados, ~1546 linhas, estrutura em `framework/pt-BR/engineering/rust/{lexis,codex}/`
- Tabela de fontes declaradas na descrição da PR: ripgrep, tokio, tikv, meilisearch, alacritty, burntsushi.net — 6 repositórios/blogs de referência da indústria estudados como base empírica para os padrões propostos

## Implicação inicial

O framework Ahrena não cobre Rust como linguagem de engenharia formalmente suportada — `engineering/backend` codifica Python; `engineering/frontend` codifica TS/React; não há clade ou subclade Rust. A existência da PR #1 demonstra que há trabalho técnico já investido e demanda interna por governance equivalente em Rust. Capturar essa demanda como Discovery dá ao framework uma decisão consciente de priorização (adotar, refinar ou rejeitar) em vez de deixar o material em limbo de PR aberta.

## Perguntas em aberto

- Qual a prioridade de Rust como linguagem suportada vs. expansão de outras stacks (Go, Kotlin, Swift)?
- Quem mantém a clade `engineering/rust/` depois de mergeada — há owner declarado entre os times Guardia?
- Como integrar Lexis transversais já existentes (`lex-logging-decorator`, `lex-test-pyramid`, `lex-dry`) à clade Rust sem duplicação ou contradição?
- A escolha de basear-se em ripgrep/tokio/tikv/meilisearch/alacritty reflete os perfis reais de workloads Rust planejados na Guardia (CLI, runtime async, storage engine, search, terminal)?
- Há overlap entre os Lexis propostos aqui (#1) e os Lexis didáticos da PR #2 — em especial `error-handling`, `library-must-define-error-type`, `no-panic`, `ffi-safety` — que demanda consolidação?
