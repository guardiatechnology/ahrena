# Codex: Testes e Documentação em Rust

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Desenvolvimento de Bibliotecas e Aplicações em Rust

## Visão Geral

Este Codex estabelece as práticas recomendadas para escrever testes (unitários, de integração e de documentação) e gerar documentação no ecossistema Rust. A filosofia do Rust é que documentação e testes são cidadãos de primeira classe, integrados diretamente nas ferramentas padrão (`cargo test`, `cargo doc`, `rustdoc`).

## Contexto

- **Domínio:** Garantia de qualidade, testes automatizados, documentação de código.
- **Público-alvo:** Desenvolvedores Rust, mantenedores de bibliotecas, Agentes de IA.
- **Atualização:** Quando novas features de `rustdoc` ou `cargo test` forem estabilizadas.

## Conteúdo

### Testes em Rust

Rust suporta nativamente três tipos de testes: Unitários, de Integração e de Documentação.

#### 1. Testes Unitários
Testam funções e módulos individuais, incluindo código privado.
- **Localização:** No mesmo arquivo que o código sendo testado.
- **Estrutura:** Dentro de um módulo `tests` anotado com `#[cfg(test)]`. Isso garante que o código de teste não seja compilado no binário final.
- **Macros Comuns:** `assert!(cond)`, `assert_eq!(a, b)`, `assert_ne!(a, b)`.
- **Panics Esperados:** Use `#[should_panic(expected = "mensagem")]` para testar se uma função falha corretamente.

```rust
pub fn add_two(a: i32) -> i32 {
    a + 2
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_add_two() {
        assert_eq!(4, add_two(2));
    }
}
```

#### 2. Testes de Integração
Testam a biblioteca de fora, usando apenas a API pública, exatamente como um usuário faria.
- **Localização:** Em um diretório `tests/` na raiz do projeto (ao lado de `src/`).
- **Estrutura:** Cada arquivo `.rs` em `tests/` é compilado como um crate separado. Não precisa de `#[cfg(test)]` (o Cargo já sabe que são testes).
- **Setup Compartilhado:** Se você precisa de código compartilhado entre testes de integração, coloque-o em `tests/common/mod.rs` e declare `mod common;` nos testes.

#### 3. Ignorando Testes
Testes lentos ou que dependem de ambiente específico podem ser anotados com `#[ignore]`. Eles só rodarão se chamados com `cargo test -- --ignored`.

### Documentação (`rustdoc`)

Rust usa comentários de documentação (Doc Comments) escritos em Markdown.

#### 1. Tipos de Comentários
- `///` (Outer doc comments): Documentam o item que vem *logo após* eles. Usados para funções, structs, traits, etc.
- `//!` (Inner doc comments): Documentam o item *dentro do qual* eles estão. Usados no topo de arquivos (`lib.rs`, `main.rs`) ou módulos para documentar o módulo inteiro.

#### 2. Estrutura Padrão de Doc Comments
A documentação de uma função pública DEVE conter as seguintes seções (se aplicáveis):
1. **Resumo:** Uma linha curta descrevendo o que a função faz.
2. **Detalhes:** (Opcional) Explicação mais longa do comportamento.
3. **`# Panics`:** Se a função puder causar um `panic!`, documente sob quais condições.
4. **`# Errors`:** Se a função retornar `Result`, documente os tipos de erro que podem ocorrer.
5. **`# Safety`:** Se a função for `unsafe`, documente os invariantes que o chamador deve garantir.
6. **`# Examples`:** Blocos de código demonstrando o uso.

```rust
/// Divide dois números.
///
/// # Errors
///
/// Retorna um erro se o divisor for zero.
///
/// # Examples
///
/// ```
/// let result = my_crate::divide(10, 2);
/// assert_eq!(result, Ok(5));
/// ```
pub fn divide(a: i32, b: i32) -> Result<i32, &'static str> {
    if b == 0 {
        Err("Divisão por zero")
    } else {
        Ok(a / b)
    }
}
```

#### 3. Testes de Documentação (Doc Tests)
Os blocos de código em Markdown (` ``` `) dentro de Doc Comments são **compilados e executados** automaticamente pelo `cargo test`.
- Isso garante que os exemplos na documentação nunca fiquem desatualizados em relação ao código.
- Para ocultar linhas de setup (como `use` statements ou inicialização) no HTML gerado, mas ainda compilá-las no teste, prefixe a linha com `# `.

```rust
/// ```
/// # use my_crate::ComplexStruct;
/// # let obj = ComplexStruct::new();
/// assert!(obj.is_ready());
/// ```
```

### Restrições Técnicas

- TODO código público (`pub`) DEVE ser documentado com `///`.
- Use `#![warn(missing_docs)]` no `lib.rs` para forçar a documentação de toda a API pública.
- Testes unitários DEVEM ser mantidos rápidos e não devem depender de I/O externo (rede, banco de dados) se possível. I/O externo pertence a testes de integração ou testes E2E.

## Referências

- [MIT Rust Book: Testing](https://web.mit.edu/rust-lang_v1.25/arch/amd64_ubuntu1404/share/doc/rust/html/book/first-edition/testing.html)
- [MIT Rust Book: Documentation](https://web.mit.edu/rust-lang_v1.25/arch/amd64_ubuntu1404/share/doc/rust/html/book/first-edition/documentation.html)
