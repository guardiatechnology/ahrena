# Lexis: Fronteiras Seguras em .NET

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebrável | **Escopo:** Entradas, autorização, segredos e integrações de aplicações .NET

## Propósito

Impedir que confiança do cliente, dados sensíveis ou valores externos atravessem fronteiras sem validação e política explícitas.

## Lei

> **Toda fronteira .NET DEVE validar entrada e autorização no servidor, obter segredos de provedores seguros, parametrizar acesso a dados e impedir que logs, erros ou telemetria exponham informação sensível.**

## Abrangência

- **Aplica-se a:** endpoints, consumers, jobs, persistence, HTTP clients e configuração
- **Agentes vinculados:** Apollo-.NET e revisores de backend
- **Exceções:** Nenhuma. Lexis não admitem exceções.

## Regras Verificáveis

1. Authentication prova identidade; authorization valida a ação e o recurso em cada operação protegida.
2. Dados do cliente, claims e headers não substituem consulta ou política server-side de ownership.
3. SQL usa parâmetros ou LINQ traduzível; concatenação de entrada em comando é proibida.
4. URLs externas controláveis por usuário exigem allowlist e mitigação de SSRF.
5. Segredos não ficam em código, `appsettings*.json` versionado, mensagens de erro, snapshots ou logs.
6. Logs usam campos estruturados e mascaramento; tokens, PAN, CVV, senha e PII desnecessária não são emitidos.

## Consequências de Violação

1. **Bloqueio:** alteração não pode ser entregue.
2. **Resposta:** se houve exposição, interromper propagação, rotacionar o segredo quando aplicável e acionar o fluxo de incidente.
3. **Remediação:** validar no boundary, mover segredo ao provider, parametrizar consulta e adicionar teste negativo.

## Exemplos

### Correto

```csharp
var card = await db.Cards.SingleOrDefaultAsync(
    item => item.Id == cardId && item.AccountId == subject.AccountId,
    cancellationToken);
```

### Incorreto

```csharp
logger.LogInformation("Authorization {Token} for card {Pan}", token, pan);
```

## Validação Automatizada

- **Ferramenta:** secret scanning, SAST, NuGet vulnerability audit, analyzers e testes de autorização
- **Momento:** pre-commit, CI e revisão de dependências
- **Métrica:** 0 segredo ou dado sensível; 0 SQL concatenado; toda operação protegida alterada tem teste de negação

## Referências

- `lex-auth`, `lex-error-handling`
- `.references/topicos/09-seguranca-privacidade-e-supply-chain.md`
