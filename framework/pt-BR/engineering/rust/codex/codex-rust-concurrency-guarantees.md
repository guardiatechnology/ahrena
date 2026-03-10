# Codex: Concorrência e Garantias em Rust

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Desenvolvimento de Bibliotecas e Aplicações em Rust

## Visão Geral

Este Codex serve como guia definitivo para concorrência e escolha de primitivas de memória em Rust. A linguagem adota o paradigma de "Fearless Concurrency" (Concorrência sem Medo), garantindo em tempo de compilação a ausência de data races. Este documento mapeia as traits `Send` e `Sync`, as primitivas de ponteiros inteligentes (`Box`, `Rc`, `Arc`) e os padrões de estado mutável compartilhado.

## Contexto

- **Domínio:** Concorrência, paralelismo, gerenciamento de memória, smart pointers.
- **Público-alvo:** Agentes de IA (Warriors), desenvolvedores Rust, arquitetos de sistemas.
- **Atualização:** Quando novas abstrações de concorrência forem adicionadas à biblioteca padrão.

## Conteúdo

### Princípios Fundamentais

1. **Ausência de Data Races Garantida:** Rust previne data races em tempo de compilação. Se o código compila e não usa `unsafe` (ou se o `unsafe` está encapsulado corretamente), é impossível ter data races.
2. **Estado Mutável Compartilhado é Controlado:** A regra de ouro de borrowing (múltiplos leitores OU um escritor) aplica-se à concorrência. Para mutar estado compartilhado entre threads, você deve usar primitivas de sincronização (como `Mutex` ou `RwLock`).
3. **Traits de Marcação (Marker Traits):** O compilador entende a segurança de concorrência através de duas traits auto-implementadas: `Send` e `Sync`.

### Send e Sync

| Trait | Significado | Exemplo Positivo | Exemplo Negativo |
|-------|-------------|------------------|------------------|
| `Send` | O tipo pode ter sua **posse (ownership)** transferida com segurança para outra thread. | `i32`, `String`, `Box<T>`, `Arc<T>` | `Rc<T>`, ponteiros brutos (`*const T`) |
| `Sync` | O tipo pode ser **referenciado** (`&T`) com segurança por múltiplas threads simultaneamente. (Um tipo `T` é `Sync` se, e somente se, `&T` é `Send`). | `i32`, `Mutex<T>`, `Arc<T>` | `Cell<T>`, `RefCell<T>` |

### Escolhendo Suas Garantias (Smart Pointers)

Rust permite que você escolha exatamente o custo de runtime e as garantias que precisa.

#### 1. Tipos Básicos (Zero-cost em runtime)
- **`Box<T>`:** Ponteiro de posse exclusiva alocado no heap. Use quando o tamanho for desconhecido em tempo de compilação (ex: tipos recursivos, trait objects) ou quando quiser mover um grande volume de dados sem copiar.
- **`&T` e `&mut T`:** Referências. Seguem o padrão "read-write lock" em tempo de compilação. Sem custo em runtime.

#### 2. Tipos de Contagem de Referência (Custo: incremento/decremento de contador)
- **`Rc<T>` (Reference Counted):** Permite múltiplos donos na mesma thread. **Não é thread-safe** (não implementa `Send` nem `Sync`). Útil para grafos ou estruturas onde a posse não é hierárquica.
- **`Arc<T>` (Atomic Reference Counted):** A versão thread-safe do `Rc`. Usa operações atômicas para atualizar o contador. Mais lento que `Rc`, mas seguro para compartilhar entre threads.

#### 3. Tipos de Mutabilidade Interior (Custo: checagem em runtime ou lock)
Estes tipos permitem mutar dados mesmo quando você tem apenas uma referência imutável (`&T`).
- **`Cell<T>`:** Para tipos que implementam `Copy`. Mutação é feita copiando o valor inteiro. Sem custo de lock, não é thread-safe.
- **`RefCell<T>`:** Para tipos complexos. Aplica as regras de borrowing (múltiplos leitores OU um escritor) em **runtime** em vez de compile-time. Causa `panic!` se as regras forem violadas. Não é thread-safe.
- **`Mutex<T>`:** Equivalente thread-safe do `RefCell`. Bloqueia a thread atual até conseguir acesso exclusivo. Se uma thread panicar enquanto segura o lock, o Mutex fica "envenenado" (poisoned).
- **`RwLock<T>`:** Permite múltiplos leitores simultâneos ou um único escritor. Melhor performance que `Mutex` quando há muito mais leituras do que escritas.

### Matriz de Decisão

```
Precisa compartilhar dados entre múltiplas partes do código?
├── Não ──► Use posse simples (T) ou Box<T> se precisar de heap.
└── Sim
    ├── Em múltiplas threads?
    │   ├── Não ──► Use Rc<T>
    │   │           └── Precisa mutar? ──► Use Rc<RefCell<T>> ou Rc<Cell<T>>
    │   │
    │   └── Sim ──► Use Arc<T>
    │               └── Precisa mutar? ──► Use Arc<Mutex<T>> ou Arc<RwLock<T>>
```

### Padrões e Convenções

- **Closures `move` em Threads:** Ao usar `thread::spawn`, você quase sempre precisará usar uma closure `move` (`thread::spawn(move || { ... })`) para forçar a transferência de posse das variáveis capturadas para a nova thread.
- **Comunicação por Canais (Channels):** Prefira passar mensagens entre threads em vez de compartilhar memória mutável quando possível. Use `std::sync::mpsc::channel`. "Não se comunique compartilhando memória; compartilhe memória comunicando-se."

### Restrições Técnicas

- NUNCA tente contornar a ausência de `Send` ou `Sync` implementando-os manualmente com `unsafe` a menos que você seja um especialista em concorrência e tenha provado formalmente a segurança.
- Evite Deadlocks: O compilador Rust previne data races, mas **NÃO previne deadlocks**. Tenha cuidado ao adquirir múltiplos locks (`Mutex`/`RwLock`). Adquira-os sempre na mesma ordem.

## Referências

- [MIT Rust Book: Concurrency](https://web.mit.edu/rust-lang_v1.25/arch/amd64_ubuntu1404/share/doc/rust/html/book/first-edition/concurrency.html)
- [MIT Rust Book: Choosing your Guarantees](https://web.mit.edu/rust-lang_v1.25/arch/amd64_ubuntu1404/share/doc/rust/html/book/first-edition/choosing-your-guarantees.html)
- [MIT Rust Book: The Stack and the Heap](https://web.mit.edu/rust-lang_v1.25/arch/amd64_ubuntu1404/share/doc/rust/html/book/first-edition/the-stack-and-the-heap.html)
