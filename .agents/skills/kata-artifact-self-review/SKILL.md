---
name: kata-artifact-self-review
description: "Auto-revisão de Artefato. Auto-revisão pré-humana de qualquer artefato produzido por agente — Lexis, Codex, Kata, Warrior, Cry, PRD, Capability Spec, ADR, release plan, PLR, wireframes"
---

# Kata: Auto-revisão de Artefato

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Auto-revisão pré-humana de qualquer artefato produzido por agente — Lexis, Codex, Kata, Warrior, Cry, PRD, Capability Spec, ADR, release plan, PLR, wireframes

## Workflow

```
Progresso:
- [ ] 1. Scan de placeholders
- [ ] 2. Scan de contradições internas
- [ ] 3. Scan de ambiguidades quantificáveis
- [ ] 4. Scan de scope drift
- [ ] 5. Scan de seções vazias e estrutura incompleta
- [ ] 6. Scan de tom e vocabulário
- [ ] 7. Verificação de equivalência multilíngue (quando aplicável)
- [ ] 8. Relatório consolidado
```

### Passo 1: Scan de placeholders

Procure por marcadores não preenchidos: `TBD`, `TODO`, `FIXME`, `XXX`, texto entre colchetes do template (`[Nome da Lei]`, `[descrição]`), reticências em conteúdo declarativo, strings genéricas (`Lorem ipsum`, `placeholder`, `inserir aqui`), headings vazios.

Para cada achado: localização (linha), conteúdo problemático, ação (preencher / remover / converter em open question).

### Passo 2: Scan de contradições internas

Verifique consistência entre seções:
- Lei/Objetivo na abertura vs. Regras/Workflow nas seções seguintes
- Exemplos "Correto" e "Incorreto" alinhados com as regras
- Inputs/outputs vs. Workflow — cada input declarado é consumido? cada output é produzido?
- Critérios numerados — N na Lei batem com N em Validação Automatizada?

### Passo 3: Scan de ambiguidades quantificáveis

Identifique declarações vagas: "muitos", "vários", "rápido", "simples", "complexo", "razoável", "alta latência", "baixo custo".

Para cada: alternativa quantificável (ex.: "muitos casos" → "≥80% dos casos observados"; "rápido" → "p99 ≤ 300ms"). Exceção: ambiguidade aceitável quando o número virá em fase posterior — documentar a postergação.

### Passo 4: Scan de scope drift

Verifique que o artefato não excedeu seu escopo:
- Lexis: trata de uma única lei? não embute kata ou codex?
- Capability Spec: segue as 8 seções rígidas? não invade design técnico?
- Kata: descreve UM procedimento?
- Warrior: orquestra mas não executa?
- PRD: foca em WHAT/WHY?

### Passo 5: Scan de seções vazias e estrutura incompleta

Verifique conformidade com template canônico (quando existir):
- Todas as seções obrigatórias presentes?
- Cada seção tem conteúdo substantivo?
- Hierarquia de headings correta?
- Frontmatter completo (quando aplicável a `.cursor/` ou `.claude/`)?
- Links internos resolvem (não 404)?

### Passo 6: Scan de tom e vocabulário

Verifique conformidade com [lex-tone](framework/pt-BR/_foundation/quality/lexis/lex-tone.md) e — quando público — [lex-brand-voice](framework/pt-BR/design/brand/lexis/lex-brand-voice.md):
- Buzzwords proibidas: "inovador", "disruptivo", "transformador", "revolucionário", "fintech" (para Guardia)
- Verbos modais RFC 2119 corretos: MUST/MUST NOT/SHOULD/MAY (en) ou DEVE/NÃO DEVE/DEVERIA/PODE (pt-BR), DEBE/NO DEBE/DEBERÍA/PUEDE (es)
- Termos canônicos preservados: Lexis, Codex, Katas, Warriors, Cries, Ahrena

### Passo 7: Verificação de equivalência multilíngue

Quando o artefato existir em múltiplos idiomas (per [lex-framework-language](framework/pt-BR/_foundation/i18n/lexis/lex-framework-language.md)):
- Mesma estrutura e ordem de seções
- Mesmo número de regras numeradas
- Tabelas com mesmo número de linhas
- Blocos de código (HARD-GATE, exemplos) preservados sem tradução incorreta de tag/sintaxe
- Termos canônicos preservados

### Passo 8: Relatório consolidado

```markdown
# Self-Review Report — {nome do artefato}

> **Reviewer:** kata-artifact-self-review · **Date:** YYYY-MM-DD · **Type:** {tipo}
> **Resultado:** APROVADO | DEVOLVIDO PARA CORREÇÃO

## Achados por categoria

### 1. Placeholders
- (vazio quando 0 achados)
- {linha N}: {descrição} → ação: {recomendação}

### 2. Contradições internas
### 3. Ambiguidades quantificáveis
### 4. Scope drift
### 5. Seções vazias / estrutura
### 6. Tom e vocabulário
### 7. Equivalência multilíngue

## Decisão

- [ ] APROVADO — pode submeter para revisão humana
- [ ] DEVOLVIDO — corrigir achados acima e re-rodar este Kata
```

Submeta artefato a humano APENAS quando relatório indicar APROVADO.

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Self-Review Report | Markdown estruturado | inline (chat) ou `docs/.review/{artefato}-{date}.md` |
| Decisão APROVADO / DEVOLVIDO | Boolean explícito | parte do relatório |

## Exemplo de Execução

### Input

```
Artefato: framework/pt-BR/_foundation/quality/lexis/lex-hard-gate-pattern.md
Tipo: lexis
Template: framework/templates/lex-sample.md
```

### Output

```markdown
# Self-Review Report — lex-hard-gate-pattern.md

> **Reviewer:** kata-artifact-self-review · **Date:** 2026-04-30 · **Type:** lexis
> **Resultado:** APROVADO

## Achados por categoria

### 1. Placeholders
- (zero achados)

### 2. Contradições internas
- (zero achados)

### 3. Ambiguidades quantificáveis
- (zero achados — métricas declaradas têm critério verificável)

### 4. Scope drift
- (zero achados)

### 5. Seções vazias / estrutura
- (zero achados — segue lex-sample.md)

### 6. Tom e vocabulário
- (zero achados — RFC 2119 corretos; sem buzzwords)

### 7. Equivalência multilíngue
- (zero achados — pt-BR, en, es estruturalmente equivalentes)

## Decisão

- [x] APROVADO — pode submeter para revisão humana
```

## Restrições

- Este Kata **detecta**, não **corrige** — correção é responsabilidade do agente que produziu o artefato.
- Self-review **não substitui** revisão humana — é fase pré-humana, complementar.
- Se o artefato falha em equivalência multilíngue, agente DEVE alinhar todos os idiomas antes de submeter — não submeter parcialmente.
- Sempre que retornar DEVOLVIDO, o relatório DEVE ser preservado em `docs/.review/` para auditoria.
