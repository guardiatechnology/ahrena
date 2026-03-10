# Codex: Design de APIs e Bibliotecas em Rust

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Design e Publicação de Bibliotecas Rust (crates)

## Visão Geral

Este Codex documenta os princípios e padrões para o design de APIs públicas em bibliotecas Rust. Uma boa API Rust é fácil de usar corretamente, difícil de usar incorretamente, ergonômica, e tira proveito do sistema de tipos para codificar invariantes em tempo de compilação. É baseado em anos de experiência de Andrew Gallant (BurntSushi) projetando e mantendo crates amplamente usados como `regex`, `csv`, `bstr`, `fst`, `walkdir`, `byteorder` e `aho-corasick`.

## Contexto

- **Domínio:** Design de API pública, ergonomia, tipos de erro, convenções de nomenclatura e estrutura de crates em Rust.
- **Público-alvo:** Agentes de IA (Warriors), desenvolvedores que criam bibliotecas Rust, arquitetos de plataforma.
- **Atualização:** Quando novas convenções da comunidade Rust (Rust API Guidelines) forem atualizadas ou quando novos padrões emergirem no ecossistema.

## Conteúdo

### Princípios

1. **Tipos de erro ricos em bibliotecas:** Bibliotecas DEVEM definir seus próprios tipos de erro (usando `thiserror`). Usar `Box<dyn Error>` ou `anyhow::Error` em APIs públicas apaga informação de tipo e remove a capacidade do chamador de tratar erros específicos de forma diferenciada.
2. **Aceite o mais genérico possível:** Prefira `&str` a `String`, `&[u8]` a `Vec<u8>`, `impl AsRef<Path>` a `&Path` ou `&str` para caminhos. Isso evita alocações desnecessárias do lado do chamador.
3. **Retorne o mais específico possível:** Retorne tipos concretos em vez de `impl Trait` quando o tipo concreto é estável e útil. Retorne `impl Iterator<Item=T>` quando o tipo concreto é um detalhe de implementação.
4. **APIs de alta performance oferecem variantes de zero alocação:** Para operações em hot paths, forneça variantes que aceitam buffers mutáveis (`&mut Vec<u8>`, `&mut String`) para amortizar alocações, além das variantes convenientes que retornam valores novos.
5. **Invariantes em tempo de compilação quando possível:** Use o sistema de tipos para tornar estados inválidos irrepresentáveis. Quando não for possível mover um invariante para o tipo, documente-o claramente e use `panic!` com `expect()` descritivo para sinalizar violações.

### Padrões e Convenções

| Aspecto | Padrão | Exemplo |
|---------|--------|---------|
| Parâmetros de string | `&str` ou `impl AsRef<str>` | `fn buscar(padrao: &str) -> ...` |
| Parâmetros de bytes | `&[u8]` ou `impl AsRef<[u8]>` | `fn encontrar(haystack: &[u8]) -> ...` |
| Parâmetros de caminho | `impl AsRef<Path>` | `fn abrir<P: AsRef<Path>>(caminho: P) -> ...` |
| Tipo de erro em biblioteca | Enum customizado com `#[derive(thiserror::Error)]` | `#[error("padrão inválido: {0}")] InvalidPattern(String)` |
| Alias de Result | `type Result<T> = std::result::Result<T, MeuErro>` | `pub type Result<T> = std::result::Result<T, RegexError>` |
| Implementação de From | Para cada erro externo que pode ocorrer | `impl From<io::Error> for MeuErro { ... }` |
| Builder pattern | Para tipos com muitas opções de configuração | `RegexBuilder::new(padrao).case_insensitive(true).build()` |
| Métodos de conveniência | Variantes de alto nível sobre primitivas de baixo nível | `Regex::is_match()` sobre `Regex::find()` |

### Decisões Vigentes

| Decisão | Descrição | Status |
|---------|---------|--------|
| `thiserror` para erros de biblioteca | Padrão de facto para definir tipos de erro em crates públicas. Gera `Display` e `Error` automaticamente. | Ativa |
| Builder pattern para configuração | Tipos com mais de 2-3 opções de configuração DEVEM usar o padrão Builder para ergonomia e extensibilidade futura. | Ativa |
| Dois níveis de API | Bibliotecas de alta performance DEVEM oferecer: (1) API de alto nível conveniente e (2) API de baixo nível com controle total. Ex: `csv::Reader` vs `csv_core`. | Ativa |
| `impl Trait` para iteradores | Retornar `impl Iterator<Item=T>` em vez de tipos concretos de iterador para flexibilidade de implementação. | Ativa |
| Documentação com exemplos executáveis | Toda função pública DEVE ter pelo menos um exemplo em `///` que compila e executa corretamente. | Ativa |

### Restrições Técnicas

- Bibliotecas NÃO DEVEM expor `anyhow::Error` em APIs públicas.
- Bibliotecas NÃO DEVEM usar `unwrap()` em código de produção (não-teste). Consulte `lex-rust-no-panic-in-production`.
- Tipos de erro de bibliotecas DEVEM implementar `Send + Sync` para compatibilidade com código assíncrono e multi-thread.
- APIs que aceitam closures DEVEM documentar se a closure é chamada zero, uma ou múltiplas vezes.
- Mudanças em APIs públicas DEVEM seguir versionamento semântico (SemVer): breaking changes incrementam a versão major.

## Diagrama de Referência

```
Anatomia de uma Crate Rust bem projetada:

minha-crate/
├── src/
│   ├── lib.rs          ← API pública (re-exports, documentação de módulo)
│   ├── error.rs        ← Tipo de erro customizado (thiserror)
│   ├── builder.rs      ← Builder pattern para configuração
│   ├── core/           ← Implementação de baixo nível (zero alocação)
│   │   └── mod.rs
│   └── high_level/     ← API de alto nível conveniente
│       └── mod.rs
├── tests/
│   ├── integration/    ← Testes de integração
│   └── fixtures/       ← Dados de teste (incluindo UTF-8 inválido)
├── benches/
│   └── bench.rs        ← Benchmarks com criterion
└── Cargo.toml

Hierarquia de API:
  Alta conveniência  ←──────────────────────────────────────────────────────►  Baixo controle
  Regex::is_match()  →  Regex::find()  →  regex_automata::meta::Regex  →  LazyDFA diretamente
```

## Glossário

| Termo | Definição |
|-------|-----------|
| **SemVer** | Versionamento Semântico. MAJOR.MINOR.PATCH. Breaking changes incrementam MAJOR. |
| **Builder pattern** | Padrão de design onde um objeto separado (Builder) acumula configurações e constrói o objeto final. Ergonômico para tipos com muitas opções. |
| **Zero alocação** | API que não aloca memória no heap durante a operação, reutilizando buffers fornecidos pelo chamador. |
| **`impl Trait`** | Sintaxe Rust para retornar ou aceitar um tipo que implementa uma trait sem nomear o tipo concreto. |
| **`AsRef<T>`** | Trait de conversão barata (sem custo) para referências. Permite que APIs aceitem múltiplos tipos que podem ser convertidos para `&T`. |
| **`thiserror`** | Crate que gera implementações de `std::error::Error` e `Display` via macros de derivação. Padrão para erros de bibliotecas. |
| **Coherence rules** | Regras do compilador Rust que determinam onde traits podem ser implementadas. Implicação: callers não podem implementar `From` no tipo de erro da biblioteca — a biblioteca deve fazê-lo. |
| **`Send + Sync`** | Traits automáticas que indicam que um tipo pode ser enviado entre threads (`Send`) e acessado concorrentemente (`Sync`). Necessário para compatibilidade com `async` e `rayon`. |

## Referências

- [Rust and CSV parsing — API design (BurntSushi)](https://burntsushi.net/csv/)
- [Regex engine internals as a library (BurntSushi)](https://burntsushi.net/regex-internals/)
- [Error Handling in Rust — Advice for library writers (BurntSushi)](https://burntsushi.net/rust-error-handling/)
- [Rust API Guidelines](https://rust-lang.github.io/api-guidelines/)
- [thiserror — crates.io](https://crates.io/crates/thiserror)
- `codex-rust-error-handling` — Referência completa de tratamento de erros
- `lex-rust-no-panic-in-production` — Lei sobre panic em produção

---

**Gerado com base nos ensinamentos de Andrew Gallant (BurntSushi) e nas práticas do ecossistema Rust.**
