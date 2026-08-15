---
name: kata-adr-write
description: "Escrever Architecture Decision Record (ADR). Produção de um ADR individual no formato MADR simplificado em docs/adr/"
---

# Kata: Escrever Architecture Decision Record (ADR)

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Produção de um ADR individual no formato MADR simplificado em `docs/adr/`

## Workflow

```
Progresso:
- [ ] 1. Detectar próximo número sequencial
- [ ] 2. Gerar slug do título
- [ ] 3. Compor conteúdo no formato MADR
- [ ] 4. Persistir em docs/adr/
- [ ] 5. Retornar referência ao invocador
```

### Passo 1: Detectar próximo número sequencial

1. Listar arquivos em `docs/adr/` com padrão `ADR-{n}-*.md`.
2. Extrair o maior `n` existente (ex.: `ADR-007-*.md` → `7`).
3. Próximo número = maior + 1 (ex.: `8`).
4. Se `docs/adr/` não existe, criar o diretório e iniciar em `1`.
5. Formatar com zero-padding de 3 dígitos (`ADR-001`, `ADR-023`, `ADR-125`).

### Passo 2: Gerar slug do título

1. Converter o título para lowercase.
2. Substituir espaços por hífens.
3. Remover caracteres não-alfanuméricos (exceto hífens).
4. Limitar a ~60 caracteres.

**Exemplo:** `"Use FastAPI routers for module separation"` → `use-fastapi-routers-for-module-separation`

**Nome do arquivo final:** `docs/adr/ADR-{n}-{slug}.md` (ex.: `docs/adr/ADR-008-use-fastapi-routers-for-module-separation.md`)

### Passo 3: Compor conteúdo no formato MADR

```markdown
# ADR-{n}: {Título}

- **Status:** {proposed | accepted | deprecated | superseded by ADR-XXX}
- **Date:** {YYYY-MM-DD}
- **Issue:** #{issue-number}  (omitir se não aplicável)

## Context

{problema ou força que motivou a decisão — 1-3 parágrafos}

## Decision

{a decisão tomada, em voz ativa — 1-2 parágrafos}

## Consequences

### Positive

- {benefício 1}
- {benefício 2}

### Negative

- {custo ou trade-off 1}
- {custo ou trade-off 2}

### Neutral

- {mudança que não é claramente benefício ou custo, mas relevante}

## Alternatives Considered

- **{Alternativa A}:** {descrição breve}. Rejeitada porque {justificativa}.
- **{Alternativa B}:** {descrição breve}. Rejeitada porque {justificativa}.
```

**Regras de conteúdo:**
- **Context** descreve o problema, não a solução. Deve ser compreensível por alguém lendo em 2 anos.
- **Decision** é declarativa e imperativa ("Adotamos X", "Usamos Y").
- **Consequences** inclui custos — um ADR sem Negative é suspeito.
- **Alternatives** precisa de pelo menos 1; "não fazer nada" é uma alternativa válida.
- Se a decisão está vinculada a uma issue, incluir `**Issue:** #{n}` com link clicável.

### Passo 4: Persistir em `docs/adr/`

1. Criar diretório `docs/adr/` se não existir.
2. Escrever o arquivo em `docs/adr/ADR-{n}-{slug}.md`.
3. Se o arquivo já existir (improvável, pois n é sequencial), parar e reportar erro.

### Passo 5: Retornar referência ao invocador

Retornar:
- Caminho relativo: `docs/adr/ADR-{n}-{slug}.md`
- Número: `ADR-{n}`
- Status: `proposed` (ou o status informado)

Esta referência é usada pelo `kata-architecture-brief` para incluir no documento de arquitetura e pelo `warrior-athena` para apresentar no Gate 1.

## Transições de Status

Após criado com status `proposed`, o ADR pode transitar para:

| Novo Status | Quando | Ação |
|---|---|---|
| `accepted` | Após aprovação humana no Gate 1 | Editar o ADR, alterar `Status:` |
| `deprecated` | Decisão deixou de ser relevante mas não foi substituída | Editar, alterar `Status:` e adicionar nota explicando |
| `superseded by ADR-XXX` | Substituído por outro ADR | Editar, alterar `Status:` e o novo ADR referencia este no `Context` |

**Importante:** ADRs são **append-only em espírito** — uma vez `accepted`, o conteúdo histórico é preservado. Mudanças são feitas criando um novo ADR que supersedes o anterior.

## Saídas

| Saída | Formato | Destino |
|-------|---------|---------|
| Arquivo ADR | Markdown MADR | `docs/adr/ADR-{n}-{slug}.md` |
| Referência ao invocador | Texto: caminho + número + status | Retorno |

## Restrições

- **Numeração sequencial inviolável:** nunca reusar números; gaps indicam ADRs removidos (o que não deve acontecer — ver "Importante" acima).
- **MADR simplificado:** seguir estritamente a estrutura acima; não adicionar seções opcionais sem justificativa.
- **Pelo menos 1 alternativa:** ADR sem alternativas é suspeito (significa que a decisão foi feita sem considerar opções).
- **Destino fixo:** `docs/adr/` conforme `lex-issue-driven` — nunca `.ahrena/` ou outro caminho.
- **Não editar ADRs `accepted` exceto para transição de status:** mudanças de decisão viram novo ADR (`superseded by`).
