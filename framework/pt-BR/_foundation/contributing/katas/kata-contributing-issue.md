# Kata: Abrir issue no repositório (template por tipo)

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Criação de issue no repositório origin via MCP do GitHub

## Objetivo

Este Kata define o procedimento padronizado para abrir uma issue no repositório origin do projeto usando um dos 4 templates de issue (feature-request, epic, user-story-for-api, user-story-for-frontend). O agente resolve o template em `.ahrena/contributing_templates/`, preenche as seções com o usuário e cria a issue **via MCP do GitHub** (fallback para `gh` CLI quando indisponível). Segue o fluxo do `codex-contributing`.

## Quando Usar

- Quando o usuário solicita abrir uma feature request, epic ou user story (API ou frontend)
- Quando invocado por um dos cries: cry-new-feature-request, cry-new-epic, cry-new-user-story-api, cry-new-user-story-frontend
- Quando invocado por cry-contribute com ação issue (e tipo indicado ou inferido)

## Inputs

| Input | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| Tipo | Sim* | `feature-request` \| `epic` \| `user-story-for-api` \| `user-story-for-frontend`. *Inferido pelo cry que invocou, se não informado.* |
| Título (resumo) | Não | Resumo breve da issue. Se omitido, o agente compõe a partir do contexto. |
| Contexto do usuário | Não | Informações adicionais para preencher placeholders do template. |

### Tabela: tipo → template

| Tipo | Arquivo de template (em `.ahrena/contributing_templates/`) |
|------|------------------------------------------------------------|
| feature-request | `feature-request.md` |
| epic | `epic.md` |
| user-story-for-api | `user-story-for-api.md` |
| user-story-for-frontend | `user-story-for-frontend.md` |

## Workflow

```
Progresso:
- [ ] 1. Resolver tipo da issue
- [ ] 2. Carregar template .md
- [ ] 3. Preencher seções/placeholders com o usuário
- [ ] 4. Criar issue via MCP do GitHub (ou gh)
- [ ] 5. Verificação final
```

### Passo 1: Resolver tipo da issue

1. Se o tipo foi passado explicitamente (ex.: pelo cry), usá-lo.
2. Caso contrário, perguntar ao usuário qual tipo deseja: feature request, epic, user story (API) ou user story (frontend).
3. Mapear para o nome do arquivo conforme a tabela acima.

### Passo 2: Carregar template .md

1. Caminho canônico: `.ahrena/contributing_templates/<arquivo>.md` (ex.: `feature-request.md`).
2. Se não existir em `.ahrena/`, usar fallback: `framework/templates/contributing_templates/<arquivo>.md` ou `.github/ISSUE_TEMPLATE/` quando aplicável.
3. Ler o conteúdo e identificar seções e placeholders (ex.: `{user_role}`, `{specific_objective}`).

### Passo 3: Preencher seções/placeholders com o usuário

1. Para cada seção obrigatória do template, obter do usuário ou do contexto as informações necessárias.
2. Substituir placeholders e preencher checkboxes quando aplicável.
3. Compor o título da issue (ex.: "feat/ resumo" para feature request; resumo breve para epic/user story).
4. Montar o body em Markdown com o template preenchido.

### Passo 4: Criar issue via MCP do GitHub (ou gh)

1. **Preferência:** usar MCP do GitHub (servidor que exponha criação de issue). Ex.: servidor `project-0-ahrena-github`, ferramenta `issue_write` com:
   - `method`: `create`
   - `owner`: organização do repositório (ex.: `guardiafinance`)
   - `repo`: nome do repositório (ex.: `ahrena`)
   - `title`: título composto
   - `body`: corpo em Markdown (template preenchido)
   - `labels`: opcional, conforme tipo (ex.: "feature request", "epic", "api", "frontend")
2. **Fallback:** se o MCP não estiver disponível, usar `gh issue create --title "..." --body "..."` (ou body via arquivo temporário).

### Passo 5: Verificação final

- [ ] A issue foi criada com sucesso
- [ ] O título e o body refletem o template preenchido
- [ ] O link da issue foi apresentado ao usuário

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Issue | GitHub Issue | Repositório origin |
| URL da issue | Link | Apresentado ao usuário |

## Restrições

- Sempre usar um dos 4 tipos e o template correspondente; não criar issue sem template quando o tipo for um dos quatro.
- Se nem `.ahrena/contributing_templates/` nem o fallback existirem, informar o usuário e sugerir executar o install do Ahrena ou criar o template manualmente.
- Em caso de falha do MCP, apresentar o erro e sugerir criação manual via `gh issue create` ou pela UI do GitHub.

## Referências

- `codex-contributing` — Fluxo de contribuição Guardia
- `.ahrena/contributing_templates/` — Templates de issue (feature-request.md, epic.md, user-story-for-api.md, user-story-for-frontend.md)
- MCP do GitHub (ex.: issue_write para criação de issue)
- Cries: cry-new-feature-request, cry-new-epic, cry-new-user-story-api, cry-new-user-story-frontend
