---
id: "rust-framework-support/insights/002-rust-mit-book-guides"
topic: "rust-framework-support"
status: approved
source_refs:
  - "https://github.com/guardiatechnology/ahrena/pull/2"
tags:
  - rust
  - onboarding
  - fundamentals
  - ownership
  - concurrency
  - traits
  - testing
created_at: "2026-05-22T04:09:25Z"
updated_at: "2026-05-22T04:09:25Z"
merged_into: null
idea_ref: null
rejected_reason: null
awaiting_evidence_reason: null
---

# Insight: Demanda por material curado de fundamentos Rust para onboarding agêntico

## Observação

A PR #2 (`feat/rust-mit-book-guides`) propôs 16 arquivos (~1444 linhas) com Lexis e Codex Rust derivados do MIT Rust Book (Primeira Edição) cobrindo fundamentos da linguagem: ownership e borrowing (`lex-rust-ownership-borrowing`), tipos de string `&str` vs `String` (`lex-rust-string-types`), segurança em FFI e isolamento de `unsafe` (`lex-rust-ffi-safety`), traits e generics com polimorfismo estático vs dinâmico (`codex-rust-traits-generics`), garantias de concorrência (Send/Sync, Box/Rc/Arc/Mutex/RwLock) (`codex-rust-concurrency-guarantees`) e testes/documentação (`codex-rust-testing-docs`). A PR declara como fontes os capítulos do MIT Rust Book sobre Ownership, References & Borrowing, Lifetimes, Strings, Deref Coercions, Concurrency, Stack vs Heap, Testing, Documentation, Traits, Generics, Closures, Iterators, Associated Types, Unsafe, Raw Pointers, FFI, Macros. Há overlap declarado entre Lexis desta PR e a PR #1 — em especial `lex-rust-library-must-define-error-type`, `lex-rust-no-assume-utf8-on-io`, `lex-rust-no-panic-in-production`, `lex-rust-no-regex-compilation-in-loops` aparecem nas duas PRs.

## Fonte

- PR #2 (`feat(rust): Guias MIT Book — Ownership, Concorrência, Traits, Testes e FFI`): 16 arquivos, ~1444 linhas, mesma estrutura `framework/pt-BR/engineering/rust/{lexis,codex}/`
- Descrição declara como base o MIT Rust Book Primeira Edição, com 3 Lexis novos e 3 Codex novos
- Sobreposição com PR #1: 4 dos 16 arquivos têm path idêntico ao da PR #1 (`lex-rust-library-must-define-error-type.md`, `lex-rust-no-assume-utf8-on-io.md`, `lex-rust-no-panic-in-production.md`, `lex-rust-no-regex-compilation-in-loops.md`), mais o `README.md` da clade — indicando que as duas PRs colidiriam em merge sequencial

## Implicação inicial

Existe uma segunda frente de trabalho técnico Rust, com viés pedagógico/didático, separada da frente de qualidade-de-produção da PR #1. O onboarding de engineers em Rust no contexto Guardia/agêntico hoje depende de cada pessoa coletar referências do Rust Book / Rustacean por conta própria. Capturar este material como Discovery permite decidir entre (a) consolidar didática + produção em uma única clade `engineering/rust/`, (b) separar em duas subclades (`fundamentals/` + `production/`), ou (c) tratar o material didático como Codex referencial sem promover a Lexis.

## Perguntas em aberto

- A sobreposição com a PR #1 nos arquivos `library-must-define-error-type`, `no-assume-utf8-on-io`, `no-panic-in-production`, `no-regex-compilation-in-loops` indica versões divergentes do mesmo Lexis — qual delas é a canônica?
- O material didático do MIT Rust Book deveria ser Codex (manual de referência) ou Lexis (lei aplicável a PRs)? Por exemplo: `lex-rust-ownership-borrowing` proíbe usar `clone()`/`Rc` "sem justificativa" — isso é regra automatizável por clippy ou critério de revisão humana?
- Qual é o tamanho real do público interno transitioning para Rust (medido por entrevistas ou survey) que justifica investimento didático curado?
- Time-to-first-PR Rust atual é mensurável retroativamente em algum dataset interno (PRs com header Rust, histórico de commits)?
- Vale referenciar o Rust Book / Rustacean explicitamente nos Codex (com permalink) ou reescrever o conteúdo internamente?
