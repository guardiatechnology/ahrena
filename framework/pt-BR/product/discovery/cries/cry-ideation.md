# Cry: Promover Insight Aprovado a Idea

> **Prefixo:** `cry-` | **Tipo:** Comando Recorrente | **Escopo:** Product Discovery — atalho para invocar `warrior-phanes` com um ou mais `insight_path` aprovados

## Descrição

Atalho que invoca `warrior-phanes` para promover insights aprovados a uma Idea sob `docs/discovery/{topic}/ideas/`. O Cry **não** invoca Lexis nem Codex diretamente — apenas aciona o Warrior, que internamente executa `kata-ideation-from-insight`, valida o HARD-GATE 1 da `lex-discovery-flow` e consulta `codex-discovery-artifacts`.

## Uso

```
/cry-ideation
```

## Parâmetros

| Parâmetro | Obrigatório | Descrição | Exemplo |
|-----------|:-----------:|-----------|---------|
| `insight_path` | Sim | Path canônico do insight a promover (string ou array quando múltiplos insights formam uma Idea única) | `docs/discovery/scheduled-payments-research/insights/001-...` |
| `additional_context` | Não | Contexto extra fornecido pelo humano (dados de telemetria, hipótese refinada, piloto disponível) que ajuda Phanes a montar `success_metric` ou `effort_estimate` | "Cliente piloto disponível: escritório Y" |

## O que o Comando Faz

1. Invoca `warrior-phanes` com os parâmetros fornecidos
2. Phanes lê `.ahrena/.directives` e internaliza `lex-discovery-flow` e `codex-discovery-artifacts`
3. Phanes valida o HARD-GATE 1 em **três momentos** (per `kata-ideation-from-insight`): preflight de input (a, d) antes de qualquer leitura, preflight de output (b, c) sobre a Idea sintetizada antes de gravar, e pós-escrita (e) com rollback transacional caso a atualização parcial dos insights falhe
4. Se preflight passar, Phanes executa `kata-ideation-from-insight`, gerando o arquivo da Idea com os 5 campos de conteúdo obrigatórios preenchidos
5. Phanes atualiza o(s) insight(s) de origem para `status: promoted` com `idea_ref` apontando para a Idea (rollback automático se falhar)
6. Phanes reporta a Idea criada e os insights promovidos, sinalizando lacunas que pedem validação adicional

## Prompt Template

```
Assuma o papel de warrior-phanes (Product Ideation).

Parâmetros recebidos:
- insight_path:
{{insight_path}}
- additional_context:
{{additional_context}}

Tarefa:
Execute kata-ideation-from-insight com os parâmetros acima.
Antes de qualquer escrita, leia .ahrena/.directives, lex-discovery-flow e codex-discovery-artifacts.
Valide o HARD-GATE 1 em três momentos, conforme o kata:
  - Preflight de input (a, d) antes de qualquer leitura
  - Preflight de output (b, c) sobre a Idea sintetizada, ANTES de gravar
  - Pós-escrita (e) com rollback transacional se a atualização parcial dos insights falhar
Se qualquer preflight falhar, interrompa e informe o humano qual ação destrava.
Se passar, gere a Idea em docs/discovery/{topic}/ideas/{NNN}-{slug}.md
com os 5 campos de conteúdo obrigatórios (problem, hypothesis, target_user, success_metric, effort_estimate)
e linked_insights[] referenciando os insights de origem.
Atualize o(s) insight(s) de origem para status: promoted + idea_ref + updated_at.
Não altere status de insight para approved (HARD-GATE 2; prerrogativa humana).

Formato de saída:
- Confirmação da Idea criada com path canônico
- Lista dos insights promovidos
- Resumo de cada um dos 5 campos de conteúdo obrigatórios
- Lacunas que pedem validação adicional antes do design cycle
```

## Exemplo de Invocação

**Input:**

```
/cry-ideation
insight_path: docs/discovery/scheduled-payments-research/insights/001-manual-reconciliation-bottleneck.md
additional_context: |
  Cliente piloto disponível: escritório Y com 80 contadores ativos
```

**Output esperado:**

```
warrior-phanes validou HARD-GATE 1 ✅ e executou kata-ideation-from-insight.

Idea criada: docs/discovery/scheduled-payments-research/ideas/001-auto-reconcile-erp-bank.md

Insights promovidos:
- scheduled-payments-research/insights/001-manual-reconciliation-bottleneck → status: promoted

Resumo da Idea:
- Problem: 4h/semana de conciliação manual, sem percepção de valor
- Hypothesis: sugestão automática com confiança ≥ 90% será aceita em ≥ 70% dos casos
- Target user: contador operacional em escritórios 50–500 clientes integrados ao ERP X
- Success metric: tempo de conciliação por mês por cliente — baseline 4h → meta 1.5h em 90 dias
- Effort estimate: M (2–4 sprints; depende de modelo de matching e webhooks ERP X)

Lacunas que pedem validação:
- Baseline 4h vem de 1 entrevista — recomendo confirmar com 3 entrevistas adicionais
- Webhooks do ERP X não foram validados com a documentação do produto

Idea pronta para consumo de warrior-prometheus.
```

**Cenário de falha:**

```
/cry-ideation
insight_path: docs/discovery/scheduled-payments-research/insights/005-payment-method-confusion.md
```

```
warrior-phanes interrompeu. HARD-GATE 1 falhou:
- (a) status: under_review ❌ (esperado: approved)

Para destravar:
1. Avalie o insight em PR review
2. Se aprovar, atualize status: approved no front-matter (decisão sua per HARD-GATE 2)
3. Reinvoque /cry-ideation com o mesmo insight_path
```

## Restrições

- Não cria Idea se o HARD-GATE 1 falhar — interrompe e informa o humano
- Não altera status de insight para `approved` — prerrogativa humana per HARD-GATE 2 da `lex-discovery-flow`
- Não modifica campos do insight de origem além de `status`, `idea_ref` e `updated_at`
- Não mistura `topics` distintos em uma única Idea
- Saída sempre no idioma definido em `language.default` do `.directives` (default: pt-BR)

## Diferença de Kata

| Aspecto | Cry | Kata |
|---------|-----|------|
| **Natureza** | Atalho de invocação de Phanes | Procedimento que Phanes executa |
| **Quem invoca** | Usuário humano | Warrior (Phanes) |
| **O que faz** | Aciona o warrior com parâmetros | Valida HARD-GATE 1 e promove insight a Idea |
| **Exemplo** | `/cry-ideation` | `kata-ideation-from-insight` |

## Referências

- `warrior-phanes` — agente invocado por este Cry
- `kata-ideation-from-insight` — procedimento executado internamente
- `lex-discovery-flow` — lei aplicável (consultada pelo warrior, não pelo cry)
- `codex-discovery-artifacts` — schema de insights e Ideas (consultado pelo warrior)
- `cry-discovery` — Cry complementar (produção de insights upstream)
