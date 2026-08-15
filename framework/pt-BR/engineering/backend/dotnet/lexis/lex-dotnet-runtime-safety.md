# Lexis: Corretude e Segurança de Memória .NET

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebrável | **Escopo:** Código C# assíncrono, nullability e ownership de recursos

## Propósito

Evitar deadlocks, operações órfãs, `NullReferenceException` previsível, vazamento de recursos, estados inválidos e pressão desnecessária sobre o garbage collector em serviços .NET.

## Lei

> **Todo código C# de produção DEVE permanecer memory-safe por padrão, tornar ownership e estados inválidos explícitos, manter nullable reference types habilitado, propagar cancelamento, evitar sync-over-async e respeitar budgets medidos de alocação nos hot paths.**

## Abrangência

- **Aplica-se a:** projetos C# de produção, workers, APIs, bibliotecas e adaptadores
- **Agentes vinculados:** Apollo-.NET e qualquer agente que altere código C#
- **Exceções:** Nenhuma. Lexis não admitem exceções.

## Regras Verificáveis

1. Projetos novos usam `<Nullable>enable</Nullable>`; warnings de nullability não podem ser suprimidos sem justificativa local verificável.
2. Método assíncrono cancelável recebe e propaga `CancellationToken`, inclusive para HTTP, banco, filas e delays.
3. `.Result`, `.Wait()` e `.GetAwaiter().GetResult()` são proibidos no fluxo assíncrono de aplicação.
4. Quem cria recurso `IDisposable`/`IAsyncDisposable` define e executa sua liberação; recursos injetados não são descartados pelo consumidor.
5. `async void` é restrito a event handlers exigidos pelo framework.
6. Código de domínio e aplicação não usa `unsafe`, ponteiros ou acesso não verificado à memória. Interop inevitável fica isolado em adapter mínimo, com justificativa, testes de bounds/lifetime e review explícito.
7. Hot paths têm budget de alocação e evidência de profiler/benchmark. Loops por item não criam coleções, strings, closures, boxing ou tasks descartáveis sem necessidade medida.
8. `Span<T>`, `Memory<T>`, `stackalloc` e `ArrayPool<T>` só entram quando reduzem alocação medida e o lifetime está demonstravelmente correto; buffers sensíveis alugados são limpos antes da devolução.
9. Value Objects pequenos e imutáveis podem usar `readonly record struct`; structs grandes ou mutáveis são evitados por custo de cópia e aliasing confuso.
10. Aritmética cujo overflow altera dinheiro, versão, sequência ou limite usa `checked` ou tipo de domínio com validação. Estados de domínio são fechados e tratados de forma exaustiva quando a linguagem permitir.

## Consequências de Violação

1. **Bloqueio:** build/análise ou quality gate falha.
2. **Diagnóstico:** informar símbolo, fluxo de cancelamento ou recurso sem ownership.
3. **Remediação:** corrigir assinatura e propagação, substituir bloqueio síncrono ou explicitar lifetime.

## Exemplos

### Correto

```csharp
public Task<Card?> FindAsync(Guid id, CancellationToken cancellationToken) =>
    db.Cards.SingleOrDefaultAsync(card => card.Id == id, cancellationToken);
```

### Incorreto

```csharp
public Card Find(Guid id) => FindAsync(id, CancellationToken.None).Result!;
```

## Validação Automatizada

- **Ferramenta:** `dotnet build`, .NET/Roslyn analyzers e testes
- **Momento:** pre-commit e CI
- **Métrica:** 0 warnings de nullability/analyzers novos; 0 sync-over-async; 100% das chamadas canceláveis alteradas propagam token; 0 `unsafe` em domínio/aplicação; hot paths alterados sem regressão do budget de alocação

## Referências

- `.references/topicos/01-csharp-runtime-e-biblioteca-padrao.md`
- Microsoft Learn e especificação C# catalogadas em `.references/fontes/dotnet-oficial.md`
