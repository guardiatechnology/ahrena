# Codex: Tratamento de Erros na Plataforma Guardia

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Plataforma Guardia — tratamento de erros

## Conteúdo

### Estrutura do payload de erro

Todos os erros DEVEM ser encapsulados no campo `errors`, que DEVE ser um array de objetos (mesmo com um único erro). Cada objeto DEVE conter:

| Propriedade | Tipo | Descrição |
|-------------|------|-----------|
| code | string | Código semântico em UPPER_SNAKE_CASE, único no domínio; prefixo ERR + código HTTP (ex.: ERR400_, ERR409_). |
| reason | string | Categoria semântica para tratamento programático; DEVE estar em Erros Conhecidos no Hub. |
| message | string | Descrição voltada ao desenvolvedor; NUNCA expor dados sensíveis ou stack trace. |

### Exemplo de payload

```json
{
  "errors": [
    {
      "code": "ERR402_INSUFFICIENT_FUNDS",
      "reason": "PAYMENT_IS_REQUIRED",
      "message": "Saldo insuficiente para a operação solicitada."
    }
  ]
}
```

### Regras gerais

- **code:** único, UPPER_SNAKE_CASE, coerente com o status HTTP.
- **reason:** indica causa específica; pode haver múltiplos reason para um mesmo code; NÃO conter dados sensíveis.
- **message:** informativa para o desenvolvedor; pode ser internacionalizável via Accept-Language; NUNCA expor informações internas sensíveis.
- **Documentação:** para cada operação, documentar os pares code/reason possíveis no contrato (OpenAPI) e no catálogo de Erros Conhecidos do projeto.

### Retentativa

- Condições para retry DEVEM ser documentadas em Erros Conhecidos.
- Quando aplicável, incluir header `Retry-After` com tempo recomendado.
- Clientes DEVEM aplicar backoff exponencial base 2 quando o tempo não for informado, até no máximo 4 tentativas.
- Após a 4ª tentativa, adotar padrão de circuit breaker; estado half-open pode ser testado a cada 60 segundos.
- Número de tentativas e intervalos configuráveis pelo cliente, respeitando limites da plataforma.

### Criação de novos erros

- DEVEM seguir a estrutura padronizada (code, reason, message).
- DEVEM ser registrados no catálogo de Erros Conhecidos do projeto.
- Novos grupos de reason DEVEM ser justificados por contextos de negócio inéditos.
- **Considerações de segurança:** evitar mensagens que permitam enumeração (ex.: usuário existe/não existe); não incluir dados internos ou stack trace.
- **Monitoramento:** garantir que novos erros sejam incluídos em métricas e alertas conforme a política da plataforma.

### Segurança

- Erros de autenticação NUNCA DEVEM indicar se um usuário existe.
- Nenhuma mensagem DEVE conter stack trace ou identificadores internos sensíveis.

### Monitoramento

- TODOS os erros DEVEM ser registrados para auditoria.
- Erros 4xx e 5xx DEVEM ser monitorados continuamente.
- Erros 5xx DEVEM acionar alertas.

### Quando usar

Esta especificação DEVE ser aplicada em: APIs REST públicas e internas; comunicação entre microsserviços; integrações com parceiros; UIs que consomem APIs da plataforma.
