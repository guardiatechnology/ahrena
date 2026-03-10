# Lexis: Segurança em FFI e Unsafe

> **Prefixo:** `lex-` | **Tipo:** Lei Absoluta | **Escopo:** Desenvolvimento em Rust

## Lei: Interfaces FFI e blocos `unsafe` DEVEM ser encapsulados em abstrações seguras.

O Rust permite interagir com código C (Foreign Function Interface - FFI) e realizar operações de baixo nível através da palavra-chave `unsafe`. No entanto, a filosofia do Rust dita que a insegurança não deve vazar para o resto do programa. Qualquer código `unsafe` DEVE ser escondido atrás de uma API pública 100% segura.

### Regras de Conformidade

1. **Encapsulamento Seguro:** Funções exportadas por bibliotecas C (via blocos `extern`) são implicitamente `unsafe`. Você NUNCA deve expor essas funções diretamente na API pública da sua crate. Crie wrappers seguros (funções normais do Rust) que chamam as funções `unsafe` internamente.
2. **Justificativa Documentada:** Todo bloco `unsafe` DEVE ser precedido por um comentário `// SAFETY:` explicando por que a operação é segura e quais invariantes estão sendo garantidos pelo programador (já que o compilador não pode verificá-los).
3. **Tipos FFI:** Ao interagir com C, use os tipos garantidos de terem o mesmo layout de memória, encontrados na crate `libc` (ex: `libc::c_int`, `libc::size_t`) em vez de assumir que um `i32` do Rust mapeia para um `int` do C em todas as plataformas.
4. **Destrutores e Propriedade:** Se uma biblioteca C aloca memória e retorna um ponteiro para o Rust, o Rust NÃO DEVE tentar liberar essa memória com as ferramentas nativas do Rust (como deixar um `Box` sair de escopo). Você DEVE implementar a trait `Drop` em um struct wrapper e chamar a função de liberação (`free` ou equivalente) da própria biblioteca C dentro do método `drop`.
5. **Panics através de fronteiras FFI:** É **Comportamento Indefinido (UB)** permitir que um `panic!` do Rust vaze (unwind) para código C, ou que uma exceção do C++ vaze para o Rust. Se sua função Rust for chamada pelo C (via `extern "C" fn`), você DEVE usar `std::panic::catch_unwind` para capturar qualquer pânico potencial e retornar um código de erro C apropriado.

### Justificativa

A palavra-chave `unsafe` não desliga o borrow checker; ela apenas dá ao programador três "superpoderes":
1. Desreferenciar ponteiros brutos (`*const T` e `*mut T`).
2. Chamar funções `unsafe` (incluindo funções C).
3. Acessar ou modificar variáveis estáticas mutáveis (`static mut`).

Se um programa Rust apresenta um segfault, a culpa é invariavelmente de um bloco `unsafe`. Ao encapsular a insegurança, limitamos a superfície de auditoria de código.

### Exemplos

#### ❌ Violação da Lei (Vazando Insegurança)
```rust
extern crate libc;

#[link(name = "snappy")]
extern {
    pub fn snappy_max_compressed_length(source_length: libc::size_t) -> libc::size_t;
}

// Ruim: O usuário da sua biblioteca é forçado a usar `unsafe` para chamar isso.
// pub use snappy_max_compressed_length;
```

#### ✅ Conformidade (Encapsulamento Seguro)
```rust
extern crate libc;

#[link(name = "snappy")]
extern {
    fn snappy_max_compressed_length(source_length: libc::size_t) -> libc::size_t;
}

// Bom: Wrapper seguro. O usuário não precisa de `unsafe`.
// O programador garante que passar qualquer `usize` para esta função C é seguro.
pub fn max_compressed_length(source_length: usize) -> usize {
    // SAFETY: A função C `snappy_max_compressed_length` é pura, não lê memória
    // não inicializada e é segura para chamar com qualquer valor de `size_t`.
    unsafe {
        snappy_max_compressed_length(source_length as libc::size_t) as usize
    }
}
```

### Referências

- [MIT Rust Book: Unsafe](https://web.mit.edu/rust-lang_v1.25/arch/amd64_ubuntu1404/share/doc/rust/html/book/first-edition/unsafe.html)
- [MIT Rust Book: FFI](https://web.mit.edu/rust-lang_v1.25/arch/amd64_ubuntu1404/share/doc/rust/html/book/first-edition/ffi.html)
