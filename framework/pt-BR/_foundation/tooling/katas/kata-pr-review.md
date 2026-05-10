# Kata: Iniciar uma Sessão de Revisão de PR (com `purpose=review` no stamp de custo)

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Iniciar uma sessão Claude Code para revisar uma Pull Request, garantindo que os turnos sejam contabilizados na seção `Review` do stamp de custo (`kata-pr-cost-stamp`)

## Objetivo

Garantir que toda sessão Claude Code dedicada à revisão de uma PR seja marcada explicitamente com `purpose=review`, para que o agregador (`scripts/pr-cost-stamp.sh --purpose review`) consiga separar custo de **desenvolvimento** de custo de **revisão** quando o `kata-pr-cost-stamp` estampar a PR. Sem essa marcação, turnos de revisão entram no balde `dev` e poluem a leitura do esforço que originou a PR.

Este Kata é um wrapper instrucional fino: o trabalho efetivo de revisão é feito por `/review` (ou prompt equivalente). O Kata existe para tornar a etiqueta `purpose=review` descobrível e consistente.

## Quando Usar

- O usuário quer revisar uma PR com Claude Code e o projeto tem `pr_cost_tracking.enabled: true`.
- O usuário quer dogfood do stamp: medir o custo de revisão da própria PR antes do merge.
- Invocado pelo `cry-pr-review`.

## Entradas

| Entrada | Obrigatório | Descrição |
|---------|:-----------:|-----------|
| Número da PR | Sim | `$PR_NUMBER` no repositório atual |
| Repositório | Não | `owner/repo`; default: `gh repo view --json nameWithOwner` |

## Fluxo de Trabalho

```
Progresso:
- [ ] 1. Verificar pré-condições
- [ ] 2. Marcar a sessão como purpose=review
- [ ] 3. Disparar a revisão
- [ ] 4. Verificação final
```

### Passo 1: Verificar pré-condições

1. Consultar `.ahrena/.directives` (`lex-directives`).
2. Confirmar `pr_cost_tracking.enabled: true`. Se desabilitado, o Kata informa que o stamp não vai diferenciar dev vs. review e prossegue assim mesmo (a revisão segue funcionando, só não é contabilizada).
3. Confirmar `pr_cost_tracking.attribution_mode: hook` (default quando ausente). Se `project`, o Kata avisa que o legado não bucketiza por `purpose` e prossegue.
4. Verificar que o hook `pr-cost-attribution.sh` está instalado em `.claude/hooks/` e wirado em `.claude/settings.json` (instalado por `scripts/install.py` quando o stamp está habilitado).

### Passo 2: Marcar a sessão como purpose=review

Há três caminhos suportados — escolha o que couber. O caminho A (env var) é o oficial e elimina dependência da heurística:

**A) Variável de ambiente — recomendado.** Inicie a sessão Claude Code com a env var setada:

```bash
GUARDIA_PURPOSE=review claude
```

ou, se o Claude Code já está aberto, exporte antes do próximo turno:

```bash
export GUARDIA_PURPOSE=review
```

O hook lê essa variável e grava `purpose=review` no sidecar para todos os turnos que vierem.

**B) Convenção textual (heurística do hook).** Se a env var não estiver setada, o hook examina a primeira linha do prompt. Comece a sessão de revisão com um prompt que case com a lista canônica:

| Padrão (case-insensitive) | Idioma | Exemplo |
|---|---|---|
| `^/review` | en | `/review PR #72` |
| `^review pr` | en | `review PR #72` |
| `^review #N` | en | `review #72` |
| `^revise pr` | en | `revise PR #72` |
| `^revisar pr` | pt-BR | `revisar PR #72` |
| `^revisão de pr` | pt-BR | `revisão de PR #72` |
| `^revisión de pr` | es | `revisión de PR #72` |
| `pull request review` (em qualquer posição da primeira linha) | en | `let's do a pull request review` |

A heurística decide turno a turno — não persiste entre turnos. Em caso de dúvida, prefira o caminho A.

**C) Combinado.** Use os dois: a env var como contrato e o prompt iniciado com `/review` como hábito. A primeira regra que casa vence (env var sempre que presente).

### Passo 3: Disparar a revisão

1. Com a sessão devidamente marcada, invoque o slash command oficial do Claude Code:
   ```
   /review #<PR_NUMBER>
   ```
   ou conduza a revisão por prompt normal — o que importa para o stamp é a marcação de `purpose`, não a forma da revisão.
2. Conduza o ciclo de revisão (leitura do diff, comentários, sugestões, follow-ups) como de costume.

### Passo 4: Verificação final

- [ ] Sessão iniciada com `GUARDIA_PURPOSE=review` exportada **ou** primeiro prompt na lista canônica
- [ ] Hook gravou ao menos uma linha em `~/.claude/projects/<hash>/branches.jsonl` com `purpose: "review"` (verificável com `tail -1` no arquivo)
- [ ] Quando o `kata-pr-cost-stamp` rodar, o bloco da PR mostrará a subseção **Review → Claude Code (local, `purpose=review`)** com a contagem de sessões correspondente.

## Saídas

| Saída | Formato | Destino |
|-------|---------|---------|
| Sidecar marcado | Linhas JSONL com `purpose: "review"` | `~/.claude/projects/<hash>/branches.jsonl` |
| Revisão da PR | Comentários, sugestões, conversas | PR alvo |

## Exemplo de Execução

```bash
# Recomendado: setar a env var antes da sessão
$ GUARDIA_PURPOSE=review claude
# Dentro da sessão:
> /review PR #72

# Verificar (em outro shell):
$ tail -1 ~/.claude/projects/-Users-fulano-projetos-ahrena/branches.jsonl
{"ts":"...","session_id":"...","purpose":"review", ...}
```

## Restrições

- **Sem efeito quando o stamp está desativado:** se `pr_cost_tracking.enabled: false`, o Kata orienta a marcação mesmo assim (custo zero), mas o stamp não vai existir para reportar.
- **Não substitui revisor humano:** revisão por agente é uma camada complementar; CODEOWNERS e políticas de PR continuam valendo (`lex-pr-quality`).
- **Sem custo público para revisores externos:** se a revisão for por outro agente AI (Gemini, Cursor, Ultrareview), `kata-pr-review` não cobre — esse caminho é detectado automaticamente pelo `pr-cost-stamp-reviews.sh` a partir dos comentários da PR.

## Referências

- `codex-pr-cost-tracking` — Manual com a cascata de detecção de `purpose` e o formato do bloco com a subseção `Review`
- `kata-pr-cost-stamp` — Estampa o resultado na PR, consumindo o sidecar
- `cry-pr-review` — Atalho que invoca este Kata
- `framework/templates/claude-code-hooks/pr-cost-attribution.sh` — Implementação do hook
- `lex-pr-quality` — Política de qualidade de PR
