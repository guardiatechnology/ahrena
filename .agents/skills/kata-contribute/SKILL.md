---
name: kata-contribute
description: "Contribuir via Pull Request. Criação de Pull Request no repositório origin via MCP"
---

# Kata: Contribuir via Pull Request

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Criação de Pull Request no repositório origin via MCP

## Workflow

```
Progresso:
- [ ] 1. Analisar mudanças
- [ ] 2. Preparar branch
- [ ] 3. Push ao remote
- [ ] 4. Compor PR
- [ ] 5. Criar PR via MCP
- [ ] 6. Verificação final
```

### Passo 1: Analisar Mudanças

1. Executar `git status` para verificar o estado do repositório
2. Executar `git log main..HEAD --oneline` para listar os commits a serem incluídos
3. Verificar que todos os commits seguem as Lexis (`lex-conventional-commits`, `lex-signed-commits`, `lex-small-commits`, `lex-commit-language`)
4. Se houver mudanças não-commitadas, invocar `kata-commit` primeiro

### Passo 2: Preparar Branch

1. Verificar o nome do branch atual:
   ```
   git branch --show-current
   ```
2. Se estiver em `main`, criar branch seguindo a convenção:
   - `feat/{nome}` para features
   - `fix/{nome}` para correções
   - `docs/{nome}` para documentação
   - O nome é inferido do escopo dos commits
3. Usar MCP `git_branch` com `action: create` e `branch_name` para criar
4. Usar MCP `git_checkout` para trocar para o novo branch

### Passo 3: Push ao Remote

1. Executar push via MCP `git_push` com `directory` apontando para o repositório
2. Se o push falhar por branch não existir no remote, o git criará automaticamente

### Passo 4: Compor PR

1. Extrair informações do remote:
   ```
   git remote get-url origin
   ```
   Parsear `repository_organization` e `repository_name` da URL
2. Compor o título em formato Conventional Commits (em inglês):
   - Se há um único commit: usar o subject do commit como título
   - Se há múltiplos commits: compor título que resume a mudança
3. Ler `.github/pull_request_template.md` e preencher o body:
   - **Description:** resumo da mudança e issue resolvida
   - **Type of Change:** marcar checkboxes relevantes
   - **Prerequisites:** associar issue, milestone e labels
   - **How Has This Been Tested:** descrever testes
   - **Checklist:** validar itens aplicáveis
   - **Related Issues:** referenciar com `Closes #N` ou `Related to #N`
   - Preencher seções opcionais (Breaking Changes, Security, Performance) quando aplicável

### Passo 5: Criar PR via MCP

Invocar MCP `pull_request_create` (server: `user-GitKraken`) com:

| Parâmetro | Valor |
|-----------|-------|
| `provider` | `github` |
| `repository_name` | Extraído do remote (ex: `ahrena`) |
| `repository_organization` | Extraído do remote (ex: `guardiatechnology`) |
| `title` | Título em Conventional Commits |
| `source_branch` | Branch atual |
| `target_branch` | `main` |
| `body` | Template preenchido |
| `is_draft` | `false` (ou `true` se o usuário solicitar) |

### Passo 6: Verificação Final

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
- Se não houver `.github/pull_request_template.md`, usar formato padrão (Description + Related Issues)
- Se o MCP `pull_request_create` falhar, apresentar o erro e sugerir criação manual via `gh pr create`
