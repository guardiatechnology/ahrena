# Codex: Performance e Arquitetura de Busca em Rust

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Desenvolvimento de Ferramentas de Alta Performance, Busca de Texto e Indexação em Rust

## Visão Geral

Este Codex documenta os princípios, padrões e decisões arquiteturais para construir software de alta performance em Rust, com foco em busca de texto, processamento de streams de bytes e indexação. É baseado na experiência prática de Andrew Gallant (BurntSushi) na construção de `ripgrep`, `regex`, `regex-automata`, `fst`, `aho-corasick`, `memchr` e `bstr` — ferramentas que definem o estado da arte em performance de busca no ecossistema Rust.

## Contexto

- **Domínio:** Performance de busca de texto, processamento de I/O, autômatos finitos, indexação e otimizações de baixo nível em Rust.
- **Público-alvo:** Agentes de IA (Warriors), desenvolvedores de ferramentas CLI, engenheiros de plataforma, arquitetos de sistemas de busca.
- **Atualização:** Quando novas versões das crates de busca (`regex`, `aho-corasick`, `memchr`, `fst`) introduzirem mudanças de API ou novas estratégias de performance.

## Conteúdo

### Princípios

1. **Nunca busque linha por linha:** O caminho ingênuo de ler um arquivo linha por linha e aplicar um padrão a cada linha é lento porque paga o overhead de parsing de linha para cada linha, mesmo quando a maioria não vai corresponder. Busque em buffers grandes e localize as linhas apenas quando houver uma correspondência.
2. **Otimizações literais primeiro:** Antes de invocar o motor de regex completo, extraia literais do padrão e use algoritmos de busca de substring acelerados por SIMD (como `memchr` e `memmem`) para encontrar candidatos rapidamente. O motor de regex só é invocado para confirmar correspondências.
3. **Amortize alocações:** Em caminhos críticos de performance, reutilize buffers em vez de criar novas alocações a cada iteração. Passe `&mut Vec<u8>` ou `&mut String` como parâmetros de saída em APIs que precisam de alta taxa de transferência.
4. **Autômatos finitos garantem linearidade:** Motores de regex baseados em autômatos finitos (NFA/DFA) garantem tempo O(m × n) no pior caso, onde `m` é o tamanho do padrão e `n` é o tamanho do texto. Motores baseados em backtracking (PCRE) podem ter comportamento exponencial em certos padrões.
5. **FST para conjuntos e mapas massivos:** Para representar conjuntos ou mapas de strings com milhões ou bilhões de chaves, Finite State Transducers (FST) oferecem compressão superior a gzip em muitos casos, com busca em tempo O(k) onde `k` é o tamanho da chave — e suportam busca fuzzy por distância de edição.

### Padrões e Convenções

| Aspecto | Padrão | Exemplo / Justificativa |
|---------|--------|---------|
| Busca de substring | `memchr::memmem` (SIMD-acelerado) | Substitui `str::contains()` em hot paths |
| Busca de múltiplos padrões | `aho_corasick::AhoCorasick` | Algoritmo Aho-Corasick + Teddy SIMD para alternações |
| Expressões regulares | `regex::Regex` compilado uma única vez | Usar `OnceLock` ou `once_cell::Lazy` |
| Internals de regex | `regex_automata` para controle fino | NFA, DFA, PikeVM, BoundedBacktracker, LazyDFA |
| Conjuntos/mapas comprimidos | `fst::Set` / `fst::Map` | Para >1M chaves ordenadas com busca fuzzy |
| Byte strings | `bstr::BStr` / `bstr::BString` | Para I/O que pode conter UTF-8 inválido |
| Leitura incremental | Buffer de tamanho fixo + `io::Read` | Evita carregar arquivo inteiro na memória |
| Paralelismo de busca | `rayon` para paralelismo de dados | Distribui arquivos entre threads de trabalho |

### Decisões Vigentes

| Decisão | Descrição | Status |
|---------|---------|--------|
| Estratégia de busca em camadas | Usar literal prefilter → motor de regex → captura de grupos. Cada camada só é invocada quando necessária. | Ativa |
| Evitar memory maps para diretórios | Memory maps são mais lentos que leitura incremental para busca em diretórios grandes (overhead de mmap em VMs e SSDs). Usar leitura incremental com buffer. | Ativa |
| Buffer intermediário para output paralelo | Threads de busca escrevem em buffers em memória; o output é serializado separadamente para evitar intercalação de resultados de arquivos diferentes. | Ativa |
| DFA lazy (híbrido NFA/DFA) como padrão | O `LazyDFA` de `regex-automata` é o motor padrão para busca sem captura de grupos — constrói estados DFA sob demanda e é muito mais rápido que o PikeVM. | Ativa |
| Teddy SIMD para alternações | Para padrões com múltiplos literais (ex: `foo|bar|baz`), usar o algoritmo Teddy (via `aho-corasick`) que examina múltiplos bytes em paralelo com instruções SIMD. | Ativa |

### Restrições Técnicas

- **Restrição 1:** Expressões regulares NÃO PODEM ser compiladas em loops ou handlers de requisição. Consulte `lex-rust-no-regex-compilation-in-loops`.
- **Restrição 2:** Código que processa I/O externo NÃO PODE assumir UTF-8 sem validação. Consulte `lex-rust-no-assume-utf8-on-io`.
- **Restrição 3:** Para busca de substring em hot paths, NÃO usar `str::contains()` da stdlib — usar `memchr::memmem::find()` que é acelerado por SIMD.
- **Restrição 4:** Motores de regex baseados em backtracking (PCRE, PCRE2) NÃO DEVEM ser usados como padrão — podem ter comportamento exponencial em inputs adversariais.

## Diagrama de Referência

```
Arquitetura de Busca em Camadas (estilo ripgrep):

Input (arquivo / stdin)
        │
        ▼
┌─────────────────────┐
│  Leitura Incremental │  ← Buffer fixo (ex: 64KB), sem memory map
│  (io::Read + buffer) │
└─────────────────────┘
        │
        ▼
┌─────────────────────┐
│  Prefilter Literal   │  ← memchr / memmem / Aho-Corasick / Teddy SIMD
│  (candidatos rápidos)│    Examina bytes sem invocar o motor de regex
└─────────────────────┘
        │ (candidatos)
        ▼
┌─────────────────────┐
│  Motor de Regex      │  ← LazyDFA (sem captura) ou PikeVM (com captura)
│  (confirmação)       │    Invocado apenas para confirmar candidatos
└─────────────────────┘
        │ (matches confirmados)
        ▼
┌─────────────────────┐
│  Output Buffer       │  ← Buffer em memória por thread
│  (serializado)       │    Dump para stdout serializado entre threads
└─────────────────────┘

Crates por camada:
  Leitura:    std::io, bstr::io::BufReadExt
  Prefilter:  memchr (memmem), aho-corasick
  Regex:      regex-automata (LazyDFA, PikeVM, BoundedBacktracker)
  Indexação:  fst (Set/Map com FST)
  Paralelismo: rayon, crossbeam
```

## Glossário

| Termo | Definição |
|-------|-----------|
| **NFA** (Nondeterministic Finite Automaton) | Autômato finito não-determinístico. Representa um padrão de regex de forma compacta. Pode estar em múltiplos estados simultaneamente. |
| **DFA** (Deterministic Finite Automaton) | Autômato finito determinístico. Derivado do NFA, está em exatamente um estado por vez. Busca mais rápida, mas pode ter tamanho exponencial. |
| **LazyDFA** (Hybrid NFA/DFA) | Constrói estados DFA sob demanda durante a busca, evitando a explosão de estados do DFA completo. Padrão do `regex-automata`. |
| **PikeVM** | Motor de regex baseado em NFA com semântica de threads virtuais. Suporta captura de grupos. Mais lento que DFA mas mais flexível. |
| **BoundedBacktracker** | Motor de backtracking com limite de memória O(m×n) para garantir terminação. Mais rápido que PikeVM para haystacks pequenos. |
| **FST** (Finite State Transducer) | Autômato finito que mapeia sequências de entrada para saídas. Usado para representar conjuntos e mapas ordenados de strings com alta compressão. |
| **Prefilter** | Otimização que busca literais extraídos do padrão para encontrar candidatos rapidamente antes de invocar o motor de regex completo. |
| **Teddy** | Algoritmo SIMD para busca de múltiplos literais simultaneamente. Inventado por Geoffrey Langdale para o Hyperscan da Intel. Usado no `aho-corasick`. |
| **memchr** | Crate Rust que fornece implementações SIMD-aceleradas de `memchr`, `memchr2`, `memchr3` e `memmem` (busca de substring). |
| **Amortização de alocação** | Técnica de reutilizar buffers alocados entre chamadas, evitando o custo de alocação/desalocação em hot paths. |
| **Hot path** | Caminho de código executado com alta frequência — o gargalo de performance mais provável. |

## Referências

- [ripgrep is faster than {grep, ag, git grep, ucg, pt, sift} (BurntSushi)](https://burntsushi.net/ripgrep/)
- [Regex engine internals as a library (BurntSushi)](https://burntsushi.net/regex-internals/)
- [Index 1,600,000,000 Keys with Automata and Rust — fst (BurntSushi)](https://burntsushi.net/transducers/)
- [A byte string library for Rust — bstr (BurntSushi)](https://burntsushi.net/bstr/)
- [memchr — crates.io](https://crates.io/crates/memchr)
- [regex-automata — crates.io](https://crates.io/crates/regex-automata)
- [aho-corasick — crates.io](https://crates.io/crates/aho-corasick)
- [fst — crates.io](https://crates.io/crates/fst)
- `lex-rust-no-regex-compilation-in-loops` — Lei sobre compilação de regex em loops
- `lex-rust-no-assume-utf8-on-io` — Lei sobre encoding em I/O

---

**Gerado com base nos ensinamentos de Andrew Gallant (BurntSushi) e nas práticas do ecossistema Rust.**
