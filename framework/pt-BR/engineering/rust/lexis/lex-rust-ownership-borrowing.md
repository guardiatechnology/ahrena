# Lexis: Ownership e Borrowing em Rust

> **Prefixo:** `lex-` | **Tipo:** Lei Absoluta | **Escopo:** Desenvolvimento em Rust

## Lei: O Sistema de Ownership e Borrowing deve ser respeitado, não contornado.

Esta lei estabelece que o sistema de Ownership e Borrowing do Rust é a fundação da segurança de memória da linguagem. Desenvolvedores DEVEM abraçar o modelo em vez de tentar lutar contra ele usando cópias desnecessárias (`clone()`), contadores de referência (`Rc`/`Arc`) prematuros ou blocos `unsafe` injustificados.

### Regras de Conformidade

1. **A Regra de Ouro do Borrowing:** Em qualquer momento, você pode ter UM dos seguintes, mas não ambos ao mesmo tempo:
   - Uma ou mais referências imutáveis (`&T`).
   - Exatamente UMA referência mutável (`&mut T`).
2. **Uso de `clone()`:** O uso de `.clone()` DEVE ser justificado. Não use `.clone()` apenas para "fazer o compilador calar a boca". Se você precisa clonar um tipo complexo repetidamente, repense o design (talvez passando referências ou usando `Rc`/`Arc`).
3. **Lifetimes:** Lifetimes explícitos (`<'a>`) DEVEM ser usados apenas quando o compilador não consegue inferi-los (Lifetime Elision). Evite criar estruturas com lifetimes complexos a menos que seja estritamente necessário para performance; prefira owned types (`String`, `Vec`) em estruturas de dados comuns para simplificar a API.
4. **Mutabilidade:** Variáveis DEVEM ser imutáveis por padrão. Use `mut` apenas quando a mutação for genuinamente necessária.
5. **Closures e Captura:** Closures DEVEM capturar variáveis pelo nível mínimo de privilégio necessário: por referência (`&T`), por referência mutável (`&mut T`) ou por valor (`T` via `move`). Use `move` closures quando a closure precisar sobreviver ao escopo atual (ex: `thread::spawn`).

### Justificativa

O sistema de Ownership (com suas regras de Borrowing) é o que permite ao Rust garantir segurança de memória (sem dangling pointers, double frees ou data races) sem o custo de um Garbage Collector. Lutar contra o borrow checker geralmente indica um problema de design na arquitetura do software.

- **Prevenção de Data Races:** A regra "múltiplos leitores OU um escritor" é exatamente a mesma regra que previne data races em concorrência.
- **Performance:** Passar referências (`&T`) é zero-cost em runtime e evita alocações/cópias desnecessárias no heap.

### Exemplos

#### ❌ Violação da Lei (Lutando contra o Borrow Checker)
```rust
// Ruim: Clonando apenas para o compilador aceitar, alocando no heap sem necessidade.
fn print_length(s: String) {
    println!("Length: {}", s.len());
}

let text = String::from("hello");
print_length(text.clone()); // Cópia desnecessária!
println!("Still using: {}", text);

// Ruim: Usando Rc prematuramente para evitar pensar em lifetimes ou ownership.
use std::rc::Rc;
struct Node {
    data: Rc<String>,
}
```

#### ✅ Conformidade (Abraçando o Borrowing)
```rust
// Bom: Usando referências (borrowing) para acesso read-only.
fn print_length(s: &str) {
    println!("Length: {}", s.len());
}

let text = String::from("hello");
print_length(&text); // Nenhuma alocação, apenas um ponteiro passado.
println!("Still using: {}", text);

// Bom: Movendo o valor quando a posse é realmente necessária.
fn consume_string(s: String) {
    // Toma posse de `s` e a destrói ao final.
}
```

### Exceções Permitidas

- Uso de `clone()` é aceitável em caminhos que não são críticos para performance (ex: inicialização, parsing de configuração) se isso simplificar drasticamente o código.
- Uso de `Rc<T>` / `Arc<T>` é perfeitamente válido e encorajado quando o tempo de vida de um dado é genuinamente compartilhado e não pode ser determinado estaticamente (ex: grafos, GUIs, estado compartilhado entre threads).

### Referências

- [MIT Rust Book: Ownership](https://web.mit.edu/rust-lang_v1.25/arch/amd64_ubuntu1404/share/doc/rust/html/book/first-edition/ownership.html)
- [MIT Rust Book: References and Borrowing](https://web.mit.edu/rust-lang_v1.25/arch/amd64_ubuntu1404/share/doc/rust/html/book/first-edition/references-and-borrowing.html)
- [MIT Rust Book: Lifetimes](https://web.mit.edu/rust-lang_v1.25/arch/amd64_ubuntu1404/share/doc/rust/html/book/first-edition/lifetimes.html)
