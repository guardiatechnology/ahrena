---
name: kata-architecture-brief
description: "Brief Arquitetural. Fase 3 do fluxo Issue-Driven — mapeamento de componentes afetados, decisões de design e delegação a warriors especialistas quando aplicável"
---

# Kata: Brief Arquitetural

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Fase 3 do fluxo Issue-Driven — mapeamento de componentes afetados, decisões de design e delegação a warriors especialistas quando aplicável

## Workflow

```
Progresso:
- [ ] 1. Ler brief + requisitos
- [ ] 2. Mapear componentes afetados
- [ ] 3. Propor abordagem técnica
- [ ] 4. Identificar decisões arquiteturais relevantes
- [ ] 5. Delegar a especialistas se aplicável (Daedalus/Kronos)
- [ ] 6. Invocar kata-adr-write para cada decisão relevante
- [ ] 7. Persistir em .ahrena/issues/{n}/03-architecture.md
- [ ] 8. Atualizar checkpoint
```

### Passo 1: Ler brief + requisitos

1. Ler `01-brief.md` e `02-requirements.md` em `.ahrena/issues/{n}/`.
2. Se algum ausente, informar e encerrar — fases predecessoras devem estar completas.
3. Identificar ACs que exigem atenção arquitetural especial (ex.: performance, consistência, idempotência).

### Passo 2: Mapear componentes afetados

Para cada AC:

1. Identificar arquivos/módulos existentes que serão modificados.
2. Identificar novos arquivos/módulos que serão criados.
3. Identificar contratos externos afetados (APIs, eventos, bancos de dados, filas).
4. **Consultar o grafo de código para impacto reverso**, quando `graphify.enabled` for `true` em `.ahrena/.directives`. Invoque `kata-codebase-graph`; não chame o binário diretamente, pois o procedimento já existe (`lex-pilars`). A leitura ad hoc encontra dependências diretas; a travessia reversa encontra quem consome o que será alterado.
5. Consolidar em uma tabela:

| Componente | Tipo | Ação | ACs cobertos | Origem |
|---|---|---|---|---|
| `src/refunds/service.py` | módulo | criar | AC-1, AC-2 | leitura |
| `src/payments/repository.py` | módulo | modificar (adicionar método) | AC-3 | leitura |
| `openapi/refunds.yaml` | spec | modificar | AC-1 | leitura |
| `events/refund.created` | evento | criar | AC-2 | leitura |
| `scripts/anonymity_guard.py` | módulo | avaliar | AC-3 | grafo (reverso) |

Esta tabela é a **fronteira de escopo** usada pelo `kata-quality-gate` no check de scope creep.

#### Consulta ao grafo — limites aferidos

Medição em `financial-context` (20.882 nós, 49.563 arestas, 31 MB) sobre 3 PRs reais, com 10 achados substantivos que a leitura direta não encontraria:

- **Limite de sementes.** Cada invocação de `graphify affected` recarrega o grafo inteiro e custa cerca de 2,5 s. Consultar todos os nós alterados de um PR grande (377 sementes na medição) levaria minutos. Consulte apenas os nós que os ACs realmente tocam.
- **Profundidade 2.** É o valor aferido. Não exceda sem nova medição.
- **Barris de reexportação.** 47% dos achados brutos foram arquivos `__init__.py` que apenas reexportam o símbolo alterado. São consumidores reais, porém de baixa informação: marque como estruturais ou omita da tabela.
- **Coluna `Origem`.** Linhas vindas de travessia reversa DEVEM ser identificadas como `grafo (reverso)` — são justamente as que a leitura ad hoc não encontraria.
- **Arestas `INFERRED`.** Linhas sustentadas apenas por aresta `INFERRED` exigem confirmação humana antes de virar fronteira de escopo. Na medição não ocorreram (0 de 19), mas isso foi um repositório em uma única profundidade.

#### Degradação

Quando o binário está ausente, `graphify.enabled` é `false`, ou `built_at_commit` divergiu do `HEAD`, este passo segue com o comportamento anterior (apenas leitura) e **declara** que o grafo estava indisponível. O grafo é insumo consultivo: nunca bloqueia esta fase.

### Passo 3: Propor abordagem técnica

Descrever em prosa estruturada:

1. **Fluxo principal:** sequência de chamadas/eventos do caso feliz.
2. **Fluxos alternativos:** erros, idempotência, retry.
3. **Persistência:** entidades afetadas, migrações necessárias.
4. **Integrações externas:** contratos, autenticação, rate limits.
5. **Observabilidade:** logs, métricas, traces relevantes.

### Passo 4: Identificar decisões arquiteturais relevantes

Para cada ponto de design, perguntar: é uma **decisão** ou um **seguimento de padrão existente**?

Usar o checklist do `codex-issue-workflow` (seção "Quando gerar ADR"):

| Gera ADR? | Exemplos |
|:-:|---|
| ✅ | Nova escolha tecnológica; deviation de padrão; trade-off significativo; afeta múltiplos componentes; afeta contrato externo |
| ❌ | Bugfix pontual; refactor local seguindo padrão; endpoint novo seguindo estrutura existente |

Registrar cada decisão candidata com: título, motivação, alternativas consideradas.

### Passo 5: Delegar a especialistas se aplicável

**Se a issue envolve design de API REST:**
1. Invocar `warrior-daedalus` → `kata-api-design-oas`
2. Passar como contexto: o brief, os requisitos, e os componentes afetados.
3. Daedalus produz OAS + Markdown em `paths.oas`.
4. Referenciar esses arquivos no documento de arquitetura desta fase.

**Se a issue envolve design de eventos (CloudEvents):**
1. Invocar `warrior-kronos` → `kata-events-doc`
2. Passar como contexto os mesmos artefatos.
3. Kronos produz catálogo de eventos em `paths.events`.
4. Referenciar esses arquivos no documento de arquitetura.

Registrar no checkpoint qual warrior foi delegado e onde está o output.

### Passo 6: Invocar `kata-adr-write` para cada decisão relevante

Para cada decisão identificada no Passo 4 que merece ADR:

1. Invocar `kata-adr-write` com: título da decisão, contexto, decisão proposta, alternativas.
2. `kata-adr-write` cria `docs/adr/ADR-{n}-{título}.md` com status `proposed`.
3. O ADR será transicionado para `accepted` após aprovação no Gate 1.
4. Referenciar cada ADR criado no documento de arquitetura.

### Passo 7: Persistir em `.ahrena/issues/{n}/03-architecture.md`

Estrutura:

```markdown
# Arquitetura — Issue #{n}: {título}

- **Referências:** [Brief](./01-brief.md) · [Requisitos](./02-requirements.md)
- **Data:** {YYYY-MM-DD}

## Componentes Afetados

| Componente | Tipo | Ação | ACs cobertos | Origem |
|---|---|---|---|---|
| ... | ... | ... | ... | leitura \| grafo (reverso) |

> Esta tabela define o escopo exato de arquivos a modificar.
> Modificações fora desta tabela são bloqueadas pelo Gate 2 como scope creep.
> A coluna `Origem` distingue o que veio da leitura direta do que veio da
> travessia reversa do grafo. Quando o grafo estava indisponível, declare-o
> aqui em vez de omitir a coluna.

## Abordagem Técnica

### Fluxo principal

{descrição em prosa, diagrama de sequência em Mermaid opcional}

### Fluxos alternativos

- **Erro {X}:** {como é tratado}
- **Idempotência:** {como é garantida}
- **Retry:** {política}

### Persistência

{entidades afetadas, migrações necessárias}

### Integrações externas

{contratos, auth, rate limits}

### Observabilidade

{logs, métricas, traces}

## Delegações a Especialistas

- **Daedalus (API):** ver `{caminho OAS}`, `{caminho doc}`
- **Kronos (Eventos):** ver `{caminho catálogo}`

(omitir seções não aplicáveis)

## Decisões Arquiteturais (ADRs)

- [ADR-{n}: {título}](../../adr/ADR-{n}-{slug}.md) — status: proposed
- [ADR-{m}: {título}](../../adr/ADR-{m}-{slug}.md) — status: proposed

(seção ausente se não houve decisão relevante)

## Riscos Técnicos

- {Risco 1 e mitigação}
- {Risco 2 e mitigação}

## Próxima fase

Gate 1 — Aprovação de Escopo (aguarda aprovação humana).
```

### Passo 8: Atualizar checkpoint

1. Atualizar `.ahrena/workflow/issue-{n}/checkpoint.md`:
   - fase concluída: 3
   - próxima: Gate 1 (aprovação humana)
   - referências: `03-architecture.md`, ADRs criados
   - delegações: warriors especialistas invocados e seus outputs
2. `warrior-athena` pede aprovação humana antes de avançar para Fase 4.

## Saídas

| Saída | Formato | Destino |
|-------|---------|---------|
| Documento de arquitetura | Markdown | `.ahrena/issues/{n}/03-architecture.md` |
| ADRs (0 ou mais) | Markdown MADR | `docs/adr/ADR-{n}-*.md` |
| OAS/doc/events (se aplicável) | conforme Daedalus/Kronos | `paths.oas`, `paths.events` |
| Checkpoint atualizado | Markdown | `.ahrena/workflow/issue-{n}/checkpoint.md` |

## Restrições

- **Tabela de componentes é vinculante:** define o escopo exato que o Gate 2 usará para scope creep check. Tudo que estiver fora dessa tabela será bloqueado.
- **ADRs em status `proposed`:** até o Gate 1, todos os ADRs produzidos nesta fase ficam com status `proposed`. A transição para `accepted` só ocorre após aprovação humana.
- **Delegação não substitui o documento desta fase:** mesmo quando delega a Daedalus/Kronos, o kata deve produzir o `03-architecture.md` com o contexto geral e referências aos outputs dos especialistas.
- **Sem codificar:** este kata descreve **o que** e **onde**, não **como** (o Apollo fará o como na Fase 4).
- **Destino fixo:** `.ahrena/issues/{n}/03-architecture.md` e `docs/adr/ADR-*` (conforme `lex-issue-driven`).
