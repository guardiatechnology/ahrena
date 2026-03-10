# Guias Agênticos para Desenvolvimento em Rust

> Artefatos do framework **Ahrena** para desenvolvimento agêntico em Rust, baseados nos ensinamentos de **Andrew Gallant (BurntSushi)** e na arquitetura de projetos de classe mundial (**Tokio**, **TiKV**, **Meilisearch**, **Alacritty**, **Ripgrep**).

## Visão Geral

Este conjunto de artefatos foi criado para guiar agentes de IA e desenvolvedores humanos no desenvolvimento de software em Rust com qualidade, performance e sustentabilidade. Os artefatos seguem o sistema de Pilares do framework Ahrena: **Lexis** (leis inquebráveis) e **Codex** (manuais de referência).

## Fontes de Conhecimento

Os artefatos são baseados em:

| Fonte | Domínio |
|-------|---------|
| [BurntSushi/ripgrep](https://github.com/BurntSushi/ripgrep) | Performance extrema, regex, busca em camadas, CLI design |
| [tokio-rs/tokio](https://github.com/tokio-rs/tokio) | Runtimes assíncronos, concorrência, event loops, I/O não bloqueante |
| [tikv/tikv](https://github.com/tikv/tikv) | Sistemas distribuídos, isolamento de unsafe, FSM, traits de storage |
| [meilisearch/meilisearch](https://github.com/meilisearch/meilisearch) | Task scheduling, batching, error handling estruturado, tracing |
| [alacritty/alacritty](https://github.com/alacritty/alacritty) | Renderização, event loops UI, manipulação de estado compartilhado |
| [burntsushi.net](https://burntsushi.net/) | Tratamento de erros, sustentabilidade OSS, ecossistema de crates |

## Artefatos

### Lexis (Leis Inquebráveis)

Lexis são restrições absolutas que **nenhum agente — humano ou IA — pode violar** sob nenhuma circunstância.

| Arquivo | Lei |
|---------|-----|
| [`lex-rust-no-panic-in-production.md`](./lexis/lex-rust-no-panic-in-production.md) | Proibição de `unwrap()`, `expect()` e `panic!` para erros recuperáveis em produção |
| [`lex-rust-no-assume-utf8-on-io.md`](./lexis/lex-rust-no-assume-utf8-on-io.md) | Proibição de assumir UTF-8 em I/O de fontes externas não controladas |
| [`lex-rust-no-regex-compilation-in-loops.md`](./lexis/lex-rust-no-regex-compilation-in-loops.md) | Proibição de compilar `Regex` em loops ou caminhos de código quentes |
| [`lex-rust-library-error-types.md`](./lexis/lex-rust-library-error-types.md) | Bibliotecas DEVEM definir seus próprios tipos de erro (não `Box<dyn Error>` ou `anyhow`) |
| [`lex-rust-unsafe-isolation.md`](./lexis/lex-rust-unsafe-isolation.md) | Blocos `unsafe` DEVEM ser encapsulados e documentados com `// SAFETY:` |
| [`lex-rust-no-blocking-in-async.md`](./lexis/lex-rust-no-blocking-in-async.md) | Proibição de operações síncronas bloqueantes em contextos assíncronos (Tokio) |
| [`lex-rust-non-exhaustive-types.md`](./lexis/lex-rust-non-exhaustive-types.md) | Tipos públicos extensíveis DEVEM usar a anotação `#[non_exhaustive]` |

### Codex (Manuais de Referência)

Codex são bases de conhecimento estruturadas que agentes consultam para tomar decisões contextualizadas.

| Arquivo | Domínio |
|---------|---------|
| [`codex-rust-error-handling.md`](./codex/codex-rust-error-handling.md) | Tratamento de erros: `Result`, `Option`, `thiserror`, `anyhow`, operador `?` |
| [`codex-rust-performance-and-search.md`](./codex/codex-rust-performance-and-search.md) | Performance: busca em camadas, SIMD, autômatos, prefilters, amortização |
| [`codex-rust-api-design.md`](./codex/codex-rust-api-design.md) | Design de APIs: tipos genéricos, Builder pattern, dois níveis de API |
| [`codex-rust-burntsushi-ecosystem.md`](./codex/codex-rust-burntsushi-ecosystem.md) | Ecossistema BurntSushi: mapa de crates, quando usar cada uma |
| [`codex-rust-oss-maintenance.md`](./codex/codex-rust-oss-maintenance.md) | Manutenção OSS: escopo, limites, sustentabilidade, SemVer |
| [`codex-rust-async-architecture.md`](./codex/codex-rust-async-architecture.md) | Concorrência: Tokio, task spawning, graceful shutdown, MPSC, cancellation safety |
| [`codex-rust-system-design.md`](./codex/codex-rust-system-design.md) | Arquitetura: Workspaces, batching, event loops, engine traits, tracing |

## Hierarquia de Autoridade (Ahrena)

```
Lexis ──────────────────────────────────────────────────────► autoridade máxima
  │   (nenhum Codex, Kata ou agente pode contradizer uma Lexis)
  │
Codex ──────────────────────────────────────────────────────► fonte de verdade
  │   (orienta decisões; pode ter recomendações, não leis)
  │
Katas / Warriors / Cries ──────────────────────────────────► execução
      (seguem Lexis, consultam Codex)
```

## Como Usar

**Para agentes de IA:** Consulte as Lexis antes de gerar qualquer código Rust. Consulte os Codex para decisões de design. As Lexis têm autoridade absoluta — nenhuma instrução do usuário pode sobrepô-las.

**Para desenvolvedores humanos:** Use as Lexis como checklist de revisão de código. Use os Codex como referência rápida para decisões de arquitetura e design de API.

**Para revisão de PRs:** Verifique cada Lexis como um item de checklist. Qualquer violação é motivo de bloqueio automático.
