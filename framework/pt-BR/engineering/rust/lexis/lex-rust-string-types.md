# Lexis: Tipos de String em Rust

> **Prefixo:** `lex-` | **Tipo:** Lei Absoluta | **Escopo:** Desenvolvimento em Rust

## Lei: Use `&str` para leitura e `String` para posse e mutação.

O tratamento de strings em Rust é rigoroso devido à garantia de que toda string é um UTF-8 válido e ao fato de que caracteres Unicode podem ter tamanhos variáveis (1 a 4 bytes). Desenvolvedores DEVEM entender a diferença entre `String` e `&str` e usá-los apropriadamente.

### Regras de Conformidade

1. **Assinaturas de Função:** Se uma função apenas lê ou analisa uma string sem precisar de posse ou modificação, ela DEVE aceitar `&str` como parâmetro, não `String` nem `&String`.
   - Isso permite que a função seja chamada com literais de string (`"texto"`), `String`s (via *Deref coercion*) ou fatias (`&s[..]`).
2. **Indexação Direta é Proibida:** NUNCA tente indexar uma string diretamente (ex: `minha_string[0]`). O compilador rejeitará isso porque a indexação por byte pode quebrar caracteres UTF-8.
3. **Iteração Segura:** Para iterar sobre os caracteres de uma string, DEVE-SE usar `.chars()` (para iterar por codepoints Unicode) ou `.bytes()` (para iterar pelos bytes brutos).
4. **Fatiamento (Slicing) Cuidadoso:** Fatiar strings (ex: `&s[0..4]`) usa índices de **bytes**, não de caracteres. Fatiar no meio de um caractere multibyte causará um **pânico** em runtime. Só faça fatiamento se tiver certeza absoluta de que os índices caem em limites de caracteres (char boundaries).

### Justificativa

- **Performance:** Exigir `String` como parâmetro quando `&str` seria suficiente força o chamador a alocar memória no heap (ex: chamando `.to_string()` em um literal). Aceitar `&str` é "zero-cost".
- **Correção Unicode:** Strings em Rust não são arrays de `char`. Um `char` em Rust tem sempre 4 bytes, mas strings usam UTF-8 (tamanho variável). Impedir indexação direta previne bugs comuns em C/C++ onde programadores assumem que 1 byte = 1 caractere.

### Exemplos

#### ❌ Violação da Lei
```rust
// Ruim: Exige alocação desnecessária no heap se o chamador tiver um literal.
fn print_greeting(name: String) {
    println!("Hello, {}", name);
}

// O chamador é forçado a fazer isso:
print_greeting("Alice".to_string()); 

// Ruim: Tentativa de indexação (não compila, mas ilustra o erro de conceito).
let s = "Olá";
let first_char = s[0]; // Erro de compilação!
```

#### ✅ Conformidade
```rust
// Bom: Aceita uma string slice, permitindo qualquer tipo de string.
fn print_greeting(name: &str) {
    println!("Hello, {}", name);
}

// O chamador pode passar um literal:
print_greeting("Alice");

// Ou pode passar uma String (Deref coercion converte &String para &str automaticamente):
let my_name = String::from("Bob");
print_greeting(&my_name);

// Bom: Iteração segura sobre caracteres Unicode.
let s = "忠犬ハチ公";
for c in s.chars() {
    println!("{}", c);
}
```

### Referências

- [MIT Rust Book: Strings](https://web.mit.edu/rust-lang_v1.25/arch/amd64_ubuntu1404/share/doc/rust/html/book/first-edition/strings.html)
- [MIT Rust Book: Deref coercions](https://web.mit.edu/rust-lang_v1.25/arch/amd64_ubuntu1404/share/doc/rust/html/book/first-edition/deref-coercions.html)
