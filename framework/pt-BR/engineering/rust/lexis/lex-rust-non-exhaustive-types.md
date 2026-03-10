# Lexis: Extensibilidade Segura com `#[non_exhaustive]`

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebrável | **Escopo:** Design de API Pública

## Propósito
Quando um `enum` ou `struct` público é modificado (adicionando uma nova variante ou campo), qualquer código cliente que faça pattern matching exaustivo ou inicialização literal quebrará, resultando em uma *breaking change* (exigindo bump de MAJOR version no SemVer). Para evitar a estagnação de APIs e permitir a evolução contínua sem quebrar a compatibilidade com versões anteriores, tipos públicos que têm potencial de crescimento devem ser explicitamente marcados como não-exaustivos.

## Lei
> **Todo `enum` de erro (`ErrorKind`), `enum` de configuração e `struct` público que não tenha sua representação matemática/lógica estritamente fechada e finalizada DEVE ser anotado com o atributo `#[non_exhaustive]`. Além disso, `structs` públicos devem fornecer métodos construtores (ex: `new()`) ou o padrão Builder.**

## Abrangência
- **Aplica-se a:** Todas as APIs públicas (`pub`) exportadas por bibliotecas ou módulos de domínio.
- **Agentes vinculados:** Todos os agentes de IA e desenvolvedores humanos.
- **Exceções:** Tipos cuja definição é matematicamente fechada (ex: `Option<T>`, `Result<T, E>`, `Coordinate { x, y }`) não devem usar `#[non_exhaustive]`.

## Consequências de Violação
1. **Quebra de Contrato:** Adicionar um campo ou variante no futuro quebrará o código dos usuários, violando as promessas do SemVer.
2. **Refatoração Forçada:** Se um tipo público for publicado sem `#[non_exhaustive]` e precisar crescer, será necessário criar um novo tipo ou forçar um bump de versão MAJOR indesejado.
3. **Bloqueio de PR:** Revisores (humanos ou IA) bloquearão o merge de tipos públicos abertos à evolução que omitam o atributo.

## Exemplos

### Correto

```rust
// CORRETO: O enum de erro pode crescer no futuro sem quebrar clientes
#[derive(Debug)]
#[non_exhaustive]
pub enum ErrorKind {
    Io(std::io::Error),
    Parse(String),
    // Se adicionarmos `Timeout` amanhã, o código cliente não quebra
    // porque eles foram forçados a usar um branch `_ => {}` no match.
}

// CORRETO: A struct de configuração pode receber novos campos
#[derive(Debug, Default)]
#[non_exhaustive]
pub struct Config {
    pub timeout_secs: u64,
    pub retries: u32,
}

impl Config {
    pub fn new() -> Self {
        Self::default()
    }
}
```

### Incorreto

```rust
// VIOLAÇÃO 1: Enum de erro sem non_exhaustive.
// Qualquer nova variante no futuro quebrará todos os matches dos clientes.
pub enum BadErrorKind {
    Database(String),
    Network(String),
}

// VIOLAÇÃO 2: Struct pública sem non_exhaustive e sem métodos de construção.
// Clientes instanciarão com `BadConfig { port: 80 }`.
// Se adicionarmos `host: String` amanhã, todo o código cliente quebra.
pub struct BadConfig {
    pub port: u16,
}
```

## Validação Automatizada
- **Ferramenta:** Revisão de código e linters de API (ex: `cargo-public-api`).
- **Momento:** Revisão de Pull Request e CI.
- **Métrica:** 0 violações em tipos de erro e configuração.

---
**Fontes de Conhecimento:**
- Repositório Ripgrep: Uso sistemático de `#[non_exhaustive]` em `crates/regex/src/error.rs` e `crates/searcher/src/searcher/mod.rs`.
- Repositório Tokio: Padrões rigorosos de evolução de API sem quebra de compatibilidade.
