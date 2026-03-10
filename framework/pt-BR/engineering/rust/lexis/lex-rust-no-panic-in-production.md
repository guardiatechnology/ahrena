# Lexis: Proibição de Panic em Código de Produção Rust

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebável | **Escopo:** Desenvolvimento e Revisão de Código Rust

## Propósito

Rust oferece duas estratégias fundamentais para lidar com situações inesperadas: retornar um `Result<T, E>` (tratamento explícito de erros como valores) ou invocar `panic!` (que aborta a thread ou o processo). O uso indiscriminado de `panic!` — e seus atalhos `unwrap()` e `expect()` — em código de produção transforma erros recuperáveis em falhas catastróficas, derruba serviços inteiros por falhas pontuais e produz mensagens de erro incompreensíveis para o usuário final. Esta lei existe para garantir que todo código Rust em produção trate erros de forma explícita, composicional e ergonômica, conforme estabelecido pelas melhores práticas consolidadas por Andrew Gallant (BurntSushi) e pela comunidade Rust.

## Lei

> **Todo código Rust destinado a produção NÃO PODE utilizar `unwrap()`, `expect()` ou `panic!` para lidar com erros recuperáveis — isto é, situações que podem ocorrer durante a operação normal do sistema, como falhas de I/O, erros de parsing de entrada de usuário, falhas de rede ou ausência de recursos.**

## Abrangência

- **Aplica-se a:** Todo código Rust em repositórios de produção (backends, serviços, bibliotecas, ferramentas CLI distribuídas).
- **Agentes vinculados:** Todos os agentes de desenvolvimento (Warriors) e revisores de código (Cries).
- **Exceções:** Nenhuma. Lexis não admitem exceções.

**Nota de contexto (não é exceção):** `unwrap()` e `expect()` são tecnicamente permitidos apenas em: (a) código dentro de blocos `#[test]`, (b) exemplos de documentação (`///`), (c) prototipagem local não destinada a produção, e (d) invariantes internos onde a violação indica estritamente um bug no código — nunca um erro de ambiente ou de entrada. Nesses casos de invariante, `expect()` com mensagem descritiva é fortemente preferível a `unwrap()`.

## Consequências de Violação

1. **Bloqueio automático:** Pull Request rejeitado automaticamente pelo CI com falha no lint de `clippy`.
2. **Alerta:** Notificação ao Tech Lead responsável pelo repositório.
3. **Remediação:** O código DEVE ser reescrito utilizando `Result<T, E>` e o operador `?` para propagação de erros antes de qualquer novo merge.

## Exemplos

### Correto

```rust
use std::fs::File;
use std::io::{self, Read};

// Correto: propaga o erro usando Result e o operador ?
fn ler_configuracao(caminho: &str) -> Result<String, io::Error> {
    let mut arquivo = File::open(caminho)?;
    let mut conteudo = String::new();
    arquivo.read_to_string(&mut conteudo)?;
    Ok(conteudo)
}

// Correto: uso de expect() para invariante interno garantido pelo código
fn primeiro_elemento_garantido(slice: &[i32]) -> i32 {
    // O chamador garante que o slice não é vazio (invariante documentado)
    *slice.first().expect("BUG: slice vazio — violação de invariante interno")
}

// Correto em testes: unwrap() é aceitável
#[test]
fn test_ler_configuracao() {
    let resultado = ler_configuracao("tests/fixtures/config.toml").unwrap();
    assert!(resultado.contains("versao"));
}
```

### Incorreto

```rust
use std::fs::File;
use std::io::Read;

// VIOLA A LEI: unwrap() em erro recuperável (arquivo pode não existir)
fn ler_configuracao_errado(caminho: &str) -> String {
    let mut arquivo = File::open(caminho).unwrap(); // Pânico se o arquivo não existir!
    let mut conteudo = String::new();
    arquivo.read_to_string(&mut conteudo).unwrap(); // Pânico em erro de I/O!
    conteudo
}

// VIOLA A LEI: panic! para controle de fluxo normal
fn processar_entrada(valor: &str) -> i32 {
    match valor.parse::<i32>() {
        Ok(n) => n,
        Err(_) => panic!("Entrada inválida: {}", valor), // Derruba o serviço!
    }
}
```

## Validação Automatizada

- **Ferramenta:** `cargo clippy` com as lints `clippy::unwrap_used` e `clippy::panic` habilitadas para código de produção (excluindo `#[cfg(test)]`).
- **Configuração recomendada no `Cargo.toml` ou `.clippy.toml`:**
  ```toml
  # .clippy.toml
  disallowed-methods = [
    { path = "std::option::Option::unwrap", reason = "Use ? ou expect() com invariante documentado" },
    { path = "std::result::Result::unwrap", reason = "Use ? ou expect() com invariante documentado" },
  ]
  ```
- **Momento:** Pipeline de CI em cada Pull Request e pre-commit hook local.
- **Métrica:** 0 violações toleradas no código de produção (`src/`, `lib/`).

---

**Referência:** Baseado em [Error Handling in Rust](https://burntsushi.net/rust-error-handling/) e [Using unwrap() in Rust is Okay](https://burntsushi.net/unwrap/) de Andrew Gallant (BurntSushi).
