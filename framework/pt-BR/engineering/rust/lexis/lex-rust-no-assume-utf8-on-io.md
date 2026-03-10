# Lexis: Proibição de Assumir UTF-8 em I/O Não Validado

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebável | **Escopo:** Desenvolvimento de Ferramentas CLI, Processamento de Arquivos e Streams em Rust

## Propósito

Rust garante que o tipo `&str` e `String` contêm sempre UTF-8 válido. Isso é uma propriedade poderosa, mas cria um problema silencioso: código que lê dados de fontes externas (arquivos, stdin, pipes, sockets) e os converte diretamente para `String` sem validação irá **falhar em pânico ou retornar erro** ao encontrar bytes que não são UTF-8 válido. Na prática, UTF-8 inválido é mais comum do que se imagina — arquivos legados em latin-1, código-fonte de projetos grandes como o Firefox (gecko-dev), arquivos de log de sistemas, e dados binários misturados com texto. Ferramentas de uso geral (como grep, parsers de log, processadores de texto) DEVEM ser capazes de lidar com esses dados sem falhar. Esta lei protege a robustez de ferramentas e serviços que processam dados externos não controlados.

## Lei

> **Todo código Rust que processa dados de fontes externas não controladas (arquivos do sistema, stdin, pipes, uploads de usuário, respostas de rede sem schema definido) NÃO PODE assumir que esses dados são UTF-8 válido sem validação explícita ou sem o uso de tipos tolerantes a bytes inválidos.**

## Abrangência

- **Aplica-se a:** Ferramentas CLI, serviços que processam arquivos de usuário, parsers de log, qualquer código que leia de `std::io::Read` sem schema de encoding garantido.
- **Agentes vinculados:** Todos os agentes de desenvolvimento (Warriors) que trabalham com I/O de arquivos, streams ou dados externos.
- **Exceções:** Nenhuma. Lexis não admitem exceções.

**Nota de contexto (não é exceção):** APIs com schema bem definido e encoding garantido (ex: JSON sobre HTTP com `Content-Type: application/json; charset=utf-8`, respostas de banco de dados com collation UTF-8 configurada) podem usar `String` diretamente, pois o protocolo garante a validade do encoding. A lei se aplica especificamente a fontes onde o encoding não é garantido pelo protocolo.

## Consequências de Violação

1. **Bloqueio automático:** Pull Request rejeitado no CI por falha em testes de integração com fixtures contendo bytes inválidos.
2. **Alerta:** Notificação ao Tech Lead com descrição do risco de falha em produção.
3. **Remediação:** O código DEVE ser reescrito utilizando `&[u8]` / `Vec<u8>` com a crate `bstr` para operações de string, ou com validação explícita via `std::str::from_utf8()` antes da conversão.

## Exemplos

### Correto

```rust
use bstr::{io::BufReadExt, ByteSlice};
use std::io::Write;

// Correto: usa bstr para processar linhas sem assumir UTF-8 válido
fn grep_robusto(agulha: &str) -> Result<(), Box<dyn std::error::Error>> {
    for resultado in std::io::stdin().lock().byte_lines() {
        let linha = resultado?;
        if linha.contains_str(agulha) {
            // Escreve exatamente o que foi lido, sem conversão para String
            std::io::stdout().write_all(&linha)?;
            std::io::stdout().write_all(b"\n")?;
        }
    }
    Ok(())
}

// Correto: validação explícita antes de converter para &str
fn processar_arquivo(caminho: &str) -> Result<(), Box<dyn std::error::Error>> {
    let bytes = std::fs::read(caminho)?;
    match std::str::from_utf8(&bytes) {
        Ok(texto) => {
            // Agora é seguro usar como &str
            println!("Arquivo UTF-8 válido com {} chars", texto.chars().count());
        }
        Err(e) => {
            // Trata o erro de encoding explicitamente
            eprintln!("Arquivo não é UTF-8 válido: {}", e);
            // Usa bstr para processar mesmo assim
            let texto_bstr = bytes.as_bstr();
            println!("Processando como byte string: {} bytes", texto_bstr.len());
        }
    }
    Ok(())
}
```

### Incorreto

```rust
use std::io::BufRead;

// VIOLA A LEI: assume UTF-8 ao ler linhas de stdin
fn grep_fragil(agulha: &str) {
    for resultado in std::io::stdin().lock().lines() {
        // lines() retorna Err se a linha não for UTF-8 válida!
        // Em vez de lidar com o dado, o programa falha.
        let linha = resultado.unwrap();
        if linha.contains(agulha) {
            println!("{}", linha);
        }
    }
}

// VIOLA A LEI: converte bytes para String sem validação
fn ler_arquivo_fragil(caminho: &str) -> String {
    let bytes = std::fs::read(caminho).unwrap();
    // Pânico se o arquivo não for UTF-8 válido!
    String::from_utf8(bytes).unwrap()
}
```

## Validação Automatizada

- **Ferramenta:** Testes de integração com fixtures de arquivos contendo bytes UTF-8 inválidos (ex: `\xFF`, `\xFE`, sequências latin-1). Esses fixtures DEVEM existir em `tests/fixtures/invalid_utf8/`.
- **Ferramenta complementar:** `cargo clippy` para detectar uso de `std::io::BufRead::lines()` em contextos de processamento de arquivos genéricos.
- **Momento:** Pipeline de CI em cada Pull Request.
- **Métrica:** 0 falhas nos testes de fixtures com bytes inválidos.

---

**Referência:** Baseado em [A byte string library for Rust (bstr)](https://burntsushi.net/bstr/) de Andrew Gallant (BurntSushi). A crate `bstr` está disponível em [crates.io/crates/bstr](https://crates.io/crates/bstr).
