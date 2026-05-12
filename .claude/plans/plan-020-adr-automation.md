---
plan_id: "020"
title: "adr-automation"
status: pending
agent: claude
issue: "TBD (a abrir antes da branch — lex-issue-first)"
created_at: "2026-05-07T22:30:00Z"
updated_at: "2026-05-07T22:30:00Z"
---

# Plano: Automação de ADRs (label trigger + check obrigatório no `validate.py`)

## Objetivo

Operacionalizar a regra 4 de `lex-issue-driven` ("Mandatory ADRs for relevant architectural decisions") via mecanismo automatizado. Hoje a Lei obriga ADRs sob `docs/adr/` quando há decisão arquitetural relevante, mas o enforcement é **self-attestation pelo Athena** — a maioria das decisões não vira ADR de fato. Entregar: (a) label `decision:required` no PR — quando aplicado por humano ou detectado heuristicamente, dispara check de CI que exige `docs/adr/ADR-{n}-*.md` no diff; (b) heurística de detecção (warrior consulta diff e sugere label se padrões conhecidos batem); (c) novo módulo no `validate.py` (plan-019) que executa o check; (d) novo cry `cry-adr-write` shortcut. Não substitui julgamento humano — adiciona forcing function.

## Contexto

### Estado atual

- `lex-issue-driven` rule 4 obriga ADR quando: (1) nova tecnologia/lib, (2) deviation de pattern existente, (3) trade-off significativo, (4) decisão multi-componente
- `kata-adr-write` existe e produz ADR em formato MADR simplificado sob `docs/adr/`
- Athena (Phase 3) **deveria** detectar e invocar `kata-adr-write` — mas é frágil, pega só o que o agente "lembra de checar"
- Resultado real: PRs com mudanças de pattern significativas mergeiam sem ADR; conhecimento das decisões fica em commit messages e na cabeça do dev

### Modelo de enforcement proposto

```
[1] Heurística (warrior detecta candidato)
        ↓
[2] Label `decision:required` aplicado ao PR
        ↓
[3] CI check (validate.py com novo módulo `adr_required.py`)
        ↓
[4] Bloqueio se label aplicado E nenhum `docs/adr/ADR-*.md` no diff
        ↓
[5] Caminho de bypass: label `decision:waived` com justificativa em comment
```

### Padrões heurísticos (warrior detecta candidato a ADR)

| Padrão no diff | Indicação |
|---|---|
| Nova entry em `pyproject.toml`/`package.json` em `dependencies` (não dev) | Possível: nova tecnologia |
| Modificação de schema de DB (Alembic migration ≠ trivial) | Possível: decisão de modelagem |
| Alteração em `framework/platforms.yaml` movendo regras entre alwaysApply true/false | Possível: estratégia de carregamento |
| Novo Lexis criado (especialmente HARD-GATE) | Quase certo: decisão arquitetural |
| Mudança em `lex-*-decorator` (logging, metrics, idempotency, resilience, transactional) | Possível: ajuste de pattern obrigatório |
| Alteração em `lex-issue-driven`, `lex-pr-quality`, `kata-quality-gate` | Quase certo: decisão de processo |
| Diff toca > 3 components diferentes em `bounded-context-template` | Possível: decisão multi-componente |
| Novo arquivo em `framework/mcp/` | Possível: novo MCP server adotado |

Heurística é **sugestão**, não decisão. Warrior comenta no PR sugerindo label; humano decide aplicar ou não.

### Decisões fechadas

| Decisão | Valor | Por quê |
|---|---|---|
| Mecanismo | Label PR + CI check (não merge queue, não force pre-merge ADR criação) | Decisão de **se** precisa ADR fica humana; decisão de **se** o ADR existe quando precisa fica automática |
| Label trigger | `decision:required` aplicado por humano ou bot | Determinístico |
| Label bypass | `decision:waived` com comment justificando | Sempre haverá exceções (e.g., bug fix que parece arquitetural mas não é) |
| Heurística | Warrior dedicado ou parte de Athena Phase 3? | **Parte de Athena Phase 3** (caminho menor) — cria menos cerimônia. Athena já lê o diff; adiciona detecção como sub-step |
| ADR location | `docs/adr/ADR-{n}-{kebab-title}.md` (já em uso) | Consistência com `lex-issue-driven` |
| Numeração | Sequencial; `validate.py` checa que número é único e contíguo | Evita gaps acidentais |
| Novo cry | `cry-adr-write` que invoca `kata-adr-write` com prompts pré-preenchidos a partir do issue/PR context | Reduz fricção; agente assiste preenchimento |
| Format do ADR | MADR simplificado (já especificado em `kata-adr-write`) | Não reinventar |
| Rollout | Inicialmente `warning-only` no `validate.py` (módulo entra em warning, vira error em PR de cleanup) | Adoção gradual |
| Idiomas (ADRs propriamente ditos) | ADRs ficam só em `language.default` do projeto (geralmente pt-BR) — ADRs não são artefatos do framework | Ahrena não governa ADR translation |

## Escopo

### Artefatos a criar

| Pilar / tipo | Caminho relativo | Conteúdo |
|---|---|---|
| Cry | `_foundation/contributing/cries/cry-adr-write.md` (3 idiomas) | Atalho para `kata-adr-write` com pre-fill de context (issue link, PR link, summary do diff) |
| Módulo validator | `scripts/_validate/adr_required.py` | Lê labels do PR (via `gh api`) ou env var `GITHUB_PR_LABELS`; se `decision:required` presente E nenhum `docs/adr/ADR-*.md` no diff → finding `error` (warning-only no merge inicial); se `decision:waived` → bypass com checagem de comment com justificativa |
| Doc interno | `docs/internal/adr-trigger-heuristic.md` (pt-BR) | Lista padrões heurísticos detalhados; quando humano deve aplicar manualmente; quando bot pode aplicar automaticamente (futuro) |

### Atualizações em artefatos existentes (3 idiomas)

| Arquivo | Mudança |
|---|---|
| `engineering/workflow/lexis/lex-issue-driven.md` rule 4 | Acrescentar: "Detecção em Phase 3 segue heurística documentada em `docs/internal/adr-trigger-heuristic.md`. Enforcement automatizado: label `decision:required` no PR dispara check em `validate.py`. Label `decision:waived` com justificativa permite bypass" |
| `engineering/workflow/warriors/warrior-athena.md` | Acrescentar em "Phase 3" da seção Operation Flow: "se diff bate heurística ADR (ver `docs/internal/adr-trigger-heuristic.md`), Athena comenta no PR sugerindo aplicar label `decision:required`" |
| `_foundation/process/katas/kata-adr-write.md` | Acrescentar referência ao novo cry; documentar que cry pré-preenche context |
| `_foundation/contributing/lexis/lex-pr-quality.md` HARD-GATE | Acrescentar critério (i): "Se label `decision:required` aplicado, ADR em `docs/adr/` está presente OU label `decision:waived` com justificativa explícita" |
| `_foundation/contributing/codex/codex-labels.md` | Adicionar `decision:required` e `decision:waived` à tabela canônica de labels com cores e descrição |
| `framework/platforms.yaml` | Registrar novo cry |
| `scripts/validate.py` | Importar e executar `_validate/adr_required.py` |
| `docs/internal/validator-rules.md` | Adicionar regra "ADR required when label applied" |

## Fora de escopo

- **Auto-aplicação do label `decision:required` por bot** — primeira iteração é Athena sugerindo via comment; aplicação fica humana. Auto-aplicação fica para iteração futura (precisa permissions específicas no GH App)
- **Auto-criação do skeleton do ADR** quando label aplicado — humano invoca `cry-adr-write`; agente preenche; humano valida
- **ADR machine-readable (YAML front-matter rico)** — formato MADR simplificado mantido; sem tooling sobre ADRs
- **Visualização de ADRs em site** — fora; MkDocs já serve `docs/`
- **Versionamento de ADR (status changes ao longo do tempo: proposed → accepted → superseded)** — formato MADR já cobre status; sem tooling adicional aqui

## Steps

- [ ] 1. **Confirmar plan-019 mergeado** (`scripts/validate.py` é prerequisite; este plan adiciona módulo)
- [ ] 2. Abrir issue com template `feature-request`, Issue Type `Feature`, label `ci 🏗️`
- [ ] 3. Criar branch `feat/{N}-adr-automation` e worktree
- [ ] 4. Atualizar status deste plan para `in-progress`
- [ ] 5. Redigir `docs/internal/adr-trigger-heuristic.md` (pt-BR) consolidando padrões heurísticos
- [ ] 6. Implementar `scripts/_validate/adr_required.py`:
  - input: `GITHUB_EVENT_PATH` ou `gh api repos/.../pulls/{n}` para labels
  - se label `decision:required`: scan diff por `docs/adr/ADR-*.md` adicionado
  - se label `decision:waived`: scan PR comments por comment com prefixo `[adr-waived]:` + texto justificativa (>20 chars)
  - emit `Finding` com severity `warning` (initial rollout)
- [ ] 7. Adicionar tests em `tests/validate/test_adr_required.py` (fixtures: PR com label + ADR; PR com label sem ADR; PR com waiver válido; PR sem label)
- [ ] 8. Atualizar `scripts/validate.py` para incluir o novo módulo
- [ ] 9. Redigir `cry-adr-write.md` em pt-BR (atalho curto para `kata-adr-write` com pre-fill)
- [ ] 10. Atualizar `lex-issue-driven.md` rule 4 em pt-BR
- [ ] 11. Atualizar `warrior-athena.md` (Phase 3 Operation Flow) em pt-BR
- [ ] 12. Atualizar `kata-adr-write.md` em pt-BR
- [ ] 13. Atualizar HARD-GATE de `lex-pr-quality.md` em pt-BR (critério (i))
- [ ] 14. Atualizar `codex-labels.md` em pt-BR (adicionar 2 labels novos com cores)
- [ ] 15. Criar labels `decision:required` (cor `#FBCA04`) e `decision:waived` (cor `#0075CA`) no repo via `gh label create`
- [ ] 16. Atualizar `framework/platforms.yaml`
- [ ] 17. Atualizar `docs/internal/validator-rules.md`
- [ ] 18. Traduzir cry novo + 4 atualizações Lex/Warrior/Kata/Codex para `es` e `en`
- [ ] 19. Rodar `python3 scripts/install.py --self --target . --platform claude-code` e `cursor`
- [ ] 20. **Smoke test 1 (label aplicado, ADR ausente)**: PR sandbox com label `decision:required`, sem ADR em diff; rodar `validate.py`; verificar finding `warning` (rollout inicial)
- [ ] 21. **Smoke test 2 (label aplicado, ADR presente)**: PR sandbox com label `decision:required` + `docs/adr/ADR-001-test.md`; verificar zero findings
- [ ] 22. **Smoke test 3 (waiver)**: PR sandbox com label `decision:waived` + comment `[adr-waived]: hot-fix bug, no architectural change`; verificar zero findings
- [ ] 23. **Smoke test 4 (waiver insuficiente)**: PR com label `decision:waived` mas sem comment válido; verificar finding `error`
- [ ] 24. **Smoke test 5 (Athena heurística)**: PR sandbox que adiciona dependency em `pyproject.toml`; rodar Athena Phase 3 mentalmente; verificar que ela sugere label
- [ ] 25. Rodar `kata-artifact-self-review` em cry e nas atualizações
- [ ] 26. Commits atômicos; push; abrir PR via `kata-contributing-pr`
- [ ] 27. Após merge: arquivar plan e remover worktree

## Dependências

- **Plan-019 mergeado** — `scripts/validate.py` precisa existir (bloqueante)
- `kata-adr-write` mergeado (já está)
- `lex-issue-driven` mergeado (já está)
- `lex-pr-quality` mergeado (já está)
- `gh` CLI autenticado para criar labels e ler PR comments
- **Independente** de plans 011-018 e 021

## Riscos

- **Heurística produz falsos positivos** (sugere ADR para mudanças triviais que mexem em pyproject.toml). Mitigação: heurística é sugestão, label é manual; codex documenta exemplos comuns que **não** precisam ADR
- **Heurística produz falsos negativos** (mudança grande passa sem sugestão). Mitigação: humano sempre pode aplicar label manualmente; heurística complementa, não substitui julgamento
- **Waiver vira escape hatch.** Mitigação: justificativa precisa ser >20 chars; auditoria periódica do uso de `decision:waived`; relatório no `validate.py` lista todos os waivers do mês
- **Conflito com PR labels existentes** (size, type, status). Mitigação: namespace `decision:` não colide com nada hoje
- **Performance impact em validate.py** ao chamar `gh api` para cada PR. Mitigação: usar `GITHUB_EVENT_PATH` (já tem labels) em CI; chamar API só localmente
- **ADR-{n} numbering colide entre PRs concorrentes.** Mitigação: validate.py checa contiguidade após merge (post-hoc); resolver no merge é responsabilidade do dev (rebase + renumber)
- **Athena adicionar comentários repetidos no PR a cada push.** Mitigação: comentário usa marcador HTML idempotente (`<!-- ahrena:adr-suggestion -->`); update em vez de append (mesmo padrão do plan-007 cost stamp)

## Verificação

1. `cry-adr-write` × 3 idiomas + `_validate/adr_required.py` + tests
2. `lex-issue-driven` rule 4 atualizada × 3 idiomas
3. `warrior-athena` Phase 3 atualizada × 3 idiomas
4. `kata-adr-write` referência ao novo cry × 3 idiomas
5. `lex-pr-quality` HARD-GATE com critério (i) × 3 idiomas
6. `codex-labels` lista os 2 labels novos × 3 idiomas
7. Labels `decision:required` e `decision:waived` criados no repo
8. `framework/platforms.yaml` lista o novo cry
9. `validate.py` invoca o novo módulo; severidade `warning` no rollout inicial
10. 5 smoke tests passam
11. PR final passa HARD-GATE de `lex-pr-quality` (incluindo o novo critério (i))
12. **Sem alteração** em `kata-quality-gate` direto (HARD-GATE de PR é onde mora; gate fluxo Athena já cobre)