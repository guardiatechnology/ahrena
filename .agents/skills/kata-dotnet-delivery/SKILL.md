---
name: kata-dotnet-delivery
description: "Entrega .NET. Implementar, revisar, refatorar ou diagnosticar aplicações .NET"
---

# Kata: Entrega .NET

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Implementar, revisar, refatorar ou diagnosticar aplicações .NET

## Workflow

```
Progresso:
- [ ] 1. Descobrir contrato do repositório
- [ ] 2. Delimitar domínio, risco e fronteiras
- [ ] 3. Construir baseline reproduzível
- [ ] 4. Projetar ou diagnosticar a menor mudança
- [ ] 5. Implementar ou registrar findings
- [ ] 6. Validar qualidade, integração e operação
- [ ] 7. Validação final
```

### Passo 1: Descobrir Contrato do Repositório

Ler instruções, `global.json`, solution/project files, propriedades centrais, pacotes, analyzers, CI e comandos locais. Confirmar SDK/TFM; não alterar versão por conveniência.

### Passo 2: Delimitar Domínio, Risco e Fronteiras

Identificar linguagem do domínio, invariantes, consumidores, contrato público, dados, concorrência, autorização e impacto operacional. Consultar `codex-domain-driven-design` quando houver decisão de domínio.

### Passo 3: Construir Baseline Reproduzível

Executar restore/build/test conforme o repo e reproduzir a falha no modo `debug`. Registrar failures preexistentes separadamente. Para refatoração, criar caracterização se faltar proteção.

### Passo 4: Projetar ou Diagnosticar a Menor Mudança

Consultar `codex-dotnet-engineering` e `codex-code-design`. Listar opções, trade-offs, `use_when`/`avoid_when` de patterns e modos de falha. Escolher a menor solução que preserve contratos.

### Passo 5: Implementar ou Registrar Findings

- `implement`: código + testes no nível do risco.
- `refactor`: passos reversíveis, sem mudança de comportamento escondida.
- `debug`: corrigir somente quando autorizado; caso contrário entregar causa e evidência.
- `review`: findings priorizados com arquivo/linha, impacto e correção verificável.

### Passo 6: Validar Qualidade, Integração e Operação

Executar format/analyzers, build e testes. Quando tocados, validar autorização negativa, SQL real, concorrência, migração, idempotência, timeout, telemetry, health, container e rollback. Para hot paths, comparar baseline de throughput, bytes/op, coleções Gen0/1/2 e memória retida; revisar ownership de buffers e disposables.

### Passo 7: Validação Final

- [ ] SDK/TFM e comandos reportados são os do repositório
- [ ] `lex-clean-code` e as três `lex-dotnet-*` passam
- [ ] Build e testes executados têm resultado explícito
- [ ] Contratos, schema e semântica de erro não mudaram silenciosamente
- [ ] Código permanece memory-safe; `unsafe`/interop está isolado e justificado
- [ ] Hot paths alterados respeitam o budget de alocação com evidência, sem pooling especulativo
- [ ] Overflow, estados inválidos e outcomes esperados têm representação e testes explícitos
- [ ] Riscos residuais, falhas preexistentes e validações não executadas estão declarados

## Outputs

| Modo | Output |
|---|---|
| implement/refactor | Código, testes e resumo de decisões |
| review | Findings priorizados ou declaração explícita de ausência |
| debug | Reprodução, causa raiz, evidência e correção se autorizada |

## Exemplo de Execução

### Input de Exemplo

`implement`: adicionar autorização idempotente de cartão em ASP.NET Core com PostgreSQL.

### Output de Exemplo

Endpoint validado, use case com invariante, constraint/idempotency store no provider real, cancellation propagado, teste de conflito e telemetria sem PAN.

## Restrições

- Não instalar/migrar SDK ou pacotes sem necessidade do projeto.
- Não substituir semântica relacional por EF Core InMemory.
- Não aplicar retry automático a efeito financeiro sem idempotência e reconciliação.
