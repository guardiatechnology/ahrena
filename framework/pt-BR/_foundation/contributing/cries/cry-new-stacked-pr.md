# Cry: Novo Stacked Pull Request

> **Prefixo:** `cry-` | **Tipo:** Comando Recorrente | **Escopo:** Atalho para iniciar uma cadeia de Pull Requests encadeados (stack) no repositório origin

## Invocação

```
/cry-new-stacked-pr [<issue-number>] [--draft]
```

## Parâmetros

| Parâmetro | Obrigatório | Descrição |
|-----------|:-----------:|-----------|
| `<issue-number>` | Não | Número da issue guarda-chuva. Se omitido, o agente pergunta. |
| `--draft` | Não | Cria todos os PRs da stack como rascunho. |

## Comportamento

1. Invoca **kata-stacked-pr-create**.
2. O kata roda **Fase 0 — Decision Checklist** mesmo em invocação explícita pelo usuário, aplicando a checklist canônica definida em `codex-stacked-prs`.
3. **Se a checklist reprovar**, o kata avisa o usuário com os sinais reais contados, propõe seguir com PR único via `kata-contributing-pr`, e só prossegue com a stack mediante override explícito do usuário (registrando a decisão).
4. **Se a checklist aprovar**, o kata propõe decomposição concreta em camadas (ver kata para detalhes), confirma com o usuário e cria a cadeia: worktree compartilhado, N branches, N PRs encadeados, mirror de labels.
5. O kata seleciona a ferramenta operacional consultando a diretiva `stacked_prs.tool` em `.ahrena/.directives`. Valores aceitos: `vanilla` (default — `git` + `gh`) e `gs` (git-spice — auto-restack documentado em `codex-git-spice`). Cada valor ativa a seção correspondente da Kata (procedimento principal vs. seção "Variant: git-spice"); a Cry não lê a diretiva diretamente.

## Kata Associado

`kata-stacked-pr-create` — Procedimento para decompor uma feature em stack e criar a cadeia de PRs.

## Restrições

- **Nunca** prossegue sem confirmação explícita do usuário sobre a decomposição em camadas
- **Nunca** ignora anti-sinais sem override consciente do usuário
- Se a issue guarda-chuva não atende `lex-issue-quality`, alerta e para — issue precisa ser corrigida antes
- Se `stacked_prs.tool` não está declarado em `.ahrena/.directives`, assume `vanilla`

## Referências

- `kata-stacked-pr-create` — Kata invocado por este Cry
- `codex-stacked-prs` — Decision Checklist canônica e modelo conceitual
- `codex-git-spice` — Manual da variante `gs` quando o projeto declara `stacked_prs.tool: gs`
- `kata-contributing-pr` — Fallback para PR único
- `cry-new-pr` — Atalho equivalente para PR único
- `lex-issue-first`, `lex-issue-quality`, `lex-git-branches`, `lex-pr-quality` — Lexis aplicáveis
