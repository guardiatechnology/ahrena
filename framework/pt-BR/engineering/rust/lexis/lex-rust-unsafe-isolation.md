# Lexis: Isolamento Obrigatório de Código Unsafe em Rust

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebrável | **Escopo:** Desenvolvimento e Revisão de Código

## Propósito
A segurança de memória é a principal garantia da linguagem Rust. O uso da palavra-chave `unsafe` desativa essas garantias, transferindo a responsabilidade do compilador para o desenvolvedor. Se o código `unsafe` não for devidamente isolado e encapsulado em abstrações seguras, a integridade de toda a aplicação (como visto em sistemas críticos como TiKV e renderizadores como Alacritty) é comprometida. Esta lei garante que o `unsafe` seja auditável e não "vaze" para a API pública.

## Lei
> **Todo bloco ou função `unsafe` DEVE ser encapsulado em uma API segura (`Safe Abstraction`) e DEVE conter um comentário `// SAFETY:` documentando explicitamente por que a operação é segura e quais invariantes o chamador deve garantir.**

## Abrangência
- **Aplica-se a:** Todos os repositórios Rust, bibliotecas e binários.
- **Agentes vinculados:** Todos os agentes de IA e desenvolvedores humanos.
- **Exceções:** Nenhuma. Interfaces FFI (Foreign Function Interface) também devem seguir esta regra encapsulando as chamadas C/C++ em wrappers seguros.

## Consequências de Violação
1. **Bloqueio automático:** Pull Requests contendo blocos `unsafe` sem o comentário `// SAFETY:` serão rejeitados no CI (via `clippy::undocumented_unsafe_blocks`).
2. **Rejeição de API:** APIs públicas marcadas como `unsafe` sem justificativa arquitetural extrema (como traits fundamentais de engine) serão vetadas na revisão de design.
3. **Auditoria de Segurança:** Código que expõe invariantes `unsafe` não verificadas exigirá reescrita completa antes do merge.

## Exemplos

### Correto

```rust
/// Wrapper seguro para um buffer de bytes otimizado.
pub struct FastBuffer {
    data: Vec<u8>,
}

impl FastBuffer {
    /// Lê um byte sem verificação de limites.
    ///
    /// # Panics
    ///
    /// Nunca entra em panic, mas pode causar undefined behavior se o índice
    /// estiver fora dos limites internamente (o que esta API previne).
    pub fn get_byte(&self, index: usize) -> Option<u8> {
        if index < self.data.len() {
            // SAFETY: O índice foi verificado no `if` acima, garantindo que
            // index < data.len(). Portanto, get_unchecked é seguro.
            Some(unsafe { *self.data.get_unchecked(index) })
        } else {
            None
        }
    }
}
```

### Incorreto

```rust
// VIOLAÇÃO 1: Função pública unsafe sem justificativa de design
pub unsafe fn read_memory(ptr: *const u8) -> u8 {
    // VIOLAÇÃO 2: Bloco unsafe sem comentário `// SAFETY:`
    *ptr
}

// VIOLAÇÃO 3: Vazamento de invariante para o usuário
pub struct BadBuffer {
    data: Vec<u8>,
}

impl BadBuffer {
    // Exige que o usuário garanta a segurança, espalhando a responsabilidade
    pub unsafe fn get_unchecked(&self, index: usize) -> u8 {
        *self.data.get_unchecked(index)
    }
}
```

## Validação Automatizada
- **Ferramenta:** `cargo clippy`
- **Momento:** Pipeline de CI (Pull Request)
- **Configuração:** O arquivo `clippy.toml` ou `.cargo/config.toml` deve conter a restrição:
  ```toml
  [lints.clippy]
  undocumented_unsafe_blocks = "deny"
  missing_safety_doc = "deny"
  ```
- **Métrica:** 0 violações toleradas.

---
**Fontes de Conhecimento:**
- Repositório TiKV: Padrões de encapsulamento em `components/tikv_util/src/buffer_vec.rs` e `codec`.
- Repositório Alacritty: Interações FFI e manipulação de ponteiros em `clipboard.rs` e `daemon.rs`.
