# Kata: Implementar Skill

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Orquestração da fase de autoria de um projeto de skill em `{paths.skills_root}/{slug}/`, delegando widgets a `warrior-hephaestus` e tools/scripts Python a `warrior-apollo`, e redigindo `SKILL.md` + `references/` diretamente

## Objetivo

Conduzir a fase `implement` do ciclo de skill: dado um projeto já scaffolded por `kata-init-skill`, identificar os gaps (widgets sem implementação, tools sem handler, scripts sem entry, `SKILL.md` ainda com placeholders) e delegar cada gap ao especialista certo, com `warrior-claudionor` consolidando o resultado. Este kata **não** implementa código próprio fora de `SKILL.md` e `references/` — sua disciplina é orquestrar.

## Quando Usar

- Logo após `cry-new-skill` quando o scaffold ainda tem placeholders e diretórios vazios
- Quando o usuário pede para "implementar" uma skill existente que tem widgets/tools/scripts incompletos
- Como passo 2 do fluxo `cry-skill --mode all` (entre validate inicial e package final)

## Inputs

| Input | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| `slug` | Sim | Nome do projeto (idêntico ao nome do diretório em `{paths.skills_root}/`) |
| `gaps` | Não | Lista de gaps já identificados; se ausente, o kata faz a varredura |

## Workflow

```
Progresso:
- [ ] 1. Carregar contexto do projeto (SKILL.md, skill.config.json)
- [ ] 2. Varredura de gaps (widgets, tools, scripts, SKILL.md, references)
- [ ] 3. Plano de delegação (quem faz o quê)
- [ ] 4. Delegar widgets → warrior-hephaestus
- [ ] 5. Delegar tools + scripts Python → warrior-apollo
- [ ] 6. Redigir/atualizar SKILL.md (corpo) e references/ in-house
- [ ] 7. Reconciliação (validar consistência entre SKILL.md e arquivos reais)
- [ ] 8. Reportar progresso ao chamador
```

### Passo 1: Carregar contexto

1. Ler `{skills_root}/{slug}/SKILL.md` e `{skills_root}/{slug}/skill.config.json`
2. Identificar o idioma declarado em `metadata.language` (usar para mensagens humanas; identificadores técnicos permanecem em inglês)
3. Identificar subdiretórios presentes (`widgets/`, `tools/`, `scripts/`, `references/`)

### Passo 2: Varredura de gaps

Considera-se gap, por convenção:

| Local | Sinal de gap |
|-------|--------------|
| `SKILL.md` | placeholders `__...__` remanescentes; corpo só com headings sem conteúdo; lista de tools/widgets fora de sincronia com filesystem |
| `widgets/` | `package.json` presente mas `src/` vazio ou sem `index.tsx`; nenhum teste; componentes sem props tipadas |
| `tools/` | diretório presente mas sem `mcp.config.json` ou sem handler para cada tool declarada |
| `scripts/` (Python) | sem `pyproject.toml`; nenhum módulo em `src/`; ausência de teste para função pública |
| `scripts/` (JS/TS) | mesmo critério traduzido para o stack JS |
| `references/` | listado em `SKILL.md` mas arquivo ausente, ou existe mas vazio |

O kata pode receber a lista via `gaps`; quando ausente, faz a varredura. Quando ambiguidade for irrecuperável, perguntar ao usuário antes de delegar.

### Passo 3: Plano de delegação

Compor explicitamente, para cada gap, o par (gap, agente responsável):

| Gap | Agente | Lexis relevantes |
|-----|--------|------------------|
| Widget React/TS | `warrior-hephaestus` | `lex-frontend-typing`, `lex-frontend-accessibility`, `lex-frontend-security`, `lex-frontend-testing` |
| Tool MCP (handler em Python) | `warrior-apollo` | `lex-mcp`, `lex-python-typing`, `lex-python-testing`, `lex-python-error-handling`, `lex-python-result-type`, `lex-python-error-object` |
| Tool MCP (handler em JS/TS) | `warrior-hephaestus` (frontend lead detém TS) | `lex-frontend-typing`, `lex-mcp` |
| Script Python | `warrior-apollo` | `lex-python-typing`, `lex-python-testing`, `lex-python-security`, `lex-python-immutability` |
| Script JS/TS | `warrior-hephaestus` | `lex-frontend-typing` |
| `SKILL.md` corpo + `references/` | **este kata** (claudionor escreve) | `lex-tone`, `codex-skill-anthropic-agent-skills` |

Apresentar o plano ao usuário em formato compacto e aguardar confirmação quando o escopo for substantivo (≥3 delegações). Para gaps triviais (um único widget), prosseguir sem gate.

### Passo 4: Delegar widgets

Invocar `warrior-hephaestus` via o subsystem de agentes com prompt mínimo contendo:

1. `skills_root/{slug}/widgets/` é o diretório-alvo (não tocar fora dele)
2. Lista de componentes a criar/completar (de `Passo 2`)
3. Lexis aplicáveis explícitas
4. Pedido de retorno: lista de arquivos produzidos + status (criados, modificados, ainda pendentes)
5. Restrição: usar `@guardia/design-system` quando a skill renderizar em superfície Guardia (`lex-design-system-library`)

Recolher o retorno; **não inferir** sucesso — somente o retorno explícito do agente conta.

### Passo 5: Delegar tools/scripts Python

Invocar `warrior-apollo` análogo, com:

1. `skills_root/{slug}/tools/` e/ou `skills_root/{slug}/scripts/` como diretórios-alvo
2. Lista de handlers/scripts a criar
3. Lexis Python aplicáveis (`lex-python-*`, `lex-mcp`)
4. Pedido de retorno idêntico ao Passo 4

### Passo 6: Redigir SKILL.md e references in-house

Este kata escreve diretamente:

1. **`SKILL.md` corpo:**
   - Resolver placeholders `__...__` remanescentes
   - Sincronizar a seção "Tools, scripts, and widgets" com o filesystem real após os Passos 4-5
   - Garantir que descrições de uso são concretas (intent + keywords) per `codex-skill-anthropic-agent-skills`
   - Aplicar `lex-tone` (direto, estratégico, sem buzzwords)
2. **`references/`:**
   - Para cada referência citada no `SKILL.md`, garantir existência e conteúdo coerente
   - Snapshots de Lexis/Codex referenciados podem ser puxados da árvore `framework/` quando aplicável; documentar `source_commit` para uso futuro pelo `kata-skill-package`

### Passo 7: Reconciliação

1. Re-ler `SKILL.md` e comparar com o filesystem:
   - Todo widget declarado tem arquivo correspondente em `widgets/src/`
   - Toda tool declarada tem handler em `tools/handlers/` (ou equivalente declarado em `mcp.config.json`)
   - Toda referência tem arquivo em `references/`
2. Invocar `kata-skill-validate` como verificação de fechamento
3. Se a validação ainda falhar, gerar um sub-plano (gaps remanescentes) e voltar ao Passo 3 — máximo 3 iterações antes de escalar para humano

### Passo 8: Reportar

1. Lista de gaps endereçados nesta execução
2. Lista de arquivos produzidos por cada delegação
3. Estado final do `kata-skill-validate`
4. Próximo passo sugerido (`cry-skill --mode package` quando pronto, ou nova rodada de `--mode implement` se houver gap residual)

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Implementação de widgets | arquivos em `widgets/` | filesystem (produzidos pelo Hephaestus) |
| Implementação de tools/scripts | arquivos em `tools/` e `scripts/` | filesystem (produzidos pelo Apollo) |
| `SKILL.md` consolidado + `references/` | Markdown | filesystem (produzido por este kata) |
| Relatório de progresso | texto humano | `stdout` |

## Exemplo de Execução

### Input

```
kata-skill-implement slug=scheduled-payments-skill
```

### Output esperado (resumo)

```
Gaps identificados (5):
  - SKILL.md: 3 placeholders __...__ remanescentes
  - widgets/: TransferForm sem implementação
  - widgets/: ApprovalReview sem implementação
  - tools/: handler validate_amount sem código
  - scripts/: validate_amount.py sem testes

Plano:
  - Hephaestus → widgets/TransferForm, widgets/ApprovalReview
  - Apollo → tools/handlers/validate_amount.py, scripts/tests/test_validate_amount.py
  - Claudionor (este kata) → resolver placeholders + sincronizar SKILL.md

Resultado:
  - 4 arquivos criados por Hephaestus
  - 2 arquivos criados por Apollo
  - SKILL.md consolidado, placeholders resolvidos
  - kata-skill-validate: ✅ no violations

Próximo passo sugerido: cry-skill --mode package --slug scheduled-payments-skill
```

## Restrições

- O kata **não** implementa widgets, tools ou scripts próprios — delega; violar essa fronteira é violar a divisão de responsabilidades entre `warrior-claudionor`, `warrior-hephaestus`, `warrior-apollo`
- O kata **escreve diretamente** apenas `SKILL.md` e `references/`; mais nada
- O kata **não** modifica `.directives`, `.gitignore`, `framework/`, ou qualquer arquivo fora de `{skills_root}/{slug}/`
- Cada delegação retorna explicitamente a lista de arquivos produzidos; o kata **não infere** conclusão de delegação sem retorno explícito
- Após 3 iterações sem fechar todos os gaps, o kata escala para humano em vez de loop infinito

## Referências

- `kata-skill-validate` — verificação de fechamento ao final
- `kata-skill-package` — sucessor invocado quando a implementação está pronta
- `warrior-claudionor` — orquestrador que invoca este kata
- `warrior-hephaestus` — delegação de widgets
- `warrior-apollo` — delegação de tools/scripts Python
- `codex-skill-anthropic-agent-skills` — frontmatter e disclosure
- `codex-skill-project-architecture` — layout do projeto
- `codex-skill-tools-and-widgets` — convenção `tools/` + `widgets/`
- `lex-skill-project-structure` — lei do layout
- `lex-tone` — tom aplicado ao `SKILL.md` e `references/`
