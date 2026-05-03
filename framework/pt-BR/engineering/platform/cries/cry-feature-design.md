# Cry: Feature Design — Domínio, API e Eventos

> **Prefixo:** `cry-` | **Tipo:** Comando Recorrente | **Escopo:** Ciclo completo de design de feature: modelagem de domínio, design de API REST e documentação de CloudEvents em sequência

## Descrição

Este comando ativa o **Warrior Prometheus** (Technical Product Manager) para orquestrar o ciclo completo de design de feature em três fases sequenciais: modelagem de domínio (warrior-theseus), design de API (warrior-daedalus) e documentação de eventos (warrior-kronos). Cada fase usa o output da fase anterior como input autoritativo. O usuário confirma cada fase antes que a próxima comece.

## Uso

```
/cry-feature-design <descrição da feature> [módulo] [restrições]
```

## Parâmetros

| Parâmetro | Obrigatório | Descrição | Exemplo |
|-----------|:-----------:|-----------|---------|
| `descrição da feature` | Sim | Descrição do escopo da feature, objetivo de negócio e quaisquer regras ou atores conhecidos | "Transferências agendadas: contadores criam, supervisores aprovam, executadas na data agendada" |
| `módulo` | Não | Identificador do módulo CloudEvents. Se omitido, Prometheus irá perguntar | `platform` |
| `restrições` | Não | Restrições conhecidas: segurança, compliance, integrações existentes, restrições de breaking change | "Sem breaking changes nos endpoints existentes /v1/transfers" |

## O que o Comando Faz

1. **Assume o papel do warrior-prometheus** e lê `language.default` em `.ahrena/.directives`
2. **Faz perguntas de clarificação** se a descrição da feature, módulo ou restrições forem insuficientes
3. **Fase 1 — Modelagem de Domínio (warrior-theseus):** modela o domínio de forma iterativa; resolve hotspots P1; confirma o modelo de domínio com o usuário antes de prosseguir
4. **Fase 2 — Design de API (warrior-daedalus):** desenha a API usando o modelo de domínio como input autoritativo; confirma o design de API com o usuário antes de prosseguir
5. **Fase 3 — Documentação de Eventos (warrior-kronos):** documenta CloudEvents usando modelo de domínio + eventos de integração da Fase 1; pula a descoberta (já realizada); confirma a documentação de eventos com o usuário
6. **Verificação de consistência:** verifica que nomes de entidade, valores de entity_type e segmentos do tipo CloudEvents coincidem com o modelo de domínio em todos os outputs
7. **Entrega o pacote final de artefatos** com os paths de todos os arquivos produzidos

## Template de Prompt

```
Contexto:
- Descrição da feature: {{descrição da feature}}
- Módulo (opcional): {{módulo}}
- Restrições (opcional): {{restrições}}

Tarefa:
Aja como o Warrior Prometheus (Technical Product Manager). Os artefatos de design
são persistidos na estrutura canônica `docs/{context}/{category}/` conforme
`lex-feature-design-docs`.

Se a descrição da feature, módulo ou restrições forem insuficientes, faça perguntas de clarificação antes de começar.

Orquestre o ciclo completo de design de feature em sequência:

1) **Fase 1 — Modelagem de Domínio (warrior-theseus):** Delegue ao warrior-theseus com a descrição da feature e o módulo. Monitore hotspots P1 — não avance até que sejam resolvidos. Apresente o resumo do modelo de domínio (catálogo de entidades, use cases, eventos de integração) e pergunte: "O modelo de domínio está correto? Devo prosseguir para o design de API?"

2) **Fase 2 — Design de API (warrior-daedalus):** Após confirmação explícita do usuário, delegue ao warrior-daedalus usando o documento de modelo de domínio como input principal. Instrua Daedalus a usar os valores de entity_type e nomes de campo do modelo de domínio (lex-entity-naming). Apresente o resumo do design de API e pergunte: "O design de API está correto? Devo prosseguir para a documentação de eventos?"

3) **Fase 3 — Documentação de Eventos (warrior-kronos):** Após confirmação explícita do usuário, delegue ao warrior-kronos com modelo de domínio + lista de eventos de integração. Instrua Kronos a pular a descoberta (os eventos foram identificados na Fase 1) e ir diretamente para a documentação. Verifique que os segmentos do tipo CloudEvents coincidam com os valores de entity_type do modelo de domínio. Apresente o resumo de eventos.

Após todas as fases, verifique a consistência: nomes de entidade em APIs e eventos devem coincidir com o modelo de domínio. Sinalize qualquer divergência com um caminho claro de resolução.

Entregue o pacote final de artefatos:
- Entidades: `docs/{context}/entities/{entity}.md` (1 arquivo por entidade)
- Especificação de API: `docs/{context}/oas/openapi.yaml` e `docs/{context}/oas/{slug}-api.md`
- Documento de eventos: `docs/{context}/events/events.md`
```

## Exemplo de Invocação

**Input:**

```
/cry-feature-design "Transferências agendadas: contadores agendam uma transferência para uma data futura, supervisores aprovam transferências acima de R$ 10.000, o sistema executa na data agendada, falhas disparam uma nova tentativa após 30 minutos" platform
```

**Output esperado:**

- **Confirmação Fase 1:** Catálogo de entidades (`ScheduledTransfer`, entity_type `scheduled_transfer`), ciclo de vida, use cases, eventos de integração — usuário confirma antes da Fase 2
- **Confirmação Fase 2:** Endpoints (POST /v1/scheduled-transfers, GET, GET/:id, PATCH, DELETE), Idempotency-Key, payloads — usuário confirma antes da Fase 3
- **Confirmação Fase 3:** Catálogo de CloudEvents (`event.guardia.platform.scheduled_transfer.requested`, `.approved`, `.executed`, `.failed`, `.cancelled`) — resumo final
- **Pacote de artefatos:**
  - `docs/scheduled-payments/entities/scheduled-transfer.md`
  - `docs/scheduled-payments/oas/openapi.yaml`
  - `docs/scheduled-payments/events/events.md`

## Quando Usar Este Cry vs Outros

| Cry | Quando usar |
|-----|-------------|
| **cry-feature-design** | Domínio é desconhecido ou deve ser modelado; precisa de um pacote consistente domínio → API → eventos |
| **cry-full-design** | Domínio já está modelado; precisa apenas de API + eventos a partir de uma descrição de feature |
| **cry-api-design** | Domínio está modelado e eventos estão fora do escopo; precisa apenas da API |
| **cry-event-storm** | Precisa apenas de descoberta ou documentação de eventos (domínio e API já existem) |

## Restrições

- Não implementa código — orquestra apenas o design
- Não avança para a próxima fase sem confirmação explícita do usuário
- Não pula a Fase 1 (modelagem de domínio) quando o domínio é genuinamente desconhecido — um domínio mal modelado produz APIs e eventos incorretos
- Exceções às Lexis devem ser documentadas em um ADR; Prometheus sinalizará quando uma decisão exigir um

## Warriors e Katas Associados

| Artefato | Papel |
|----------|-------|
| `warrior-prometheus` | Orquestrador — invocado por este Cry |
| `warrior-theseus` | Fase 1 — Modelagem de Domínio |
| `warrior-daedalus` | Fase 2 — Design de API |
| `warrior-kronos` | Fase 3 — Documentação de Eventos |
| `kata-domain-model` | Executado pelo warrior-theseus |
| `kata-api-design-oas` | Executado pelo warrior-daedalus |
| `kata-api-design-doc` | Executado pelo warrior-daedalus |
| `kata-events-doc` | Executado pelo warrior-kronos |

## Referências

- `warrior-prometheus` — Technical Product Manager e orquestrador de design de feature
- `lex-feature-design-docs` — estrutura canônica `docs/{context}/{category}/`
- `lex-entity-naming` — regras snake_case/PascalCase aplicadas em todas as fases
- `lex-entities` — estrutura base de entidades (entity_id, entity_type, version, timestamps) consultada durante a modelagem de domínio
- `lex-cloudevents` — formato do tipo CloudEvents consultado durante a documentação de eventos
