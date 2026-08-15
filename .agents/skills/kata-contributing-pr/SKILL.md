---
name: kata-contributing-pr
description: "Contribuir via Pull Request. Criar Pull Request no repositório de origem via GitHub MCP ou CLI gh"
---

# Kata: Contribuir via Pull Request

> **Prefix:** `kata-` | **Type:** Skill Repetível | **Scope:** Criar Pull Request no repositório de origem via GitHub MCP ou CLI gh

## Entradas

| Entrada | Obrigatório | Descrição |
|---------|:-----------:|-----------|
| Commits realizados | Sim | Commits prontos na branch local (já validados por `kata-commit`) |
| Título | Não | Título do PR no formato Conventional Commits. Se omitido, o agente infere a partir dos commits |
| Issue relacionado | Não | Número do issue que o PR resolve. Se omitido, o agente pergunta |

## Fluxo de Trabalho

```
Progresso:
- [ ] 1. Analisar as mudanças
- [ ] 2. Preparar a branch
- [ ] 3. Push para o remoto
- [ ] 4. Compor o PR (template em .ahrena/contributing_templates/)
- [ ] 5. Criar PR via GitHub MCP (ou gh)
- [ ] 6. Aplicar labels e assignee
- [ ] 7. Estampar custo (opcional, conforme `.directives`)
- [ ] 8. Verificação final
```

### Passo 1: Analisar as mudanças

1. Executar `git status` para verificar o estado do repositório.
2. Executar `git log main..HEAD --oneline` para listar os commits a serem incluídos.
3. Verificar que todos os commits seguem as Lexis (`lex-conventional-commits`, `lex-signed-commits`, `lex-small-commits`, `lex-commit-language`).
4. Se houver mudanças não commitadas, invocar `kata-commit` primeiro.

### Passo 2: Preparar a branch

1. Verificar o nome da branch atual: `git branch --show-current`.
2. A branch DEVE seguir o formato `{type}/{issue-number}-{slug}` conforme `lex-git-branches`. Se não seguir, renomeá-la antes de continuar.
3. Confirmar que o issue associado existe e está completo conforme `lex-issue-quality`.

### Passo 3: Push para o remoto

1. Fazer push da branch:
   ```bash
   git push -u origin $(git branch --show-current)
   ```
2. Se o push falhar (branch não existe no remoto), `git push` a cria automaticamente.

### Passo 4: Compor o PR (template)

1. Extrair `owner` e `repo` da URL remota (por exemplo, `git remote get-url origin`).
2. Compor o título em Conventional Commits (em inglês): um commit → assunto do commit; múltiplos commits → um título resumindo o conjunto de mudanças.
3. **Template:** Ler `.ahrena/contributing_templates/pull_request_template.md`; se não existir, usar `.github/pull_request_template.md`.
4. Preencher o corpo: Descrição, Tipo de Mudança, Pré-requisitos, Como Foi Testado, Checklist, Issues Relacionados (`Closes #N` ou `Refs #N`); Breaking Changes, Segurança, Performance quando aplicável.

### Passo 5: Criar PR via GitHub MCP (ou gh)

**Preferencial:** Usar a ferramenta GitHub MCP `pull_request_create` (ou `issue_write` com método `create_pr`) com: `owner`; `repo`; `title`; `source_branch`; `target_branch`: `main`; `body`; `assignees`: `["@me"]`; `is_draft` conforme necessário.

**Fallback (CLI gh):**
```bash
gh pr create \
  --title "..." \
  --base main \
  --body "..." \
  --assignee "@me"
```

Registrar o número do PR retornado — necessário para o Passo 6.

### Passo 6: Aplicar labels e assignee

Labels de tamanho são aplicados **automaticamente** pelo GitHub Actions — não os aplique manualmente.

Aplicar labels manualmente:

1. **Obter labels do issue associado:**
   ```bash
   gh issue view $ISSUE_NUMBER --repo $OWNER/$REPO \
     --json labels --jq '[.labels[].name] | join(",")'
   ```
2. **Espelhar cada label no PR:**
   ```bash
   gh pr edit $PR_NUMBER --repo $OWNER/$REPO \
     --add-label "label1" --add-label "label2"
   ```
3. **Aplicar labels específicos de PR quando aplicável** (ver `codex-labels`):
   - `breaking change 💥` — se algum commit introduz uma mudança incompatível de API
   - `security 🛡️` — se o PR resolve um problema de segurança

### Passo 7: Estampar custo (opcional)

Passo opcional, ativado por `pr_cost_tracking.enabled: true` em `.ahrena/.directives`. Não-bloqueante: uma falha do stamp não impede a PR.

1. Consultar `.ahrena/.directives`. Se `pr_cost_tracking.enabled` estiver ausente ou `false`, pular este passo.
2. Invocar `kata-pr-cost-stamp` com `$PR_NUMBER` registrado no Passo 5.
3. Se o stamp falhar (rede, ferramenta indisponível, parsing), registrar aviso no log e prosseguir para o Passo 8.

### Passo 8: Verificação final

- [ ] O PR foi criado com sucesso
- [ ] O título segue Conventional Commits em inglês
- [ ] O corpo está preenchido com o template do repositório
- [ ] O issue é referenciado com `Closes #N` ou `Refs #N`
- [ ] Todos os labels do issue estão espelhados no PR
- [ ] Labels específicos de PR aplicados quando aplicável (`breaking change 💥`, `security 🛡️`)
- [ ] O PR está auto-atribuído (`@me`)
- [ ] Todos os commits estão assinados (verificação GPG)
- [ ] A branch de origem segue o formato `lex-git-branches`
- [ ] Stamp de custo executado com sucesso ou pulado conforme `pr_cost_tracking.enabled` em `.directives` (Passo 7)

## Saídas

| Saída | Formato | Destino |
|-------|---------|---------|
| Pull Request | GitHub PR | Repositório de origem |
| URL do PR | Link | Apresentado ao usuário |

## Restrições

- Não criar um PR a menos que os commits estejam em conformidade com as 4 Lexis de commit.
- Não criar um PR diretamente em `main` (sempre usar uma branch seguindo `lex-git-branches`).
- Não aplicar labels `size/*` manualmente — eles são auto-aplicados pelo GitHub Actions.
- Se não houver template em `.ahrena/` ou `.github/`, usar o formato padrão (Descrição + Issues Relacionados).
- Sempre auto-atribuir o PR (`--assignee "@me"`), a menos que o usuário especifique explicitamente um assignee diferente.
