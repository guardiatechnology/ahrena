# Lexis: Código Intencional e Verificável

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebrável | **Escopo:** Código de aplicação, testes e automações mantidos no repositório

## Lei

> **Todo código versionado DEVE expressar comportamento ativo com nomes do domínio, sem código morto ou comentado, sem comentários que apenas repitam a implementação e dentro dos limites de complexidade configurados pelo projeto.**

## Regras Verificáveis

1. Comentários explicam decisão, restrição, risco ou comportamento não evidente; não narram a linha seguinte.
2. Código comentado, imports, parâmetros, variáveis e membros privados sem uso não podem ser versionados.
3. Nomes devem ser pesquisáveis e refletir a linguagem do bounded context; abreviações locais não documentadas são proibidas.
4. Limites de complexidade, tamanho de função, parâmetros e nesting devem estar declarados na configuração do analisador do projeto. Na ausência de configuração, o CI deve adotar o baseline oficial da stack e impedir regressão.
5. Um alerta de complexidade exige investigação e refatoração ou decisão registrada; não autoriza extração mecânica que reduza coesão.

<HARD-GATE>
Subject: alteração de código antes de commit ou entrega
Action: bloquear a entrega quando houver código comentado, símbolo morto, comentário que apenas repete o código ou regressão nos limites configurados de complexidade
Preconditions: analisadores da stack executados sobre os arquivos alterados; diff revisado quanto a nomes e comentários
Scope: código de aplicação, testes e scripts versionados
Counter-pretexts: prazo curto, código gerado manualmente, compatibilidade temporária, lint desabilitado localmente
Exceptions: nenhuma
</HARD-GATE>

## Exemplos

### Correto

```csharp
// O provedor pode confirmar depois do timeout; a chave preserva a deduplicação na reconciliação.
await gateway.AuthorizeAsync(request, idempotencyKey, cancellationToken);
```

### Incorreto

```csharp
// Autoriza o pagamento.
await gateway.AuthorizeAsync(request, key, CancellationToken.None);
// await legacyGateway.AuthorizeAsync(request);
```

## Validação Automatizada

- **Ferramenta:** analisadores nativos da stack (por exemplo, Roslyn/.NET analyzers, Ruff, ESLint), detector de código morto e `kata-quality-gate`
- **Momento:** pre-commit e CI de pull request
- **Métrica:** 0 código comentado ou morto; 0 regressões sobre os limites configurados; 0 comentários puramente narrativos no diff
