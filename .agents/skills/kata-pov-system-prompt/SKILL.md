---
name: kata-pov-system-prompt
description: "Redigir System Prompt de PoV. Engenharia — Agents (estágio pré-operacional): redação do system prompt mínimo viável de um PoV, com declaração explícita de stage: pre-operational"
---

# Kata: Redigir System Prompt de PoV

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Engenharia — Agents (estágio pré-operacional): redação do system prompt mínimo viável de um PoV, com declaração explícita de `stage: pre-operational`

## Workflow

```
Progresso:
- [ ] 1. Ler pov.md e extrair persona/escopo
- [ ] 2. Escrever bloco Identidade (com stage: pre-operational)
- [ ] 3. Escrever bloco Capacidades (mínimo viável)
- [ ] 4. Escrever bloco Restrições (mínimo viável)
- [ ] 5. Escrever bloco Estilo de saída (1-2 linhas)
- [ ] 6. Validar adversarial mínimo via kata-system-prompt-adversarial-validate
- [ ] 7. Persistir system-prompt.md
```

### Passo 1: Ler pov.md e extrair persona/escopo

1. Lê `docs/{context}/agents-pov/{agent}/pov.md`.
2. Extrai: persona (1 frase), caso de uso primário, value metric, critério de descontinuação.
3. Confirma que `pov.md` contém `stage: pre-operational`. Se ausente, retorna ao `kata-pov-scope-define` (não tenta corrigir aqui).

### Passo 2: Escrever bloco Identidade

Bloco mínimo viável dos 4 obrigatórios de `lex-system-prompt`:

```
# Identidade

Você é {nome do PoV}, um assistente em estágio **pre-operational** focado em
{caso de uso primário extraído de pov.md}.

stage: pre-operational
```

A linha `stage: pre-operational` é **literal** e obrigatória — é o gancho que `kata-dooc-validate` (plan-032) inspecionará no item 9.

### Passo 3: Escrever bloco Capacidades

```
# Capacidades

Você pode:
- {capacidade 1, alinhada ao caso de uso primário}
- {capacidade 2, opcional, ainda dentro do escopo}
```

Máximo 3 capacidades. Mais que isso quebra Diretriz 05 (Escopo Restrito).

### Passo 4: Escrever bloco Restrições

```
# Restrições

Você não pode:
- Executar ações fora do caso de uso primário declarado em pov.md
- Persistir dados além da janela de contexto atual (sem memória persistente)
- Substituir o critério de descontinuação ou alterar a value metric
```

Restrições adicionais surgem da `pov.md::Fora de escopo` (cópia literal).

### Passo 5: Escrever bloco Estilo de saída

```
# Estilo

Respostas curtas, diretas, em {idioma de `language.default`}. Cita evidências
do contexto quando aplicável. Nunca inventa dados não recebidos.
```

### Passo 6: Validar adversarial mínimo

Invoca `kata-system-prompt-adversarial-validate` em modo `--minimum-viable`:

- Suite reduzida: prompt injection trivial, exfiltração de instrução, jailbreak básico
- Suite completa (5 controles OWASP) fica para quando agent for promovido a `operational-concrete`
- Se passa → seguir; se falha → endurece restrição correspondente e re-roda

### Passo 7: Persistir system-prompt.md

1. Grava `docs/{context}/agents-pov/{agent}/system-prompt.md` com os 4 blocos.
2. No rodapé do arquivo, anota: `# Notas`, `kata-pov-system-prompt`, data, hash do `pov.md` consumido (para rastreabilidade).

### Validação Final

- [ ] System prompt tem os 4 blocos (Identidade, Capacidades, Restrições, Estilo)
- [ ] Linha `stage: pre-operational` aparece literalmente no bloco Identidade
- [ ] Suite adversarial mínima passa
- [ ] Restrições copiam literalmente o `Fora de escopo` do overview
- [ ] Sem placeholders `{...}` remanescentes

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| `system-prompt.md` | Markdown (system prompt) | `docs/{context}/agents-pov/{agent}/system-prompt.md` |

## Exemplo de Execução

### Input (pov.md, extrato)

```
Persona: Assistente que sugere pareamentos extrato↔lançamento contábil.
stage: pre-operational
Value metric: % de reconciliação automática ≥ 60% em 4 semanas.
```

### Output (system-prompt.md, extrato)

```
# Identidade

Você é o Assistente de Reconciliação, em estágio pre-operational, focado em
sugerir pareamentos entre transações de extrato bancário e lançamentos contábeis
do ERP da mesma janela temporal.

stage: pre-operational

# Capacidades

Você pode:
- Sugerir o pareamento mais provável por valor + data + descrição similar
- Indicar nível de confiança (alto / médio / baixo) por sugestão

# Restrições

Você não pode:
- Criar lançamentos no ERP (apenas sugerir)
- Conciliar entre contas distintas
- Detectar fraude
- Persistir dados fora da janela de contexto atual

# Estilo

Respostas curtas, diretas, em português. Cita o ID da transação e do lançamento.
Nunca inventa dados não recebidos no contexto.
```

## Restrições

- **Nunca** omitir `stage: pre-operational` — bloqueia DoOC.
- **Nunca** templates de produção (controles OWASP completos, ferramentas complexas) — escopo é minimum viable.
- **Nunca** mais de 3 capacidades. Forçar redução é melhor que inflar.

---

**Modelo:** Este Kata aplica a Diretriz 01 (`lex-agent-construction-directives`) no rigor pré-operacional. Templates de produção pertencem a `kata-system-prompt-author` (Mêtis) — não a este kata.
