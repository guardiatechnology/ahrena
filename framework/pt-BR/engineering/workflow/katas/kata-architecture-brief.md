# Kata: Brief Arquitetural

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Fase 3 do fluxo Issue-Driven — mapeamento de componentes afetados, decisões de design e delegação a warriors especialistas quando aplicável

## Objetivo

A partir do brief (Fase 1) e dos requisitos (Fase 2), produzir um documento de design arquitetural contendo: mapa dos componentes afetados, abordagem técnica proposta, decisões que precisam ser tomadas, delegação a warriors especialistas (Daedalus para API, Kronos para eventos), e invocação de `kata-adr-write` quando houver decisão arquitetural relevante. O documento final em `.issues/{n}/03-architecture.md` é a base do Gate 1 e delimita o escopo contra o qual o Gate 2 fará scope creep check.

## Quando Usar

- Fase 3 do fluxo orquestrado por `warrior-athena`, após Fase 2 (`kata-requirements-brief`)
- Quando é necessário definir tecnicamente como implementar os ACs antes de codificar

## Inputs

| Input | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| Brief Fase 1 | Sim | `.issues/{n}/01-brief.md` |
| Requisitos Fase 2 | Sim | `.issues/{n}/02-requirements.md` |
| Stack do projeto | Sim | Linguagem, frameworks, padrões existentes (detectado via leitura do repo) |

## Workflow

```
Progresso:
- [ ] 1. Ler brief + requisitos
- [ ] 2. Mapear componentes afetados
- [ ] 3. Propor abordagem técnica
- [ ] 4. Identificar decisões arquiteturais relevantes
- [ ] 5. Delegar a especialistas se aplicável (Daedalus/Kronos)
- [ ] 6. Invocar kata-adr-write para cada decisão relevante
- [ ] 7. Persistir em .issues/{n}/03-architecture.md
- [ ] 8. Atualizar checkpoint
```

### Passo 1: Ler brief + requisitos

1. Ler `01-brief.md` e `02-requirements.md` em `.issues/{n}/`.
2. Se algum ausente, informar e encerrar — fases predecessoras devem estar completas.
3. Identificar ACs que exigem atenção arquitetural especial (ex.: performance, consistência, idempotência).

### Passo 2: Mapear componentes afetados

Para cada AC:

1. Identificar arquivos/módulos existentes que serão modificados.
2. Identificar novos arquivos/módulos que serão criados.
3. Identificar contratos externos afetados (APIs, eventos, bancos de dados, filas).
4. Consolidar em uma tabela:

| Componente | Tipo | Ação | ACs cobertos |
|---|---|---|---|
| `src/refunds/service.py` | módulo | criar | AC-1, AC-2 |
| `src/payments/repository.py` | módulo | modificar (adicionar método) | AC-3 |
| `openapi/refunds.yaml` | spec | modificar | AC-1 |
| `events/refund.created` | evento | criar | AC-2 |

Esta tabela é a **fronteira de escopo** usada pelo `kata-quality-gate` no check de scope creep.

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

### Passo 7: Persistir em `.issues/{n}/03-architecture.md`

Estrutura:

```markdown
# Arquitetura — Issue #{n}: {título}

- **Referências:** [Brief](./01-brief.md) · [Requisitos](./02-requirements.md)
- **Data:** {YYYY-MM-DD}

## Componentes Afetados

| Componente | Tipo | Ação | ACs cobertos |
|---|---|---|---|
| ... | ... | ... | ... |

> Esta tabela define o escopo exato de arquivos a modificar.
> Modificações fora desta tabela são bloqueadas pelo Gate 2 como scope creep.

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
| Documento de arquitetura | Markdown | `.issues/{n}/03-architecture.md` |
| ADRs (0 ou mais) | Markdown MADR | `docs/adr/ADR-{n}-*.md` |
| OAS/doc/events (se aplicável) | conforme Daedalus/Kronos | `paths.oas`, `paths.events` |
| Checkpoint atualizado | Markdown | `.ahrena/workflow/issue-{n}/checkpoint.md` |

## Restrições

- **Tabela de componentes é vinculante:** define o escopo exato que o Gate 2 usará para scope creep check. Tudo que estiver fora dessa tabela será bloqueado.
- **ADRs em status `proposed`:** até o Gate 1, todos os ADRs produzidos nesta fase ficam com status `proposed`. A transição para `accepted` só ocorre após aprovação humana.
- **Delegação não substitui o documento desta fase:** mesmo quando delega a Daedalus/Kronos, o kata deve produzir o `03-architecture.md` com o contexto geral e referências aos outputs dos especialistas.
- **Sem codificar:** este kata descreve **o que** e **onde**, não **como** (o Apollo fará o como na Fase 4).
- **Destino fixo:** `.issues/{n}/03-architecture.md` e `docs/adr/ADR-*` (conforme `lex-issue-driven`).

## Referências

- `lex-issue-driven` — leis do fluxo
- `codex-issue-workflow` — checklist de quando gerar ADR
- `kata-adr-write` — escrita de ADR no formato MADR
- `warrior-daedalus`, `kata-api-design-oas` — delegação para API
- `warrior-kronos`, `kata-events-doc` — delegação para eventos
- `codex-codex`, `codex-lexis` — convenções de artefato
