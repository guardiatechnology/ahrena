# Engenharia Rust - Ahrena Framework

Este diretório contém os guias (Lexis e Codex) para desenvolvimento agêntico e de sistemas em Rust dentro do ecossistema Guardia Finance.

O conteúdo aqui foi consolidado a partir do estudo das melhores práticas da comunidade Rust, dos crates fundamentais mantidos por Andrew Gallant (BurntSushi), de grandes projetos open source (TiKV, Tokio, Alacritty, Meilisearch, Ripgrep) e do livro clássico de Rust do MIT.

## Lexis (Leis Inquebráveis)

Lexis são regras absolutas que não devem ser violadas no desenvolvimento de produção.

- `lex-rust-no-panic-in-production`: Proíbe o uso de `unwrap()`, `expect()` e `panic!` para erros recuperáveis em produção.
- `lex-rust-no-assume-utf8-on-io`: Proíbe assumir UTF-8 em I/O não validado.
- `lex-rust-no-regex-compilation-in-loops`: Proíbe compilar expressões regulares dentro de loops ou caminhos quentes.
- `lex-rust-library-must-define-error-type`: Exige que bibliotecas definam seus próprios tipos de erro (não use `anyhow` em API pública).
- `lex-rust-unsafe-isolation`: Exige que todo código `unsafe` seja isolado e documentado com `// SAFETY:`.
- `lex-rust-no-blocking-in-async`: Proíbe I/O síncrono e CPU-bound em funções assíncronas (sem `spawn_blocking`).
- `lex-rust-library-error-types`: (Complemento) Restrições sobre `anyhow` vs `thiserror`.
- `lex-rust-non-exhaustive-types`: Exige o uso de `#[non_exhaustive]` para tipos públicos extensíveis.
- `lex-rust-ownership-borrowing`: O Sistema de Ownership e Borrowing deve ser respeitado, não contornado (evite `clone` e `Rc` desnecessários).
- `lex-rust-string-types`: Use `&str` para leitura e `String` para posse e mutação.
- `lex-rust-ffi-safety`: Interfaces FFI e blocos `unsafe` DEVEM ser encapsulados em abstrações seguras.

## Codex (Manuais de Referência)

Codex são guias de design, arquitetura e melhores práticas.

- `codex-rust-error-handling`: Guia definitivo sobre `Result`, `Option`, `thiserror` e `anyhow`.
- `codex-rust-performance-and-search`: Técnicas de performance (SIMD, NFA/DFA, FST, alocações amortizadas).
- `codex-rust-api-design`: Padrões de design de API (Builder, Tipos Genéricos, SemVer).
- `codex-rust-burntsushi-ecosystem`: Mapa do ecossistema de crates de BurntSushi (`regex`, `bstr`, `fst`, etc).
- `codex-rust-oss-maintenance`: Filosofia de manutenção open source (sustentabilidade, limites, gestão de issues).
- `codex-rust-async-architecture`: Arquitetura assíncrona com Tokio (JoinSet, Actor Pattern, Graceful Shutdown).
- `codex-rust-system-design`: Padrões de design de sistemas complexos (Batching, Event Loops, Engine Traits, FSM).
- `codex-rust-concurrency-guarantees`: Concorrência e primitivas de memória (`Send`, `Sync`, `Arc`, `Mutex`, `RwLock`).
- `codex-rust-testing-docs`: Práticas de testes (Unitários, Integração) e documentação (`rustdoc`).
- `codex-rust-traits-generics`: Polimorfismo estático (Generics) vs dinâmico (Trait Objects) e regras de traits.
