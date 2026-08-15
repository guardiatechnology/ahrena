# Cry: Trabalho .NET

> **Prefixo:** `cry-` | **Tipo:** Comando Recorrente | **Escopo:** Entrada única para implementação, review, refatoração e debug .NET

## Descrição

Invoca Apollo-.NET e `kata-dotnet-delivery` no modo solicitado, usando o contrato técnico real do repositório.

## Uso

```
/cry-dotnet <implement|review|refactor|debug> <objetivo> [evidência]
```

## Parâmetros

| Parâmetro | Obrigatório | Descrição |
|---|:---:|---|
| `modo` | Sim | Operação a executar |
| `objetivo` | Sim | Feature, diff, componente ou falha |
| `evidência` | Não | Issue, logs, stack trace, contrato ou restrições |

## O que o Comando Faz

1. Invoca `warrior-apollo-dotnet` com o contexto recebido.
2. O Warrior executa `kata-dotnet-delivery` no modo indicado.
3. Retorna mudança validada, findings priorizados ou diagnóstico com evidência.

## Prompt Template

```
Contexto:
- Modo: {{modo}}
- Objetivo: {{objetivo}}
- Evidência: {{evidência}}

Tarefa:
Assuma `warrior-apollo-dotnet` e execute `kata-dotnet-delivery`. Descubra o SDK/TFM e os comandos do repositório antes de agir. Aplique as Lexis .NET, `codex-dotnet-engineering`, `codex-code-design` e `codex-domain-driven-design` quando houver domínio.

Saída:
- Resultado principal
- Validações executadas e resultados
- Riscos residuais ou bloqueios
```

## Exemplo de Invocação

`/cry-dotnet implement "Adicionar autorização idempotente" "Contrato OAS em docs/cards/oas"`

## Diferença de Kata

| Aspecto | Cry | Kata |
|---|---|---|
| Papel | Entrada rápida | Procedimento completo e verificável |
| Inputs | Modo, objetivo, evidência | Descoberta, baseline, execução e validação |
| Lógica | Delega | Define os passos |

## Restrições

- O Cry não executa ferramenta diretamente; delega ao Kata via Warrior.
- Se o modo for inválido, solicitar correção antes de prosseguir.

## Referências

- `warrior-apollo-dotnet`
- `kata-dotnet-delivery`
