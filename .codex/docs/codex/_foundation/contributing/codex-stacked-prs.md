# Codex: Stacked Pull Requests no Contexto Ahrena

> **Prefixo:** `codex-` | **Tipo:** Manual de Referência | **Escopo:** Conceito, modelo de decisão e operação de Pull Requests encadeados (stacked) para features grandes em qualquer repositório Guardia

## 1. Modelo conceitual

### 1.1 Cadeia de branches

```
main
 └── feat/{N}-stack-1-{slug}     ← PR #X (base: main)
      └── feat/{N}-stack-2-{slug}  ← PR #Y (base: feat/{N}-stack-1-{slug})
           └── feat/{N}-stack-3-{slug}  ← PR #Z (base: feat/{N}-stack-2-{slug})
```

Cada camada é um PR real no GitHub, com base apontando para a camada anterior. A camada da base aponta para `main`. Todos os PRs compartilham um único worktree compartilhado (ver seção 4).

### 1.2 Modelo de issue (1 → N)

Uma única issue guarda-chuva governa toda a stack. As camadas referenciam:

| Camada | Body do PR |
|---|---|
| 1..N-1 (intermediárias) | `Refs #N` |
| N (última) | `Closes #N` |

Quando a última camada mergeia, GitHub fecha a issue automaticamente. **Não criar issues filhas** por camada — o modelo é umbrella issue + ACs numerados que mapeiam para camadas. Veja `lex-issue-first` para a regra base.

### 1.3 Naming pattern

Compatível com `lex-git-branches`:

```
{type}/{N}-stack-{layer}-{slug}
```

| Campo | Regra |
|---|---|
| `type` | Um dos tipos Conventional Commits: `feat`, `fix`, `docs`, `build`, `chore`, `ci`, `style`, `refactor`, `perf`, `test` |
| `N` | Número da issue guarda-chuva |
| `layer` | Inteiro 1, 2, 3, ... (camada na stack, base→topo) |
| `slug` | kebab-case, máximo 50 caracteres no total |

Exemplos válidos:
- `feat/42-stack-1-schema`
- `feat/42-stack-2-api`
- `feat/42-stack-3-ui`

A presença do segmento literal `stack-{layer}` no slug é o sinal canônico de que a branch faz parte de uma stack.

> **Importante:** `{slug}` é único e compartilhado por toda a stack — é o mesmo `{slug}` usado no diretório do worktree (`.worktrees/{N}-{slug}-stack/`); somente `{layer}` distingue camadas. Os nomes `schema`/`api`/`ui` nos exemplos acima são valores de `{layer}`, não de `{slug}`.

---

## 2. Decision Checklist (canônica)

Esta seção é a **fonte de verdade** consultada pelo `kata-stacked-pr-create` na Fase 0 (Pre-flight) e pelo `cry-new-stacked-pr` em invocação explícita. Não duplicar critérios em outros artefatos.

### 2.1 Sinais altos (cada um conta 1 ponto)

| Sinal | Threshold |
|---|---|
| Tamanho estimado do diff | > 500 linhas modificadas |
| ACs independentes na issue | ≥ 4 ACs |
| Pilares técnicos atravessados | ≥ 2 (ex.: backend + frontend) |
| Camadas óbvias presentes | schema → API → UI; data → service → handler; ou equivalente |
| Independência de review | reviewer A consegue avaliar camada X sem precisar do contexto de Y |
| Risco de rollback por camada | mudança com migração + feature visível na mesma issue |

### 2.2 Anti-sinais (presença de qualquer um veta a stack)

| Anti-sinal | Razão |
|---|---|
| Hotfix / resposta a incidente | velocidade > granularidade; cascade rebase atrasa o fix |
| Cross-fork PR | ferramentas de stack não suportam bem; manualmente é frágil |
| Refactor monolítico | mudança que não decompõe em camadas independentes (ex.: rename atravessando todo o módulo) |

### 2.3 Heurística

- **≥ 3 sinais altos AND 0 anti-sinais** → propor stack com decomposição concreta
- **Caso contrário** → redirecionar para PR único (`kata-contributing-pr`)

A decisão final é sempre do humano. Agente **propõe**, usuário **confirma**.

### 2.4 Decomposição típica

| Tipo de feature | Camadas sugeridas |
|---|---|
| API nova com persistência | 1) migration + entity, 2) repository + use case, 3) router + DTOs, 4) tests + observability |
| UI feature com backend | 1) schema + migration, 2) API endpoints, 3) frontend components, 4) E2E + telemetry |
| Refactor com extração de módulo | 1) novo módulo isolado, 2) pontos de uso migrados, 3) cleanup do código antigo |
| Adoção de Lexis nova | 1) Lexis + Codex, 2) Kata operacional, 3) Cry e atualizações em platforms.yaml |

---

## 3. Mapeamento por Lexis afetadas

Stacked PRs convivem com as Lexis existentes. A tabela abaixo é referência rápida:

| Lexis | Status | Como Stacked PRs respeita |
|---|---|---|
| `lex-protected-trunk` | ✅ | Force-push só em branches da stack, nunca em trunk; PRs mergeiam via fluxo normal |
| `lex-issue-first` | ✅ | Issue guarda-chuva existe antes da branch base; cada PR referencia via `Refs #N` ou `Closes #N` |
| `lex-issue-quality` | ✅ | Issue guarda-chuva atende os 5 critérios canônicos uma vez; camadas herdam |
| `lex-git-branches` | ✅ | Naming `{type}/{N}-stack-{layer}-{slug}` segue o regex `^(feat\|fix\|...)\/[0-9]+-[a-z0-9][a-z0-9-]{0,49}$` |
| `lex-git-worktrees` | ⚠️ exceção | Stack ocupa **um único** worktree compartilhado: `.worktrees/{N}-{slug}-stack/`. Cláusula declarada em "Allowed exceptions" da Lexis |
| `lex-pr-quality` | ✅ | HARD-GATE de 8 critérios aplica **por PR da stack** (cada camada é um PR real); labels do issue são espelhados em cada um |
| `lex-conventional-commits` | ✅ | Cada camada usa commits convencionais normalmente |
| `lex-small-commits` | ✅ | Camadas reforçam atomicidade — uma mudança lógica por camada |
| `lex-signed-commits` | ✅ | Rebase preserva assinatura GPG quando `commit.gpgsign=true` |
| `lex-commit-language` | ✅ | Sem mudança |
| `lex-issue-driven` | 🔄 follow-up | Athena ainda não orquestra stacks; coberto pelo plan-006 (futuro) |

---

## 4. Worktree compartilhado

Diferente do fluxo padrão (1 branch = 1 worktree), uma stack inteira ocupa **um único** worktree:

```
.worktrees/{N}-{slug}-stack/
```

| Campo | Regra |
|---|---|
| `N` | Número da issue guarda-chuva |
| `slug` | Slug descritivo, sem o segmento `stack-{layer}` |

Exemplo: para a issue #42 (scheduled payments), o worktree é `.worktrees/42-scheduled-payments-stack/`. Dentro dele, o agente troca entre as branches da stack via `git checkout`.

Razão técnica: o cascade rebase opera lendo e re-escrevendo as branches em sequência; um worktree por branch quebra o pressuposto de working dir único.

A exceção está declarada em `lex-git-worktrees` na seção "Allowed exceptions".

---

## 5. Ciclo de vida da stack

```
issue guarda-chuva existe
    ↓
Decision Checklist (Fase 0 do kata-create)  →  reprovou: PR único
    ↓ aprovado
criar worktree compartilhado
    ↓
para cada camada i de 1..N:
    git checkout -b feat/{N}-stack-{i}-{slug}
    work
    commit assinado
    push
    gh pr create --base {camada anterior}
    gh pr edit (mirror de labels/assignee/reviewers)
    ↓
review acontece em paralelo (camada inferior primeiro)
    ↓
mudança em camada inferior?  →  cascade rebase (kata-rebase)
    ↓
merge bottom-up (kata-merge):
    merge layer 1
    gh pr edit layer 2 --base main
    rebase layer 2 onto main
    repete para camadas superiores
    ↓
após última camada mergear:
    git worktree remove
    cleanup branches locais
```

Detalhes operacionais ficam nos katas dedicados:

- `kata-stacked-pr-create` — Fase 0 (Decision Checklist) e criação da cadeia
- `kata-stacked-pr-rebase` — cascade rebase manual após mudança em camada inferior
- `kata-stacked-pr-merge` — política bottom-up e cleanup

---

## 6. Limites recomendados

| Aspecto | Limite vanilla | Quando ultrapassar |
|---|---|---|
| Número de camadas | 3-4 | Considerar git-spice (plan-005) que automatiza cascade rebase |
| Tamanho médio por camada | 200-500 linhas | Camadas muito pequenas indicam decomposição artificial; muito grandes cancelam o benefício de review |
| Duração da stack viva | ≤ 2 semanas | Stacks longas acumulam conflito com `main`; preferir mergear camadas baixas e abrir nova stack |
| ACs por camada | 1-3 ACs | Mais que isso indica camada muito ampla; refinar a decomposição |

---

## 7. Trade-offs do caminho vanilla

| Vantagem | Trade-off |
|---|---|
| Zero dependência externa — funciona em qualquer repositório GitHub hoje | Cascade rebase é manual; cada mudança em camada inferior exige 1 rebase + 1 push por camada superior |
| Fluxo transparente — cada comando é um `git`/`gh` legível | Mais propenso a erro humano (rebase contra branch errada, force-push sem lease) |
| Compatível com qualquer hook/lint/CI existente | Sem UI nativa de "stack map"; revisores precisam navegar PR a PR |
| Auditável passo a passo | Reorder de camadas no meio é caro (recriar manualmente) |

Para stacks de 4+ camadas ou alta frequência de iteração, considerar `git-spice` quando plan-005 mergear.

---

## 8. Boas práticas

1. **Decompor por contrato, não por arquivo.** Camadas devem representar interfaces estáveis (schema, API, UI), não diretórios. Reviewer da camada N+1 confia no contrato fechado pela camada N.
2. **`--force-with-lease` sempre.** Nunca `--force` cego. O lease evita sobrescrever commits de outra pessoa que estava revisando a camada.
3. **Mergear camadas baixas rápido.** Não esperar a stack inteira para mergear a base — quanto mais tempo viva, mais conflito acumula.
4. **Atualizar `base` do PR seguinte explicitamente após cada merge.** GitHub não migra automaticamente; veja `kata-stacked-pr-merge`.
5. **Espelhar labels em cada camada.** `lex-pr-quality` aplica por PR; `kata-stacked-pr-create` automatiza via `gh pr edit`.
6. **Escrever no body de cada PR qual fatia ela cobre.** Ex.: `Refs #42 (2/3 — API endpoints)`. Ajuda reviewer a entender a posição.

---

## 9. Quando NÃO usar stacked PRs

- Mudança trivial (typo, docs minor, single-file refactor) — overhead de N PRs supera o ganho
- Hotfix de incidente — velocidade > granularidade
- Stack proposta sem camadas naturais (forçar decomposição artificial)
- Time não familiarizado com `git rebase` — risco de erro de cascade
- Cross-fork — limitação técnica das ferramentas de stack

Em qualquer um desses casos, agente redireciona para `kata-contributing-pr` (PR único).

---

## 10. Diretiva `stacked_prs.tool`

Em `.ahrena/.directives`:

```yaml
stacked_prs:
  tool: vanilla   # vanilla | gs
```

| Valor | Comportamento |
|---|---|
| `vanilla` | Default; segue os procedimentos descritos neste codex e nos katas correspondentes |
| `gs` | Disponível após plan-005 mergear; ativa as seções "Variant: git-spice" dos katas |

Ausência da diretiva = `vanilla` implícito.

---
