# Lexis: Bibliotecas Rust DEVEM Definir Tipos de Erro Próprios

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebável | **Escopo:** Design e Publicação de Bibliotecas Rust (crates)

## Propósito

Quando uma biblioteca Rust retorna `Box<dyn std::error::Error>`, `anyhow::Error` ou `String` como tipo de erro em sua API pública, ela apaga toda a informação de tipo sobre o erro. O chamador não consegue distinguir um erro de I/O de um erro de parsing, não consegue tratar erros específicos de forma diferenciada, e perde a capacidade de inspecionar a causa raiz programaticamente. Isso é o equivalente a retornar `Object` em Java ou `any` em TypeScript — destrói a segurança de tipo que é o principal valor de Rust. Andrew Gallant (BurntSushi) estabelece claramente: "Se você está escrevendo uma biblioteca e seu código pode produzir erros, defina seu próprio tipo de erro e implemente a trait `std::error::Error`." Esta lei garante que bibliotecas Rust respeitem o contrato de tipos que seus usuários esperam.

## Lei

> **Toda biblioteca Rust (crate do tipo `lib`) NÃO PODE expor `Box<dyn std::error::Error>`, `anyhow::Error`, `String` ou `&str` como tipo de erro em funções ou métodos públicos. A biblioteca DEVE definir e expor seu próprio tipo de erro que implementa `std::error::Error`, `Debug` e `Display`.**

## Abrangência

- **Aplica-se a:** Todas as crates do tipo biblioteca (`lib`) com API pública destinada a uso por outros crates.
- **Agentes vinculados:** Todos os agentes de desenvolvimento (Warriors) que criam ou modificam bibliotecas Rust.
- **Exceções:** Nenhuma. Lexis não admitem exceções.

**Nota de contexto (não é exceção):** Binários (crates do tipo `bin`) e aplicações finais podem usar `anyhow::Error` em suas funções internas e em `main()`. A lei se aplica exclusivamente à API pública de bibliotecas.

## Consequências de Violação

1. **Bloqueio automático:** Pull Request rejeitado no CI por falha em verificação de API pública.
2. **Alerta:** Notificação ao Tech Lead com identificação das funções que violam a lei.
3. **Remediação:** O tipo de erro DEVE ser definido como um `enum` ou `struct` com `#[derive(thiserror::Error)]`, e as funções públicas DEVEM ser atualizadas para retornar `Result<T, MeuErro>`.

## Exemplos

### Correto

```rust
// error.rs
use thiserror::Error;

#[derive(Debug, Error)]
pub enum MinhaCrateError {
    #[error("erro de I/O: {0}")]
    Io(#[from] std::io::Error),

    #[error("padrão de regex inválido '{padrao}': {causa}")]
    InvalidPattern {
        padrao: String,
        causa: String,
    },

    #[error("dado não encontrado: {chave}")]
    NotFound { chave: String },
}

// lib.rs
pub type Result<T> = std::result::Result<T, MinhaCrateError>;

pub fn buscar(padrao: &str, arquivo: &str) -> Result<Vec<String>> {
    let re = regex::Regex::new(padrao).map_err(|e| MinhaCrateError::InvalidPattern {
        padrao: padrao.to_string(),
        causa: e.to_string(),
    })?;
    let conteudo = std::fs::read_to_string(arquivo)?; // From<io::Error> automático
    Ok(re.find_iter(&conteudo).map(|m| m.as_str().to_string()).collect())
}
```

### Incorreto

```rust
// VIOLA A LEI: retorna Box<dyn Error> — apaga informação de tipo
pub fn buscar_errado(padrao: &str, arquivo: &str)
    -> Result<Vec<String>, Box<dyn std::error::Error>>
{
    let re = regex::Regex::new(padrao)?;
    let conteudo = std::fs::read_to_string(arquivo)?;
    Ok(re.find_iter(&conteudo).map(|m| m.as_str().to_string()).collect())
}

// VIOLA A LEI: retorna String como erro — perde toda a estrutura
pub fn buscar_pior(padrao: &str, arquivo: &str) -> Result<Vec<String>, String> {
    let re = regex::Regex::new(padrao).map_err(|e| e.to_string())?;
    let conteudo = std::fs::read_to_string(arquivo).map_err(|e| e.to_string())?;
    Ok(re.find_iter(&conteudo).map(|m| m.as_str().to_string()).collect())
}
```

## Validação Automatizada

- **Ferramenta:** `cargo-semver-checks` para detectar mudanças de API pública. Análise estática customizada para detectar `Box<dyn Error>` em assinaturas públicas.
- **Ferramenta complementar:** Revisão de código com checklist: toda função `pub` que retorna `Result` deve ter um tipo de erro concreto definido na crate.
- **Momento:** Pipeline de CI em cada Pull Request e antes de publicação no crates.io.
- **Métrica:** 0 funções ou métodos públicos retornando `Box<dyn Error>`, `anyhow::Error` ou `String` como tipo de erro.

---

**Referência:** Baseado em [Error Handling in Rust — Advice for library writers](https://burntsushi.net/rust-error-handling/) de Andrew Gallant (BurntSushi). A crate `thiserror` está em [crates.io/crates/thiserror](https://crates.io/crates/thiserror).
