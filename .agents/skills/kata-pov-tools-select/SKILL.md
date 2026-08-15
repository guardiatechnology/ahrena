---
name: kata-pov-tools-select
description: "Selecionar Ferramentas de PoV. Engenharia — Agents (estágio pré-operacional): seleção do subconjunto mínimo de ferramentas Anthropic para alimentar o caso de uso primário"
---

# Kata: Selecionar Ferramentas de PoV

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Engenharia — Agents (estágio pré-operacional): seleção do subconjunto mínimo de ferramentas Anthropic para alimentar o caso de uso primário

## Workflow

```
Progresso:
- [ ] 1. Ler pov.md e listar capacidades requeridas
- [ ] 2. Mapear capacidades → tools Anthropic nativos
- [ ] 3. Recusar tooling fora do escopo
- [ ] 4. Documentar parâmetros mínimos e exemplos
- [ ] 5. Persistir tools.md
```

### Passo 1: Ler pov.md e listar capacidades requeridas

1. Lê `docs/{context}/agents-pov/{agent}/pov.md`.
2. Para cada capacidade implícita no caso de uso primário, lista a operação concreta (ex.: "buscar lançamentos do ERP" → leitura de arquivo CSV; "validar reconciliação" → execução de script Python).

### Passo 2: Mapear capacidades → tools Anthropic nativos

Catálogo permitido em PoV:

| Tool Anthropic | Quando usar |
|---|---|
| `web_search` | Quando o PoV precisa de informação pública (regulamentação, FX, taxas) |
| `str_replace_editor` / file write | Quando precisa ler/editar arquivos do projeto |
| `code execution` (sandbox Anthropic) | Quando precisa rodar Python para validar regra de negócio |
| `bash` (sandbox) | Quando precisa orquestrar comandos shell idempotentes |

Para cada item da lista do Passo 1, aponta exatamente 1 tool do catálogo. Se nenhum cobre, **reescopa o caso de uso** (volta ao `kata-pov-scope-define`) — não tente custom.

### Passo 3: Recusar tooling fora do escopo

Vetado em PoV:

- MCP servers custom (MCP servers oficiais listados em `.ahrena/.directives::mcp.servers` são OK — não exige ser autoria Anthropic, desde que estejam declarados e respeitem `lex-mcp` Rule 5 sobre ordem de preferência de transports)
- Bibliotecas de ML treinadas (transformers, scikit-learn) — fica para `warrior-apollo-agents` (plan-013) quando Mêtis projetar produção
- Integração com API externa **paga** sem sandbox público
- Cache persistente entre sessões — Diretriz 02 em PoV é apenas curto-prazo

Se o caso de uso primário **exige** algo da lista vetada, isso é sinal forte de que o PoV está prematuro: documenta o gap em `pov.md::Fora de escopo` e prossegue sem o tool.

### Passo 4: Documentar parâmetros mínimos e exemplos

Para cada tool selecionada, documenta:

- Operação (verbo + objeto)
- Parâmetros mínimos requeridos
- Exemplo de invocação real (não fictícia)
- Limite (ex.: "web_search ≤ 3 chamadas por turn")

### Passo 5: Persistir tools.md

Grava `docs/{context}/agents-pov/{agent}/tools.md` com seções: Capacidades requeridas, Mapping capacidade→tool, Tools selecionadas (uma seção por tool), Tools recusadas (com justificativa), Limites por turn.

### Validação Final

- [ ] Todas as capacidades do caso de uso primário têm tool mapeada
- [ ] Zero MCP custom
- [ ] Zero biblioteca ML
- [ ] Exemplos de invocação reais (não inventados)
- [ ] Limites por turn declarados

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| `tools.md` | Markdown | `docs/{context}/agents-pov/{agent}/tools.md` |

## Exemplo de Execução

### Input (pov.md, extrato)

```
Caso de uso primário: sugerir pareamento extrato↔lançamento contábil por valor + data + descrição.
```

### Output (tools.md, extrato)

```markdown
## Capacidades requeridas

1. Ler extrato bancário (CSV/OFX) do projeto
2. Ler lançamentos contábeis (CSV exportado do ERP)
3. Executar lógica de comparação (similaridade de strings)

## Mapping capacidade → tool

| Capacidade | Tool Anthropic |
|---|---|
| Ler extrato + lançamentos | str_replace_editor (read) |
| Executar similaridade | code execution (Python sandbox) |

## Tools selecionadas

### str_replace_editor (read)

- Operação: leitura de arquivo
- Parâmetros mínimos: `command=view, path=<file>`
- Exemplo: leitura de `inputs/statement-2026-04.csv`
- Limite: ≤ 5 leituras por turn

### code execution (Python sandbox)

- Operação: rodar comparação de strings
- Parâmetros: `code=<python>`, com `rapidfuzz` permitido como dependência leve
- Exemplo: `compare("Pagamento aluguel", "ALUGUEL REF MAR/26") -> 0.82`
- Limite: ≤ 1 execução por turn (caro)

## Tools recusadas

- MCP custom para ERP: gap declarado em pov.md::Fora de escopo
- Modelo NER treinado: prematuro para PoV
```

## Restrições

- **Nunca** introduzir MCP custom em PoV. Se necessário, é sinal de que o caso de uso já passou do estágio pré-operacional.
- **Nunca** declarar tool sem exemplo real de invocação.
- **Nunca** mais de 3 tools por PoV. Mais que isso indica escopo amplo demais.

---

**Modelo:** Este Kata aplica a Diretriz 03 (`lex-agent-construction-directives`) no rigor pré-operacional. Tooling sofisticado fica para Mêtis (plan-032) quando agent for promovido.
