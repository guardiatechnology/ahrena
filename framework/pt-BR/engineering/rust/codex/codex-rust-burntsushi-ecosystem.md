# Codex: Ecossistema de Crates BurntSushi para Rust

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Seleção e Uso de Crates do Ecossistema Andrew Gallant (BurntSushi)

## Visão Geral

Este Codex é um guia de referência rápida para as crates criadas e mantidas por Andrew Gallant (BurntSushi) — um dos contribuidores mais influentes do ecossistema Rust. Suas crates definem o estado da arte em busca de texto, processamento de bytes, parsing e indexação. Este Codex descreve quando usar cada crate, como elas se relacionam entre si e quais são as decisões de design que as tornam excepcionais.

## Contexto

- **Domínio:** Seleção de crates, integração de bibliotecas de busca e processamento de texto em Rust.
- **Público-alvo:** Agentes de IA (Warriors), desenvolvedores Rust, arquitetos de plataforma.
- **Atualização:** Quando novas versões major das crates forem lançadas ou quando novas crates forem adicionadas ao ecossistema BurntSushi.

## Conteúdo

### Princípios

1. **Cada crate tem um escopo bem definido:** As crates de BurntSushi seguem o princípio Unix de fazer uma coisa e fazê-la bem. Elas são compostas entre si em vez de serem monolíticas.
2. **Dois níveis de API são comuns:** Muitas crates oferecem uma API de alto nível (conveniente) e uma de baixo nível (controle total). Ex: `regex` vs `regex-automata`, `csv` vs `csv-core`.
3. **Performance é uma feature, não um acidente:** Todas as crates são benchmarkadas e otimizadas. Usar essas crates significa herdar anos de trabalho de otimização.
4. **Compatibilidade com dados reais:** As crates são projetadas para lidar com dados do mundo real, incluindo UTF-8 inválido, arquivos binários e inputs adversariais.

### Mapa de Crates

| Crate | Propósito | Quando Usar |
|-------|-----------|-------------|
| `regex` | Expressões regulares com garantia de tempo linear | Busca de padrões em texto; padrão para a maioria dos casos |
| `regex-automata` | Internals do motor de regex como API pública | Controle fino sobre NFA/DFA/PikeVM; casos avançados |
| `regex-syntax` | Parser e AST de sintaxe de regex | Análise de padrões de regex sem executar busca |
| `aho-corasick` | Busca de múltiplos padrões simultaneamente | Alternações de literais (`foo|bar|baz`); mais rápido que regex para literais |
| `memchr` | Busca de bytes e substrings acelerada por SIMD | Busca de um byte (`memchr`), dois (`memchr2`), ou substring (`memmem`) |
| `bstr` | Byte strings com operações de string sem exigir UTF-8 | I/O de arquivos, stdin, pipes; qualquer dado que pode ter UTF-8 inválido |
| `fst` | Conjuntos e mapas comprimidos com FST | Índices de milhões/bilhões de chaves; busca fuzzy por distância de edição |
| `csv` | Parsing e escrita de CSV com Serde | Leitura/escrita de arquivos CSV; integração com tipos Rust via Serde |
| `walkdir` | Iteração recursiva eficiente de diretórios | Travessia de árvores de diretórios; substitui `std::fs::read_dir` recursivo |
| `byteorder` | Leitura/escrita de inteiros com controle de endianness | Formatos binários, protocolos de rede, arquivos com endianness específico |
| `jiff` | Biblioteca de data e hora inspirada no Temporal | Manipulação de datas, fusos horários, durações; alternativa moderna ao `chrono` |
| `quickcheck` | Testes baseados em propriedades (property-based testing) | Geração automática de casos de teste; encontra edge cases que testes manuais perdem |
| `ripgrep` (ferramenta) | Ferramenta de busca de texto de alta performance | Busca em repositórios de código; referência de implementação de busca |

### Relações entre Crates

```
memchr ──────────────────────────────────────────────────────► base SIMD
    │
    └──► aho-corasick (prefilter de múltiplos literais)
    │         │
    └──► regex-automata (motor de regex)
              │
              └──► regex (API de alto nível)
                        │
                        └──► ripgrep (ferramenta CLI)

bstr ──────────────────────────────────────────────────────────► byte strings
    │
    └──► integração com regex-automata para busca em bytes

fst ───────────────────────────────────────────────────────────► indexação comprimida
    │
    └──► integração com regex-automata para busca com regex em FST

csv ───────────────────────────────────────────────────────────► parsing CSV
    │
    └──► csv-core (parser sem std, para no_std e performance)
```

### Decisões de Uso

| Situação | Crate Recomendada | Justificativa |
|----------|-------------------|---------------|
| Busca de padrão simples em `&str` | `regex` | API de alto nível, fácil de usar |
| Busca de múltiplos literais (`foo|bar`) | `aho-corasick` | Mais rápido que regex para alternações de literais |
| Busca de substring em `&[u8]` | `memchr::memmem` | SIMD-acelerado, sem overhead de regex |
| Busca de um byte específico | `memchr::memchr` | A função mais rápida para encontrar um byte |
| Processamento de arquivo com possível UTF-8 inválido | `bstr` | Operações de string sem exigir UTF-8 válido |
| Índice de milhões de chaves | `fst` | Compressão + busca O(k) + fuzzy search |
| Parsing de CSV com tipos Rust | `csv` + `serde` | Desserialização automática para structs |
| Travessia de diretório | `walkdir` | Eficiente, segue symlinks, limita file descriptors |
| Controle fino de regex (NFA/DFA) | `regex-automata` | Para casos avançados: streaming, DFA serializado, etc. |
| Data e hora com fusos horários | `jiff` | API moderna, inspirada no Temporal, suporte IANA |

### Restrições Técnicas

- **Restrição 1:** `regex::Regex` NÃO PODE ser compilado em loops. Consulte `lex-rust-no-regex-compilation-in-loops`.
- **Restrição 2:** `bstr` DEVE ser usado quando dados de I/O podem conter UTF-8 inválido. Consulte `lex-rust-no-assume-utf8-on-io`.
- **Restrição 3:** Para busca de substring em hot paths, preferir `memchr::memmem` a `str::contains()` — o primeiro usa SIMD, o segundo não (em versões antigas da stdlib).
- **Restrição 4:** `fst` requer que as chaves sejam inseridas em **ordem lexicográfica**. Inserção fora de ordem resulta em erro.

## Glossário

| Termo | Definição |
|-------|-----------|
| **SIMD** | Single Instruction, Multiple Data. Instruções de CPU que processam múltiplos dados em paralelo (ex: SSE2, AVX2). Usado por `memchr`, `aho-corasick` (Teddy) para alta performance. |
| **Teddy** | Algoritmo SIMD para busca de múltiplos padrões literais simultaneamente. Inventado por Geoffrey Langdale para o Hyperscan da Intel. Integrado ao `aho-corasick`. |
| **Aho-Corasick** | Algoritmo de busca de múltiplos padrões em tempo O(n + m + z), onde n é o tamanho do texto, m a soma dos tamanhos dos padrões e z o número de ocorrências. |
| **FST** | Finite State Transducer. Autômato que mapeia strings para valores. Usado pelo `fst` para representar conjuntos e mapas comprimidos. |
| **Levenshtein** | Distância de edição entre duas strings (número mínimo de inserções, deleções e substituições). Suportado pelo `fst` para busca fuzzy. |
| **`no_std`** | Modo de compilação Rust sem a biblioteca padrão. Usado em sistemas embarcados. `csv-core` e `regex-automata` suportam `no_std`. |
| **Serde** | Framework de serialização/desserialização de facto em Rust. Integrado ao `csv`, `bstr` e `jiff`. |
| **Property-based testing** | Estratégia de teste onde propriedades do código são verificadas contra inputs gerados aleatoriamente. `quickcheck` implementa isso em Rust. |

## Referências

- [Andrew Gallant's Blog — Projects](https://burntsushi.net/projects/)
- [regex — crates.io](https://crates.io/crates/regex)
- [regex-automata — crates.io](https://crates.io/crates/regex-automata)
- [aho-corasick — crates.io](https://crates.io/crates/aho-corasick)
- [memchr — crates.io](https://crates.io/crates/memchr)
- [bstr — crates.io](https://crates.io/crates/bstr)
- [fst — crates.io](https://crates.io/crates/fst)
- [csv — crates.io](https://crates.io/crates/csv)
- [walkdir — crates.io](https://crates.io/crates/walkdir)
- [jiff — crates.io](https://crates.io/crates/jiff)
- [ripgrep — GitHub](https://github.com/BurntSushi/ripgrep)
- `codex-rust-performance-and-search` — Arquitetura de busca em camadas
- `codex-rust-error-handling` — Tratamento de erros em Rust

---

**Gerado com base nos projetos e ensinamentos de Andrew Gallant (BurntSushi).**
