# Kata: Contribuir Pilar ao Framework

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Submissão de Pilares ao repositório do Ahrena

## Objetivo

Este Kata define o procedimento padronizado para contribuir um Pilar (ou conjunto de Pilares) ao repositório do framework Ahrena — incluindo validação, commit e submissão via PR ou commit direto dependendo do papel do contribuidor.

## Quando Usar

- Quando um novo Pilar foi criado (via `kata-create-*`) e precisa ser incorporado ao framework
- Quando o usuário solicita submeter uma contribuição ao repositório do Ahrena
- Quando invocado pelo `cry-contribute`

## Inputs

| Input | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| Caminho do Pilar | Sim | Caminho do artefato principal no idioma padrão (ex: `framework/pt-BR/.../lex-example.md`) |
| Mensagem | Não | Descrição da contribuição. Se omitido, o agente compõe a partir do Pilar |

## Workflow

```
Progresso:
- [ ] 1. Validação do Pilar
- [ ] 2. Verificação de i18n
- [ ] 3. Detecção de permissão
- [ ] 4. Commit das mudanças
- [ ] 5. Submissão
- [ ] 6. Verificação final
```

### Passo 1: Validação do Pilar

1. Verificar que o artefato segue o template oficial (`lex-template-usage`):
   - Identificar o Pilar pelo prefixo do arquivo
   - Ler o template correspondente (`templates/{pilar}-sample.md`)
   - Verificar que todas as seções obrigatórias estão presentes
2. Verificar que o artefato está no caminho correto da taxonomia:
   - Segue o endereçamento `{lang}/{clade}/{subclade}/{pilar}/{prefixo}-{nome}.md`
   - Usa kebab-case
   - Usa o prefixo correto do Pilar
3. Verificar que não contradiz Lexis existentes
4. Verificar que não duplica artefatos existentes

### Passo 2: Verificação de i18n

1. Ler `.ahrena/.directives` para obter `language.i18n`
2. Para cada idioma obrigatório, verificar que existe a versão traduzida:
   - `framework/pt-BR/.../{artefato}.md`
   - `framework/es/.../{artefato}.md`
   - `framework/en/.../{artefato}.md`
3. Se faltam traduções, alertar e sugerir usar `kata-translate` ou `cry-translate`

### Passo 3: Detecção de Permissão

1. Verificar se o repositório atual é o Ahrena:
   ```
   git remote get-url origin
   ```
2. Verificar se o usuário é codeowner consultando `.github/CODEOWNERS`
3. Opcionalmente, verificar via API:
   ```
   gh api repos/{owner}/{repo}/collaborators/{username}/permission
   ```
4. Determinar o caminho:
   - **Codeowner:** commit direto + push
   - **Contribuidor externo:** branch + PR

### Passo 4: Commit das Mudanças

1. Executar `git add` para os arquivos do Pilar (todas as versões i18n)
2. Invocar `kata-commit` com:
   - Tipo: `docs` (para artefatos do framework)
   - Escopo: nome do Pilar (ex: `lex-conventional-commits`)
   - Descrição em inglês descrevendo a contribuição

### Passo 5: Submissão

**Se codeowner:**
1. Push direto ao branch:
   ```
   git push origin HEAD
   ```

**Se contribuidor externo:**
1. Criar branch:
   ```
   git checkout -b docs/{pilar-name}
   ```
2. Push ao fork:
   ```
   git push -u origin docs/{pilar-name}
   ```
3. Abrir PR:
   ```
   gh pr create --title "docs({pilar}): add {name}" --body "..."
   ```
4. Preencher o body do PR com:
   - O que: descrição do Pilar
   - Por quê: justificativa
   - Referências: issue ou discussão relacionada

### Passo 6: Verificação Final

- [ ] O Pilar segue o template oficial (`lex-template-usage`)
- [ ] Existe versão em todos os idiomas de `language.i18n`
- [ ] O commit segue as 4 Lexis de commit
- [ ] O commit está assinado (GPG verified)
- [ ] A submissão foi feita (push ou PR criado)
- [ ] CI está passando (se aplicável)

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Commit(s) assinado(s) | Git commit | Repositório local/remoto |
| PR (se contribuidor externo) | GitHub Pull Request | Repositório do Ahrena |

## Restrições

- Nunca submeter Pilar sem validação completa (template + i18n)
- Nunca pular a assinatura GPG
- Se houver dúvida sobre o Clade/Subclade correto, escalar para humano
- Se o Pilar contradiz uma Lexis existente, escalar para humano

## Referências

- `codex-contributing` — Fluxo de contribuição Guardia
- `codex-commit-standards` — Standards de mensagem de commit
- `kata-commit` — Procedimento para fazer commits conformes
- `lex-template-usage` — Lei de uso obrigatório de templates
- `lex-framework-language` — Lei de estrutura de idiomas
- `warrior-framework-curator` — Agente que executa este Kata
- `cry-contribute` — Atalho que invoca este Kata
