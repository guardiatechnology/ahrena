# Kata: Modelagem de Domínio (DDD)

> **Prefixo:** `kata-` | **Tipo:** Skill Repetível | **Escopo:** Plataforma Guardia — descoberta e modelagem de domínio para uma feature ou módulo usando Domain-Driven Design

## Objetivo

Produzir um modelo de domínio completo para uma feature ou módulo por meio de diálogo DDD estruturado com o usuário: estabelecer a Linguagem Ubíqua, mapear Bounded Contexts, definir Entidades e Agregados (conforme lex-entities e lex-entity-naming), documentar Use Cases e Application Services, identificar eventos de integração e anti-corruption layers, e desenhar um Context Map. O output alimenta diretamente o design de API (warrior-daedalus) e a documentação de eventos (warrior-kronos).

## Quando Usar

- Antes de desenhar APIs ou documentar eventos para uma nova feature ou módulo
- Quando o domínio é complexo, tem múltiplos atores ou cruza fronteiras de serviço
- Quando invocado pelo warrior-theseus ou warrior-prometheus como primeira fase do design de feature
- Quando a equipe precisa de uma Linguagem Ubíqua compartilhada antes do início da implementação

## Inputs

| Input | Obrigatório | Descrição |
|-------|:-----------:|-----------|
| Descrição do domínio | Sim | Domínio de negócio, escopo da feature ou módulo a ser modelado |
| Nome do módulo | Sim | Identificador do módulo Guardia (ex.: `platform`, `reconciliation`, `fiscal`) |
| Entidades conhecidas | Não | Entidades já identificadas; se fornecidas, validar e estender a partir delas |
| Escopo de bounded context | Não | Único ou múltiplos contextos; se omitido, o agente determina a partir da descrição |

## Fluxo de Trabalho

```
Progresso:
- [ ] 1. Ler diretivas e escopo
- [ ] 2. Consultar Lexis e Codex
- [ ] 3. Elicitar descrição do domínio
- [ ] 4. Definir Linguagem Ubíqua
- [ ] 5. Mapear Bounded Contexts
- [ ] 6. Definir Entidades e Agregados
- [ ] 7. Definir Use Cases e Application Services
- [ ] 8. Identificar eventos de integração e anti-corruption layers
- [ ] 9. Desenhar Context Map
- [ ] 10. Produzir documento de modelo de domínio
```

### Passo 1: Ler Diretivas e Escopo

1. Ler `.ahrena/.directives` para obter `paths.domain`, `language.default` e nome do módulo
2. Confirmar que a descrição do domínio e o nome do módulo foram fornecidos; se insuficientes, **perguntar ao usuário** (Qual é o processo de negócio principal? Quem são os atores? Quais são os limites do sistema? O que dispara a primeira ação?) e aguardar respostas
3. Verificar se já existe um documento de modelo de domínio em `paths.domain` para este módulo — incorporá-lo como input se disponível
4. Identificar o escopo de bounded context: único ou múltiplos contextos

### Passo 2: Consultar Lexis e Codex

1. Consultar **lex-entities** — toda entidade persistente DEVE ter entity_id (UUID v7), entity_type, version, created_at, updated_at, discarded_at
2. Consultar **lex-entity-naming** — `entity_type` e nomes de campo usam snake_case; nomes de agregados em documentos DDD usam PascalCase
3. Consultar **lex-cloudevents** — eventos seguem `event.guardia.{module}.{entity_type}.{event_name}` com segmentos em snake_case
4. Consultar **codex-entities** — referência do modelo de entidades base

### Passo 3: Elicitar Descrição do Domínio

Se a descrição do domínio for insuficiente para iniciar a modelagem, fazer perguntas direcionadas ao usuário:

1. **Processo de negócio:** "Descreva o fluxo principal passo a passo. O que o inicia e o que o conclui?"
2. **Atores:** "Quem inicia as ações — usuários, sistemas externos, jobs agendados?"
3. **Regras de negócio:** "Quais são as principais restrições? O que pode ou não pode acontecer?"
4. **Limites do sistema:** "O que está dentro deste módulo e o que pertence a outro serviço?"
5. **Pontos problemáticos conhecidos:** "Há áreas do domínio que são pouco claras ou disputadas?"

Aguardar respostas antes de prosseguir para o Passo 4.

### Passo 4: Definir Linguagem Ubíqua

Estabelecer um vocabulário compartilhado que especialistas de domínio e engenheiros usarão consistentemente:

1. Para cada termo-chave do domínio, documentar:
   - **Termo** — nome acordado (PascalCase para entidades/agregados, simples para conceitos)
   - **Definição** — significado preciso neste bounded context
   - **Sinônimos a evitar** — termos alternativos que não devem ser usados (para evitar ambiguidade)
2. Resolver conflitos de nomenclatura: se dois stakeholders usam termos diferentes para o mesmo conceito, acordar em um e documentar o alternativo rejeitado
3. Validar termos contra lex-entity-naming: nomes de entidade em snake_case para APIs/eventos, PascalCase em documentos DDD

Exemplo de entrada no glossário:
| Termo | Definição | Sinônimos a Evitar |
|-------|-----------|-------------------|
| ScheduledTransfer | Transferência bancária ordenada por um contador para execução em data futura, exigindo aprovação do supervisor | "transferência planejada", "pagamento futuro" |
| Execution | O momento em que a transferência é processada pelo parceiro bancário na data agendada | "processamento", "liquidação" |

### Passo 5: Mapear Bounded Contexts

Um Bounded Context é um limite dentro do qual um modelo de domínio específico é definido e aplicável:

1. Identificar limites onde os termos mudam de significado ou a responsabilidade muda
2. Para cada Bounded Context, documentar:
   - **Nome** — descritivo, reflete sua responsabilidade (ex.: `ScheduledPayments`, `Approval`, `Reconciliation`)
   - **Responsabilidade** — o que possui e decide
   - **Responsável** — equipe ou serviço responsável
   - **Entidades que possui** — lista de agregados dentro deste contexto
3. Marcar entidades que aparecem em múltiplos contextos — exigirão mapeamento explícito nos limites
4. Sinalizar limites de contexto que não estão claros como hotspots

### Passo 6: Definir Entidades e Agregados

#### Entidades

Para cada entidade persistente, documentar (conforme lex-entities):

| Campo | Requisito |
|-------|-----------|
| Nome | PascalCase no documento DDD; snake_case como `entity_type` em APIs/eventos |
| `entity_type` | String em snake_case (ex.: `scheduled_transfer`) |
| Bounded Context | Qual contexto é dono desta entidade |
| Campos-chave | Atributos relevantes para o negócio (além da estrutura base) |
| Estados do ciclo de vida | Estados pelos quais a entidade transita (ex.: `requested → approved → executed`) |

Todas as entidades DEVEM incluir a estrutura base do lex-entities: `entity_id`, `entity_type`, `version`, `created_at`, `updated_at`, `discarded_at`.

#### Agregados

Um Agregado é um conjunto de entidades e value objects tratados como uma única unidade com uma entidade raiz:

1. Identificar a **Raiz do Agregado** — o ponto de entrada; todas as referências externas passam por ela
2. Documentar:
   - **Raiz do Agregado** — a entidade raiz (ex.: `ScheduledTransfer`)
   - **Membros** — entidades e value objects dentro do limite do agregado
   - **Invariantes** — regras de negócio que sempre se mantêm no agregado (ex.: "Um ScheduledTransfer não pode ser executado se seu status não for `approved`")
   - **Comandos aceitos** — operações que o agregado processa
   - **Eventos produzidos** — eventos de domínio emitidos na mudança de estado

### Passo 7: Definir Use Cases e Application Services

Use Cases descrevem o que o sistema faz da perspectiva do ator:

1. Para cada use case, documentar:
   - **Nome** — verbo imperativo + substantivo (ex.: `RequestScheduledTransfer`, `ApproveScheduledTransfer`)
   - **Ator** — quem inicia (papel de usuário, sistema externo, scheduler)
   - **Pré-condições** — o que deve ser verdade antes do use case poder executar
   - **Passos** — sequência ordenada de ações
   - **Pós-condições** — o que é verdade após execução bem-sucedida
   - **Caminhos de falha** — o que acontece quando o use case não pode completar (listar como hotspots se indefinidos)
   - **Agregado tocado** — qual agregado processa o comando
   - **Eventos emitidos** — eventos de domínio produzidos no sucesso

2. Agrupar use cases por ator ou por agregado para legibilidade

### Passo 8: Identificar Eventos de Integração e Anti-Corruption Layers

**Eventos de integração** cruzam limites de bounded context:

1. Para cada evento que deve sair do bounded context, documentar:
   - **Tipo de evento** — `event.guardia.{module}.{entity_type}.{event_name}` (lex-cloudevents)
   - **Publicador** — qual bounded context / agregado o produz
   - **Consumidores** — quais contextos o consomem
   - **Esboço de payload** — campos de dados principais (snake_case conforme lex-entity-naming)
2. Sinalizar eventos onde o mesmo conceito tem nomes diferentes em contextos diferentes — exigem **tradução no limite**

**Anti-Corruption Layers (ACL):**

1. Identificar sistemas externos cujos modelos diferem do modelo de domínio Guardia
2. Para cada ACL, documentar:
   - **Sistema externo** — nome e responsável
   - **Tradução** — como conceitos externos mapeiam para entidades Guardia
   - **Direção** — entrada (externo → Guardia) ou saída (Guardia → externo)

### Passo 9: Desenhar Context Map

Produzir um Context Map textual ou em tabela Markdown mostrando relacionamentos entre bounded contexts:

| Padrão de Relacionamento | Quando Usar |
|--------------------------|-------------|
| **Shared Kernel** | Dois contextos compartilham um subconjunto do modelo de domínio; mudanças requerem coordenação |
| **Customer/Supplier** | Contexto upstream fornece o que o downstream consome; downstream tem requisitos |
| **Conformist** | Downstream adota o modelo upstream sem influência |
| **Anti-Corruption Layer** | Downstream traduz o modelo upstream para proteger o seu próprio |
| **Open Host Service** | Upstream publica um protocolo / API para múltiplos downstreams |
| **Published Language** | Linguagem compartilhada (ex.: CloudEvents) usada entre contextos |

Para cada par de contextos com relacionamento, documentar o padrão e quaisquer restrições.

### Passo 10: Produzir Documento de Modelo de Domínio

Gerar um documento Markdown estruturado e salvá-lo em `paths.domain`:

1. **Cabeçalho** — módulo, descrição do domínio, data, participantes, escopo
2. **Linguagem Ubíqua** — tabela de glossário: Termo | Definição | Sinônimos a Evitar
3. **Bounded Contexts** — uma subseção por contexto: nome, responsabilidade, responsável, entidades que possui
4. **Catálogo de Entidades e Agregados** — tabela: Entidade | entity_type | Bounded Context | Estados do Ciclo de Vida | Raiz do Agregado
5. **Detalhes dos Agregados** — uma subseção por agregado: raiz, membros, invariantes, comandos, eventos
6. **Use Cases** — uma subseção por use case: ator, pré-condições, passos, pós-condições, caminhos de falha, eventos emitidos
7. **Eventos de Integração** — tabela: Tipo de Evento | Publicador | Consumidores | Esboço de Payload
8. **Anti-Corruption Layers** — tabela: Sistema Externo | Direção | Tradução
9. **Context Map** — tabela ou diagrama: Contexto A | Relacionamento | Contexto B | Restrições
10. **Hotspots em Aberto** — tabela: Descrição | Prioridade (P1/P2/P3) | Responsável

## Outputs

| Output | Formato | Destino |
|--------|---------|---------|
| Documento de modelo de domínio | Markdown | `paths.domain` (ex.: `docs/domain/{module}-domain-model.md`) |
| Glossário de linguagem ubíqua | Tabela no documento | Compartilhado com a equipe antes da implementação |
| Catálogo de entidades/agregados | Tabela no documento | Input para warrior-daedalus (APIs) e warrior-kronos (eventos) |
| Lista de eventos de integração | Tabela no documento | Input para warrior-kronos (documentação de eventos) |

## Exemplo de Execução

### Input

```
Domínio: Transferências agendadas — contadores agendam transferências bancárias futuras; aprovação do supervisor obrigatória antes da execução; um scheduler dispara a execução na data agendada.
Módulo: platform
```

### Resumo do Output

Arquivo `docs/domain/platform-domain-model.md` contendo:

**Linguagem Ubíqua:**
| Termo | Definição | Sinônimos a Evitar |
|-------|-----------|-------------------|
| ScheduledTransfer | Transferência ordenada para execução futura, exigindo aprovação | "transferência planejada", "pagamento futuro" |
| Execution | Processamento pelo parceiro bancário na data agendada | "processamento", "liquidação" |

**Bounded Contexts:** `ScheduledPayments` (dono de ScheduledTransfer), `Approval` (dono do fluxo de aprovação), `BankingIntegration` (ACL para parceiro bancário)

**Catálogo de Entidades:**
| Entidade | entity_type | Bounded Context | Ciclo de Vida |
|----------|-------------|-----------------|---------------|
| ScheduledTransfer | `scheduled_transfer` | ScheduledPayments | requested → approved → executed \| failed \| cancelled |

**Use Cases:** `RequestScheduledTransfer`, `ApproveScheduledTransfer`, `ExecuteScheduledTransfer`, `CancelScheduledTransfer`

**Eventos de Integração:** `event.guardia.platform.scheduled_transfer.requested`, `.approved`, `.executed`, `.failed`, `.cancelled`

**Hotspots em Aberto:**
| Descrição | Prioridade | Responsável |
|-----------|------------|-------------|
| Política de retry em falha de execução não definida | P1 | Equipe de plataforma |

## Restrições

- Este Kata produz apenas o documento de modelo de domínio; não desenha APIs nem documenta CloudEvents
- Não omitir a identificação de hotspots — toda incerteza não documentada se torna um bug ou lacuna de escopo
- O catálogo de entidades DEVE ser completo o suficiente para alimentar warrior-daedalus e warrior-kronos sem descoberta adicional
- Escalar para humano quando a responsabilidade do bounded context for ambígua ou quando um único agregado abranger múltiplas equipes sem um dono claro
- Valores de entity_type no catálogo DEVEM estar em snake_case (lex-entity-naming); nomes de agregados nas seções DDD DEVEM estar em PascalCase

## Referências

- `lex-entities` — estrutura base de entidades
- `lex-entity-naming` — snake_case para entity_type, campos e segmentos CloudEvents
- `lex-cloudevents` — formato do tipo CloudEvents
- `codex-entities` — referência do modelo de entidades
- [Domain-Driven Design — Eric Evans](https://www.domainlanguage.com/ddd/reference/)
- [Implementing Domain-Driven Design — Vaughn Vernon](https://vaughnvernon.com/)
