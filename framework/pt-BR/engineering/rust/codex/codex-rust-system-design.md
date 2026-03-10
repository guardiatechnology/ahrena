# Codex: System Design e Padrões de Arquitetura em Rust

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Arquitetura de Sistemas, Design de Bibliotecas e Aplicações

## Visão Geral
Este Codex documenta os padrões arquiteturais de alto nível para construir sistemas complexos em Rust. Ele consolida aprendizados de sistemas massivos como TiKV (banco de dados distribuído), Meilisearch (motor de busca de alta performance) e Alacritty (renderizador de terminal acelerado por GPU), bem como ferramentas CLI ultra-rápidas como ripgrep.

## Contexto
- **Domínio:** Arquitetura de software, estruturação de workspaces, observabilidade, FSM (Finite State Machines).
- **Público-alvo:** Arquitetos de Software, Tech Leads, Agentes de IA (Warriors de Design).
- **Atualização:** Quando novos padrões arquiteturais dominarem o ecossistema Rust.

## Conteúdo

### Princípios

1. **Arquitetura Orientada a Crates (Workspaces):** Sistemas grandes em Rust não devem ser monólitos monolíticos de código. Devem ser divididos em múltiplos *crates* usando o recurso de `[workspace]` do Cargo. Isso melhora os tempos de compilação, impõe fronteiras de dependência estritas e facilita testes isolados (ex: `ripgrep` possui crates `core`, `regex`, `searcher`; `meilisearch` possui `index-scheduler`, `milli`, etc).
2. **Separação entre Lógica Pura e Efeitos (I/O):** A lógica de negócio principal (como parsing, busca, regras de negócio) deve ser pura, síncrona e livre de I/O. Efeitos colaterais (rede, disco) devem ser empurrados para as bordas do sistema.
3. **Observabilidade desde o Dia 0:** Logs, métricas e tracing não são *afterthoughts*. Em Rust, o ecossistema `tracing` é o padrão absoluto para instrumentação estruturada e deve ser integrado nas fundações da aplicação.

### Padrões e Convenções

| Padrão | Descrição | Exemplo de Uso |
|---------|-----------|----------------|
| **Workspace Dependencies** | Usar `[workspace.dependencies]` no Cargo.toml raiz para garantir que todos os crates usem a mesma versão de uma dependência. | TiKV, Meilisearch, Tokio. |
| **FSM (Finite State Machine)** | Modelar ciclos de vida complexos como máquinas de estado onde transições inválidas são impossíveis de compilar. | `batch-system` do TiKV. |
| **Newtype Pattern** | Envolver tipos primitivos em structs (ex: `struct TaskId(u32)`) para garantir type safety e evitar confusão de parâmetros. | `index-scheduler` do Meilisearch. |
| **Trait Objects vs Generics** | Usar Genéricos (`impl Trait` ou `<T: Trait>`) para performance máxima (monomorfização). Usar Trait Objects (`Box<dyn Trait>`) para reduzir tempo de compilação ou quando heterogeneidade é necessária. | `Matcher` trait no Ripgrep. |

### Decisões Vigentes

| Decisão | Descrição | Status |
|---------|---------|--------|
| Workspace Obrigatório | Projetos com mais de 5.000 linhas de código DEVEM ser estruturados como um Cargo Workspace. | Ativa |
| Instrumentação com Tracing | Todo componente lógico importante DEVE ser instrumentado com a macro `#[tracing::instrument]`. | Ativa |
| Configuração Centralizada | A configuração de linting (`clippy.toml` ou `.cargo/config.toml`) DEVE ser definida na raiz do workspace e herdada. | Ativa |

### Padrões Arquiteturais

#### 1. Arquitetura de Event Loop (Padrão Alacritty)
Para sistemas interativos ou que processam eventos contínuos, um Event Loop central gerencia o estado, enquanto sistemas de polling e renderização/processamento correm em paralelo.
- **Contexto da Janela:** O estado é encapsulado em um contexto (ex: `WindowContext`).
- **Comunicação:** Eventos são passados via canais MPSC (`mpsc::channel`) ou proxies do event loop (`EventLoopProxy`).

#### 2. Batching e Task Queues (Padrão Meilisearch / TiKV)
Para sistemas que processam alto volume de mutações, processar requisições uma a uma destrói a performance devido ao overhead de I/O.
- **Task Scheduler:** Requisições de escrita são inseridas em uma fila durável.
- **Batching:** Uma thread de background (o *scheduler*) acorda, retira múltiplas tasks da fila e as processa em um único lote (batch), amortizando o custo de I/O de disco.
- **Snapshot Isolation:** Leituras (buscas) ocorrem simultaneamente contra um *snapshot* read-only do banco de dados, sem serem bloqueadas pelas escritas.

#### 3. Traits de Abstração de Engine (Padrão TiKV)
Para sistemas que dependem de infraestrutura pesada (como RocksDB), a lógica não deve depender diretamente da implementação.
- **Engine Traits:** Crie um crate (ex: `engine_traits`) contendo apenas traits (`KvEngine`, `Snapshot`, `WriteBatch`).
- **Implementações:** Crie crates separados (ex: `engine_rocks`) que implementam as traits.
- Isso permite mockar o banco de dados em testes e trocar a engine no futuro.

### Restrições Técnicas

- **Proibição de `std::thread::spawn` direto:** Em sistemas grandes, o uso direto de threads do SO deve ser desencorajado em favor de thread pools nomeadas ou do runtime assíncrono (para rastreabilidade e controle de pânico). Se necessário, use builders que configurem hooks de pânico e nomes (como o `sys::thread` do TiKV).
- **Tratamento de Pânico:** Binários de servidor ou daemon DEVEM configurar um panic hook customizado (via `std::panic::set_hook`) para garantir que pânicos sejam logados via `tracing` antes do processo abortar.

## Glossário

| Termo | Definição |
|-------|-----------|
| **Cargo Workspace** | Funcionalidade do Cargo que permite gerenciar múltiplos crates dentro de um único repositório, compartilhando o `Cargo.lock` e o diretório `target/`. |
| **Monomorfização** | Processo onde o compilador Rust gera uma cópia específica de uma função genérica para cada tipo com o qual ela é chamada. Garante performance máxima, mas aumenta o tempo de compilação e o tamanho do binário. |
| **Newtype** | Padrão idiomático em Rust de criar uma struct tuple com um único campo (ex: `struct UserId(String)`) para obter garantias estritas de tipagem em tempo de compilação. |

## Referências
- [The Rust Performance Book](https://nnethercote.github.io/perf-book/)
- [TiKV Architecture](https://tikv.org/docs/5.1/concepts/architecture/)
- [Meilisearch Engine Architecture](https://blog.meilisearch.com/meilisearch-architecture/)
- `lex-rust-library-error-types`

---
**Gerado com base na arquitetura de TiKV, Meilisearch, Alacritty e Ripgrep.**
