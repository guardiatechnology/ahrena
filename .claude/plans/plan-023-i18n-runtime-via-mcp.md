---
plan_id: "023"
title: "i18n-runtime-via-mcp"
status: pending
agent: claude
issue: "TBD (a abrir antes da branch — lex-issue-first)"
created_at: "2026-05-07T23:30:00Z"
updated_at: "2026-05-07T23:30:00Z"
---

# Plano: i18n em runtime via Ahrena MCP — tradução parametrizada com cache, em vez de 3 árvores no disco

## Objetivo

Reduzir o custo de armazenamento e manutenção de traduções tratando idiomas como **parâmetro de runtime** servido pelo Ahrena MCP server (plan-021). Hoje cada Lex/Codex/Warrior/Cry vive em 3 cópias estruturalmente equivalentes (`framework/{pt-BR,es,en}/...`), gerando 3× peso, 3× cold-start, e 3× propagação a cada mudança. Estratégia: manter pt-BR (ou `language.default`) como **única fonte canônica em disco**; demais idiomas servidos sob demanda por tool MCP que traduz via LLM com cache filesystem keyed por hash do source. Adoção opt-in via diretiva. Coexistência com árvores estáticas durante a transição.

## Contexto

### Custo atual da estratégia "3 árvores"

| Métrica | Hoje | Com runtime i18n |
|---|--:|--:|
| Tamanho do `framework/` | 3× canonical | 1× canonical + cache (~0.3× efetivo se cache poda) |
| Cold-start (clone + sync) | 3× IO | 1× IO |
| Propagação por mudança | 3× edits + revisão tradutor | 1× edit + invalidação automática do cache |
| Token cost por sessão | Carrega só a língua usada (já otimo) | Idem (sem regressão) |
| Lock-in de tradução manual | Tradutor humano por idioma | LLM + revisão amostral |
| Quality control de tradução | Revisão humana 100% | Revisão amostral + smoke test |

A maior dor não é runtime — é manutenção. Toda mudança hoje requer atualizar 3 árvores (frequentemente esquecida em es/en, gerando drift detectado por plan-019).

### Como funciona em runtime

```
Cliente MCP (Cursor, Claude Code, Strands)
   │
   │ tools/call: ahrena_query_lex(name="lex-idempotency", lang="es")
   ▼
Ahrena MCP server (plan-021)
   │
   ├─ Cache hit (.ahrena/cache/i18n/{hash}/es.md)?
   │       └─ retorna direto
   │
   ├─ Cache miss
   │       ├─ Lê fonte canonical (framework/pt-BR/.../lex-idempotency.md)
   │       ├─ Computa hash do conteúdo + frontmatter
   │       ├─ Chama LLM provider configurado (default: Anthropic)
   │       │   com prompt baseado em codex-language-{es} + lex-language-{es}
   │       │   (regras de tradução já existentes!)
   │       ├─ Persiste em .ahrena/cache/i18n/{hash}/es.md
   │       └─ Retorna
   │
   └─ Source mudou? Hash diferente do cacheado → invalida cache antigo
```

### Decisões fechadas

| Decisão | Valor | Por quê |
|---|---|---|
| Adoção | Opt-in via `i18n.runtime.enabled: true` em `.directives` | Requer LLM key + cache budget; default `false` para zero impacto |
| Coexistência com árvores estáticas | Sim, durante transição | Phase 1: runtime é "preview" complementar; Phase 2 (plan futuro): árvores estáticas viram opt-in inverso |
| Idioma canonical | `language.default` (hoje pt-BR) | Continuidade |
| Cache backend | Filesystem (`.ahrena/cache/i18n/{path-hash}/{lang}.md`) na primeira iteração; DB ou Redis em iteração futura | Filesystem é suficiente em dev e CI; DB se virar produção |
| Cache key | SHA256 do (canonical_content + canonical_frontmatter) | Mudança no source → invalidação automática |
| Provider LLM | Configurável; default = Anthropic Claude (mesmo da sessão atual via MCP) | Reusa key existente; sem nova credencial |
| Budget de tradução | Custo declarado em `i18n.runtime.budget_usd_monthly` (alarme se excede) | Visibilidade de gasto |
| Quality control | (a) Smoke test step compara tradução runtime vs versão estática existente; (b) review amostral mensal de 5 traduções runtime via tool `ahrena_review_translation` | Confiança gradual |
| Validador (plan-019) | Novo módulo: quando `i18n.runtime.enabled: true`, warns para artefatos com tradução manual divergindo do cache (drift) | Detecta divergência; humano decide qual é canônica |
| HARD-GATE | Não — adoção opcional, sem bloqueio | Nenhum projeto deve ser forçado a mudar |
| Rollback | Trivial — desativa diretiva; árvores estáticas continuam |  |
| Pre-warm cache em CI | Opcional — task `make i18n-warm` que pré-traduz conteúdo recém-modificado e commita o cache |  |

### Quem se beneficia mais

| Cenário | Ganho |
|---|---|
| Repositório novo adotando Ahrena | Clone 1/3 do tamanho |
| Mudança em Lex que requer 3 traduções | 1 edit + cache rebuild on-query (~5s + LLM cost) vs 3 edits manuais + tradução humana |
| Adicionar 4º idioma (e.g., fr) | Zero edits no source; instantâneo no MCP query |
| Sessão Claude Code padrão (uma língua usada) | Igual ao atual (sem ganho de runtime, mas sem regressão) |

## Escopo

### Artefatos a criar (3 idiomas onde aplicável)

| Pilar | Caminho relativo | Conteúdo principal |
|---|---|---|
| Codex | `_foundation/i18n/codex/codex-i18n-runtime.md` (3 idiomas) | Conceito; arquitetura (canonical + cache + LLM); diretiva `i18n.runtime`; tools MCP envolvidas (`ahrena_query_lex`, `ahrena_query_codex`, `ahrena_warm_cache`, `ahrena_review_translation`); pre-warm flow; limitações; quando NÃO usar (ex: ambientes air-gapped) |
| Cry | `_foundation/i18n/cries/cry-i18n-warm.md` (3 idiomas) | Atalho para invocar `ahrena_warm_cache` recursivamente sobre `framework/{language.default}/...`; commit do cache opcionalmente |
| Tools (extensão de plan-021) | Em `tools/ahrena-mcp/src/ahrena_mcp/tools/` | `query_lex.py` e `query_codex.py` ganham parâmetro `lang`; novo `warm_cache.py`; novo `review_translation.py` (lista X traduções runtime aleatórias com side-by-side ao canonical) |

### Atualizações em artefatos existentes (3 idiomas)

| Arquivo | Mudança |
|---|---|
| `_foundation/i18n/lexis/lex-framework-language.md` | Acrescentar exceção: "Quando `i18n.runtime.enabled: true`, requirement 'Mandatory completeness' (rule 2) é satisfeito por (a) árvores estáticas para línguas declaradas em `language.i18n.static`, OU (b) servidor MCP runtime-translating para línguas em `language.i18n.runtime`. Se a língua aparece em ambos, static prevalece" |
| `_foundation/i18n/codex/codex-language*.md` (4 arquivos) | Acrescentar nota: "Estas regras alimentam o prompt de tradução LLM em runtime quando `i18n.runtime.enabled: true`" |
| `framework/.directives.sample` | Adicionar bloco comentado:<br>`# i18n:`<br>`#   runtime:`<br>`#     enabled: false`<br>`#     provider: anthropic`<br>`#     cache_dir: .ahrena/cache/i18n`<br>`#     budget_usd_monthly: 5`<br>`#   languages:`<br>`#     static: [pt-BR, es, en]   # mantém árvores estáticas`<br>`#     runtime: []                # quando enabled, lista linguas server-side` |
| `scripts/_validate/translation_drift.py` (novo, dependa do validate.py do plan-019) | Quando runtime ON: compara tradução runtime vs estática; emite warning se divergem |
| `scripts/validate.py` | Importa o novo módulo |
| `framework/platforms.yaml` | Registrar codex e cry novos |

## Fora de escopo

- **Remover árvores estáticas** (`framework/es/`, `framework/en/`) — phase 2 em plan futuro depois de validação real do runtime
- **Editor que escreve diretamente em runtime** — fonte canônica em disco continua sendo a verdade; runtime só serve traduções
- **Tradução para idiomas com baixo recurso LLM** (e.g., dialetos minoritários) — codex documenta limitação; recomendação é manter estático para esses
- **Auto-publicação no MkDocs** das traduções runtime — site ainda renderiza só árvores estáticas; iteração futura pode pré-gerar a partir do cache
- **Versionamento de traduções runtime** — cache invalidate-and-regenerate; sem histórico
- **Validação semântica da tradução** (i.e., LLM verifica que tradução preserva significado) — fora; smoke test compara estrutural (mesmas seções, mesmos blocos de código preservados)

## Steps

- [ ] 1. **Confirmar plan-021 mergeado** — Ahrena MCP server precisa existir (bloqueante)
- [ ] 2. **Confirmar plan-019 mergeado** — `validate.py` para receber novo módulo
- [ ] 3. Abrir issue com template `feature-request`, Issue Type `Feature`, label `evolvability ♻️`
- [ ] 4. Criar branch `feat/{N}-i18n-runtime-via-mcp` e worktree
- [ ] 5. Atualizar status deste plan para `in-progress`
- [ ] 6. **Spike de viabilidade**: rodar manualmente um prompt de tradução com claude-haiku-4-5 sobre `framework/pt-BR/.../lex-idempotency.md` para `es`; comparar com `framework/es/.../lex-idempotency.md`; medir tokens consumidos; medir tempo; aceitar/rejeitar abordagem antes de seguir
- [ ] 7. Implementar `query_lex.py` e `query_codex.py` extension em `tools/ahrena-mcp/`: adicionar parâmetro `lang`; quando `lang != canonical`, lookup em cache; quando miss, traduzir via LLM provider configurado
- [ ] 8. Implementar `warm_cache.py`: tool MCP que itera sobre `framework/{canonical}/...` e pré-traduz para todas as línguas em `i18n.languages.runtime`
- [ ] 9. Implementar `review_translation.py`: amostragem aleatória; mostra side-by-side canonical vs runtime; usado para quality control mensal
- [ ] 10. Implementar `scripts/_validate/translation_drift.py`: compara cache runtime vs árvores estáticas quando ambas existem
- [ ] 11. Atualizar `scripts/validate.py` para importar o novo módulo
- [ ] 12. Redigir `codex-i18n-runtime.md` em pt-BR (canonical)
- [ ] 13. Redigir `cry-i18n-warm.md` em pt-BR
- [ ] 14. Atualizar `lex-framework-language.md` em pt-BR (exceção runtime)
- [ ] 15. Atualizar 4 codex `codex-language*.md` em pt-BR (nota sobre uso em prompt LLM)
- [ ] 16. Adicionar bloco `i18n.runtime` em `framework/.directives.sample`
- [ ] 17. Atualizar `framework/platforms.yaml`
- [ ] 18. Traduzir codex novo + cry novo + atualizações para `es` e `en` (fila estática — esta plan-023 ainda usa o caminho legado para ela mesma)
- [ ] 19. Rodar `python3 scripts/install.py --self --target . --platform claude-code` e `cursor`
- [ ] 20. **Smoke test 1 (cache miss → tradução)**: ativar `i18n.runtime.enabled: true` em sandbox; chamar `ahrena_query_lex(name="lex-idempotency", lang="fr")`; verificar tradução gerada e cacheada em `.ahrena/cache/i18n/...`
- [ ] 21. **Smoke test 2 (cache hit)**: rechamar mesma query; verificar < 50ms (cache hit); verificar mesmo conteúdo
- [ ] 22. **Smoke test 3 (invalidação)**: alterar fonte canonical; rechamar; verificar que cache foi invalidado e nova tradução gerada
- [ ] 23. **Smoke test 4 (validate.py drift)**: ativar runtime; manter `framework/es/lex-idempotency.md` divergindo do cache; rodar `validate.py`; verificar warning de drift
- [ ] 24. **Smoke test 5 (review_translation)**: chamar tool `ahrena_review_translation(samples=3, lang="es")`; verificar side-by-side; humano valida qualidade
- [ ] 25. **Smoke test 6 (budget)**: simular consumo > `budget_usd_monthly`; verificar alarme
- [ ] 26. Rodar `kata-artifact-self-review` em codex e cry novos
- [ ] 27. Commits atômicos; push; abrir PR via `kata-contributing-pr`
- [ ] 28. Após merge: arquivar plan e remover worktree

## Dependências

- **Plan-021 mergeado** — Ahrena MCP server (bloqueante)
- **Plan-019 mergeado** — `scripts/validate.py` (bloqueante)
- LLM provider key (Anthropic) acessível via env var
- `lex-mcp` mergeado (já está)
- **Independente** de plans 011-018, 020, 022
- **Sinérgico** com plan-022 (token-optimization-codification) — runtime i18n é uma das técnicas que o codex pode listar em iteração futura quando provada

## Riscos

- **Qualidade de tradução LLM inferior à humana.** Mitigação: spike step 6 valida amostra; review amostral mensal (step 24); humano pode "fixar" tradução em árvore estática que prevalece sobre runtime; se qualidade insuficiente, plan rollback é trivial
- **Custo LLM extrapola budget.** Mitigação: budget declarado e alarmado; cache agressivo (TTL infinito até source mudar); pre-warm em CI evita queries ad-hoc; smoke test step 25 valida alarme
- **Cache poluído com tradução ruim** que volta para múltiplas sessões. Mitigação: tool `ahrena_invalidate_translation(name, lang)` documentada; código simples para purgar `.ahrena/cache/i18n/{hash}/{lang}.md`
- **LLM provider mudar API.** Mitigação: provider configurável; wrapper isola; pin de versão do SDK
- **Runtime i18n e árvores estáticas saem de sync.** Mitigação: `validate.py` drift detector emite warning; codex documenta política (estática prevalece quando ambos presentes)
- **Air-gapped environments** não podem chamar LLM. Mitigação: codex documenta limitação; default `enabled: false` cobre esses casos automaticamente
- **Tradução em runtime atrasa primeira sessão**. Mitigação: pre-warm via `make i18n-warm` em CI ou em script de bootstrap; primeira query miss leva ~5s, depois cache hit é < 50ms
- **Provider Anthropic processando conteúdo do framework levanta concerns de privacidade**. Mitigação: framework é open source; conteúdo não é sensível; codex documenta a observação para projetos com requisitos específicos (alternativa: provider local via Ollama configurável)

## Verificação

1. `codex-i18n-runtime` × 3 idiomas + `cry-i18n-warm` × 3 idiomas = 6 arquivos novos (last batch produzida via tradução estática manual — runtime documenta a si mesma)
2. `tools/ahrena-mcp/src/ahrena_mcp/tools/` ganha 4 tools novas/estendidas
3. `lex-framework-language` × 3 idiomas com exceção runtime
4. 4 codex `codex-language*` × 3 idiomas atualizados
5. `framework/.directives.sample` tem bloco `i18n.runtime`
6. `scripts/_validate/translation_drift.py` + tests
7. 6 smoke tests passam (miss, hit, invalidação, drift, review, budget)
8. Default `i18n.runtime.enabled: false` — projetos sem opt-in têm zero impacto (regressão zero)
9. **Sem alteração** em árvores estáticas existentes (`framework/{pt-BR,es,en}/...`) — coexistência preservada
10. PR final passa HARD-GATE de `lex-pr-quality`; carrega stamp de custo se plan-007 mergeado
