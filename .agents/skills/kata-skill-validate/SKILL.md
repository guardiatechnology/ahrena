---
name: kata-skill-validate
description: "Validar Projeto de Skill. Validação determinística de um projeto de skill em {paths.skills_root}/{slug}/ contra lex-skill-project-structure e o frontmatter exigido por codex-skill-anthropic-agent-skills"
---

# Kata: Validar Projeto de Skill

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Validação determinística de um projeto de skill em `{paths.skills_root}/{slug}/` contra `lex-skill-project-structure` e o frontmatter exigido por `codex-skill-anthropic-agent-skills`

## Workflow

```
Progresso:
- [ ] 1. Resolver caminho e confirmar existência
- [ ] 2. Invocar scripts/skills/validate.py
- [ ] 3. Coletar violações (regra, severidade, arquivo, mensagem)
- [ ] 4. Classificar resultado (ok / com warnings / com erros)
- [ ] 5. Reportar ao chamador
```

### Passo 1: Resolver caminho e confirmar existência

1. Aceitar o caminho como argumento absoluto ou relativo à raiz do repositório
2. Verificar que `skill_path` existe e é diretório; caso contrário, reportar violação `lex-skill-project-structure#location` e encerrar

### Passo 2: Invocar `scripts/skills/validate.py`

1. Executar `python3 scripts/skills/validate.py <skill_path> --format json`
2. Capturar stdout e exit code
3. Não filtrar a saída — o validador é a fonte da verdade; o kata apenas orquestra

O validador cobre, em uma única passada:

| Regra | Severidade | O que verifica |
|-------|:----------:|----------------|
| `lex-skill-project-structure#slug-regex` | erro | nome do diretório casa com regex Anthropic |
| `lex-skill-project-structure#slug-reserved` | erro | slug não contém `anthropic` ou `claude` |
| `lex-skill-project-structure#required-files` | erro | `SKILL.md` e `skill.config.json` presentes |
| `lex-skill-project-structure#frontmatter` | erro | `SKILL.md` tem bloco YAML `---` |
| `lex-skill-project-structure#frontmatter-name` | erro | frontmatter tem `name` não-vazio |
| `lex-skill-project-structure#name-matches-slug` | erro | `name` do frontmatter == nome do diretório |
| `codex-skill-anthropic-agent-skills#description` | erro | `description` presente |
| `codex-skill-anthropic-agent-skills#description-length` | erro | `description` em `[1, 1024]` chars |
| `lex-semantic-version` | erro | `metadata.version` é SemVer (quando declarado) |
| `lex-skill-project-structure#cross-references` | erro | links relativos no `SKILL.md` resolvem dentro do projeto |
| `lex-skill-project-structure#optional-subdirs` | warning | subdiretórios fora da allow-list (`references/`, `scripts/`, `tools/`, `widgets/`, `assets/`) |

### Passo 3: Coletar violações

1. Cada item da saída JSON tem o shape `{rule, severity, file, message}`
2. Separar errors (severidade `error`) de warnings (severidade `warning`)
3. Não inferir nada além do reportado — o kata é "thin": delega a regra ao validador

### Passo 4: Classificar resultado

| Resultado | Critério |
|-----------|----------|
| ✅ `ok` | zero violações |
| ⚠️ `ok-with-warnings` | apenas warnings |
| ❌ `failed` | uma ou mais violações com severidade `error` |

`warrior-claudionor` só prossegue para `kata-skill-package` quando o resultado for `ok` ou `ok-with-warnings` (warnings não bloqueiam empacotamento, mas devem ser apresentados).

### Passo 5: Reportar ao chamador

1. **Format `text` (default):** imprimir o relatório legível por humano (cabeçalho + linhas por violação)
2. **Format `json`:** retornar o array de violações puro, sem encapsulamento, para consumo programático
3. Em qualquer formato, retornar exit code `0` quando todos os itens forem `warning`, `1` quando houver pelo menos um `error`

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Relatório humano | Texto multilinha | `stdout` |
| Relatório agente | JSON `[{rule, severity, file, message}, ...]` | `stdout` |
| Exit code | `0` (ok ou warnings) / `1` (erros) | shell |

## Exemplo de Execução

### Input

```
kata-skill-validate skills/scheduled-payments-skill --format text
```

### Output (sucesso)

```
✅ no violations
```

### Output (com erros)

```
❌ 2 violation(s):
  [error] lex-skill-project-structure#name-matches-slug
      file:    skills/scheduled-payments-skill/SKILL.md
      message: frontmatter name 'scheduled-payments' does not match directory slug 'scheduled-payments-skill'
  [error] lex-skill-project-structure#cross-references
      file:    skills/scheduled-payments-skill/SKILL.md
      message: reference 'references/missing.md' does not exist at ...
```

## Restrições

- O kata **não modifica** arquivos — apenas reporta violações
- O kata **não interpreta** o resultado além do que o validador retorna; novas regras nascem na Lex e descem para o script, nunca o contrário
- O kata invoca o validador via subprocesso para preservar isolamento (drift do interpretador Python da sessão não afeta o resultado)
- Toda mensagem em pt-BR, es ou en conforme `language.default`; identificadores técnicos (paths, nomes de regra) preservados
