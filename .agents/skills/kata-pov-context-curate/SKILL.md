---
name: kata-pov-context-curate
description: "Curar Context Pack de PoV. Engenharia — Agents (estágio pré-operacional): curadoria de few-shot + exemplos negativos do domínio para alimentar o contexto do PoV"
---

# Kata: Curar Context Pack de PoV

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Engenharia — Agents (estágio pré-operacional): curadoria de few-shot + exemplos negativos do domínio para alimentar o contexto do PoV

## Workflow

```
Progresso:
- [ ] 1. Ler overview + system-prompt
- [ ] 2. Coletar 3-5 inputs reais representativos
- [ ] 3. Escrever few-shot positivos (input → resposta ideal)
- [ ] 4. Identificar 2-3 anti-padrões e escrever exemplos negativos
- [ ] 5. Anonimizar PII (lex-data-retention)
- [ ] 6. Persistir context-pack.md
```

### Passo 1: Ler overview + system-prompt

1. Lê os dois arquivos.
2. Anota: caso de uso primário, formato esperado de saída, restrições do prompt.

### Passo 2: Coletar 3-5 inputs reais representativos

1. Cobre o **espaço do caso de uso**: caso fácil, caso médio, caso ambíguo. Não 5 versões do mesmo cenário.
2. Se `--inputs-dir` foi passado, lista e seleciona; se não, pede ao usuário 3-5 inputs reais. **Sem inputs reais, kata aborta** — context-pack inventado é violação direta de Diretriz 06.

### Passo 3: Escrever few-shot positivos

Para cada input selecionado:

- **Input bloco:** dados literais (anonimizados)
- **Resposta ideal:** o que o agent **deveria** produzir, no formato declarado em `system-prompt.md`

Os exemplos seguem o template `<input> → <output>` consistente com o estilo de saída do prompt. Evite over-engineering: resposta ideal é o que o cliente aceitaria, não um ideal perfeccionista.

### Passo 4: Identificar 2-3 anti-padrões e escrever exemplos negativos

Anti-padrões típicos em LLM básico para o domínio:

- **Alucinação:** inventa ID/valor ausente do input
- **Over-confidence:** diz "alta confiança" quando dados são insuficientes
- **Out-of-scope drift:** responde sobre caso de uso secundário não declarado
- **Format breakage:** quebra o formato declarado no prompt

Para cada anti-padrão, escreve:

- **Input bloco:** o caso que disparou o erro
- **❌ Resposta indesejada:** o que LLM básico produziu
- **✅ Resposta correta:** o que deveria ter produzido (a mesma estrutura dos few-shot positivos)

### Passo 5: Anonimizar PII

Aplica `lex-data-retention`:

- Remove ou mascara: CPF/CNPJ, e-mail, telefone, nome completo, endereço
- Mantém: estrutura do input (campos, padrões), valores quantitativos (com ofuscação leve se sensíveis)
- Marca cada exemplo com `# Origem: anonimizado de dados do cliente em <data>` para rastreabilidade

### Passo 6: Persistir context-pack.md

Grava `docs/{context}/agents-pov/{agent}/context-pack.md` com seções: Few-shot positivos (3-5), Anti-padrões (2-3), Notas de anonimização, Critérios de qualidade aplicados.

### Validação Final

- [ ] 3 a 5 few-shot positivos cobrindo casos representativos
- [ ] 2 a 3 anti-padrões com `❌` e `✅`
- [ ] Zero PII (CPF, CNPJ, nome completo, e-mail)
- [ ] Exemplos derivados de inputs reais (não fictícios)
- [ ] Formato de saída dos few-shot é consistente com `system-prompt.md`

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| `context-pack.md` | Markdown | `docs/{context}/agents-pov/{agent}/context-pack.md` |

## Exemplo de Execução

### Output (context-pack.md, extrato)

```markdown
## Few-shot positivos

### Exemplo 1 (caso fácil)

**Input:**
- Extrato: TX-001 | 2026-04-01 | R$ 1.200,00 | "Aluguel ref 04/26"
- Lançamentos:
  - L-100 | 2026-04-01 | R$ 1.200,00 | "PAG ALUGUEL ABR/26"
  - L-101 | 2026-04-02 | R$ 350,00 | "INTERNET"

**Resposta ideal:**
TX-001 ↔ L-100 | confiança: alta | base: valor + data + descrição similar

### Exemplo 2 (caso médio — descrição divergente)
...

## Anti-padrões

### Anti-padrão A: Alucinação de ID

**Input:**
- Extrato: TX-007 | 2026-04-15 | R$ 500,00 | "PIX 12345"
- Lançamentos: (vazio para essa janela)

**❌ Resposta indesejada:**
TX-007 ↔ L-999 | confiança: alta
(L-999 não existe nos lançamentos — alucinação.)

**✅ Resposta correta:**
TX-007 ↔ nenhum candidato | confiança: n/a | observação: revisão manual necessária.
```

## Restrições

- **Nunca** context-pack com exemplos inventados — Diretriz 06 exige dados reais.
- **Nunca** PII no arquivo final — `lex-data-retention` aplica.
- **Nunca** menos de 3 ou mais de 5 few-shot positivos. Faixa codifica trade-off entre cobertura e ruído.
- **Sempre** marca origem do exemplo (anonimização date stamp) para rastrear retrofit.

---

**Modelo:** Este Kata aplica a Diretriz 06 (`lex-agent-construction-directives`). O context-pack é o ativo mais transferível para Mêtis via `--from-pov`.
