---
name: kata-event-storm
description: "Event Storming. Plataforma Guardia — descoberta de eventos de domínio, comandos, agregados, políticas e bounded contexts para uma feature ou módulo"
---

# Kata: Event Storming

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Plataforma Guardia — descoberta de eventos de domínio, comandos, agregados, políticas e bounded contexts para uma feature ou módulo

## Workflow

```
Progresso:
- [ ] 1. Ler diretivas e escopo
- [ ] 2. Consultar Lexis e Codex
- [ ] 3. Identificar eventos de domínio (timeline)
- [ ] 4. Identificar comandos e atores
- [ ] 5. Identificar agregados
- [ ] 6. Identificar políticas (reações automáticas)
- [ ] 7. Identificar sistemas externos e read models
- [ ] 8. Marcar hotspots
- [ ] 9. Identificar bounded contexts
- [ ] 10. Mapear para tipos CloudEvents
- [ ] 11. Produzir documento de Event Storming
```

### Passo 1: Ler Diretivas e Escopo

1. Ler `.ahrena/.directives` para obter `language.default`
2. Confirmar que a descrição do domínio/feature, o nome do Bounded Context (PascalCase) e o módulo CloudEvents foram fornecidos. Se insuficientes, **perguntar ao usuário** (qual é o processo de negócio principal? quem são os atores? qual é o limite do sistema? o que dispara a primeira ação?) e aguardar as respostas
3. Verificar se já existe `docs/{context}/events/events.md` — incorporá-lo como input se disponível
4. Identificar o escopo de bounded context: único ou múltiplos contextos

### Passo 2: Consultar Lexis e Codex

1. Consultar **lex-cloudevents** — eventos DEVEM seguir a spec CloudEvents; formato do tipo `event.guardia.{module}.{entity_type}.{event_name}`
2. Consultar **codex-cloudevents** — estrutura do evento: id, source, specversion, type, time, subject, idempotencykey, data; tamanho < 12KB
3. Consultar **lex-entities** e **codex-entities** — campos de entidade em `data` (entity_id, entity_type, version, created_at, updated_at; history omitido)
4. Consultar **lex-idempotency** — eventos DEVEM carregar idempotencykey; consumidores DEVEM deduplicar

### Passo 3: Identificar Eventos de Domínio (Timeline)

Eventos de domínio são **coisas que aconteceram** no domínio — declarados no passado, da perspectiva do negócio:

1. Perguntar ao usuário: "Descreva o processo de negócio passo a passo. O que acontece primeiro e o que vem depois?" — ou inferir da descrição quando o fluxo estiver claro
2. Listar todos os eventos de domínio em **ordem cronológica** (ex: `TransferenciaAgendadaSolicitada`, `TransferenciaAgendadaAprovada`, `TransferenciaAgendadaExecutada`, `TransferenciaAgendadaFalhou`)
3. Para cada evento, registrar:
   - **Nome** — tempo passado, PascalCase (ex: `TransferenciaAgendadaExecutada`)
   - **Quando ocorre** — gatilho de negócio (ex: "após o contador enviar o formulário de transferência")
   - **Entidade relacionada** — o agregado afetado
4. Identificar **lacunas** na timeline — eventos que logicamente devem existir entre dois outros, mas ainda não foram nomeados
5. Marcar eventos contestados ou incertos como hotspots (ver Passo 8)

### Passo 4: Identificar Comandos e Atores

Comandos são **intenções que disparam eventos** — declarados no imperativo, representando algo que um usuário ou sistema quer que aconteça:

1. Para cada evento de domínio, perguntar: "O que disparou isso? Quem ou o que emitiu o comando?"
2. Identificar o **ator**: papel de usuário, sistema interno, sistema externo, timer/scheduler ou política (reação automática)
3. Documentar a cadeia: `[Ator] → [Comando] → [Evento de Domínio]`
   - ex: `Contador → SolicitarTransferenciaAgendada → TransferenciaAgendadaSolicitada`
   - ex: `Scheduler → ExecutarTransferenciaAgendada → TransferenciaAgendadaExecutada`
4. Sinalizar comandos sem ator claro como hotspots

### Passo 5: Identificar Agregados

Agregados são **entidades que tratam comandos e produzem eventos** — eles aplicam regras de negócio e mantêm consistência:

1. Agrupar comandos e eventos relacionados pela entidade que os processa
2. Nomear cada agregado (substantivo singular, PascalCase, ex: `TransferenciaAgendada`, `LancamentoContabil`, `ExecucaoReconciliacao`)
3. Para cada agregado, documentar:
   - **Comandos que aceita** — lista de nomes de comandos
   - **Eventos que produz** — lista de nomes de eventos de domínio
   - **Invariantes** — regras de negócio que aplica (ex: "uma transferência não pode ser executada se o saldo da origem for insuficiente")
4. Identificar agregados referenciados em múltiplos comandos — candidatos potenciais a shared kernel ou anti-corruption layer

### Passo 6: Identificar Políticas (Reações Automáticas)

Políticas são **reações automáticas** que disparam em resposta a eventos: "Quando [Evento], então [Comando]":

1. Para cada evento de domínio, perguntar: "Esse evento dispara automaticamente alguma outra coisa no sistema?"
2. Documentar cada política: `Quando {EventoDomínio} → Então {Comando} (em {Agregado})`
   - ex: `Quando TransferenciaAgendadaExecutada → Então LançarNoContábil (em LancamentoContabil)`
   - ex: `Quando ReconciliacaoCompleta → Então NotificarContador (em Notificacao)`
3. Identificar políticas que **cruzam bounded contexts** — essas se tornam eventos de integração e precisam de roteamento explícito

### Passo 7: Identificar Sistemas Externos e Read Models

**Sistemas externos** — serviços fora deste bounded context:

1. Nomear cada sistema (ex: `ParceiroBancario`, `AutoridadeFiscal`, `ServicoNotificacao`, `ServicoContabil`)
2. Identificar se cada sistema **produz eventos** (entrada) ou **recebe comandos** (saída)
3. Documentar o ponto de integração de cada um

**Read models** — projeções de dados necessárias para suportar decisões ou visualizações de usuário:

1. Nomear cada read model (ex: `HistoricoTransferenciasAgendadas`, `DashboardReconciliacao`)
2. Identificar quais eventos de domínio alimentam cada read model (projeções)
3. Registrar o consumidor de cada visualização (papel de usuário, relatório externo, Isac)

### Passo 8: Marcar Hotspots

Hotspots são **perguntas, incertezas, conflitos e riscos** que precisam de resolução humana antes da implementação:

1. Documentar cada hotspot com:
   - **Tipo** — `Dúvida` (regra ou responsabilidade unclear) | `Conflito` (duas interpretações válidas) | `Lacuna` (evento ausente) | `Risco` (race condition, perda de dados, conformidade)
   - **Descrição** — declaração precisa da incerteza
   - **Prioridade** — `P1` (bloqueia o design, resolver antes de prosseguir) | `P2` (resolver antes da implementação) | `P3` (pode endereçar em follow-up)
   - **Responsável** — time ou pessoa que deve resolver
2. Não pular este passo — hotspots não resolvidos são a principal fonte de bugs de integração e escopo não controlado

### Passo 9: Identificar Bounded Contexts

1. Agrupar agregados e eventos em **bounded contexts** — áreas onde os termos têm um significado consistente e compartilhado
2. Nomear cada bounded context e descrever sua responsabilidade (ex: `Pagamentos`, `Reconciliacao`, `RelatorioFiscal`)
3. Identificar **limites de contexto** — onde eventos de domínio cruzam de um contexto para outro (esses se tornam eventos publicados de integração)
4. Mapear responsabilidade: qual time ou serviço é responsável por cada bounded context

### Passo 10: Mapear para Tipos CloudEvents

Traduzir cada evento de domínio para a convenção de nomenclatura CloudEvents da Guardia:

1. Para cada evento de domínio, produzir o `type` CloudEvents:
   - Formato: `event.guardia.{module}.{entity_type}.{event_name}`
   - `entity_type` — nome da entidade em snake_case (ex: `scheduled_transfer`, `reconciliation_run`)
   - `event_name` — verbo no passado em snake_case (ex: `created`, `approved`, `executed`, `failed`, `cancelled`)
2. Para cada tipo, definir o shape inicial de `data` conforme codex-entities:
   - Obrigatório: `entity_id`, `entity_type`, campos de negócio chave relevantes para consumidores
   - Omitir `history`; não incluir PII a menos que estritamente necessário
3. Marcar eventos de integração (que cruzam bounded contexts) — eles exigem valores explícitos de `source` e `subject`

### Passo 11: Entregar o Catálogo de Descoberta

A descoberta **não vira um arquivo monolítico**. O resultado é entregue como entrada para a Fase 2 (`kata-events-doc`) e como notas que o `warrior-prometheus` consolida.

Estrutura interna a passar adiante:

1. **Cabeçalho** — domínio, Bounded Context, módulo CloudEvents, data, escopo
2. **Timeline de Eventos de Domínio** — lista cronológica: nome, gatilho, entidade
3. **Comandos e Atores** — tabela: Ator | Comando | Evento de Domínio
4. **Agregados** — uma subseção por agregado: comandos aceitos, eventos produzidos, invariantes
5. **Políticas** — tabela: Quando (Evento) | Então (Comando) | Em (Agregado)
6. **Sistemas Externos** — tabela: Sistema | Direção (entrada/saída) | Eventos / Comandos
7. **Read Models** — tabela: Visualização | Eventos que a alimentam | Consumidor
8. **Hotspots** — tabela: Tipo | Descrição | Prioridade | Responsável
9. **Bounded Contexts** — diagrama ou tabela: Contexto | Responsabilidade | Time | Eventos de Integração
10. **Catálogo CloudEvents** — tabela: Evento de Domínio | Tipo CloudEvents | Shape inicial de data

A persistência canônica dos eventos descobertos acontece na Fase 2, em `docs/{context}/events/events.md`, via `kata-events-doc` + `kata-feature-design-docs`. Hotspots e descobertas auxiliares são publicados pelo Prometheus no Notion (Guardia Platform > Domain Models).

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Catálogo CloudEvents | Tabela em memória | Input direto para `kata-events-doc` |
| Lista de hotspots | Tabela | Notas para `warrior-prometheus` revisar e resolver |

## Exemplo de Execução

### Input de Exemplo

```
Domínio: Transferências agendadas — contadores podem agendar transferências bancárias para execução em data futura. Um supervisor deve aprovar antes da execução. O scheduler dispara a execução no horário agendado.
Módulo: platform
```

### Output de Exemplo (resumo)

Catálogo de descoberta entregue à Fase 2 (`kata-events-doc`):

**Timeline:** TransferenciaAgendadaSolicitada → TransferenciaAgendadaAprovada → TransferenciaAgendadaExecutada | TransferenciaAgendadaFalhou → TransferenciaAgendadaCancelada

**Comandos e atores:**
| Ator | Comando | Evento de Domínio |
|------|---------|-------------------|
| Contador | SolicitarTransferenciaAgendada | TransferenciaAgendadaSolicitada |
| Supervisor | AprovarTransferenciaAgendada | TransferenciaAgendadaAprovada |
| Scheduler | ExecutarTransferenciaAgendada | TransferenciaAgendadaExecutada / TransferenciaAgendadaFalhou |
| Contador | CancelarTransferenciaAgendada | TransferenciaAgendadaCancelada |

**Hotspots:**
| Tipo | Descrição | Prioridade | Responsável |
|------|-----------|------------|-------------|
| Dúvida | O que acontece em caso de falha de execução: falha imediata ou retry? Política de retry indefinida | P1 | Time de plataforma |
| Risco | Race condition se supervisor aprovar enquanto scheduler já está executando | P1 | Time de plataforma |

**Catálogo CloudEvents:**
| Evento de Domínio | Tipo CloudEvents | data (campos chave) |
|---|---|---|
| TransferenciaAgendadaSolicitada | event.guardia.financial.scheduled_transfer.requested | entity_id, amount, currency, scheduled_date, requestor_id |
| TransferenciaAgendadaAprovada | event.guardia.financial.scheduled_transfer.approved | entity_id, approver_id, approved_at |
| TransferenciaAgendadaExecutada | event.guardia.financial.scheduled_transfer.executed | entity_id, executed_at, ledger_entry_id |
| TransferenciaAgendadaFalhou | event.guardia.financial.scheduled_transfer.failed | entity_id, failure_reason, failed_at |
| TransferenciaAgendadaCancelada | event.guardia.financial.scheduled_transfer.cancelled | entity_id, cancelled_by, cancelled_at |

## Restrições

- Este Kata produz apenas o documento de descoberta; não implementa publishers, consumers ou contratos de API
- Não pular a identificação de hotspots — toda incerteza não documentada se torna um bug ou lacuna de escopo
- O catálogo CloudEvents produzido aqui DEVE ser completo o suficiente para executar `kata-events-doc` sem descoberta adicional; sinalizar campos ausentes explicitamente
- Escalar para um humano quando a responsabilidade de bounded context for ambígua ou quando um único evento abranger múltiplos agregados sem dono claro
- Não assumir que a timeline de eventos está completa — verificar ativamente eventos ausentes em cada lacuna da cadeia causal
