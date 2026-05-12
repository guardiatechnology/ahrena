---
plan_id: "022"
title: "token-optimization-codification"
status: pending
agent: claude
issue: "TBD (a abrir antes da branch — lex-issue-first)"
created_at: "2026-05-07T23:00:00Z"
updated_at: "2026-05-07T23:00:00Z"
---

# Plano: Codificação da estratégia de otimização de tokens (codex + lex + integração no quality gate)

## Objetivo

Transformar a estratégia de otimização de tokens — hoje distribuída entre os plans 011-021 e a cabeça do mantenedor — em **artefatos consultáveis do framework**. Entregar (a) `codex-token-optimization` como manual de referência das 6 técnicas transversais, (b) `lex-token-budget` com HARD-GATE obrigando declaração de budget em todo novo warrior/lex, (c) atualização dos templates de warrior e lex para incluir campo de budget no frontmatter, (d) atualização do `kata-quality-gate` Check 7 para validar budget, (e) cross-references dos 11 plans atuais ao novo codex. Future-proofing: futuros contribuidores e agentes consultam um lugar canônico em vez de redescobrir a estratégia.

## Contexto

### Por que codex + lex (e não só codex)

| Camada | Papel | Granularidade da obrigação |
|---|---|---|
| `codex-token-optimization` (Codex) | Manual — explica as 6 técnicas e quando aplicar cada uma | "Como otimizar" — guia |
| `lex-token-budget` (Lex) | Lei — obriga declaração de budget e enforça budgets numéricos | "Tem que declarar e respeitar" — contrato |

Codex sozinho vira sugestão ignorável. Lex sozinha sem manual vira regra sem porquê. Os dois juntos é o padrão: `lex-hard-gate-pattern` + `codex-tone` é o exemplo prévio dessa simbiose.

### Estratégia consolidada (vai para o codex)

Seis técnicas transversais identificadas nos plans 011-021:

| # | Técnica | Onde aplicar | Plans que já a usam |
|---|---|---|---|
| 1 | **Lazy-load via `paths:`** em `platforms.yaml` | Toda Lex/Codex/Warrior carregada por glob de arquivo | 002, 003, 011, 012, 013, 014, 021 |
| 2 | **Decorator + allow-list em `pyproject.toml`** | Lexis prescritivas que banem chamadas inline | 015, 016, 017, 018 (e existente: lex-logging-decorator) |
| 3 | **Codex referenciado** (Lex curta + Codex carrega o "como") | Toda nova Lex que tenha conteúdo > ~80 linhas | 015, 016, 017, 018, 020 |
| 4 | **HARD-GATE compacto** (6 elementos canônicos vs prose livre) | Toda Lex bloqueante | 016, 017, 018, 020, 022 (este plan), e existentes |
| 5 | **Router retrocompatível** | Quando split de warrior tem cries legados consumindo o monolítico | 013 |
| 6 | **Smoke test com medição de tokens** | Toda mudança que afeta footprint de sessão | 013, 014, 015, 016, 017, 018, 021 |

Cada técnica vira seção própria do codex com: objetivo, mecanismo, aplicabilidade, trade-off, exemplo de uso, e referência ao plan/Lex que primeiro a aplicou.

### Token budgets numéricos (vai para a lex)

| Categoria de artefato | Budget alvo (linhas no `.md`) | Justificativa | Exceções declaráveis |
|---|--:|---|---|
| Warrior especialista (cobre 1 component) | < 80 | Especialização restringe escopo; 80 linhas cobrem Identity + Mission + Lexis/Codex/Kata tables + Behavior + Escalation + 1 Interaction Example | Nenhuma — se passa de 80, vira candidato a split ou enxugamento |
| Warrior router/coordinator | < 60 | Só descreve a regra de delegação | Nenhuma |
| Warrior orquestrador cross-cutting | < 130 (target) ou exceção declarada | Athena tem 189 — protocolo grande é intrínseco | Sim, com nota explícita e link para issue justificando |
| Warrior generalista (single-surface coesa, não-router) | < 130 | Iris (146), Atlas (170), Demeter (150) hoje passam — alvo para enxugar via plan-014 | Sim, declarável |
| Lex declarativa (sem HARD-GATE) | < 80 | Convenção curta; lei + escopo + exemplos | Sim |
| Lex bloqueante (com HARD-GATE) | < 120 | Lei + HARD-GATE + escopo + violation consequences + exemplos + automated validation | Sim |
| Codex de referência | sem budget hard | Manuais detalhados; lazy-load via `paths:` é o controle | — |
| Kata | < 200 | Procedimento step-by-step pode ser longo, mas compacto | Sim |
| Cry | < 40 | Atalho — invoca warrior/kata com pouco contexto | Nenhuma |

### Decisões fechadas

| Decisão | Valor | Por quê |
|---|---|---|
| Frontmatter de Warrior/Lex ganha campo `token_budget` | `token_budget: { category: specialist|router|orchestrator|generalist|declarative|hard_gate, target_lines: N, exception: null|"reason" }` | Declaração explícita = enforcement automático via plan-019 validator |
| Validador (plan-019) ganha módulo `token_budget.py` | Lê frontmatter; conta linhas; falha se exceder sem exceção declarada | Mesmo modelo dos outros módulos |
| `kata-quality-gate` Check 7 (performance budget) | Estende para incluir token budget de artefatos modificados/criados | Performance budget hoje é vago; consolida |
| Aplicação a artefatos existentes | **Gradual** — Lex obriga **novos artefatos**; existentes ganham declaração + ajuste em sub-PRs (plan-014 já cobre os warriors; uma "onda 2" cobre Lex/Kata/Cry) | Evita big-bang refactor |
| HARD-GATE em `lex-token-budget` | Sim | Bloqueia merge de novo warrior/lex sem declaração |
| Codex registra **medições reais** | Tabela com baseline e ganhos por plan, atualizada após cada merge | Mantém o codex vivo, não estático |
| Cross-references aos 11 plans | Cada plan 011-021 ganha link para `codex-token-optimization` na seção de estratégia | Autoatualizável — o codex é o single source |
| Idiomas | 3 (pt-BR canonical + es + en) | `lex-framework-language` |

## Escopo

### Artefatos a criar (3 idiomas, exceto onde marcado)

| Pilar | Caminho relativo | Conteúdo principal |
|---|---|---|
| Codex | `_foundation/quality/codex/codex-token-optimization.md` | Conceito (por que matter); 6 técnicas transversais com exemplo cada; tabela de budgets numéricos; medições reais (atualizadas com cada merge); como medir (referência ao plan-007 + ccusage); pitfalls e anti-patterns |
| Lexis | `_foundation/quality/lexis/lex-token-budget.md` | Lei: todo novo Warrior e toda nova Lex MUST declarar `token_budget` no frontmatter; budget cumprido OU exceção justificada; HARD-GATE; validação automatizada via plan-019 |
| Doc interno | `docs/internal/token-strategy-snapshot.md` (pt-BR-only) | Snapshot atual da estratégia consolidada (cópia da resposta de síntese), atualizada conforme evolui — versionada em git para histórico |

### Atualizações em artefatos existentes

| Arquivo | Mudança |
|---|---|
| `templates/warrior-sample.md` (3 idiomas) | Adicionar campo `token_budget:` no frontmatter com placeholder |
| `templates/lex-sample.md` (3 idiomas) | Idem |
| `templates/kata-sample.md`, `templates/cry-sample.md` (3 idiomas) | Adicionar campo `token_budget:` (opcional para Kata, obrigatório para Cry) |
| `kata-quality-gate.md` (3 idiomas) — Check 7 | Estender para validar `token_budget` declarado em artefatos novos/modificados; falha se ausente ou se conteúdo excede budget sem exceção |
| `kata-create-warrior.md`, `kata-create-lexis.md`, `kata-create-codex.md`, `kata-create-kata.md`, `kata-create-cry.md` (3 idiomas) | Adicionar step "Declarar token_budget no frontmatter" |
| `scripts/_validate/token_budget.py` (novo) | Módulo do plan-019 que verifica frontmatter + linecount; depende de plan-019 mergeado |
| `scripts/validate.py` | Importar e executar o novo módulo |
| `framework/platforms.yaml` | Registrar codex e lex novos |
| **Plans 011-021 (cada arquivo `.claude/plans/plan-{NNN}-*.md`)** | Substituir "estratégia ad-hoc" por link para `codex-token-optimization` com a técnica específica que aplica |

## Fora de escopo

- **Refactor de Lex/Codex/Kata existentes** para caber em budget — adoção gradual; plan-014 cobre warriors; outros pilares ficam para "onda 2" se demanda surgir
- **Token budget para artefatos compilados** (`.cursor/rules/*.mdc`, `.claude/docs/*`) — derivados de `framework/`; budget aplica à fonte canônica
- **Validação de tokens em runtime** (medir cada sessão real) — fora; plan-007 já cobre via PR stamp
- **Auto-shrink** (script que tenta encolher um artefato automaticamente) — humano enxuga; ferramenta apenas detecta
- **Budget para skills externos** (plan-010) — skills têm dinâmica própria; codex menciona como nota mas não obriga
- **Tradução do doc interno** (`docs/internal/token-strategy-snapshot.md`) — pt-BR-only, é decisão interna

## Steps

- [ ] 1. **Confirmar plan-019 mergeado** — `scripts/validate.py` precisa existir para receber o módulo `token_budget.py` (bloqueante)
- [ ] 2. Abrir issue com template `feature-request`, Issue Type `Feature`, label `evolvability ♻️`, título "feat(framework): codify token optimization strategy (codex + lex-token-budget + quality gate integration)"
- [ ] 3. Criar branch `feat/{N}-token-optimization-codification` e worktree
- [ ] 4. Atualizar status deste plan para `in-progress`
- [ ] 5. Redigir `codex-token-optimization.md` em pt-BR — 6 técnicas + tabela de budgets + medições atuais (extrair dos baselines registrados nos plans 013/014/021 quando mergeados; deixar TBD onde ainda não medido)
- [ ] 6. Redigir `lex-token-budget.md` em pt-BR com HARD-GATE
- [ ] 7. Redigir `docs/internal/token-strategy-snapshot.md` (pt-BR-only) consolidando a síntese atual
- [ ] 8. Atualizar `templates/warrior-sample.md` em pt-BR adicionando `token_budget` no frontmatter (com 3 categorias documentadas)
- [ ] 9. Atualizar `templates/lex-sample.md`, `templates/kata-sample.md`, `templates/cry-sample.md` em pt-BR
- [ ] 10. Atualizar `kata-quality-gate.md` Check 7 em pt-BR
- [ ] 11. Atualizar os 5 katas `kata-create-*` em pt-BR adicionando step de declaração
- [ ] 12. Implementar `scripts/_validate/token_budget.py` + tests
- [ ] 13. Atualizar `scripts/validate.py` para importar o novo módulo
- [ ] 14. Atualizar `framework/platforms.yaml`
- [ ] 15. Traduzir codex novo + lex nova + 4 templates atualizados + kata-quality-gate atualizado + 5 katas-create atualizados para `es` e `en`
- [ ] 16. Rodar `python3 scripts/install.py --self --target . --platform claude-code` e `cursor`
- [ ] 17. **Smoke test 1 (warrior dentro do budget)**: criar warrior sandbox com 75 linhas e `token_budget: { category: specialist, target_lines: 80 }`; rodar `validate.py`; zero findings
- [ ] 18. **Smoke test 2 (warrior excedendo)**: criar warrior sandbox com 200 linhas, category specialist, sem exception; verificar `error`
- [ ] 19. **Smoke test 3 (exceção declarada)**: warrior sandbox com 200 linhas, category orchestrator, `exception: "Athena protocol intrínseco — ver issue #X"`; verificar passa com `info`
- [ ] 20. **Smoke test 4 (frontmatter ausente)**: warrior sandbox sem campo `token_budget`; verificar `error`
- [ ] 21. **Smoke test 5 (kata-quality-gate)**: rodar gate em PR sandbox modificando warrior existente — Check 7 estendido detecta budget violado
- [ ] 22. Atualizar **cada plan 011-021** trocando a seção "token strategy" / "estratégia de redução" por bullet point + link para `codex-token-optimization` com a técnica aplicada (commits separados por plan? ou batch? — recomendação: 1 commit `chore(plans): cross-reference codex-token-optimization`)
- [ ] 23. Rodar `kata-artifact-self-review` em codex e lex novos
- [ ] 24. Commits atômicos por artefato; commit dedicado para os 11 plans atualizados
- [ ] 25. Push e abrir PR via `kata-contributing-pr`
- [ ] 26. Após merge: arquivar plan e remover worktree

## Dependências

- **Plan-019 mergeado** — `scripts/validate.py` é prerequisite (bloqueante)
- `lex-hard-gate-pattern` mergeada (já está) — usado pelo `lex-token-budget`
- `templates/*-sample.md` presentes (já estão)
- `kata-quality-gate` mergeada (já está)
- Plan-007 (token cost stamp) **opcional** — se mergeado, o codex pode trazer dados reais; se não, baselines ficam TBD
- Independente de plans 011-018, 020, 021 — pode ser escrito em paralelo. Mas o **valor** do plan vem com plans 011-021 mergeados (medições populam o codex)

## Riscos

- **Budget numérico vira camisa-de-força** que força artefatos a sair piores (super condensados, sem clareza). Mitigação: exceção declarável com justificativa (não é bypass mas é válvula de escape); auditoria manual em PRs onde exceção é invocada
- **Frontmatter `token_budget` vira lixo declarado** ("category: specialist, target_lines: 80" copy-paste). Mitigação: `kata-create-*` tem step explícito; `kata-artifact-self-review` checklist inclui revisão de declaração
- **Adoção gradual leva a estado misto** (alguns artefatos com budget, outros sem). Mitigação: Lex aplica a **novos** artefatos; existentes ganham declaração via "onda 2" sem urgência
- **Codex fica desatualizado** com medições reais. Mitigação: regra explícita no codex "atualizar tabela de medições a cada merge de plan que mediu" — vira ritual leve
- **Cross-reference em 11 plans gera diff grande** num único PR. Mitigação: commit dedicado e isolado para os 11 plans (`chore(plans): cross-reference codex-token-optimization`); review fica simples
- **Conflito com plan-014 (audit warriors)** que também toca warriors com budget. Mitigação: plan-014 já mergeado é prerequisite implícito; este plan **valida** o que aquele entregou
- **`token_budget` no frontmatter conflita com convenções de outras ferramentas** (Cursor MCP frontmatter, Claude Code skills frontmatter). Mitigação: campo é namespace-friendly (`token_budget`); install.py não toca; smoke test step 16 confirma derivados `.cursor/.claude/` continuam válidos

## Verificação

1. `codex-token-optimization` × 3 idiomas + `lex-token-budget` × 3 idiomas + `docs/internal/token-strategy-snapshot.md` (pt-BR) = 7 arquivos novos
2. HARD-GATE em `lex-token-budget` × 3 idiomas
3. 4 templates atualizados × 3 idiomas
4. `kata-quality-gate` Check 7 × 3 idiomas estendido
5. 5 katas `kata-create-*` × 3 idiomas atualizados
6. `scripts/_validate/token_budget.py` + tests
7. `framework/platforms.yaml` lista codex e lex novos
8. 5 smoke tests passam (dentro budget, excedendo, exceção, frontmatter ausente, quality gate integration)
9. **11 plans (011-021) com cross-reference** ao novo codex em commit dedicado
10. **Sem alteração** em: lex-pr-quality, lex-issue-driven, kata-contributing-pr, demais Lexis/Codex
11. PR final passa HARD-GATE de `lex-pr-quality` (incluindo o novo critério se plan-020 mergeado)
12. Performance do `validate.py` continua < 10s mesmo com novo módulo
