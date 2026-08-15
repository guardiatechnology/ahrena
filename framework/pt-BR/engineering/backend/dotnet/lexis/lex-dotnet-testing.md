# Lexis: Testes de Mudança .NET

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebrável | **Escopo:** Mudanças funcionais e correções em projetos .NET

## Propósito

Garantir que comportamento alterado seja protegido no nível capaz de detectar seu risco real, inclusive semântica relacional e contratos de fronteira.

## Lei

> **Toda mudança de comportamento .NET DEVE incluir teste determinístico que falhe sem a mudança e use infraestrutura real quando o risco depender da semântica do provedor.**

## Abrangência

- **Aplica-se a:** features, correções, migrações, contratos e refatorações com comportamento novo
- **Agentes vinculados:** Apollo-.NET e qualquer agente que produza código .NET
- **Exceções:** Nenhuma. Lexis não admitem exceções.

## Regras Verificáveis

1. Regra de domínio usa teste unitário; boundary HTTP/evento usa teste de contrato ou integração; persistência relacional usa o provider real em container ou ambiente isolado.
2. EF Core InMemory não valida tradução SQL, constraints, transações ou concorrência do banco relacional.
3. Testes não dependem de relógio, aleatoriedade, rede ou ordem global sem controle explícito.
4. Mocks representam fronteiras controladas; não reproduzem internamente EF Core, ASP.NET Core ou o provider externo.
5. Flaky test é defeito: deve ser corrigido, isolado com owner e prazo, ou bloquear a entrega.

## Consequências de Violação

1. **Bloqueio:** mudança funcional sem proteção não passa pelo quality gate.
2. **Diagnóstico:** indicar risco sem cobertura ou double inadequado.
3. **Remediação:** adicionar teste no nível correto e evidência de falha antes da correção quando reproduzível.

## Exemplos

### Correto

```csharp
[Fact]
public async Task Rejects_second_authorization_with_same_idempotency_key() { /* real database */ }
```

### Incorreto

```csharp
[Fact]
public void Always_passes() => Assert.True(true);
```

## Validação Automatizada

- **Ferramenta:** `dotnet test`, test runner escolhido, Coverlet quando configurado e Testcontainers para semântica externa
- **Momento:** CI do pull request
- **Métrica:** 0 mudança funcional sem teste; 0 teste flaky tolerado silenciosamente; 0 uso de EF InMemory para afirmar comportamento relacional

## Referências

- `lex-test-pyramid`, `lex-test-isolation`, `codex-test-strategy`
- `.references/topicos/05-testes-e-qualidade.md`
