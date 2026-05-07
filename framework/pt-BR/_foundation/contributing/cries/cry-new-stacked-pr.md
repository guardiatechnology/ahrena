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
2. O kata roda **Fase 0 — Decision Checklist** mesmo em invocação explícita pelo usuário, usando os critérios canônicos de `codex-stacked-prs` (≥ 3 sinais altos AND 0 anti-sinais).
3. **Se a checklist reprovar** (anti-sinal presente ou sinais altos < 3), o agente avisa:
   ```
   Esta issue não atende a checklist canônica para stacked PR:
     Sinais altos: X (mínimo 3)
     Anti-sinais detectados: [lista]

   Proposta: prosseguir com PR único via kata-contributing-pr.

   Quer forçar a stack mesmo assim? (s/n)
   ```
   - Se `n` (default), redireciona para `kata-contributing-pr` (PR único)
   - Se `s` (override explícito do usuário), prossegue com a stack registrando a decisão de override
4. **Se a checklist aprovar**, o kata propõe decomposição concreta em camadas (ver kata para detalhes), confirma com o usuário e cria a cadeia: worktree compartilhado, N branches, N PRs encadeados, mirror de labels.
5. Lê `.ahrena/.directives` para `stacked_prs.tool`:
   - `vanilla` (default) → segue o fluxo desta Kata
   - `gs` → segue a seção "Variant: git-spice" da Kata (disponível após plan-005)

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
- `kata-contributing-pr` — Fallback para PR único
- `cry-new-pr` — Atalho equivalente para PR único
- `lex-issue-first`, `lex-issue-quality`, `lex-git-branches`, `lex-pr-quality` — Lexis aplicáveis
