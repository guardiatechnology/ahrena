# Lexis: Tipos de Erro Específicos para Bibliotecas e Roteadores

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebrável | **Escopo:** Design de API e Desenvolvimento de Bibliotecas

## Propósito
Em Rust, a forma como os erros são expostos define como os usuários podem reagir a eles. Bibliotecas (crates) e módulos centrais que exportam APIs públicas não devem forçar o consumidor a inspecionar strings ou fazer downcasts inseguros para entender o que deu errado. O uso de tipos de erro opacos como `Box<dyn std::error::Error>` ou genéricos como `anyhow::Error` em assinaturas de API pública destrói a capacidade do chamador de tratar erros programaticamente (ex: tentar novamente, ignorar condicionalmente, ou traduzir para códigos HTTP específicos).

## Lei
> **Toda biblioteca, crate ou módulo de domínio público DEVE definir e retornar seus próprios tipos de erro concretos (ex: `pub enum Error`) que implementem a trait `std::error::Error`. O uso de `anyhow::Error` ou `Box<dyn Error>` é ESTRITAMENTE PROIBIDO nas assinaturas de funções públicas dessas camadas.**

## Abrangência
- **Aplica-se a:** Todos os crates de biblioteca, módulos de domínio (`core`/`domain`), e interfaces de serviços.
- **Agentes vinculados:** Todos os agentes de IA e desenvolvedores humanos.
- **Exceções:** O uso de `anyhow::Error` é permitido **apenas** em binários finais (ex: `main.rs`, handlers de CLI) onde o erro será formatado para o usuário final e não será inspecionado programaticamente.

## Consequências de Violação
1. **Bloqueio na Revisão de Design:** APIs que não definem seus próprios tipos de erro serão vetadas antes da implementação.
2. **Refatoração em Cascata:** Se descoberto tardiamente, exigirá uma *breaking change* (incremento de MAJOR version) para corrigir, afetando todos os consumidores.
3. **Falha em Testes de Integração:** O chamador não conseguirá escrever testes robustos que afirmem que um erro específico ocorreu.

## Exemplos

### Correto

```rust
use thiserror::Error;

/// Erro específico do módulo de parsing.
#[derive(Debug, Error)]
pub enum ParseError {
    #[error("I/O error occurred: {0}")]
    Io(#[from] std::io::Error),
    
    #[error("Invalid syntax at line {line}, column {col}")]
    Syntax { line: usize, col: usize },
    
    #[error("Value '{0}' exceeds maximum allowed limit")]
    LimitExceeded(String),
}

// A função pública retorna o erro concreto
pub fn parse_file(path: &str) -> Result<Ast, ParseError> {
    // ...
}
```

### Incorreto

```rust
// VIOLAÇÃO 1: Uso de anyhow em API pública
pub fn parse_file_bad(path: &str) -> anyhow::Result<Ast> {
    // O consumidor não sabe se falhou por I/O, sintaxe ou limite
    // sem inspecionar a string do erro.
}

// VIOLAÇÃO 2: Uso de Box<dyn Error>
pub fn connect_db() -> Result<Connection, Box<dyn std::error::Error>> {
    // Força o chamador a fazer downcasting manual
}
```

## Validação Automatizada
- **Ferramenta:** Revisão manual e análise estática customizada.
- **Momento:** Pull Request.
- **Regra Mental:** Se a função tem `pub` e não está no `main.rs`, ela não deve retornar `anyhow::Result`.

---
**Fontes de Conhecimento:**
- Repositório Meilisearch: Padrões rigorosos de conversão de erros em códigos HTTP (`crates/meilisearch-types/src/error.rs`).
- Repositório Ripgrep: Definição meticulosa de `ErrorKind` e `Error` para parsing de regex e busca (`crates/regex/src/error.rs`).
