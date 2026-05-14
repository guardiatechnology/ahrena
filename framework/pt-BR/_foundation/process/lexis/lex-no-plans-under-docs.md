# Lexis: Planos Não Vivem em `docs/`

> **Prefixo:** `lex-` | **Tipo:** Lei Inquebrável | **Escopo:** Caminhos canônicos para arquivos de plano (`plan-*.md`) em projetos Ahrena

## Propósito

O diretório `docs/` é reservado para artefatos canônicos de documentação: fases do fluxo Issue-Driven (`docs/issues/issue-{N}/`), feature design docs (`docs/{context}/{entities,oas,events,agents,metrics}/`), ADRs (`docs/adr/`) e runbooks (`docs/runbooks/`).

Planos de execução (`plan-*.md`) seguem o modelo hierárquico Issue → Plan → PR descrito em `lex-agent-planning`: o corpo da sub-issue Plan no GitHub é a fonte de verdade canônica; provider caches locais (`.claude/plans/` ou `.cursor/plans/`) materializam o conteúdo durante a sessão e são gitignored.

Misturar planos sob `docs/` quebra essa separação: confunde a navegação do projeto, polui artefatos de fase com estado operacional, e abre porta para múltiplas fontes de verdade não sincronizadas. Violação observada em consumidores downstream do Ahrena: arquivos do tipo `docs/skills/{slug}/plans/plan-{M}-{slug}.md` materializados ao lado de specs.

## Lei

> **Materializar arquivos de plano (`plan-*.md`) sob `docs/`, sob qualquer caminho que combine `docs/` com `plans/` como segmentos do path, ou em qualquer subdiretório de `docs/` é FORBIDDEN. Os caminhos canônicos para planos são exatamente três: (a) `.claude/plans/plan-{M}-{slug}.md` (provider cache Claude Code, gitignored); (b) `.cursor/plans/plan-{M}-{slug}.md` (provider cache Cursor, gitignored); (c) corpo da sub-issue Plan no GitHub (canônico, committed via API GitHub). Nenhum outro caminho é válido.**

## Abrangência

- **Aplica-se a:** todos os repositórios que adotam o framework Ahrena, incluindo o repositório do próprio framework e projetos consumidores downstream
- **Agentes vinculados:** todos os agentes que materializam, movem ou propõem criar arquivos de plano — `warrior-athena`, `warrior-eunomia`, `warrior-apollo`, `warrior-hephaestus`, `warrior-claudionor`, e qualquer Kata de plano (`kata-plan-task`, `kata-load-plan-from-subissue`, `kata-flush-plan-to-subissue`, `kata-decompose-issue-into-plans`)
- **Exceções:** Nenhuma. Lexis não admitem exceções

## Aplicabilidade Prospectiva

Esta Lex aplica-se prospectivamente: arquivos de plano legados detectados sob `docs/` em projetos que adotaram Ahrena antes desta Lex devem ser migrados para o caminho canônico (corpo da sub-issue + provider cache) na próxima sessão que tocar aquele plano. Não há bloqueio retroativo cego — o agente que detectar o plano órfão DEVE sinalizar a migração ao humano antes de prosseguir com qualquer outro trabalho naquele plano.

<HARD-GATE>
Todo agente NÃO DEVE criar, mover ou aceitar instrução para materializar
arquivo de plano (`plan-*.md`) em qualquer caminho que combine `docs/`
e `plans/` como segmentos do path.

Pré-condições obrigatórias para criar/materializar um plano:
  (a) O caminho começa com `.claude/plans/` ou `.cursor/plans/` (provider cache local, gitignored)
  (b) Ou o destino é o corpo da sub-issue Plan no GitHub via API
  (c) Nenhum segmento do path contém `docs/`
  (d) Nenhum segmento do path contém `plans/` sob `docs/`

Esta regra se aplica a TODO projeto Ahrena, independentemente de:
  - tamanho percebido ("é só um arquivo de plano de skill")
  - urgência ("preciso documentar agora")
  - quem solicitou ("o usuário pediu para colocar lá")
  - padrão histórico do projeto ("sempre fizemos assim")

Exceção única: Nenhuma. Planos órfãos legados sob `docs/`
devem ser migrados; nunca normalizados.
</HARD-GATE>

## Protocolo de Detecção

Ao encontrar um arquivo `plan-*.md` sob `docs/` durante qualquer operação (leitura, busca, listagem), o agente DEVE:

1. PAUSAR a operação corrente
2. Sinalizar ao humano: caminho do arquivo órfão, parent Issue (se identificável), recomendação de migração
3. Aguardar direção humana antes de tocar o arquivo (não migrar unilateralmente — o conteúdo pode ter contexto de fase ou ser candidato a outra categoria de documento)

## Exemplos

### Correto

```
.claude/plans/plan-163-codify-3-lexis-hard-gate-rules.md   # provider cache Claude (gitignored)
.cursor/plans/plan-163-codify-3-lexis-hard-gate-rules.md   # provider cache Cursor (gitignored)
GitHub Issue #163 body (canonical)                          # via lex-agent-planning
```

### Incorreto

```
docs/skills/guardia-hello/plans/plan-001-init.md           # FORBIDDEN — combina docs/ + plans/
docs/issues/issue-163/plans/plan-execution.md              # FORBIDDEN — plans/ sob docs/
docs/plans/plan-163.md                                      # FORBIDDEN — plans/ sob docs/
docs/{context}/plans/plan-design.md                         # FORBIDDEN — combina docs/ + plans/
```

## Validação Automatizada

- **Ferramenta:** CI lint script (extensão de `lint-paths.yml`) que faz `find docs/ -name 'plan-*.md' -o -path '*/plans/*'` e falha o pipeline quando encontrar qualquer match
- **Momento:** pre-commit hook local + CI em todo PR + auditoria mensal em projetos downstream
- **Métrica:** 0 arquivos `plan-*.md` sob `docs/` em qualquer repositório Ahrena; 0 segmentos `docs/**/plans/**` em qualquer árvore do projeto
