# Codex: Traits e Generics em Rust

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Desenvolvimento de Bibliotecas e Aplicações em Rust

## Visão Geral

O sistema de Traits e Generics é a espinha dorsal do polimorfismo em Rust. Ao contrário de linguagens orientadas a objetos baseadas em herança de classes, Rust utiliza composição e interfaces (Traits) para definir comportamento compartilhado. Este Codex define as melhores práticas para o uso de generics, trait bounds, monomorfização e trait objects (dynamic dispatch).

## Contexto

- **Domínio:** Design de API, polimorfismo, performance, extensibilidade.
- **Público-alvo:** Desenvolvedores Rust, arquitetos de software.
- **Atualização:** Quando novas features de traits (como impl Trait em novos contextos) forem estabilizadas.

## Conteúdo

### Princípios

1. **Composição sobre Herança:** Rust não tem herança de classes. O reuso de código é feito através da composição de structs e da implementação de traits.
2. **Polimorfismo Estático (Generics) por Padrão:** Generics em Rust usam monomorfização. O compilador gera uma cópia separada da função para cada tipo concreto usado. Isso resulta em abstrações de custo zero (zero-cost abstractions) com máxima performance (inlining), ao custo de maior tempo de compilação e tamanho do binário.
3. **Polimorfismo Dinâmico (Trait Objects) sob Demanda:** Quando você precisa armazenar tipos heterogêneos na mesma coleção (ex: um `Vec` contendo diferentes tipos que implementam `Draw`), use Trait Objects (`Box<dyn Trait>`). Isso usa *dynamic dispatch* (vtable), o que tem um pequeno custo de performance, mas reduz o tamanho do binário e permite flexibilidade em runtime.

### Regras de Implementação de Traits (Regra do Órfão)

Você só pode implementar um trait para um tipo se:
- O trait foi definido no seu crate, OU
- O tipo foi definido no seu crate.

Você NÃO PODE implementar um trait externo (ex: `std::fmt::Display`) para um tipo externo (ex: `std::vec::Vec`). Isso previne conflitos caso duas bibliotecas tentem fazer a mesma coisa. Se precisar contornar isso, use o **Newtype Pattern** (crie um struct wrapper em torno do tipo externo).

### Padrões e Convenções

#### 1. Trait Bounds
Use trait bounds para restringir os tipos que uma função genérica aceita.
- **Sintaxe Inline:** `fn print_area<T: HasArea>(shape: T)`
- **Sintaxe Where Clause:** Para assinaturas complexas, a cláusula `where` melhora a legibilidade.
```rust
fn do_something<T, U>(t: T, u: U) -> i32
where
    T: Clone + Debug,
    U: Clone + Debug + Into<String>,
{ ... }
```

#### 2. Default Type Parameters e Operator Overloading
Você pode fornecer tipos padrão para parâmetros genéricos. Isso é amplamente usado na sobrecarga de operadores (via traits em `std::ops`).
```rust
trait Add<RHS=Self> {
    type Output;
    fn add(self, rhs: RHS) -> Self::Output;
}
```

#### 3. Associated Types vs Generic Parameters
- **Associated Types (`type Item;`):** Use quando houver apenas UMA implementação possível do trait para um dado tipo. (Ex: `Iterator`. Um tipo só pode iterar sobre um tipo específico de item).
- **Generic Parameters (`trait From<T>`):** Use quando um tipo puder implementar o trait múltiplas vezes para diferentes tipos. (Ex: `String` implementa `From<&str>`, `From<char>`, etc).

#### 4. Closures e Traits
Closures em Rust são implementadas via traits:
- `FnOnce`: Pode ser chamada apenas uma vez (toma posse do ambiente por valor).
- `FnMut`: Pode ser chamada múltiplas vezes e pode mutar seu ambiente (captura por referência mutável).
- `Fn`: Pode ser chamada múltiplas vezes sem mutar o ambiente (captura por referência imutável).

Ao receber uma closure como parâmetro genérico, exija a trait menos restritiva possível (geralmente `FnOnce` se você só for chamá-la uma vez, ou `FnMut` se for chamá-la num loop).

### Restrições Técnicas

- **Object Safety:** Nem todo trait pode ser transformado em um Trait Object (`dyn Trait`). Um trait é "object safe" apenas se:
  - Não exige que `Self: Sized`.
  - Todos os seus métodos não usam parâmetros genéricos e não retornam `Self` (exceto o próprio receptor `&self` / `&mut self`).
- Se um trait não for object safe, você não pode criar um `Box<dyn Trait>` dele.

## Referências

- [MIT Rust Book: Traits](https://web.mit.edu/rust-lang_v1.25/arch/amd64_ubuntu1404/share/doc/rust/html/book/first-edition/traits.html)
- [MIT Rust Book: Trait Objects](https://web.mit.edu/rust-lang_v1.25/arch/amd64_ubuntu1404/share/doc/rust/html/book/first-edition/trait-objects.html)
- [MIT Rust Book: Closures](https://web.mit.edu/rust-lang_v1.25/arch/amd64_ubuntu1404/share/doc/rust/html/book/first-edition/closures.html)
- [MIT Rust Book: Associated Types](https://web.mit.edu/rust-lang_v1.25/arch/amd64_ubuntu1404/share/doc/rust/html/book/first-edition/associated-types.html)
