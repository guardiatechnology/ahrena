# Kata: Revisão de CloudEvents

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Plataforma Guardia — revisão de conformidade de documentação, publishers e consumers de CloudEvents contra Lexis e Codex Guardia

## Objetivo

Este Kata define o procedimento para **revisar mudanças relacionadas a CloudEvents** (documentação em `docs/{context}/events/events.md`, código de publisher e consumer, definições de schema e payload) contra Lexis e Codex de CloudEvents da Guardia, identificando violações de conformidade, lacunas, breaking changes, e produzindo um relatório de revisão estruturado com findings classificados por severidade. É o par simétrico de `kata-api-design-review` para a superfície de eventos.

## Quando Usar

- Quando uma PR modifica `events.md` ou qualquer arquivo sob `docs/{context}/events/`
- Quando uma PR modifica código que publica ou consome CloudEvents (publishers, handlers de consumer, definições de event schema)
- Quando invocado por `warrior-argos` durante uma revisão de Pull Request multi-eixo
- Quando `cry-review-pr` é disparado e o diff toca superfícies de eventos

## Inputs

| Input | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| Diff ou caminho do events.md | Sim | Caminho do arquivo `events.md` modificado ou diff unificado contendo mudanças na superfície de eventos |
| Versão antiga do events.md (para checagem de breaking change) | Não | Se omitido, o kata busca `git show HEAD~1:<path>` da branch base ao revisar uma PR |
| Nome do Bounded Context | Não | Se omitido, infere do caminho `docs/{context}/events/events.md` |
| Modo de correção | Não | `report` (padrão) — apenas findings; `fix` — propõe correções inline junto com findings |

## Workflow

```
Progresso:
- [ ] 1. Ler directives e localizar a superfície de eventos
- [ ] 2. Consultar Lexis e Codex
- [ ] 3. Validar formato do type e nomenclatura
- [ ] 4. Validar presença de idempotencykey
- [ ] 5. Validar payload (data) contra catálogo de entidades
- [ ] 6. Validar tamanho e serialização
- [ ] 7. Detectar breaking changes contra a versão base
- [ ] 8. Validar publishers e consumers (quando no diff)
- [ ] 9. Produzir relatório de revisão
```

### Passo 1: Ler Directives e Localizar a Superfície de Eventos

1. Leia `.ahrena/.directives` para obter `language.default`
2. Identifique a superfície de eventos no diff:
   - Documentação: arquivos no padrão `docs/*/events/events.md`
   - Código: arquivos que importam ou emitem CloudEvents (heurística: grep por `event.guardia.`, `idempotencykey`, `cloudevents`)
3. Se nem documentação nem código tocam a superfície de eventos, encerre cedo com `not applicable: no event surface in diff`
4. Registre o Bounded Context inferido do caminho

### Passo 2: Consultar Lexis e Codex

1. Consulte **lex-cloudevents** — eventos DEVEM seguir CloudEvents (estrutura, propriedades obrigatórias, idempotencykey, JSON, tamanho < 12KB)
2. Consulte **codex-cloudevents** — estrutura do evento, formato do type `event.guardia.{module}.{entity_type}.{event_name}`, formato de `data` por codex-entities
3. Consulte **lex-entities** e **codex-entities** — campos da entidade em `data` (entity_id, entity_type, version, created_at, updated_at, discarded_at; history omitido)
4. Consulte **lex-entity-naming** — `entity_type`, nomes de campo JSON e segmentos do type CloudEvents DEVEM estar em snake_case
5. Consulte **lex-idempotency** e **codex-idempotency** — idempotencykey obrigatório em todo evento publicado; consumers DEVEM deduplicar
6. Consulte **lex-feature-design-docs** — estrutura canônica sob `docs/{context}/events/events.md`

### Passo 3: Validar Formato do Type e Nomenclatura

Para cada evento documentado ou emitido no diff:

1. **Regex do type** — DEVE casar com `^event\.guardia\.[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*$`. Sinalize qualquer desvio como 🔴 BLOCKER.
2. **Segmento module** — declarado e estável; renomear um module existente é breaking change
3. **Segmento entity_type** — snake_case singular (e.g., `scheduled_transfer`, não `scheduledTransfer` nem `scheduled_transfers`)
4. **Segmento event_name** — verbo em snake_case no particípio passado (e.g., `created`, `approved`, `executed`, `cancelled`)
5. **Presença no catálogo** — todo type documentado DEVE aparecer na tabela do catálogo de eventos no topo do `events.md`

### Passo 4: Validar Presença do idempotencykey

Para cada evento documentado ou emitido:

1. **Na documentação** — todo exemplo JSON em `events.md` DEVE incluir `idempotencykey` no nível do envelope
2. **No código publisher** — todo call site que constrói um CloudEvent DEVE definir `idempotencykey` (tipicamente igual ao `entity_id` do request originador)
3. **No código consumer** — handlers DEVEM persistir `(type, idempotencykey)` e curto-circuitar em duplicata
4. Sinalize qualquer evento sem `idempotencykey` como 🔴 BLOCKER citando `lex-idempotency`

### Passo 5: Validar Payload (data) Contra Catálogo de Entidades

Para cada evento cujo `data` representa uma entidade persistente:

1. **entity_id** — presente, tipado como UUID v7
2. **entity_type** — presente, snake_case, casa com o segmento do type
3. **created_at, updated_at** — presentes como timestamps ISO 8601
4. **version** — presente quando optimistic locking é documentado para a entidade
5. **history** — DEVE ser omitido de `data` (por lex-entities)
6. **Nomenclatura de campos** — todos os campos de `data` DEVEM ser snake_case (por lex-entity-naming)
7. **Cross-referência** — campos em `data` DEVEM existir no catálogo `docs/{context}/entities/{entity}.md` correspondente. Sinalize qualquer campo presente em `data` mas ausente do catálogo da entidade como 🟡 WARNING (catálogo desatualizado) ou 🔴 BLOCKER (vazamento silencioso de campo interno)

### Passo 6: Validar Tamanho e Serialização

1. **Serialização** — JSON UTF-8 (por lex-cloudevents)
2. **Tamanho** — payload < 12KB. Quando o diff inclui um exemplo representativo, calcule o tamanho em bytes e sinalize se ≥ 12KB
3. **Content-Type** — `datacontenttype: application/json` declarado

### Passo 7: Detectar Breaking Changes Contra a Versão Base

Para cada evento presente em **ambas** versões (base e nova) do `events.md` (ou schema):

| Mudança | Severidade | Razão |
|---------|------------|-------|
| `type` renomeado (qualquer segmento alterado) | 🔴 BLOCKER | Consumers inscritos no type antigo silenciosamente deixam de receber |
| Campo obrigatório removido de `data` | 🔴 BLOCKER | Consumers que leem o campo quebram |
| Tipo de campo restringido (e.g., `string` → `enum<a,b>`) | 🔴 BLOCKER | Valores existentes tornam-se inválidos |
| Campo obrigatório adicionado sem plano de backfill | 🔴 BLOCKER | Consumers antigos desconhecem; emissores publicando sem ele quebram o contrato |
| Campo renomeado | 🔴 BLOCKER | Equivalente a remover + adicionar |
| Campo opcional adicionado com default | 🟡 WARNING | Consumers DEVERIAM ignorar campos desconhecidos, mas sinalize para conscientização |
| Segmento `module` de uma entidade existente alterado | 🔴 BLOCKER | Roteamento de tópicos quebra |

Método de detecção: compare a tabela do catálogo de eventos (entity_type × event_name × type) e a lista de campos `data` por evento. Use git: `git show <base-sha>:<path>` versus atual.

Para eventos **apenas na versão nova** (adicionados): nenhum breaking change — registre como 🟡 WARNING somente quando a entidade correspondente existe na base mas o diagrama de lifecycle não inclui o novo estado.

### Passo 8: Validar Publishers e Consumers (quando no diff)

Quando código de publisher ou consumer está no diff:

1. **Publisher** — confirme que o call site:
   - define o segmento `type` conforme o catálogo
   - inclui `idempotencykey`
   - serializa `data` com campos em snake_case
   - propaga trace context conforme `lex-observability-required`
2. **Consumer** — confirme que o handler:
   - assina o `type` catalogado (sem typos)
   - verifica idempotência antes de processar
   - retorna ACK após persistência (não antes)
   - registra falhas com correlation_id sem expor PII

### Passo 9: Produzir Relatório de Revisão

Gere um relatório de revisão Markdown estruturado:

1. **Cabeçalho** — superfície de eventos revisada (caminhos, total de eventos, total de publishers/consumers no diff), veredito geral:
   - ✅ **Conforme** — zero BLOCKERs e zero WARNINGs
   - 🟡 **Warnings** — zero BLOCKERs, um ou mais WARNINGs
   - 🔴 **Violações** — um ou mais BLOCKERs
2. **Tabela de findings** — uma linha por finding:

   | Severidade | Evento / Arquivo | Lexis / Codex | Finding | Sugestão |
   |------------|------------------|---------------|---------|----------|

   Níveis de severidade:
   - `🔴 BLOCKER` — violação de Lexis ou breaking change; DEVE ser corrigido antes do merge
   - `🟡 WARNING` — desvio de Codex ou ponto não-bloqueante; DEVERIA ser corrigido nesta PR ou em follow-up

3. **Resumo de contagens** — total BLOCKER / WARNING
4. **Matriz de breaking change** — quando o Passo 7 encontrar algo, liste antigo → novo com o tipo de mudança
5. **Próximos passos** — em modo `fix`, anexe correção inline para cada BLOCKER e WARNING; em modo `report`, liste os eventos que demandam atenção

Se sem findings, declare: "Superfície de eventos totalmente conforme com Lexis e Codex Guardia; nenhum breaking change detectado."

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Relatório de revisão | Markdown | Retornado ao chamador (tipicamente `warrior-argos`) para inclusão no review-comment consolidado da PR |

## Exemplo de Execução

### Input de Exemplo

```
Caminho do diff: docs/scheduled-payments/events/events.md
SHA base: 12bf878 (main)
Modo de correção: report
```

### Output de Exemplo (resumo)

```markdown
## Revisão de CloudEvents — docs/scheduled-payments/events/events.md

**Eventos revisados:** 6 | **Veredito:** 🔴 1 BLOCKER, 2 WARNINGs

| Severidade | Evento / Arquivo | Regra | Finding | Sugestão |
|------------|------------------|-------|---------|----------|
| 🔴 BLOCKER | event.guardia.platform.scheduledTransfer.approved | lex-entity-naming | Segmento entity_type em camelCase | Renomeie para `scheduled_transfer` (snake_case) |
| 🟡 WARNING | event.guardia.platform.scheduled_transfer.executed | lex-cloudevents | data.failure_reason marcado opcional mas ausente do catálogo da entidade | Adicione `failure_reason` em docs/scheduled-payments/entities/scheduled-transfer.md |
| 🟡 WARNING | tabela do catálogo events.md | codex-feature-design-docs | Coluna Consumers ausente | Preencha a coluna Consumers para todas as linhas |

**Matriz de breaking change:** nenhuma.

**Próximos passos:** corrigir 1 BLOCKER antes do merge; tratar 2 WARNINGs nesta PR ou abrir Issue de follow-up.
```

## Restrições

- Este Kata produz apenas relatório de revisão; não modifica documentação ou código a menos que o modo `fix` seja explicitamente requisitado
- Toda divergência DEVE ser classificada como 🔴 BLOCKER (violação de Lexis ou breaking change) ou 🟡 WARNING (desvio de Codex ou não-bloqueante) — nunca aceite silenciosamente
- Escale ao humano quando uma divergência puder ser exceção intencional exigindo ADR
- Não sinalize divergências em eventos explicitamente excluídos do escopo da revisão
- A checagem de breaking change requer versão base; se indisponível, pule o Passo 7 e reporte `breaking-change check skipped: base version unavailable` como 🟡 WARNING

## Referências

- `lex-cloudevents`, `codex-cloudevents`
- `lex-entities`, `codex-entities`, `lex-entity-naming`
- `lex-idempotency`, `codex-idempotency`
- `lex-feature-design-docs`, `codex-feature-design-docs`
- `lex-observability-required`
- `kata-api-design-review` — par simétrico para contratos de API HTTP
- `kata-events-doc` — contrapartida de autoria
- [CloudEvents Specification](https://cloudevents.io/)
