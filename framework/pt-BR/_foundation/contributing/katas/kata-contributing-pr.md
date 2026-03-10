# Kata: Contribuir via Pull Request

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Criação de Pull Request no repositório origin via MCP

## Objetivo

Este Kata define o procedimento padronizado para abrir um Pull Request no repositório origin do projeto, usando as ferramentas MCP do GitKraken e o template em `.ahrena/contributing_templates/pull_request_template.md` (ou `.github/pull_request_template.md`). Ele garante que toda contribuição siga o fluxo unificado definido no `codex-contributing`. Alinha-se ao `kata-contribute` existente.

## Quando Usar

- Quando mudanças estão prontas para submissão ao repositório
- Quando o usuário solicita criar um PR
- Quando invocado pelo cry-new-pr ou pelo cry-contribute com ação pr

## Inputs

| Input | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| Mudanças commitadas | Sim | Commits prontos no branch local (já validados pelo `kata-commit`) |
| Título | Não | Título do PR em Conventional Commits. Se omitido, o agente infere dos commits |
| Issue relacionada | Não | Número da issue que o PR resolve. Se omitido, o agente pergunta |

## Workflow

```
Progresso:
- [ ] 1. Analisar mudanças
- [ ] 2. Preparar branch
- [ ] 3. Push ao remote
- [ ] 4. Compor PR (template em .ahrena/contributing_templates/)
- [ ] 5. Criar PR via MCP (GitKraken: pull_request_create)
- [ ] 6. Verificação final
```

### Passo 1: Analisar mudanças

1. Executar `git status` para verificar o estado do repositório
2. Executar `git log main..HEAD --oneline` para listar os commits a serem incluídos
3. Verificar que todos os commits seguem as Lexis (`lex-conventional-commits`, `lex-signed-commits`, `lex-small-commits`, `lex-commit-language`)
4. Se houver mudanças não-commitadas, invocar `kata-commit` primeiro

### Passo 2: Preparar branch

1. Verificar o nome do branch atual: `git branch --show-current`
2. Se estiver em `main`, criar branch seguindo a convenção: `feat/{nome}`, `fix/{nome}`, `docs/{nome}` (nome inferido do escopo dos commits)
3. Usar MCP `git_branch` com `action: create` e `branch_name`; MCP `git_checkout` para trocar para o novo branch

### Passo 3: Push ao remote

1. Executar push via MCP `git_push` com `directory` apontando para o repositório
2. Se o push falhar por branch não existir no remote, o git criará automaticamente

### Passo 4: Compor PR (template)

1. Extrair `repository_organization` e `repository_name` do remote (ex.: `git remote get-url origin`)
2. Compor o título em Conventional Commits (em inglês): um commit → subject do commit; vários commits → título que resume a mudança
3. **Template:** Ler `.ahrena/contributing_templates/pull_request_template.md`; se não existir, usar `.github/pull_request_template.md`
4. Preencher o body: Description, Type of Change, Prerequisites, How Has This Been Tested, Checklist, Related Issues (`Closes #N` ou `Related to #N`); Breaking Changes, Security, Performance quando aplicável

### Passo 5: Criar PR via MCP

Invocar MCP `pull_request_create` (server: `user-GitKraken`) com:

| Parâmetro | Valor |
|-----------|-------|
| `provider` | `github` |
| `repository_name` | Extraído do remote (ex.: `ahrena`) |
| `repository_organization` | Extraído do remote (ex.: `guardiafinance`) |
| `title` | Título em Conventional Commits |
| `source_branch` | Branch atual |
| `target_branch` | `main` |
| `body` | Template preenchido |
| `is_draft` | `false` (ou `true` se o usuário solicitar) |

### Passo 6: Verificação final

- [ ] O PR foi criado com sucesso
- [ ] O título segue Conventional Commits em inglês
- [ ] O body está preenchido com o template do repositório
- [ ] A issue está referenciada no PR
- [ ] Todos os commits estão assinados (GPG verified)
- [ ] O branch source está correto

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Pull Request | GitHub PR | Repositório origin |
| URL do PR | Link | Apresentado ao usuário |

## Restrições

- Nunca criar PR sem que os commits estejam conformes com as 4 Lexis de commit
- Nunca criar PR diretamente em `main` (sempre usar branch)
- Se não houver template em `.ahrena/` nem em `.github/`, usar formato padrão (Description + Related Issues)
- Se o MCP `pull_request_create` falhar, apresentar o erro e sugerir criação manual via `gh pr create`

## Referências

- `codex-contributing` — Fluxo de contribuição Guardia
- `codex-commit-standards` — Standards de mensagem de commit
- `kata-commit` — Procedimento para fazer commits conformes
- `kata-contribute` — Procedimento canônico de PR (este kata alinha ou reutiliza)
- `cry-new-pr`, `cry-contribute` — Atalhos que invocam este Kata
- `.ahrena/contributing_templates/pull_request_template.md` — Template de PR (fonte canônica após install)
