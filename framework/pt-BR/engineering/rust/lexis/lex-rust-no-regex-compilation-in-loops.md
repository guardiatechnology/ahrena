# Lexis: Proibição de Compilação de Regex em Loops ou Caminhos Quentes

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebável | **Escopo:** Desenvolvimento de Código Rust com Expressões Regulares

## Propósito

A compilação de uma expressão regular é uma operação custosa: envolve parsing da sintaxe, construção de um NFA (Nondeterministic Finite Automaton), potencial compilação para DFA (Deterministic Finite Automaton) e alocação de memória. Quando essa compilação ocorre dentro de um loop ou em um caminho de código executado frequentemente (hot path), o custo se multiplica por cada iteração, destruindo a performance que o uso de regex deveria proporcionar. A crate `regex` de Rust é extremamente rápida para busca, mas pressupõe que a compilação é feita uma única vez. Esta lei garante que o custo de compilação seja pago apenas uma vez, na inicialização, e não repetido a cada chamada.

## Lei

> **Todo código Rust que utiliza expressões regulares NÃO PODE compilar um `Regex` (ou qualquer tipo de autômato derivado de padrão de texto) dentro de loops, closures chamadas repetidamente, handlers de requisição HTTP, ou qualquer função chamada mais de uma vez durante o ciclo de vida da aplicação.**

## Abrangência

- **Aplica-se a:** Todo código Rust que utiliza as crates `regex`, `regex-automata`, `aho-corasick`, ou qualquer outra biblioteca de busca de padrões.
- **Agentes vinculados:** Todos os agentes de desenvolvimento (Warriors).
- **Exceções:** Nenhuma. Lexis não admitem exceções.

## Consequências de Violação

1. **Bloqueio automático:** Pull Request rejeitado no CI por falha em benchmarks de performance ou por detecção via lint customizado.
2. **Alerta:** Notificação ao Tech Lead com evidência do custo de performance medido.
3. **Remediação:** O `Regex` DEVE ser movido para fora do loop, utilizando `std::sync::OnceLock`, `once_cell::sync::Lazy` ou `lazy_static!` para inicialização lazy thread-safe.

## Exemplos

### Correto

```rust
use regex::Regex;
use std::sync::OnceLock;

// Correto: compilação única usando OnceLock (estável desde Rust 1.70)
static REGEX_EMAIL: OnceLock<Regex> = OnceLock::new();

fn regex_email() -> &'static Regex {
    REGEX_EMAIL.get_or_init(|| {
        Regex::new(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}").unwrap()
        // unwrap() é aceitável aqui: é um invariante interno — o padrão é
        // um literal estático escrito pelo programador. Se falhar, é um bug.
    })
}

fn validar_emails(emails: &[&str]) -> Vec<bool> {
    let re = regex_email(); // Compilado apenas uma vez
    emails.iter().map(|e| re.is_match(e)).collect()
}

// Correto: usando once_cell para casos mais complexos
use once_cell::sync::Lazy;

static REGEX_CPF: Lazy<Regex> = Lazy::new(|| {
    Regex::new(r"\d{3}\.\d{3}\.\d{3}-\d{2}").unwrap()
});

fn extrair_cpfs(texto: &str) -> Vec<&str> {
    REGEX_CPF.find_iter(texto).map(|m| m.as_str()).collect()
}
```

### Incorreto

```rust
use regex::Regex;

// VIOLA A LEI: Regex compilado dentro de um loop
fn validar_emails_errado(emails: &[&str]) -> Vec<bool> {
    emails.iter().map(|email| {
        // COMPILAÇÃO A CADA ITERAÇÃO — custo O(n * custo_compilacao)!
        let re = Regex::new(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}").unwrap();
        re.is_match(email)
    }).collect()
}

// VIOLA A LEI: Regex compilado em handler de requisição HTTP
async fn handler_busca(query: String) -> String {
    // Compilado a cada requisição HTTP!
    let re = Regex::new(&format!(r"(?i){}", regex::escape(&query))).unwrap();
    // ...
    String::new()
}
```

## Validação Automatizada

- **Ferramenta:** Lint customizado via `cargo clippy` ou análise estática para detectar chamadas a `Regex::new()` dentro de closures passadas a `.map()`, `.filter()`, `.for_each()`, ou dentro de funções marcadas com `#[tokio::main]` / handlers de frameworks web.
- **Ferramenta complementar:** Benchmarks com `criterion` que medem o tempo de execução de funções críticas — uma regressão significativa pode indicar compilação repetida.
- **Momento:** Pipeline de CI em cada Pull Request.
- **Métrica:** 0 instâncias de `Regex::new()` dentro de iteradores ou handlers de requisição.

---

**Referência:** Baseado em [Regex engine internals as a library](https://burntsushi.net/regex-internals/) e [ripgrep is faster than {grep, ag, git grep, ucg, pt, sift}](https://burntsushi.net/ripgrep/) de Andrew Gallant (BurntSushi). A crate `regex` está em [crates.io/crates/regex](https://crates.io/crates/regex).
