# Codex: Tratamento de Erros em Rust

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Desenvolvimento de Bibliotecas e Aplicações em Rust

## Visão Geral

Este Codex é a referência central para decisões de tratamento de erros em Rust. Cobre a escolha entre `Result` e `Option`, a definição de tipos de erro customizados, o uso do operador `?`, a diferença de estratégia entre bibliotecas e aplicações, e quando `panic!` é e não é apropriado. É baseado nos princípios consolidados por Andrew Gallant (BurntSushi) ao longo de anos de manutenção de crates críticos do ecossistema Rust.

## Contexto

- **Domínio:** Tratamento de erros, tipos de erro, propagação, ergonomia de API em Rust.
- **Público-alvo:** Agentes de IA (Warriors), desenvolvedores Rust, revisores de código.
- **Atualização:** Quando novas versões do Rust introduzirem mudanças na trait `Error` ou no operador `?`, ou quando novas crates de erro se tornarem padrão do ecossistema.

## Conteúdo

### Princípios

1. **Erros são valores, não exceções:** Rust não tem exceções. Erros são retornados como valores do tipo `Result<T, E>` ou `Option<T>`. Isso força o chamador a lidar com eles explicitamente, tornando o fluxo de erros visível e composicional.
2. **Bibliotecas definem tipos de erro ricos; aplicações usam tipos de erro flexíveis:** Bibliotecas DEVEM definir seus próprios tipos de erro (implementando `std::error::Error`) para não remover escolhas do chamador. Aplicações podem usar `anyhow::Error` para flexibilidade e contexto automático.
3. **O operador `?` é a cola do sistema:** O operador `?` combina análise de caso, controle de fluxo e conversão de tipo de erro em uma única expressão. É o mecanismo central de ergonomia de tratamento de erros em Rust.
4. **`panic!` é para bugs, não para erros:** Se um pânico ocorre, significa que há um bug no programa. Erros de ambiente (arquivo não encontrado, rede indisponível, entrada inválida do usuário) NUNCA devem causar pânico em código de produção.
5. **Prefira `expect()` a `unwrap()` para invariantes:** Quando um pânico é justificado (invariante interno), use `expect("mensagem descritiva do invariante")` em vez de `unwrap()` para facilitar o diagnóstico.

### Padrões e Convenções

| Contexto | Estratégia | Crate/Tipo |
|----------|-----------|------------|
| Biblioteca pública | Tipo de erro customizado com `thiserror` | `#[derive(thiserror::Error)]` |
| Aplicação / binário | Tipo de erro flexível com contexto | `anyhow::Result<T>` |
| Função com múltiplos erros | Propagação com conversão automática | Operador `?` + `From` impl |
| Erro de invariante interno | Pânico com mensagem descritiva | `.expect("BUG: descrição do invariante")` |
| Ausência de valor (não é erro) | Option sem erro | `Option<T>` com `.ok_or()` para converter |
| Alias de Result por módulo | Reduzir verbosidade | `type Result<T> = std::result::Result<T, MeuErro>` |

### Decisões Vigentes

| Decisão | Descrição | Status |
|---------|---------|--------|
| `thiserror` para bibliotecas | A crate `thiserror` é o padrão para definir tipos de erro em bibliotecas. Ela gera automaticamente as implementações de `Display` e `std::error::Error` via macros de derivação. | Ativa |
| `anyhow` para aplicações | A crate `anyhow` é o padrão para aplicações (binários). Permite adicionar contexto a erros com `.context("...")` e `.with_context(|| ...)`. | Ativa |
| `From` para conversão automática | Implementar `From<ErroExterno>` no tipo de erro da biblioteca permite que o operador `?` converta erros automaticamente, sem `map_err()`. | Ativa |
| Alias de `Result` por módulo | Módulos com muitas funções que retornam o mesmo tipo de erro DEVEM definir `type Result<T> = std::result::Result<T, MeuErro>` para reduzir verbosidade. | Ativa |

### Restrições Técnicas

- Bibliotecas NÃO DEVEM usar `anyhow::Error` em suas APIs públicas — isso apaga informação de tipo e remove escolhas do chamador.
- Tipos de erro de bibliotecas DEVEM implementar `std::error::Error`, `Debug` e `Display`.
- O operador `?` DEVE ser preferido a `.unwrap()`, `.map_err()` encadeados ou `match` explícito para propagação de erros.
- Consulte `lex-rust-no-panic-in-production` para a lei absoluta sobre uso de `panic!` em produção.

## Diagrama de Referência

```
Situação de Erro
      │
      ├─── É um bug no código? ──────────────► panic! / expect() / assert!
      │         (invariante violado)
      │
      └─── É um erro de ambiente/usuário? ───► Result<T, E>
                (recuperável)                        │
                                                     ├─── Biblioteca? ──► tipo customizado (thiserror)
                                                     │
                                                     └─── Aplicação? ───► anyhow::Result<T>

Propagação:
  fn foo() -> Result<T, E> {
      let x = operacao_que_pode_falhar()?;  // ? = match + return Err + From::from
      Ok(x)
  }
```

## Glossário

| Termo | Definição |
|-------|-----------|
| `Result<T, E>` | Tipo enum com variantes `Ok(T)` (sucesso) e `Err(E)` (falha). É o mecanismo central de tratamento de erros em Rust. |
| `Option<T>` | Tipo enum com variantes `Some(T)` (valor presente) e `None` (ausência). Usado quando a ausência não é um erro, mas uma condição normal. |
| Operador `?` | Açúcar sintático que, aplicado a um `Result` ou `Option`, retorna o valor em caso de sucesso ou propaga o erro (após conversão via `From`) em caso de falha. |
| `thiserror` | Crate que fornece macros de derivação para implementar `std::error::Error` em tipos customizados com mínimo boilerplate. Padrão para bibliotecas. |
| `anyhow` | Crate que fornece `anyhow::Error`, um tipo de erro dinâmico que pode encapsular qualquer erro e adicionar contexto. Padrão para aplicações. |
| `From` trait | Trait de conversão. Implementar `From<ErroA>` para `ErroB` permite que o operador `?` converta automaticamente `ErroA` em `ErroB`. |
| Invariante interno | Condição que o código garante ser sempre verdadeira. Sua violação indica um bug no programa, não um erro de ambiente. |
| Pânico | Mecanismo de Rust para sinalizar bugs irrecuperáveis. Aborta a thread (ou o processo, dependendo da configuração). NÃO é tratamento de erro. |

## Referências

- [Error Handling in Rust (BurntSushi)](https://burntsushi.net/rust-error-handling/)
- [Using unwrap() in Rust is Okay (BurntSushi)](https://burntsushi.net/unwrap/)
- [thiserror — crates.io](https://crates.io/crates/thiserror)
- [anyhow — crates.io](https://crates.io/crates/anyhow)
- `lex-rust-no-panic-in-production` — Lei absoluta sobre panic em produção

---

**Gerado com base nos ensinamentos de Andrew Gallant (BurntSushi) e nas práticas do ecossistema Rust.**
