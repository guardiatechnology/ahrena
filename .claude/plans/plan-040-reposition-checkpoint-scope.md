---
plan_id: "040"
title: "reposition-checkpoint-scope"
status: in-progress
agent: claude
issue: "guardiatechnology/ahrena#73"
created_at: "2026-05-09T00:00:00Z"
updated_at: "2026-05-10T01:50:00Z"
---

# Plano: Reposicionar `.checkpoint` para o que `lex-agent-planning` não cobre

## Objetivo

Reescrever `lex-checkpoint` para eliminar sobreposição com `lex-agent-planning` e devolver propósito real ao `.checkpoint`. Hoje a Lex obriga ler/salvar `.checkpoint` em toda sessão com schema redundante (Activity, Progress com `[x]`, Decisions made, Next steps, Artifacts produced) — exatamente o que o plano em `.claude/plans/plan-NNN-{slug}.md` já carrega, e **com vantagem de ser commitado**. Resultado: ecossistema não consome `.checkpoint`; Lex virou letra morta. Reposicionar para o que plano não cobre — **scratchpad pré-plano**, **contexto entre conversas longas que não se materializa em plano único**, **hand-off rápido entre sessões** — com schema enxuto e gatilhos claros.

## Contexto

### Sintomas de que `.checkpoint` não funciona hoje

1. **Sobreposição com plano:** `lex-agent-planning` (Lex) obriga plano para qualquer task multi-step com Steps `[x]`, Decisões fechadas, Riscos, status lifecycle (`pending → in-progress → done`). `lex-checkpoint` repete Activity, Status, Progress, Decisions made, Next steps. Dois artefatos para a mesma coisa.
2. **Plano vence em durabilidade:** plano é committed alongside the work (`lex-agent-planning` rule); `.checkpoint` é gitignored (`lex-checkpoint` rule 4). Quem persiste estado canônico é o plano.
3. **Sem ecossistema:** não há `kata-checkpoint-read`/`save`, nenhum warrior tem hook explícito para `.checkpoint`, nenhum cry o invoca. Lex existe; ninguém executa.
4. **Referências espalhadas mas inertes:** vários katas/codex/warriors mencionam `.checkpoint` como obrigação genérica sem amarrar em ação concreta. Boilerplate documental.
5. **Plan-026 (commit-readiness-observer) já tinha que se virar:** a versão atual lê `.checkpoint > Artifacts produced` como scope hint, mas isso só funciona se alguém escrever lá — e ninguém escreve.

### Reposicionamento proposto

`.checkpoint` cobre **apenas** o que plano não cobre:

| Cenário | Plano cobre? | `.checkpoint` cobre? |
|---|:---:|:---:|
| Task multi-step formal (Lexis/Codex/Kata/feature) | ✅ | ❌ |
| Pré-plano: usuário e agente exploram problema, sem plano ainda existir | ❌ | ✅ |
| Múltiplos planos ativos na sessão (hand-off entre eles) | ❌ | ✅ |
| Conversa longa com decisões transversais que não cabem em 1 plano | ❌ | ✅ |
| Resumir contexto para retomar conversa amanhã sem reler tudo | ❌ | ✅ |
| Anotação rápida durante sessão exploratória ("voltar a isso depois") | ❌ | ✅ |
| Status, decisões, steps, artifacts de uma task | ✅ | ❌ |

`.checkpoint` deixa de duplicar o plano — vira scratchpad de **sessão**, não de **task**.

### Decisões fechadas

| Decisão | Valor | Por quê |
|---|---|---|
| Schema enxuto | 4 seções: `Session focus`, `Open threads`, `Active plans`, `Notes` | Cada seção cobre uma necessidade não-coberta pelo plano |
| Activity/Status/Progress/Decisions made/Next steps removidos | Sim | Sobreposição direta com `lex-agent-planning`; plano é a fonte de verdade |
| `Artifacts produced` removido | Sim | git diff + plano `## Steps` cobrem; observer (plan-026) passa a usar `git diff --name-only` filtrado por timestamp da sessão |
| Gatilho de leitura | Início de sessão (mantido) | Continua útil para retomar contexto rápido |
| Gatilho de escrita | **Sob demanda** + fim de sessão (não automático após cada activity) | Reduz overhead; usuário decide quando vale a pena |
| Preferência automatic/manual | Removida | Sem activity-level granularity, a pergunta perde sentido; default é "salvar ao fim da sessão se houver mudança" |
| Plan ↔ checkpoint relação | `Active plans` lista plan-IDs ativos com 1 linha de contexto cada | Permite hand-off entre planos; não duplica conteúdo do plano |
| Backward compat | `kata-checkpoint-read` detecta schema antigo, emite warning ("schema antigo detectado; será reinicializado na próxima gravação"), prossegue sem parsear; próxima invocação de `kata-checkpoint-save` sobrescreve com schema novo | `.checkpoint` é gitignored e per-machine; não há frota compartilhada que justifique migration tool dedicada; `rm .checkpoint` é alternativa válida para o usuário |
| Ecossistema mínimo | `kata-checkpoint-read` (start session) + `kata-checkpoint-save` (sob demanda + fim) + `cry-checkpoint` (atalho usuário) | Sem isso, mesmo a versão reposicionada vira letra morta |
| Plan-026 integration | Observer deixa de depender de `.checkpoint`; usa `git diff --name-only --diff-filter=AM` + mtime para inferir scope da sessão | `.checkpoint` vira opcional, não fonte de scope |
| Idiomas | 3 (pt-BR canonical + es + en) per `lex-framework-language` | Padrão do framework |
| `.checkpoint` continua gitignored | Sim | É per-machine, per-session; commitar viria com noise |

### Schema reposicionado (proposta)

```markdown
# Session checkpoint

- **Last update:** YYYY-MM-DDTHH:MM:SSZ
- **Session id:** {chat/session id ou commit short SHA do HEAD}

## Session focus

{1-3 frases: qual o foco geral desta janela de trabalho. Ex: "explorando reposicionamento do `.checkpoint` em paralelo com revisão de plan-026". Não é Activity formal — é o ponteiro mental.}

## Active plans

- `plan-026` — commit-readiness-observer; aguardando confirmação do usuário sobre escopo do `.checkpoint`
- `plan-040` — reposicionamento do `.checkpoint`; em redação

## Open threads

{Threads de conversa que não viraram plano formal mas não devem ser esquecidas. Cada uma 1-2 linhas.}

- Avaliar se `lex-agent-planning` deveria absorver `Risks` da sessão como categoria não-bloqueante
- Decisão pendente: se `cry-checkpoint-migrate` é one-shot (deletar após uso) ou permanente

## Notes

{Texto livre. Pensamentos, links, referências, snippets que ajudam a retomar amanhã. Sem schema obrigatório.}
```

Tudo o mais (Activity, Status, Progress, Decisions made, Next steps, Artifacts produced) sai — vive no plano.

## Escopo

### Artefatos a reescrever (3 idiomas)

| Caminho | Mudança |
|---|---|
| `framework/{lang}/_foundation/process/lexis/lex-checkpoint.md` | Reescrita completa: novo schema, novos gatilhos, deprecation note do schema antigo, referência cruzada para `lex-agent-planning` (delineação clara do que vai onde) |
| `framework/{lang}/_foundation/process/codex/codex-checkpoint.md` (novo) | Codex novo: explica reposicionamento; uso típico (scratchpad pré-plano, hand-off multi-plano, retomar amanhã); diferenças do schema antigo; troubleshooting |

### Artefatos a criar (3 idiomas)

| Caminho | Conteúdo |
|---|---|
| `framework/{lang}/_foundation/process/katas/kata-checkpoint-read.md` | Procedimento: localizar `.checkpoint`; detectar schema (novo vs antigo); se novo, parsear e apresentar resumo (Session focus + Active plans + Open threads), perguntar resume/start-new; se antigo, emitir warning de deprecation e prosseguir como se não houvesse checkpoint |
| `framework/{lang}/_foundation/process/katas/kata-checkpoint-save.md` | Procedimento: coletar Session focus, Active plans (plan-NNN ativos com 1-line context), Open threads, Notes do contexto da sessão; gravar `.checkpoint`; respeita schema novo (sobrescreve qualquer schema antigo silenciosamente) |
| `framework/{lang}/_foundation/process/cries/cry-checkpoint.md` | Atalho usuário → invoca `kata-checkpoint-save` sob demanda |

### Atualizações em artefatos existentes (3 idiomas)

| Arquivo | Mudança |
|---|---|
| `lex-agent-planning.md` | Adicionar seção "Relação com `.checkpoint`": delineação clara — plano = task; checkpoint = sessão. Sem sobreposição |
| `codex-agent-planning.md` | Idem (reflexo) |
| `kata-plan-task.md` | Acrescentar nota: "ao iniciar plano, opcional registrar plan-id em `.checkpoint > Active plans` via `cry-checkpoint`" |
| `codex-pilars.md`, `codex-katas.md`, `codex-platforms.md`, `codex-issue-workflow.md` | Remover ou reescrever menções genéricas a `.checkpoint` que assumiam o schema antigo |
| `kata-quality-gate.md`, `kata-pr-prepare.md`, `kata-issue-analysis.md`, `kata-requirements-brief.md`, `kata-architecture-brief.md`, `kata-security-review.md`, `kata-test-plan-design.md` | Auditar referências a checkpoint; remover obrigação de check, deixar opcional para retomar contexto longo |
| `lex-issue-driven.md` | Remover obrigação de checkpoint entre fases; já há checkpoint próprio do flow em `.ahrena/workflow/issue-{n}/checkpoint.md` (artefato distinto, fora do escopo desta mudança) |
| `warrior-athena.md` | Remover gancho de checkpoint genérico; manter só o checkpoint específico do Issue-Driven flow |
| `lex-feature-design-docs.md` | Auditar referência a checkpoint; remover se for boilerplate antigo |
| `framework/platforms.yaml` | Registrar codex novo + 2 katas + 2 cries; remover entradas obsoletas se houver |
| `README.md` (3 idiomas) | Atualizar menção a `.checkpoint` se mencionar schema antigo |

### Atualização em plan-026 (PR ainda não aberto)

| Arquivo | Mudança |
|---|---|
| `.claude/plans/plan-026-commit-readiness-observer.md` | Substituir leitura de `.checkpoint > Artifacts produced` por `git diff --name-only --diff-filter=AM` filtrado por mtime da sessão; cache nativo de tooling continua igual; nota: `.checkpoint > Active plans` opcional para amarrar com plan alignment do sinal #6 |

## Fora de escopo

- **Migrar histórico** de `.checkpoint` antigos em projetos clientes — `cry-checkpoint-migrate` resolve sob demanda; não há pipeline batch
- **Schema do checkpoint do Issue-Driven flow** (`.ahrena/workflow/issue-{n}/checkpoint.md`) — é artefato distinto, governado por `lex-issue-driven`; não muda nesta reformulação
- **Eliminar `lex-checkpoint` por completo** — opção 1 da pergunta original; não é essa direção
- **Hooks automáticos de Claude Code/Cursor** que escrevem `.checkpoint` sem intervenção — fora do escopo inicial; codex documenta como evolução possível
- **Sincronização multi-máquina** de `.checkpoint` — fora; permanece per-machine

## Steps

- [x] 1. Abrir issue com template `feature-request`, Issue Type `Feature`, label `evolvability ♻️` + `documentation 📃` — **issue #73**
- [x] 2. Criar branch `feat/73-reposition-checkpoint-scope` e worktree
- [x] 3. Atualizar status deste plan para `in-progress`
- [x] 4. Reescrever `lex-checkpoint.md` em pt-BR com schema novo + gatilhos novos + deprecation note
- [x] 5. Redigir `codex-checkpoint.md` em pt-BR
- [x] 6. Redigir `kata-checkpoint-read.md` em pt-BR
- [x] 7. Redigir `kata-checkpoint-save.md` em pt-BR
- [x] 8. Redigir `cry-checkpoint.md` em pt-BR
- [x] 9. Atualizar `lex-agent-planning.md` + `codex-agent-planning.md` + `kata-plan-task.md` em pt-BR (delineação plano vs checkpoint)
- [x] 10. Auditar e atualizar referências em pt-BR: `codex-pilars`, `codex-katas`, `codex-platforms`, `codex-issue-workflow`, katas e warriors do flow Issue-Driven, `lex-feature-design-docs`, `README` — **conclusão: todas as menções remanescentes a "checkpoint" referem-se a `.ahrena/workflow/issue-{n}/checkpoint.md` (handoff do Issue-Driven flow, governado por `lex-issue-driven`), artefato distinto de `.checkpoint` (raiz do workspace). Nenhuma edição adicional necessária em pt-BR.**
- [ ] 11. Atualizar `framework/platforms.yaml` com novos artefatos
- [ ] 12. Atualizar `.claude/plans/plan-026-commit-readiness-observer.md` substituindo dependência de `.checkpoint > Artifacts produced` por `git diff` + mtime
- [ ] 13. Traduzir todos os artefatos novos e atualizados para `es` e `en`
- [ ] 14. Rodar `python3 scripts/install.py --self --target . --platform claude-code` e `cursor`
- [ ] 15. **Smoke test 1 (read schema novo)**: criar `.checkpoint` no schema novo; invocar `kata-checkpoint-read`; verificar resumo apresentado e prompt resume/start-new
- [ ] 16. **Smoke test 2 (save schema novo)**: invocar `cry-checkpoint`; verificar gravação respeitando schema novo (4 seções)
- [ ] 17. **Smoke test 3 (read schema antigo emite warning)**: criar `.checkpoint` no schema antigo; invocar `kata-checkpoint-read`; verificar warning emitido (sem parsear conteúdo) e fluxo prossegue como se não houvesse checkpoint; próximo `kata-checkpoint-save` sobrescreve com schema novo
- [ ] 18. **Smoke test 4 (read sem checkpoint)**: workspace sem `.checkpoint`; `kata-checkpoint-read` retorna "nenhum" e prossegue silenciosamente
- [ ] 19. **Smoke test 5 (delineação plano vs checkpoint)**: sessão exploratória sem plano → vira Open threads; quando plano é criado, plan-id entra em Active plans; checkpoint não duplica steps do plano
- [ ] 20. **Smoke test 6 (plan-026 sem dependência de `.checkpoint`)**: rodar observer com `.checkpoint` ausente; verificar que continua funcionando (cache miss completo, sem regressão); rodar com `.checkpoint > Active plans` populado; verificar que sinal #6 (plan alignment) consome essa hint corretamente
- [ ] 21. Rodar `kata-artifact-self-review` em todos os artefatos novos e reescritos
- [ ] 22. Commits atômicos por componente (1 commit Lex, 1 commit codex, 1 por kata, 1 por cry, 1 por updates de delineação, 1 por traduções)
- [ ] 23. Push e abrir PR via `kata-contributing-pr`
- [ ] 24. Após merge: arquivar plan-040 e remover worktree

## Dependências

- **Plan-026** ainda não mergeado: este plan-040 atualiza o plan-026 antes do PR; coordenar ordem (ou plan-040 sai primeiro, plan-026 já nasce com novo design; ou plan-026 sai primeiro com `.checkpoint` antigo e plan-040 ajusta depois). Preferência: **plan-040 primeiro**, plan-026 nasce coerente
- `lex-agent-planning`, `lex-framework-language`, `lex-template-usage`, `lex-platforms-rules` mergeados (já estão)
- Não depende de plans 011-018, 020-025, 027-039

## Riscos

- **Quebra de projetos clientes** que tinham `.checkpoint` no schema antigo. Mitigação: `kata-checkpoint-read` detecta schema antigo, emite warning de deprecation e prossegue como se não houvesse checkpoint; próxima invocação de save sobrescreve com schema novo. `.checkpoint` é gitignored e per-machine — não há frota compartilhada com risco real de perda de dados; quem quiser começar limpo: `rm .checkpoint`
- **Reposicionamento ainda não materializa ecossistema** se `kata-checkpoint-read/save` não forem invocados por warriors ou cries de outros flows. Mitigação: este plano cria explicitamente os katas + cries; warriors do Issue-Driven flow têm seus próprios checkpoints (independentes); para outros, usuário invoca via `cry-checkpoint` quando vale
- **Active plans pode duplicar info do plano** se mal implementado. Mitigação: schema obriga 1-linha por plan-id (não copia steps); kata-checkpoint-save valida ≤ 80 chars por entrada
- **Open threads vira lixeira de TODOs**. Mitigação: codex documenta como **temporário de sessão**, não TODO list permanente; sessão fechada → revisar e ou virar plano ou descartar
- **Sobreposição residual com `.ahrena/workflow/issue-{n}/checkpoint.md`** (Issue-Driven flow). Mitigação: codex deixa explícito que são artefatos distintos com escopos distintos; nomes diferentes mitigam confusão
- **Esforço de tradução** (3 idiomas × ~12 arquivos) é significativo. Mitigação: mesmo esforço de qualquer mudança de Lex; sem novidade
- **Lex perdendo força** se virar opcional demais. Mitigação: Lex continua obrigatória nos gatilhos novos (read no início, save sob demanda + fim com mudança); o que é opcional é o conteúdo (Open threads pode ser vazio), não o ritual

## Verificação

1. `lex-checkpoint` × 3 idiomas reescrita; schema novo documentado; deprecation note do schema antigo presente
2. `codex-checkpoint` × 3 idiomas novo; cobre uso típico, diferenças, troubleshooting
3. `kata-checkpoint-read`, `kata-checkpoint-save`, `cry-checkpoint` × 3 idiomas
4. `lex-agent-planning`, `codex-agent-planning`, `kata-plan-task` × 3 idiomas com seção "Relação com `.checkpoint`" delimitando plano vs checkpoint
5. Auditoria: 0 referências a schema antigo (`Activity`, `Progress` com `[x]`, `Decisions made`, `Next steps`, `Artifacts produced`) em katas, codex, warriors fora de `lex-checkpoint` (que é a deprecation note)
6. `framework/platforms.yaml` lista novos artefatos
7. plan-026 atualizado: zero dependência hard de `.checkpoint > Artifacts produced`; `.checkpoint > Active plans` é dica opcional, não fonte de scope
8. **6 smoke tests passam** (steps 16-21)
9. **Sem regressão:** projeto que adota o framework e nunca usa `.checkpoint` continua funcionando exatamente como antes (Lex obriga ler, mas ler "não existe" é cenário válido coberto por rule 1.4 da Lex original)
10. PR final passa HARD-GATE de `lex-pr-quality`; passa `lex-issue-quality` (issue Why/What/How preenchido)
