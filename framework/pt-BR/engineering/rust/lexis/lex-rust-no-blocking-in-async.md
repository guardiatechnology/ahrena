# Lexis: Proibição de Bloqueio em Runtimes Assíncronos

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebrável | **Escopo:** Desenvolvimento e Concorrência

## Propósito
Em ecossistemas assíncronos como o Tokio, as tasks são executadas por um número limitado de threads do runtime (worker threads). Se uma thread for bloqueada por operações síncronas pesadas (I/O bloqueante, cálculos CPU-bound longos, ou primitivas de sincronização síncronas), outras tasks assíncronas prontas para execução sofrerão *starvation* (inanição). Isso degrada severamente a performance, aumenta a latência e pode causar deadlocks no sistema.

## Lei
> **É estritamente proibido executar operações de I/O síncronas, chamadas de sistema bloqueantes ou cálculos CPU-bound demorados dentro de um contexto assíncrono (como `async fn` ou `tokio::spawn`) sem utilizar as primitivas de delegação apropriadas (`tokio::task::spawn_blocking` ou `tokio::task::block_in_place`).**

## Abrangência
- **Aplica-se a:** Todo código que roda sob um runtime assíncrono (Tokio, async-std, smol).
- **Agentes vinculados:** Todos os agentes de IA e desenvolvedores humanos.
- **Exceções:** Cálculos puramente em memória que demoram menos de ~10-100 microssegundos podem ser executados diretamente.

## Consequências de Violação
1. **Bloqueio automático:** Pull Requests que utilizam `std::fs`, `std::thread::sleep`, ou primitivas de lock síncronas (`std::sync::Mutex` retendo lock através de pontos de `await`) serão rejeitados.
2. **Degradação de Performance:** A aplicação sofrerá gargalos severos de throughput sob carga.
3. **Revisão Obrigatória:** O código deverá ser refatorado para usar as contrapartes assíncronas (ex: `tokio::fs`, `tokio::time::sleep`) ou delegado para a pool de threads bloqueantes.

## Exemplos

### Correto

```rust
use tokio::task;

async fn process_data() {
    // CORRETO: I/O assíncrono não bloqueia a thread do worker
    let data = tokio::fs::read("config.json").await.unwrap();
    
    // CORRETO: Cálculo pesado delegado para a thread pool de blocking
    let result = task::spawn_blocking(move || {
        heavy_cryptographic_hash(&data)
    }).await.unwrap();
    
    println!("Hash: {}", result);
}
```

### Incorreto

```rust
async fn process_data_bad() {
    // VIOLAÇÃO 1: I/O Síncrono em contexto async. Bloqueia a thread inteira do Tokio.
    let data = std::fs::read("config.json").unwrap();
    
    // VIOLAÇÃO 2: Cálculo CPU-bound na thread do worker. Outras tasks ficam paradas.
    let result = heavy_cryptographic_hash(&data);
    
    // VIOLAÇÃO 3: Sleep síncrono. Trava a thread do worker.
    std::thread::sleep(std::time::Duration::from_secs(1));
}
```

## Validação Automatizada
- **Ferramenta:** `cargo clippy`
- **Momento:** Pipeline de CI
- **Configuração:** O arquivo `clippy.toml` deve proibir métodos síncronos conhecidos:
  ```toml
  [[disallowed-methods]]
  path = "std::thread::sleep"
  reason = "Use tokio::time::sleep in async contexts."
  
  [[disallowed-methods]]
  path = "std::fs::read"
  reason = "Use tokio::fs::read or spawn_blocking."
  
  [[await-holding-invalid-types]]
  path = "std::sync::MutexGuard"
  reason = "Do not hold synchronous locks across await points."
  ```
- **Métrica:** 0 violações toleradas.

---
**Fontes de Conhecimento:**
- Repositório Tokio: Padrões de `task::blocking.rs` e `spawn_blocking`.
- Repositório Meilisearch: Uso intensivo de task queues e separação de processamento síncrono/assíncrono em `index-scheduler`.
