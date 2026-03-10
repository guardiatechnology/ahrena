# Codex: Arquitetura Assíncrona e Concorrência com Tokio

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Concorrência, Runtimes Assíncronos, Tokio

## Visão Geral
Este Codex documenta os padrões arquiteturais, primitivas de concorrência e melhores práticas para construir sistemas assíncronos robustos em Rust, baseando-se intensamente nos padrões de design do próprio framework `tokio` e em sistemas distribuídos como `meilisearch` e `tikv`. O objetivo é guiar desenvolvedores e agentes de IA a extrair o máximo de performance sem comprometer a segurança ou a latência.

## Contexto
- **Domínio:** Concorrência, paralelismo, event loops, I/O não bloqueante.
- **Público-alvo:** Desenvolvedores Backend, Engenheiros de Plataforma, Agentes de IA.
- **Atualização:** A cada nova versão MAJOR/MINOR relevante do Tokio.

## Conteúdo

### Princípios

1. **Assincronismo não é Paralelismo:** Runtimes assíncronos (como Tokio) usam concorrência cooperativa (cooperative multitasking). Uma única thread pode gerenciar milhares de conexões (`concorrência`), mas apenas executará uma de cada vez. Para `paralelismo`, é necessário usar o runtime multithreaded (padrão no `#[tokio::main]`) e delegar trabalho pesado.
2. **Yield é Rei:** Tasks assíncronas devem ceder o controle de volta ao executor (via `await`) frequentemente. O bloqueio de uma thread de worker causa *starvation* nas outras tasks.
3. **Cancellation Safety:** Futures em Rust podem ser canceladas a qualquer momento sendo simplesmente *dropadas* (desalocadas). Todo código assíncrono, especialmente dentro de macros como `tokio::select!`, deve ser desenhado para suportar cancelamento sem deixar o estado corrompido.

### Padrões e Convenções

| Padrão | Descrição | Exemplo de Uso |
|---------|-----------|----------------|
| **Task Spawning** | Usar `tokio::spawn` para trabalho independente que deve viver além do escopo atual. | Aceitar conexões TCP e delegar para uma nova task. |
| **JoinSet** | Usar `tokio::task::JoinSet` em vez de `Vec<JoinHandle>` para gerenciar e aguardar múltiplas tasks. | Processamento de batch em Meilisearch. |
| **Spawn Blocking** | Usar `tokio::task::spawn_blocking` para I/O síncrono legado ou CPU-bound intenso. | Hashes criptográficos, acesso a banco SQLite síncrono. |
| **Canais MPSC** | Usar `tokio::sync::mpsc` para comunicação entre tasks (message passing). | Envio de métricas, loggers assíncronos. |
| **Watch Channel** | Usar `tokio::sync::watch` para transmitir estado atualizado para muitos leitores. | Configurações dinâmicas, flags de shutdown. |

### Decisões Vigentes

| Decisão | Descrição | Status |
|---------|---------|--------|
| Proibição de Bloqueio | É proibido usar `std::thread::sleep` ou locks síncronos longos em `async fn`. (Ver `lex-rust-no-blocking-in-async`) | Ativa |
| Graceful Shutdown | Sistemas DEVEM implementar shutdown gracioso usando `CancellationToken` ou `watch` channels. | Ativa |
| Limite de Concorrência | Loops assíncronos não limitados (`futures::stream::StreamExt::for_each_concurrent(None)`) são proibidos; sempre defina um limite explícito. | Ativa |

### Padrões Arquiteturais

#### 1. Graceful Shutdown (Cancelamento Coordenado)
Sistemas devem escutar sinais do SO (ex: SIGTERM) e coordenar o encerramento das tasks sem perder dados.

```rust
use tokio::signal;
use tokio::sync::watch;

async fn main_loop() {
    let (shutdown_tx, mut shutdown_rx) = watch::channel(false);

    // Task de monitoramento de sinal
    tokio::spawn(async move {
        signal::ctrl_c().await.unwrap();
        let _ = shutdown_tx.send(true);
    });

    // Task de trabalho
    tokio::spawn(async move {
        loop {
            tokio::select! {
                _ = do_work() => { /* trabalho normal */ }
                _ = shutdown_rx.changed() => {
                    println!("Recebido sinal de shutdown. Limpando...");
                    break;
                }
            }
        }
    });
}
```

#### 2. Actor Pattern (Encapsulamento de Estado)
Em vez de compartilhar estado mutável com `Arc<Mutex<T>>`, encapsule o estado em uma task (ator) e comunique-se via canais.

```rust
use tokio::sync::{mpsc, oneshot};

enum Command {
    Increment,
    Get { responder: oneshot::Sender<u32> },
}

// O Ator
async fn counter_actor(mut rx: mpsc::Receiver<Command>) {
    let mut count = 0;
    while let Some(cmd) = rx.recv().await {
        match cmd {
            Command::Increment => count += 1,
            Command::Get { responder } => {
                let _ = responder.send(count);
            }
        }
    }
}
```

#### 3. Select e Cancellation Safety
O macro `tokio::select!` avalia múltiplas futures simultaneamente. Quando uma termina, as outras são *dropadas*. Apenas use em branches futures que são "Cancellation Safe" (ex: `mpsc::Receiver::recv`).

**Perigo:** Ler de um stream de bytes (`AsyncReadExt::read`) não é cancellation safe. Se a future for dropada no meio da leitura, bytes podem ser perdidos.

### Restrições Técnicas

- **Mutex Assíncrono:** Use `tokio::sync::Mutex` **apenas** se precisar segurar o lock através de um ponto de `.await`. Para locks rápidos em memória, `std::sync::Mutex` ou `parking_lot::Mutex` são muito mais performáticos.
- **Evite `.await` em loops críticos:** Se uma operação CPU-bound possui um loop longo, insira `tokio::task::yield_now().await` periodicamente para evitar starvation do runtime.

## Diagrama de Referência

```
Runtime Tokio (Multi-thread)
┌───────────────────────────────────────────────────────────┐
│  Worker Thread 1                  Worker Thread 2         │
│ ┌─────────────────┐             ┌─────────────────┐       │
│ │ Task A (yield)  │ ◄─ Steal ── │ Task C (run)    │       │
│ │ Task B (run)    │             │ Task D (yield)  │       │
│ └─────────────────┘             └─────────────────┘       │
│          ▲                               ▲                │
│          │                               │                │
│          └─────────── Global Queue ──────┘                │
│                              ▲                            │
│                              │ (I/O, Timers)              │
│                        I/O Driver                         │
└───────────────────────────────────────────────────────────┘
                               │ (spawn_blocking)
┌──────────────────────────────▼────────────────────────────┐
│  Blocking Thread Pool (I/O Síncrono, CPU-bound)           │
│  [ Thread 3 ]  [ Thread 4 ]  [ Thread N ]                 │
└───────────────────────────────────────────────────────────┘
```

## Glossário

| Termo | Definição |
|-------|-----------|
| **Future** | Um valor que representa uma computação assíncrona que pode ainda não ter sido concluída. Em Rust, são *lazy* (não fazem nada até sofrerem `poll`). |
| **Executor/Runtime** | O motor que faz o *poll* (avaliação) das Futures. O compilador Rust não inclui um runtime; o Tokio é a escolha padrão da indústria. |
| **Starvation** | Situação onde tasks prontas para executar não ganham tempo de CPU porque outras tasks não estão cedendo (yielding) a thread. |
| **Cancellation Safety** | A propriedade de uma future que garante que nenhum estado é corrompido ou perdido se a future for descartada (dropped) antes de concluir. |

## Referências
- [Tokio Tutorial](https://tokio.rs/tokio/tutorial)
- [Tokio: Cancellation Safety](https://docs.rs/tokio/latest/tokio/macro.select.html#cancellation-safety)
- [Repositório Tokio (Examples)](https://github.com/tokio-rs/tokio/tree/master/examples)
- `lex-rust-no-blocking-in-async`

---
**Gerado com base nos padrões do ecossistema Tokio e sistemas distribuídos em Rust.**
